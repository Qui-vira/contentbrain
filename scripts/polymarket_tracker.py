"""
Polymarket Portfolio Tracker — Signal tracking + auto-resolve.

Tracks all approved Polymarket signals, auto-resolves by checking the
Polymarket API for closed markets, and calculates performance metrics.

Usage:
    python scripts/polymarket_tracker.py --status             # Show all active signals
    python scripts/polymarket_tracker.py --resolve            # Auto-resolve closed markets
    python scripts/polymarket_tracker.py --performance        # Win rate, ROI, breakdown
    python scripts/polymarket_tracker.py --weekly             # Weekly summary report
    python scripts/polymarket_tracker.py --json               # JSON output
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from polymarket_scanner import GAMMA_API, fetch_active_markets

# --- Paths ---

VAULT_DIR = os.path.join(os.path.dirname(__file__), "..")
SIGNALS_LOG = os.path.join(
    VAULT_DIR, "07-Analytics", "signal-performance", "polymarket-signals-log.md"
)
SCAN_LOG = os.path.join(
    VAULT_DIR, "07-Analytics", "polymarket", "scan-log.md"
)


# --- Signals Log Management ---

def ensure_signals_log():
    """Create the polymarket signals log if it doesn't exist."""
    if os.path.exists(SIGNALS_LOG):
        return

    os.makedirs(os.path.dirname(SIGNALS_LOG), exist_ok=True)
    content = """# Polymarket Signals Log

> Every approved Polymarket signal is logged here. Used by /signal-tracker for performance calculations.
> Source: polymarket-scanner

---

## Log Format

| # | Date | Market | Recommendation | Odds@Entry | Model% | Edge% | Confidence | Status | Result | P&L |
|---|------|--------|----------------|------------|--------|-------|------------|--------|--------|-----|

---

## Status Key

- **ACTIVE** — Approved and tracking
- **WON** — Market resolved in our favor
- **LOST** — Market resolved against us
- **EXPIRED** — Market expired without resolution
- **CANCELLED** — Rejected before distribution

---

*Log begins when the system goes live.*
"""
    with open(SIGNALS_LOG, "w", encoding="utf-8") as f:
        f.write(content)


def parse_signals_log():
    """Parse the polymarket-signals-log.md markdown table."""
    ensure_signals_log()

    with open(SIGNALS_LOG, "r", encoding="utf-8") as f:
        content = f.read()

    signals = []
    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip header and separator rows
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 11:
            continue
        if cells[0] in ("#", "---", ""):
            continue
        if not cells[0].strip().isdigit():
            continue

        signals.append({
            "num": int(cells[0]),
            "date": cells[1],
            "market": cells[2],
            "recommendation": cells[3],
            "odds_at_entry": cells[4],
            "model_pct": cells[5],
            "edge_pct": cells[6],
            "confidence": cells[7],
            "status": cells[8],
            "result": cells[9],
            "pnl": cells[10],
        })

    return signals


