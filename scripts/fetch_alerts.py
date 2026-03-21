"""
Fetch unprocessed TradingView webhook alerts from Supabase.
Saves each alert as a markdown file in the vault.

Usage:
    python scripts/fetch_alerts.py                        # Fetch & save unprocessed alerts
    python scripts/fetch_alerts.py --mark-processed <id>  # Mark alert as processed
    python scripts/fetch_alerts.py --json                 # Output as JSON
    python scripts/fetch_alerts.py --all                  # Show all alerts (including processed)
    python scripts/fetch_alerts.py --no-save              # List alerts without saving to vault
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

import requests

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

# Vault path for saving alert markdown files
ALERTS_DIR = os.path.join(
    os.path.dirname(__file__), '..', '03-Trends', 'tradingview-alerts'
)


def get_headers():
    """Build Supabase REST API headers."""
    return {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }


def fetch_alerts(unprocessed_only=True, limit=50):
    """Fetch alerts from Supabase webhook_alerts table."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)

    url = f"{SUPABASE_URL}/rest/v1/webhook_alerts"
    params = {
        'order': 'created_at.desc',
        'limit': str(limit),
    }
    if unprocessed_only:
        params['processed'] = 'eq.false'

    resp = requests.get(url, headers=get_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def mark_processed(alert_id, signal_id=None):
    """Mark an alert as processed."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)

    url = f"{SUPABASE_URL}/rest/v1/webhook_alerts"
    params = {'id': f'eq.{alert_id}'}
    body = {
        'processed': True,
        'processed_at': datetime.now(timezone.utc).isoformat(),
    }
    if signal_id:
        body['signal_id'] = signal_id

    resp = requests.patch(url, headers=get_headers(), params=params, json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()


def save_alert_to_vault(alert):
    """Save a single alert as a markdown file in 03-Trends/tradingview-alerts/."""
    os.makedirs(ALERTS_DIR, exist_ok=True)

    pair = alert.get('pair', 'UNKNOWN').replace('/', '-')
    created = alert.get('created_at', '')
    date_str = created[:10] if created else datetime.now().strftime('%Y-%m-%d')
    time_str = created[11:19].replace(':', '') if len(created) > 19 else ''

    filename = f"{pair}-{date_str}"
    if time_str:
        filename += f"-{time_str}"
    filename += ".md"
    filepath = os.path.join(ALERTS_DIR, filename)

    # Don't overwrite existing files
    if os.path.exists(filepath):
        return filepath

    alert_type = alert.get('alert_type', 'N/A')
    direction = alert.get('direction', 'N/A')
    timeframe = alert.get('timeframe', 'N/A')
    price = alert.get('price')
    high = alert.get('high')
    low = alert.get('low')
    alert_time = alert.get('alert_time', 'N/A')
    alert_name = alert.get('alert_name', 'N/A')
    alert_message = alert.get('alert_message', '')
    alert_id = alert.get('id', 'N/A')

    price_str = f"${price:,.2f}" if price else "N/A"
    high_str = f"${high:,.2f}" if high else "N/A"
    low_str = f"${low:,.2f}" if low else "N/A"

    content = f"""# TradingView Alert: {pair}

> Auto-captured from TradingView webhook on {date_str}

---

| Field | Value |
|-------|-------|
| **Pair** | {alert.get('pair', 'UNKNOWN')} |
| **Alert Type** | {alert_type} |
| **Direction** | {direction} |
| **Timeframe** | {timeframe} |
| **Price** | {price_str} |
| **High** | {high_str} |
| **Low** | {low_str} |
| **Alert Time** | {alert_time} |
| **Alert Name** | {alert_name} |
| **Source** | TradingView |
| **DB ID** | `{alert_id[:8]}...` |

---

## Alert Message

{alert_message if alert_message else '_No message provided._'}

---

## Status

- **Processed**: {'Yes' if alert.get('processed') else 'No — awaiting /technical-analyst analysis'}
- **Signal ID**: {alert.get('signal_id') or '_Not yet linked to a signal_'}

---

## Next Steps

1. Run `/technical-analyst` in alert mode to analyze this setup
2. If signal generated, approve or reject
3. Mark processed: `python scripts/fetch_alerts.py --mark-processed {alert_id}`

---

## Raw Payload

```json
{json.dumps(alert.get('raw_payload', {}), indent=2)}
```
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def format_alert(alert):
    """Format a single alert for display."""
    created = alert.get('created_at', 'N/A')
    if 'T' in str(created):
        created = created[:19].replace('T', ' ')
    pair = alert.get('pair', 'UNKNOWN')
    direction = alert.get('direction', '-')
    timeframe = alert.get('timeframe', '-')
    alert_type = alert.get('alert_type', '-')
    price = alert.get('price')
    price_str = f"${price:,.2f}" if price else "-"
    status = 'PROCESSED' if alert.get('processed') else 'PENDING'
    return f"  [{status}] {created} | {pair} {direction} {timeframe} | {alert_type} @ {price_str} | ID: {alert['id'][:8]}..."


def main():
    parser = argparse.ArgumentParser(description='Fetch TradingView webhook alerts from Supabase')
    parser.add_argument('--mark-processed', type=str, metavar='ID',
                        help='Mark an alert as processed by UUID')
    parser.add_argument('--signal-id', type=str, default=None,
                        help='Signal ID to attach when marking processed')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--all', action='store_true', help='Show all alerts (including processed)')
    parser.add_argument('--limit', type=int, default=50, help='Max alerts to fetch')
    parser.add_argument('--no-save', action='store_true', help='Do not save alerts to vault')
    args = parser.parse_args()

    if args.mark_processed:
        result = mark_processed(args.mark_processed, args.signal_id)
        if result:
            print(f"Marked alert {args.mark_processed[:8]}... as processed.")
        else:
            print(f"No alert found with ID: {args.mark_processed}")
        return

    alerts = fetch_alerts(unprocessed_only=not args.all, limit=args.limit)

    if args.json:
        print(json.dumps(alerts, indent=2))
        return

    if not alerts:
        label = "alerts" if args.all else "unprocessed alerts"
        print(f"No {label} found.")
        return

    # Save unprocessed alerts to vault
    saved_count = 0
    if not args.no_save:
        for alert in alerts:
            if not alert.get('processed'):
                filepath = save_alert_to_vault(alert)
                if filepath:
                    saved_count += 1

    label = "All Alerts" if args.all else "Unprocessed Alerts"
    print(f"\n{label} ({len(alerts)}):\n")
    for alert in alerts:
        print(format_alert(alert))

    if saved_count > 0:
        print(f"\n  Saved {saved_count} alert(s) to 03-Trends/tradingview-alerts/")
    print()


if __name__ == '__main__':
    main()
