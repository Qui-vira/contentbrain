"""
Unified Outreach Review Bot — Daily Telegram review for BOTH pipelines.
Sends summary + top 5 drafts with inline Approve/Reject buttons.

Runs daily at 10:30 WAT (after both drafters finish at 10:00).
Queries both altara_outreach_drafts and kol_outreach_drafts.

Usage:
    python scripts/outreach_review_bot.py              # Send daily review
    python scripts/outreach_review_bot.py --dry-run    # Preview without sending
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv('OUTREACH_BOT_TOKEN', '')
ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '1284204539')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', '')
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'https://bigquivdigitals.com/admin/outreach')

TOP_N = 5


def sb_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }


def send_message(text, reply_markup=None, parse_mode='HTML'):
    """Send Telegram message with optional inline keyboard."""
    if not BOT_TOKEN:
        print(f'WARN: No TELEGRAM_BOT_TOKEN. Message:\n{text}')
        return None

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': ADMIN_CHAT_ID,
        'text': text,
        'parse_mode': parse_mode,
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()
        if data.get('ok'):
            return data
        # Retry without parse_mode
        print(f'Telegram error: {data.get("description")}. Retrying plain...')
        payload.pop('parse_mode', None)
        resp = requests.post(url, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        print(f'Telegram send failed: {e}')
        return None


# --- Load pending drafts ---

def load_pending_drafts(table):
    """Load pending drafts from a Supabase table, ordered by score join."""
    if not SUPABASE_URL:
        return []

    url = f'{SUPABASE_URL}/rest/v1/{table}'
    query = f'{url}?status=eq.pending&order=created_at.desc&limit=50'
    resp = requests.get(query, headers=sb_headers(), timeout=15)
    if resp.ok:
        return resp.json()
    return []


def get_lead_score(draft, pipeline):
    """Get the score for the lead associated with this draft."""
    lead_id = draft.get('lead_id', '')
    if not lead_id:
        return 0

    table = 'altara_client_leads' if pipeline == 'altara' else 'kol_leads'
    url = f'{SUPABASE_URL}/rest/v1/{table}?id=eq.{lead_id}&select=score&limit=1'
    resp = requests.get(url, headers=sb_headers(), timeout=10)
    if resp.ok and resp.json():
        return resp.json()[0].get('score', 0)
    return 0


# --- Build summary ---

def build_summary(altara_drafts, kol_drafts):
    """Build the daily summary message."""
    today = datetime.now(timezone.utc).strftime('%B %d, %Y')

    # Count by type
    altara_by_type = {}
    for d in altara_drafts:
        lt = d.get('lead_type', 'unknown')
        altara_by_type[lt] = altara_by_type.get(lt, 0) + 1

    kol_by_type = {}
    for d in kol_drafts:
        lt = d.get('lead_type', 'unknown')
        kol_by_type[lt] = kol_by_type.get(lt, 0) + 1

    msg = f'\U0001f4ec <b>Outreach Review \u2014 {today}</b>\n'

    # Altara section
    msg += f'\n<b>ALTARA AERIAL:</b> {len(altara_drafts)} drafts'
    type_labels = {'real_estate': 'Real estate agents', 'construction': 'Construction firms', 'wedding': 'Wedding planners'}
    for lt, count in altara_by_type.items():
        label = type_labels.get(lt, lt)
        msg += f'\n\u251c\u2500\u2500 {label}: {count}'

    # KOL section
    msg += f'\n\n<b>KOL BUSINESS:</b> {len(kol_drafts)} drafts'
    type_labels_kol = {
        'new_exchange': 'New exchanges', 'defi_protocol': 'DeFi protocols',
        'funded_project': 'Funded projects', 'ai_consulting': 'AI consulting',
        'competitor_deal': 'Competitor deals', 'new_token': 'New tokens',
    }
    for lt, count in kol_by_type.items():
        label = type_labels_kol.get(lt, lt)
        msg += f'\n\u251c\u2500\u2500 {label}: {count}'

    return msg


def build_review_card(draft, pipeline, score):
    """Build a single draft review message with inline buttons."""
    tag = '[ALTARA]' if pipeline == 'altara' else '[KOL]'
    lead_name = draft.get('lead_name', 'Unknown')
    lead_type = draft.get('lead_type', '')
    subject = draft.get('subject', 'No subject')
    body = draft.get('body', '')[:200]
    draft_id = draft.get('id', '')

    msg = f'<b>{tag}</b> {lead_name}\n'
    msg += f'<b>Type:</b> {lead_type} | <b>Score:</b> {score}\n'
    msg += f'<b>Subject:</b> {subject}\n\n'
    msg += f'{body}...'

    # Callback data: a=approve, r=reject, al=altara, kl=kol
    prefix = 'al' if pipeline == 'altara' else 'kl'
    keyboard = {
        'inline_keyboard': [[
            {'text': '\u2705 Approve', 'callback_data': f'a:{prefix}:{draft_id}'},
            {'text': '\u274c Reject', 'callback_data': f'r:{prefix}:{draft_id}'},
        ]]
    }

    return msg, keyboard


# --- Main ---

def run(dry_run=False):
    print('=' * 50)
    print('  UNIFIED OUTREACH REVIEW BOT')
    print(f'  Mode: {"DRY RUN" if dry_run else "LIVE"}')
    print('=' * 50)

    # Load all pending drafts
    altara_drafts = load_pending_drafts('altara_outreach_drafts')
    kol_drafts = load_pending_drafts('kol_outreach_drafts')

    print(f'\n  Altara pending: {len(altara_drafts)}')
    print(f'  KOL pending: {len(kol_drafts)}')

    if not altara_drafts and not kol_drafts:
        print('  No pending drafts. Skipping.')
        return

    # Send summary
    summary = build_summary(altara_drafts, kol_drafts)
    summary += f'\n\n<b>Top {TOP_N} highest priority (tap to review):</b>'

    if not dry_run:
        send_message(summary)
    else:
        print(f'\n--- SUMMARY ---\n{summary}\n')

    # Score all drafts and pick top 5
    scored = []
    for d in altara_drafts:
        score = get_lead_score(d, 'altara')
        scored.append((d, 'altara', score))
    for d in kol_drafts:
        score = get_lead_score(d, 'kol')
        scored.append((d, 'kol', score))

    scored.sort(key=lambda x: x[2], reverse=True)
    top = scored[:TOP_N]

    # Send individual review cards
    for draft, pipeline, score in top:
        msg, keyboard = build_review_card(draft, pipeline, score)
        if not dry_run:
            send_message(msg, reply_markup=keyboard)
        else:
            print(f'\n--- CARD ---\n{msg}\n')

    # Send remaining count
    remaining = len(scored) - TOP_N
    if remaining > 0:
        footer = f'\U0001f4cb {remaining} more drafts in dashboard \u2192 <a href="{DASHBOARD_URL}">Review all</a>'
        if not dry_run:
            send_message(footer)
        else:
            print(f'\n--- FOOTER ---\n{footer}')

    print(f'\n  Sent {min(len(scored), TOP_N)} review cards + summary')


def main():
    parser = argparse.ArgumentParser(description='Unified Outreach Review Bot')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