def update_signal_status(signal_num, new_status, result="", pnl=""):
    """Update a signal's status in the log."""
    with open(SIGNALS_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 11:
            continue
        if not cells[0].strip().isdigit():
            continue
        if int(cells[0]) == signal_num:
            cells[8] = new_status
            if result:
                cells[9] = result
            if pnl:
                cells[10] = pnl
            lines[i] = "| " + " | ".join(cells) + " |\n"
            updated = True
            break

    if updated:
        with open(SIGNALS_LOG, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return updated


# --- Auto-Resolve ---

def fetch_resolved_markets():
    """Fetch recently closed/resolved markets from Polymarket."""
    url = f"{GAMMA_API}/markets"
    params = {
        "closed": "true",
        "limit": "50",
        "order": "endDate",
        "ascending": "false",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("data", [])
    except requests.RequestException as e:
        print(f"ERROR fetching resolved markets: {e}")
        return []


def determine_winner(market):
    """Determine which outcome won based on outcomePrices."""
    prices_str = market.get("outcomePrices", "")
    try:
        if isinstance(prices_str, str):
            prices = json.loads(prices_str)
        else:
            prices = prices_str
        if not prices:
            return None
        # "1" at position 0 = YES won, "1" at position 1 = NO won
        yes_price = float(prices[0])
        no_price = float(prices[1]) if len(prices) > 1 else (1 - yes_price)

        if yes_price >= 0.95:
            return "YES"
        elif no_price >= 0.95:
            return "NO"
        else:
            return None  # Not yet fully resolved
    except (json.JSONDecodeError, TypeError, IndexError):
        return None


def auto_resolve():
    """Check resolved markets and update signal statuses."""
    signals = parse_signals_log()
    active_signals = [s for s in signals if s["status"] == "ACTIVE"]

    if not active_signals:
        print("No active signals to resolve.")
        return []

    print(f"Checking {len(active_signals)} active signal(s) against resolved markets...")

    resolved_markets = fetch_resolved_markets()
    if not resolved_markets:
        print("Could not fetch resolved markets.")
        return []

    # Build lookup of resolved market questions
    resolved_lookup = {}
    for m in resolved_markets:
        q = m.get("question", "").lower()
        winner = determine_winner(m)
        if winner:
            resolved_lookup[q] = winner

    updates = []
    for signal in active_signals:
        market_name = signal["market"].lower()
        # Try to match by partial question
        for resolved_q, winner in resolved_lookup.items():
            if market_name in resolved_q or resolved_q in market_name:
                rec = signal["recommendation"]
                won = (rec == winner)
                new_status = "WON" if won else "LOST"
                result = f"{winner} won"

                # Calculate P&L
                try:
                    odds_str = signal["odds_at_entry"].replace("%", "").split("/")[0]
                    entry_odds = float(odds_str) / 100
                    if won:
                        pnl = f"+{((1/entry_odds - 1) * 100):.0f}%"
                    else:
                        pnl = "-100%"
                except (ValueError, IndexError):
                    pnl = "WON" if won else "LOST"

                update_signal_status(signal["num"], new_status, result, pnl)
                updates.append({
                    "signal": signal["num"],
                    "market": signal["market"],
                    "old_status": "ACTIVE",
                    "new_status": new_status,
                    "result": result,
                    "pnl": pnl,
                })
                print(f"  #{signal['num']} {signal['market'][:40]}: {new_status} ({result})")
                break

    if not updates:
        print("No signals resolved in this check.")

    return updates


# --- Performance Metrics ---

def calculate_performance(signals=None):
    """Calculate performance metrics from signals log."""
    if signals is None:
        signals = parse_signals_log()

    resolved = [s for s in signals if s["status"] in ("WON", "LOST")]

    if not resolved:
        return {
            "total_signals": len(signals),
            "active": len([s for s in signals if s["status"] == "ACTIVE"]),
            "resolved": 0,
            "win_rate": 0,
            "wins": 0,
            "losses": 0,
            "avg_confidence": 0,
            "avg_edge": 0,
            "categories": {},
        }

    wins = [s for s in resolved if s["status"] == "WON"]
    losses = [s for s in resolved if s["status"] == "LOST"]
    win_rate = len(wins) / len(resolved) * 100 if resolved else 0

    # Average confidence and edge
    confidences = []
    edges = []
    for s in resolved:
        try:
            confidences.append(float(s["confidence"]))
        except ValueError:
            pass
        try:
            edge_val = s["edge_pct"].replace("+", "").replace("%", "")
            edges.append(float(edge_val))
        except ValueError:
            pass

    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    avg_edge = sum(edges) / len(edges) if edges else 0

    # Category breakdown
    categories = {}
    for s in resolved:
        # Extract category from market name (rough heuristic)
        cat = "other"
        market_lower = s["market"].lower()
        for c in ["crypto", "politics", "sports", "culture", "science"]:
            if c in market_lower:
                cat = c
                break
        if cat not in categories:
            categories[cat] = {"wins": 0, "losses": 0}
        if s["status"] == "WON":
            categories[cat]["wins"] += 1
        else:
            categories[cat]["losses"] += 1

    return {
        "total_signals": len(signals),
        "active": len([s for s in signals if s["status"] == "ACTIVE"]),
        "resolved": len(resolved),
        "win_rate": round(win_rate, 1),
        "wins": len(wins),
        "losses": len(losses),
        "avg_confidence": round(avg_conf, 1),
        "avg_edge": round(avg_edge, 1),
        "categories": categories,
    }


def print_performance(metrics, json_output=False):
    """Print performance report."""
    if json_output:
        print(json.dumps(metrics, indent=2))
        return

    print("\n" + "=" * 50)
    print("  POLYMARKET SIGNAL PERFORMANCE")
    print("=" * 50)
    print(f"  Total Signals:    {metrics['total_signals']}")
    print(f"  Active:           {metrics['active']}")
    print(f"  Resolved:         {metrics['resolved']}")
    print(f"  Win Rate:         {metrics['win_rate']}%")
    print(f"  Wins/Losses:      {metrics['wins']}W / {metrics['losses']}L")
    print(f"  Avg Confidence:   {metrics['avg_confidence']}")
    print(f"  Avg Edge:         +{metrics['avg_edge']}%")

    if metrics["categories"]:
        print(f"\n  Category Breakdown:")
        for cat, data in metrics["categories"].items():
            total = data["wins"] + data["losses"]
            wr = data["wins"] / total * 100 if total > 0 else 0
            print(f"    {cat.upper():12s} {data['wins']}W/{data['losses']}L ({wr:.0f}%)")

    print("=" * 50 + "\n")


def generate_weekly_report():
    """Generate weekly summary report."""
    signals = parse_signals_log()
    metrics = calculate_performance(signals)

    # Filter to last 7 days
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    weekly_signals = []
    for s in signals:
        try:
            sig_date = datetime.strptime(s["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if sig_date >= week_ago:
                weekly_signals.append(s)
        except ValueError:
            pass

    weekly_metrics = calculate_performance(weekly_signals)

    report = f"""# Polymarket Weekly Report — {now.strftime('%Y-%m-%d')}

## This Week
- Signals generated: {len(weekly_signals)}
- Resolved: {weekly_metrics['resolved']}
- Win rate: {weekly_metrics['win_rate']}%
- Record: {weekly_metrics['wins']}W / {weekly_metrics['losses']}L

## All-Time
- Total signals: {metrics['total_signals']}
- Win rate: {metrics['win_rate']}%
- Record: {metrics['wins']}W / {metrics['losses']}L
- Avg confidence: {metrics['avg_confidence']}
- Avg edge: +{metrics['avg_edge']}%

## Active Positions
"""
    active = [s for s in signals if s["status"] == "ACTIVE"]
    if active:
        for s in active:
            report += f"- #{s['num']} {s['market']} — {s['recommendation']} ({s['confidence']})\n"
    else:
        report += "- None\n"

    report += f"\n---\n*Generated: {now.isoformat()}*\n"

    # Save report
    report_dir = os.path.join(VAULT_DIR, "07-Analytics", "polymarket")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"weekly-{now.strftime('%Y-%m-%d')}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report, report_path


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Polymarket Portfolio Tracker")
    parser.add_argument("--status", action="store_true", help="Show all active signals")
    parser.add_argument("--resolve", action="store_true", help="Auto-resolve closed markets")
    parser.add_argument("--performance", action="store_true", help="Show performance metrics")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--init", action="store_true", help="Initialize signals log file")
    args = parser.parse_args()

    if args.init:
        ensure_signals_log()
        print(f"Signals log ready at: {SIGNALS_LOG}")
        return

    if args.status:
        signals = parse_signals_log()
        active = [s for s in signals if s["status"] == "ACTIVE"]
        if args.json:
            print(json.dumps(active, indent=2))
        elif active:
            print(f"\nActive Polymarket Signals ({len(active)}):\n")
            for s in active:
                print(f"  #{s['num']} | {s['date']} | {s['market'][:40]} | "
                      f"{s['recommendation']} | Edge: {s['edge_pct']} | Conf: {s['confidence']}")
            print()
        else:
            print("No active signals.")
        return

    if args.resolve:
        updates = auto_resolve()
        if args.json:
            print(json.dumps(updates, indent=2))
        return

    if args.performance:
        metrics = calculate_performance()
        print_performance(metrics, json_output=args.json)
        return

    if args.weekly:
        report, path = generate_weekly_report()
        if args.json:
            print(json.dumps({"report": report, "path": path}))
        else:
            print(report)
            print(f"\nSaved to: {path}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
