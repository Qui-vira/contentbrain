"""
Altara Aerial — Outreach Sender
Runs daily 2PM. Reads approved drafts from altara_outreach_drafts.
Sends emails via Gmail API. Marks as sent.
Updates lead lifecycle from Subscriber to MQL in /revops pipeline.

Usage:
    python scripts/altara_outreach_sender.py              # Send all approved drafts
    python scripts/altara_outreach_sender.py --dry-run    # Preview without sending
"""

import os
import sys
import json
import base64
import argparse
import requests
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.dirname(__file__))
from altara_lead_base import (
    get_supabase, TABLE_CLIENTS, TABLE_DRAFTS, log_scan
)
from altara_telegram import notify_outreach_sent

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Gmail API config
GMAIL_SENDER = os.getenv('GMAIL_SENDER', '')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')

# Outreach.io config (fallback)
OUTREACH_API_KEY = os.getenv('OUTREACH_API_KEY', '')
OUTREACH_BASE = 'https://api.outreach.io/api/v2'


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
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        print('  WARN: GMAIL_SENDER or GMAIL_APP_PASSWORD not set')
        return False

    import smtplib

    msg = MIMEMultipart()
    msg['From'] = GMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'  Gmail send failed: {e}')
        return False


def send_via_outreach(prospect_email, subject, body):
    """Send via Outreach.io API if configured."""
    if not OUTREACH_API_KEY:
        return False

    headers = {
        'Authorization': f'Bearer {OUTREACH_API_KEY}',
        'Content-Type': 'application/vnd.api+json',
    }

    # Create prospect if needed, then create mailing
    # Simplified: just create a mailing task
    payload = {
        'data': {
            'type': 'mailing',
            'attributes': {
                'subject': subject,
                'bodyText': body,
            },
        }
    }

    try:
        resp = requests.post(
            f'{OUTREACH_BASE}/mailings',
            json=payload, headers=headers, timeout=30
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f'  Outreach send failed: {e}')
        return False


def send_email(draft):
    """Send an email using available channel. Gmail SMTP primary, Outreach.io fallback."""
    to_email = draft.get('lead_contact', '')
    subject = draft.get('subject', '')
    body = draft.get('body', '')
    channel = draft.get('channel', 'email')

    if channel == 'dm':
        # DM drafts are manual (Instagram/WhatsApp)
        print(f'  SKIP (DM): {draft.get("lead_name", "?")} — manual send required')
        return 'manual'

    if not to_email or '@' not in to_email:
        print(f'  SKIP: No email for {draft.get("lead_name", "?")}')
        return 'no_email'

    # Try Gmail first
    if GMAIL_SENDER and GMAIL_APP_PASSWORD:
        if send_via_gmail_smtp(to_email, subject, body):
            return 'sent'

    # Fallback to Outreach.io
    if OUTREACH_API_KEY:
        if send_via_outreach(to_email, subject, body):
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

    url = f"{sb['url']}/rest/v1/{TABLE_CLIENTS}?id=eq.{lead_id}"
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

def main():
    parser = argparse.ArgumentParser(description='Altara Aerial — Outreach Sender')
    parser.add_argument('--dry-run', action='store_true', help='Preview without sending')
    args = parser.parse_args()

    print('=' * 50)
    print('  ALTARA AERIAL — Outreach Sender')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    drafts = load_approved_drafts()
    print(f'\n  Approved drafts: {len(drafts)}')

    if not drafts:
        print('  No approved drafts to send.')
        notify_outreach_sent(0)
        return

    sent_count = 0
    failed_count = 0
    manual_count = 0

    for draft in drafts:
        draft_id = draft.get('id', '')
        lead_id = draft.get('lead_id', '')
        lead_name = draft.get('lead_name', 'Unknown')

        if args.dry_run:
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
    if not args.dry_run:
        notify_outreach_sent(sent_count, failed_count)

    # Log
    log_scan('outreach_sender', len(drafts), sent_count, sent_count)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE')
    print(f'  Sent: {sent_count}')
    print(f'  Manual (DMs): {manual_count}')
    print(f'  Failed: {failed_count}')
    print(f'  Leads promoted to MQL: {sent_count}')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
