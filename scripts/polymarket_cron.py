"""
Polymarket Cron — Hourly scan wrapper for scheduling.

Runs the scanner, sends qualifying signals to approval channel,
and auto-resolves any closed markets. Designed for Windows Task Scheduler or cron.

Usage:
    python scripts/polymarket_cron.py                  # Run full cycle
    python scripts/polymarket_cron.py --scan-only      # Scan without sending to Telegram
    python scripts/polymarket_cron.py --resolve-only   # Only auto-resolve, no scan
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from polymarket_scanner import run_scan
from polymarket_bot import send_to_approval
from polymarket_tracker import auto_resolve, ensure_signals_log

# --- Paths ---

VAULT_DIR = os.path.join(os.path.dirname(__file__), "..")
SCAN_LOG = os.path.join(VAULT_DIR, "07-Analytics", "polymarket", "scan-log.md")


# --- Logging ---

def log_scan_run(signals_found, signals_sent, resolved, errors=None):
    """Log scan run to scan-log.md."""
    os.makedirs(os.path.dirname(SCAN_LOG), exist_ok=True)

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    # Create log file if it doesn't exist
    if not os.path.exists(SCAN_LOG):
        header = """# Polymarket Scan Log

> Automated scan runs logged here.

| Timestamp | Signals Found | Sent to Approval | Resolved | Errors |
|-----------|---------------|------------------|----------|--------|
"""
        with open(SCAN_LOG, "w", encoding="utf-8") as f:
            f.write(header)

    # Append row
    error_str = str(errors) if errors else "—"
    row = f"| {timestamp} | {signals_found} | {signals_sent} | {resolved} | {error_str} |\n"

    with open(SCAN_LOG, "a", encoding="utf-8") as f:
        f.write(row)


# --- Main Cycle ---

def run_full_cycle(scan_only=False, resolve_only=False):
    """Run the full scan-approve-resolve cycle."""
    now = datetime.now(timezone.utc)
    print(f"\n{'='*50}")
    print(f"  POLYMARKET SCAN — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}\n")

    signals_found = 0
    signals_sent = 0
    resolved_count = 0
    errors = []

    # Ensure signals log exists
    ensure_signals_log()

    # Phase 1: Auto-resolve existing signals
    if not scan_only:
        print("--- Phase 1: Auto-resolve ---")
        try:
            updates = auto_resolve()
            resolved_count = len(updates)
        except Exception as e:
            errors.append(f"resolve: {e}")
            print(f"ERROR in auto-resolve: {e}")

    # Phase 2: Scan for new signals
    if not resolve_only:
        print("\n--- Phase 2: Scan markets ---")
        try:
            signals = run_scan(json_output=False)
            signals_found = len(signals)

            if signals and not scan_only:
                print(f"\nSending {len(signals)} signal(s) to approval channel...")
                for signal in signals:
                    try:
                        msg_id = send_to_approval(signal)
                        if msg_id:
                            signals_sent += 1
                    except Exception as e:
                        errors.append(f"send: {e}")
                        print(f"  ERROR sending signal: {e}")
        except Exception as e:
            errors.append(f"scan: {e}")
            print(f"ERROR in scan: {e}")

    # Log results
    log_scan_run(
        signals_found=signals_found,
        signals_sent=signals_sent,
        resolved=resolved_count,
        errors="; ".join(errors) if errors else None,
    )

    # Summary
    print(f"\n{'='*50}")
    print(f"  SCAN COMPLETE")
    print(f"  Signals found:       {signals_found}")
    print(f"  Sent to approval:    {signals_sent}")
    print(f"  Markets resolved:    {resolved_count}")
    if errors:
        print(f"  Errors:              {len(errors)}")
    print(f"{'='*50}\n")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Polymarket Cron — Hourly scan automation")
    parser.add_argument("--scan-only", action="store_true", help="Scan without sending to Telegram")
    parser.add_argument("--resolve-only", action="store_true", help="Only auto-resolve, no scan")
    args = parser.parse_args()

    run_full_cycle(scan_only=args.scan_only, resolve_only=args.resolve_only)


if __name__ == "__main__":
    main()
