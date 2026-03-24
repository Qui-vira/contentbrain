"""
Unified Auto-Scanner — Orchestrates crypto, forex, and polymarket scanning.

Runs all three signal sources on a schedule with daily caps,
ranks signals by strength, and sends top signals for approval.

Usage:
    python scripts/unified_auto_scanner.py              # Single run (for cron/testing)
    python scripts/unified_auto_scanner.py --dry-run    # Scan without sending signals
"""

import os
import sys
import json
import argparse
import subprocess
import time
from datetime import datetime, timezone

# Ensure scripts directory is on path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from market_data import get_kill_zone

# --- Config ---

VAULT_DIR = os.path.join(os.path.dirname(__file__), "..")
STATE_FILE = os.path.join(VAULT_DIR, "07-Analytics", "signal-performance", "auto_scan_state.json")
SCAN_LOG = os.path.join(VAULT_DIR, "07-Analytics", "auto-scan-log.md")
SCRIPTS_DIR = os.path.dirname(__file__)

DEFAULT_CAP = int(os.getenv("AUTO_SIGNAL_CAP", "3"))


# --- State Management ---

def load_state():
    """Load auto-scan state. Resets daily."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            # Reset if date changed
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if state.get('date') != today:
                return _new_state()
            return state
        except (json.JSONDecodeError, IOError):
            pass
    return _new_state()


def _new_state():
    """Create fresh daily state."""
    return {
        'date': datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        'signals_sent': 0,
        'cap_override': None,
        'last_scan_at': None,
    }


def save_state(state):
    """Save state to disk."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_cap(state):
    """Get current daily cap (override or env default)."""
    override = state.get('cap_override')
    if override is not None:
        return int(override)
    return DEFAULT_CAP


def update_cap(new_cap):
    """Update the daily cap override. Called by /setcap command."""
    state = load_state()
    state['cap_override'] = int(new_cap)
    save_state(state)
    return get_cap(state)


# --- Runner Subprocess ---

