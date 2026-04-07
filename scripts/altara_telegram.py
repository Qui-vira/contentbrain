"""
Altara Aerial — Telegram Notification Module
Follows polymarket_bot.py pattern. Sends notifications to admin DM.
"""

import os
import json
import requests
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '1284204539')


def send_message(text, chat_id=None, parse_mode='HTML'):
    """Send a Telegram message. Defaults to admin DM."""
    if not BOT_TOKEN:
        print('WARN: TELEGRAM_BOT_TOKEN not set. Skipping notification.')
        return None

    target = chat_id or ADMIN_CHAT_ID
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': target,
        'text': text,
        'parse_mode': parse_mode,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()
        if data.get('ok'):
            return data
        # Retry without parse_mode if HTML fails
        print(f'Telegram error: {data.get("description", "Unknown")}. Retrying plain text...')
        payload.pop('parse_mode', None)
        resp = requests.post(url, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        print(f'Telegram send failed: {e}')
        return None


def notify_scan_complete(script_name, leads_found, leads_new, leads_promoted=0, errors=None):
    """Send a standardized scan completion notification."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = '🔴' if errors else '🟢'

    msg = f"""{status} <b>Altara Lead Scan</b>

<b>Script:</b> {script_name}
<b>Time:</b> {now}
<b>Leads found:</b> {leads_found}
<b>New leads saved:</b> {leads_new}"""

    if leads_promoted:
        msg += f'\n<b>Promoted to MQL:</b> {leads_promoted}'

    if errors:
        msg += f'\n\n⚠️ <b>Errors:</b> {errors}'

    return send_message(msg)


def notify_outreach_summary(drafts_generated, by_type=None):
    """Send daily outreach draft summary."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    msg = f"""📝 <b>Altara Outreach Drafts</b>

<b>Time:</b> {now}
<b>Drafts generated today:</b> {drafts_generated}"""

    if by_type:
        msg += '\n\n<b>Breakdown:</b>'
        for lead_type, count in by_type.items():
            emoji = {'real_estate': '🏠', 'construction': '🏗️', 'wedding': '💒'}.get(lead_type, '📋')
            msg += f'\n  {emoji} {lead_type}: {count}'

    msg += '\n\n<i>Review drafts in Supabase dashboard.</i>'
    return send_message(msg)


def notify_outreach_sent(sent_count, failed_count=0):
    """Send notification after outreach emails are dispatched."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = '🔴' if failed_count > 0 else '🟢'

    msg = f"""{status} <b>Altara Outreach Sent</b>

<b>Time:</b> {now}
<b>Emails sent:</b> {sent_count}
<b>Failed:</b> {failed_count}"""

    if sent_count > 0:
        msg += '\n\n<i>Leads promoted to MQL in pipeline.</i>'

    return send_message(msg)
