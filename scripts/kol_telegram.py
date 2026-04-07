"""
KOL & Consulting — Telegram Notification Module
Follows altara_telegram.py pattern. Sends notifications to admin DM.
"""

import os
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
    status = '\U0001f534' if errors else '\U0001f7e2'

    msg = f"""{status} <b>KOL Lead Scan</b>

<b>Script:</b> {script_name}
<b>Time:</b> {now}
<b>Leads found:</b> {leads_found}
<b>New leads saved:</b> {leads_new}"""

    if leads_promoted:
        msg += f'\n<b>Promoted to MQL:</b> {leads_promoted}'

    if errors:
        msg += f'\n\n\u26a0\ufe0f <b>Errors:</b> {errors}'

    return send_message(msg)


def notify_outreach_summary(drafts_generated, by_type=None):
    """Send daily outreach draft summary."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    msg = f"""\U0001f4dd <b>KOL Outreach Drafts</b>

<b>Time:</b> {now}
<b>Drafts generated today:</b> {drafts_generated}"""

    if by_type:
        msg += '\n\n<b>Breakdown:</b>'
        for lead_type, count in by_type.items():
            emoji = {
                'new_exchange': '\U0001f3e6',
                'funded_project': '\U0001f4b0',
                'ai_consulting': '\U0001f916',
                'competitor_deal': '\U0001f440',
                'defi_protocol': '\U0001f4ca',
                'new_token': '\U0001fa99',
            }.get(lead_type, '\U0001f4cb')
            msg += f'\n  {emoji} {lead_type}: {count}'

    msg += '\n\n<i>Review drafts in Supabase dashboard.</i>'
    return send_message(msg)


def notify_outreach_sent(sent_count, failed_count=0):
    """Send notification after outreach emails are dispatched."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = '\U0001f534' if failed_count > 0 else '\U0001f7e2'

    msg = f"""{status} <b>KOL Outreach Sent</b>

<b>Time:</b> {now}
<b>Emails sent:</b> {sent_count}
<b>Failed:</b> {failed_count}"""

    if sent_count > 0:
        msg += '\n\n<i>Leads promoted to MQL in pipeline.</i>'

    return send_message(msg)


def notify_competitor_alert(project_name, competitor, deal_type, post_url=''):
    """High-priority alert for detected competitor KOL deal."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    msg = f"""\U0001f6a8 <b>Competitor Deal Detected</b>

<b>Project:</b> {project_name}
<b>Competitor:</b> @{competitor}
<b>Deal type:</b> {deal_type}
<b>Time:</b> {now}"""

    if post_url:
        msg += f'\n<b>Post:</b> {post_url}'

    msg += '\n\n<i>This project is spending on KOL marketing. Pitch them before they lock budgets.</i>'
    return send_message(msg)
