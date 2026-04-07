"""
KOL Lead Gen — Outreach Sender
Reads approved drafts from kol_outreach_drafts.
Sends emails via Gmail SMTP. DMs flagged for manual send.
Updates lead lifecycle to MQL after sending.

Schedule: Daily 2PM WAT

Usage:
    python scripts/kol_outreach_sender.py              # Send all approved drafts
    python scripts/kol_outreach_sender.py --dry-run    # Preview without sending
"""

import os
import sys
import argparse
import requests
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    get_supabase, TABLE_LEADS, TABLE_DRAFTS, log_scan
)
from kol_telegram import notify_outreach_sent

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Gmail config — falls back to shared GMAIL_SENDER / KOL_GMAIL_APP_PASSWORD
KOL_GMAIL_SENDER = os.getenv('KOL_GMAIL_SENDER', '') or os.getenv('GMAIL_SENDER', '')
KOL_KOL_GMAIL_APP_PASSWORD = os.getenv('KOL_KOL_GMAIL_APP_PASSWORD', '') or os.getenv('KOL_GMAIL_APP_PASSWORD', '')


# --- Load approved drafts ---

def load_approved_drafts():
    """Load drafts with status='approved' from Supabase."""
    sb = get_supabase()
    if not sb:
        return []

    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}"
    query = f"{url}?status=eq.approved&order=created_at.asc&limit=50"
    resp = requests.get(query, headers=sb['headers'], timeout=15)
    if resp.ok:
        return resp.json()
    print(f'  WARN: Failed to load drafts: {resp.status_code}')
    return []


# --- Email sending ---

def send_via_gmail_smtp(to_email, subject, body):
    """Send email via Gmail SMTP with app password."""
    if not KOL_GMAIL_SENDER or not KOL_GMAIL_APP_PASSWORD:
        print('  WARN: Gmail credentials not set')
        return False

    import smtplib

    msg = MIMEMultipart()
    msg['From'] = KOL_GMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(KOL_GMAIL_SENDER, KOL_GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'  Gmail send failed: {e}')
        return False


def send_email(draft):
    """Send an email using Gmail SMTP. DMs flagged for manual send."""
    to_email = draft.get('lead_contact', '')
    subject = draft.get('subject', '')
    body = draft.get('body', '')
    channel = draft.get('channel', 'email')

    if channel in ('dm', 'telegram'):
        print(f'  SKIP (DM): {draft.get("lead_name", "?")} — manual send required')
        return 'manual'

    if not to_email or '@' not in to_email:
        print(f'  SKIP: No email for {draft.get("lead_name", "?")}')
        return 'no_email'

    if send_via_gmail_smtp(to_email, subject, body):
        return 'sent'

    print(f'  FAIL: Could not send to {to_email}')
    return 'failed'


# --- Update Supabase ---

def mark_draft_sent(draft_id):
    """Mark draft as sent in Supabase."""
    sb = get_supabase()
    if not sb:
        return

    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}?id=eq.{draft_id}"
    requests.patch(
        url,
        json={'status': 'sent', 'sent_at': datetime.now(timezone.utc).isoformat()},
        headers=sb['headers'], timeout=10
    )


def mark_draft_manual(draft_id):
    """Mark DM draft as needing manual send."""
    sb = get_supabase()
    if not sb:
        return

    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}?id=eq.{draft_id}"
    requests.patch(
        url,
        json={'status': 'manual_required'},
        headers=sb['headers'], timeout=10
    )


def promote_lead_to_mql(lead_id):
    """Promote lead from subscriber to MQL after outreach sent."""
    sb = get_supabase()
    if not sb:
        return

    url = f"{sb['url']}/rest/v1/{TABLE_LEADS}?id=eq.{lead_id}"
    requests.patch(
        url,
        json={
            'lifecycle_stage': 'mql',
            'outreach_status': 'sent',
            'updated_at': datetime.now(timezone.utc).isoformat(),
        },
        headers=sb['headers'], timeout=10
    )


# --- Main ---

def run(dry_run=False):
    """Entry point for cron orchestrator."""
    drafts = load_approved_drafts()
    print(f'\n  Approved drafts: {len(drafts)}')

    if not drafts:
        print('  No approved drafts to send.')
        notify_outreach_sent(0)
        return 0

    sent_count = 0
    failed_count = 0
    manual_count = 0

    for draft in drafts:
        draft_id = draft.get('id', '')
        lead_id = draft.get('lead_id', '')
        lead_name = draft.get('lead_name', 'Unknown')

        if dry_run:
            print(f'  [DRY RUN] Would send to: {lead_name} ({draft.get("lead_contact", "")})')
            print(f'    Subject: {draft.get("subject", "")}')
            sent_count += 1
            continue

        result = send_email(draft)

        if result == 'sent':
            mark_draft_sent(draft_id)
            promote_lead_to_mql(lead_id)
            sent_count += 1
            print(f'  SENT: {lead_name}')
        elif result == 'manual':
            mark_draft_manual(draft_id)
            manual_count += 1
        elif result == 'no_email':
            manual_count += 1
        else:
            failed_count += 1

    # Telegram notification
    if not dry_run:
        notify_outreach_sent(sent_count, failed_count)

    # Log
    log_scan('kol_outreach_sender', len(drafts), sent_count, sent_count)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE')
    print(f'  Sent: {sent_count}')
    print(f'  Manual (DMs): {manual_count}')
    print(f'  Failed: {failed_count}')
    print(f'  Leads promoted to MQL: {sent_count}')
    print(f'{"=" * 50}')

    return sent_count


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — Outreach Sender')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — Outreach Sender')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