def run_scanner(script_name, label):
    """Run a scanner script via subprocess. Returns True on success."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"  [{label}] Script not found: {script_path}")
        return False

    print(f"  [{label}] Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True,
            timeout=600,  # 10 min max
            cwd=VAULT_DIR,
        )
        if result.returncode != 0:
            print(f"  [{label}] Error: {result.stderr[:200]}")
            return False
        # Print last line of output as status
        lines = result.stdout.strip().split('\n')
        if lines:
            print(f"  [{label}] {lines[-1]}")
        return True
    except subprocess.TimeoutExpired:
        print(f"  [{label}] Timed out after 600s")
        return False
    except Exception as e:
        print(f"  [{label}] Failed: {e}")
        return False


# --- Signal Collection ---

def collect_crypto_signals():
    """Load crypto trading signals from binance_ta_summary.json."""
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        for s in signals:
            s['market_type'] = 'CRYPTO'
        return signals
    except Exception as e:
        print(f"  [CRYPTO] Signal load error: {e}")
        return []


def collect_forex_signals():
    """Load forex trading signals from forex_ta_summary.json."""
    try:
        from forex_ta_runner import load_forex_signals
        signals = load_forex_signals(max_age_minutes=90)
        # market_type already set by load_forex_signals
        return signals
    except Exception as e:
        print(f"  [FOREX] Signal load error: {e}")
        return []


def collect_polymarket_signals():
    """Run polymarket scan and return qualifying signals."""
    try:
        from polymarket_scanner import run_scan
        raw_signals = run_scan(json_output=False)
        if not raw_signals:
            return []

        # Filter: edge >= 5% and confidence >= 65
        signals = []
        for s in raw_signals:
            edge = s.get('edge', 0)
            confidence = s.get('confidence', 0)
            if edge >= 0.05 and confidence >= 65:
                s['market_type'] = 'POLYMARKET'
                signals.append(s)
        return signals
    except Exception as e:
        print(f"  [POLYMARKET] Scan error: {e}")
        return []


# --- Signal Ranking ---

def rank_signals(all_signals):
    """Rank all signals by strength. Trading by strength_score, polymarket by edge*100."""
    def sort_key(s):
        if s.get('market_type') == 'POLYMARKET':
            return s.get('edge', 0) * 100
        return s.get('strength_score', 0)

    return sorted(all_signals, key=sort_key, reverse=True)


# --- Logging ---

def log_scan_run(session, crypto_count, forex_count, poly_count, sent_count, cap):
    """Append scan run to auto-scan-log.md."""
    os.makedirs(os.path.dirname(SCAN_LOG), exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # Create file with header if needed
    if not os.path.exists(SCAN_LOG):
        header = (
            "# Auto-Scan Log\n\n"
            "| Timestamp | Session | Crypto | Forex | Poly | Sent | Cap |\n"
            "|-----------|---------|--------|-------|------|------|-----|\n"
        )
        with open(SCAN_LOG, 'w', encoding='utf-8') as f:
            f.write(header)

    row = f"| {now} | {session} | {crypto_count} | {forex_count} | {poly_count} | {sent_count} | {cap} |\n"
    with open(SCAN_LOG, 'a', encoding='utf-8') as f:
        f.write(row)


# --- Main Orchestrator ---

def run_auto_scan(dry_run=False):
    """Run one cycle of the unified auto-scanner."""
    print("=" * 50)
    print(f"UNIFIED AUTO-SCANNER — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    # 0. Cooldown check — skip if last scan was < 4 hours ago
    scan_interval_hours = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))
    state = load_state()
    last_scan = state.get('last_scan_at')
    if last_scan:
        try:
            last_dt = datetime.fromisoformat(last_scan)
            hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
            if hours_since < scan_interval_hours:
                print(f"Cooldown active: last scan was {hours_since:.1f}h ago "
                      f"(need {scan_interval_hours}h). Skipping.")
                return
        except (ValueError, TypeError):
            pass  # corrupted timestamp, proceed with scan

    # 1. Check session
    session, is_active = get_kill_zone()
    print(f"Session: {session} ({'ACTIVE' if is_active else 'off-session'})")
    cap = get_cap(state)
    remaining = cap - state['signals_sent']

    if remaining <= 0:
        print(f"Daily cap reached ({state['signals_sent']}/{cap}). Exiting.")
        state['last_scan_at'] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        log_scan_run(session, 0, 0, 0, 0, cap)
        return

    print(f"Daily cap: {state['signals_sent']}/{cap} used, {remaining} remaining")

    # 3. Run scanners
    # Crypto runs 24/7 (market never closes). Forex only during kill zones.
    crypto_ran = run_scanner('binance_ta_runner.py', 'CRYPTO')
    forex_ran = False

    if is_active:
        forex_ran = run_scanner('forex_ta_runner.py', 'FOREX')
    else:
        print(f"  Skipping forex scanner (off-session: {session})")

    # 4. Collect signals
    print("\nCollecting signals...")
    crypto_signals = collect_crypto_signals() if crypto_ran else []
    forex_signals = collect_forex_signals() if forex_ran else []
    poly_signals = collect_polymarket_signals()

    # Tag all as auto-sourced
    for s in crypto_signals + forex_signals + poly_signals:
        s['source'] = 'auto'

    print(f"  Crypto: {len(crypto_signals)} | Forex: {len(forex_signals)} | Polymarket: {len(poly_signals)}")

    # 5. Rank and select top signals
    all_signals = crypto_signals + forex_signals + poly_signals
    ranked = rank_signals(all_signals)
    to_send = ranked[:remaining]

    if not to_send:
        print("\nNo qualifying signals found.")
        state['last_scan_at'] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        log_scan_run(session, len(crypto_signals), len(forex_signals), len(poly_signals), 0, cap)
        return

    # 6. Send signals
    print(f"\nSending top {len(to_send)} signal(s) for approval...")

    if dry_run:
        for i, s in enumerate(to_send, 1):
            mtype = s.get('market_type', '?')
            if mtype == 'POLYMARKET':
                label = s.get('market_question', 'N/A')[:40]
                score = f"edge={s.get('edge', 0)*100:.1f}%"
            else:
                label = f"{s.get('pair', '?')} {s.get('timeframe', '?')} {s.get('direction', '?')}"
                score = f"strength={s.get('strength_score', 0)}/10"
            print(f"  {i}. [{mtype}] {label} ({score})")
        print("\n[DRY RUN] No signals sent.")
        log_scan_run(session, len(crypto_signals), len(forex_signals), len(poly_signals), 0, cap)
        return

    sent_count = 0
    from polymarket_bot import send_to_approval, _send_to_test_channel, TEST_CHANNEL_ID

    # Auto-send ALL qualifying signals to test channel (no approval needed)
    if TEST_CHANNEL_ID and to_send:
        test_sent = _send_to_test_channel(to_send)
        print(f"  [TEST] Auto-sent {test_sent} signal(s) to test channel.")

    for s in to_send:
        mtype = s.get('market_type', 'UNKNOWN')
        # Add auto-scan prefix to signal for Telegram formatting
        s['auto_scan_prefix'] = f"[AUTO] [{mtype}] SIGNAL"
        s['auto_scan_footer'] = f"Source: Auto-scan | Session: {session} | Daily cap: {state['signals_sent'] + sent_count + 1}/{cap}"

        msg_id = send_to_approval(s)
        if msg_id:
            sent_count += 1
            if s.get('signal_type') == 'trading':
                print(f"  Sent: [{mtype}] {s.get('pair', '?')} {s.get('direction', '?')} (msg:{msg_id})")
            else:
                print(f"  Sent: [{mtype}] {s.get('market_question', '?')[:40]} (msg:{msg_id})")

    # 7. Update state
    state['signals_sent'] += sent_count
    state['last_scan_at'] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    # 8. Log
    log_scan_run(session, len(crypto_signals), len(forex_signals), len(poly_signals), sent_count, cap)

    print(f"\nScan complete. {sent_count} signal(s) sent. "
          f"Daily total: {state['signals_sent']}/{cap}")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='Unified Auto-Scanner — Crypto + Forex + Polymarket')
    parser.add_argument('--dry-run', action='store_true', help='Scan without sending signals')
    args = parser.parse_args()

    run_auto_scan(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
