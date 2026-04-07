"""
Altara Aerial — Cold Outreach Drafter
Runs daily 10AM. Reads leads from Supabase where outreach_status='pending'.
Generates personalized email/DM drafts using Pain-Bridge-Solution framework
and Altara Aerial vault data. Saves drafts to altara_outreach_drafts table.
Sends Telegram summary.

Usage:
    python scripts/generate_altara_outreach.py                     # All lead types
    python scripts/generate_altara_outreach.py --type real_estate  # Single type
    python scripts/generate_altara_outreach.py --dry-run           # Skip Supabase writes
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from altara_lead_base import (
    get_supabase, ensure_dirs, OUTPUT_DIR, VAULT_DIR,
    TABLE_CLIENTS, TABLE_PILOTS, TABLE_DRAFTS, log_scan
)
from altara_telegram import notify_outreach_summary

DATE = datetime.now().strftime('%Y-%m-%d')

# Daily draft cap
DAILY_CAP = 20


# --- Draft cap helpers ---

def get_today_draft_count():
    """Count drafts created today in altara_outreach_drafts."""
    sb = get_supabase()
    if not sb:
        return 0
    today_start = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}?created_at=gte.{today_start}&select=id"
    resp = requests.get(url, headers={**sb['headers'], 'Prefer': 'count=exact'}, timeout=10)
    if resp.ok:
        return len(resp.json())
    return 0


def get_global_draft_count():
    """Count drafts created today across BOTH altara and kol tables."""
    sb = get_supabase()
    if not sb:
        return 0
    today_start = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
    total = 0
    for table in [TABLE_DRAFTS, 'kol_outreach_drafts']:
        url = f"{sb['url']}/rest/v1/{table}?created_at=gte.{today_start}&select=id"
        resp = requests.get(url, headers={**sb['headers'], 'Prefer': 'count=exact'}, timeout=10)
        if resp.ok:
            total += len(resp.json())
    return total


# --- Load leads from Supabase ---

def load_pending_leads(lead_type=None):
    """Load leads with outreach_status='not_contacted' from Supabase."""
    sb = get_supabase()
    if not sb:
        return []

    url = f"{sb['url']}/rest/v1/{TABLE_CLIENTS}"
    query = f"{url}?outreach_status=eq.not_contacted&order=score.desc&limit=30"
    if lead_type:
        query += f'&lead_type=eq.{lead_type}'

    resp = requests.get(query, headers=sb['headers'], timeout=15)
    if resp.ok:
        return resp.json()
    print(f'  WARN: Failed to load leads: {resp.status_code}')
    return []


def load_pending_pilots():
    """Load pilot prospects that haven't been contacted."""
    sb = get_supabase()
    if not sb:
        return []

    url = f"{sb['url']}/rest/v1/{TABLE_PILOTS}"
    query = f"{url}?outreach_status=eq.not_contacted&order=score.desc&limit=20"
    resp = requests.get(query, headers=sb['headers'], timeout=15)
    if resp.ok:
        return resp.json()
    return []


# --- Email generators (Pain-Bridge-Solution) ---

def generate_real_estate_email(lead):
    name = lead.get('name', '').strip()
    city = lead.get('city', 'Lagos')
    listing_url = lead.get('listing_url', '')
    first_name = name.split()[0] if name else 'Hi'

    listing_ref = ''
    if listing_url:
        listing_ref = f'\n\nI was looking at one of your listings ({listing_url}). Great property. But the photos are all ground-level. No aerial shots.'

    return {
        'subject': f'Your {city} listings are missing one thing',
        'body': f"""{first_name},{listing_ref}

Real talk. Buyers scroll past listings without aerial photos. They want to see the compound, the street layout, proximity to landmarks. Ground-level photos don't show that.

Right now you probably find drone pilots on WhatsApp. 3 hours searching. No verified portfolio. No insurance. Pay upfront and hope for the best.

Altara Aerial connects you to NCAA-certified drone pilots in {city}. Verified portfolios. Escrow payment protection. You only pay when you approve the footage.

N100,000 to N250,000 per property shoot. 5 minutes to book instead of 3 hours.

First property shoot is free. No card needed. I'll set it up for you personally.

Worth a quick call this week?

Quivira
Altara Aerial""",
        'channel': 'email',
    }


def generate_construction_email(lead):
    company = lead.get('company', '').strip()
    city = lead.get('city', 'Lagos')

    return {
        'subject': f'Drone monitoring for {company} projects',
        'body': f"""Hi,

Quick question. How are you currently handling aerial monitoring for your construction sites in {city}?

Most firms I talk to use WhatsApp to find drone operators. No NCAA certification on file. No insurance documentation. No audit trail.

That works until a project manager asks for compliance docs. Or until something goes wrong mid-flight.

Altara Aerial is a drone services platform built for construction. Every pilot is NCAA-certified. Insurance is mandatory on every gig. You get a dashboard tracking all your projects, all your pilots, all your documentation in one place.

N200,000 to N1,000,000 per mission depending on scope. Monthly invoicing for corporate accounts.

Three things you get that WhatsApp can't give you:
1. NCAA certification verified before every booking
2. Liability insurance on every flight
3. Audit-ready documentation delivered automatically

I'd like to set up a free trial flight on one of your active sites. 30 minutes of your time to see the difference.

Quivira
Altara Aerial""",
        'channel': 'email',
    }


def generate_wedding_email(lead):
    name = lead.get('name', '').strip()
    instagram = lead.get('instagram', '').strip()
    city = lead.get('city', 'Lagos')
    followers = int(lead.get('followers', 0) or 0)
    first_name = name.split()[0] if name else 'Hi'

    ig_ref = ''
    if instagram:
        ig_ref = f" I found you through @{instagram}. Your work is clean."

    referral_line = ''
    if followers >= 5000:
        referral_line = '\n\nWith your audience, you could also earn N10,000 for every client you refer to the platform. That adds up fast during wedding season.'

    return {
        'subject': f'Verified drone pilots for your {city} events',
        'body': f"""{first_name},{ig_ref}

Quick question. When a client asks for drone coverage at their wedding, how confident are you in the pilot showing up?

Most planners find drone operators through referrals or WhatsApp groups. No way to check their work beforehand. No insurance if something goes wrong. No backup if they cancel last minute.

Altara Aerial gives you verified drone pilots in {city}. NCAA-certified. Insured. Rated by past clients. You can see their portfolio before booking.

N80,000 to N200,000 per event. Book months in advance with confirmation. Escrow payment so you only pay when delivery is confirmed.{referral_line}

Your clients trust you to handle every detail. Drone coverage should be the easiest one. I'll set up your first booking for free so you can test the quality.

Quivira
Altara Aerial""",
        'channel': instagram and 'dm' or 'email',
    }


GENERATORS = {
    'real_estate': generate_real_estate_email,
    'construction': generate_construction_email,
    'wedding': generate_wedding_email,
}


# --- Save drafts to Supabase ---

def save_draft_to_supabase(lead, email_data, lead_type):
    """Save an outreach draft to altara_outreach_drafts table."""
    sb = get_supabase()
    if not sb:
        return False

    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}"
    row = {
        'lead_id': lead.get('id', ''),
        'lead_type': lead_type,
        'lead_name': lead.get('name', '') or lead.get('company', ''),
        'lead_city': lead.get('city', ''),
        'lead_contact': lead.get('phone', '') or lead.get('email', '') or lead.get('instagram', ''),
        'channel': email_data.get('channel', 'email'),
        'subject': email_data.get('subject', ''),
        'body': email_data.get('body', ''),
        'status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    resp = requests.post(url, json=row, headers=sb['headers'], timeout=10)
    if resp.status_code in (200, 201, 204):
        # Mark lead as drafted
        lead_url = f"{sb['url']}/rest/v1/{TABLE_CLIENTS}?id=eq.{lead.get('id', '')}"
        requests.patch(
            lead_url,
            json={'outreach_status': 'draft_ready', 'updated_at': datetime.now(timezone.utc).isoformat()},
            headers=sb['headers'], timeout=10
        )
        return True

    print(f'  WARN: Draft save failed: {resp.status_code} {resp.text[:100]}')
    return False


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description='Altara Aerial — Cold Outreach Drafter')
    parser.add_argument('--type', choices=['real_estate', 'construction', 'wedding'])
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    lead_types = [args.type] if args.type else ['real_estate', 'construction', 'wedding']

    print('=' * 50)
    print('  ALTARA AERIAL — Cold Outreach Drafter')
    print(f'  Lead types: {", ".join(lead_types)}')
    print('=' * 50)

    total_drafts = 0
    by_type = {}

    # Enforce daily cap
    local_today = get_today_draft_count()
    global_today = get_global_draft_count()
    remaining_local = max(DAILY_CAP - local_today, 0)
    remaining_global = max(40 - global_today, 0)
    remaining = min(remaining_local, remaining_global)
    print(f'\n  Daily cap: {DAILY_CAP} | Altara today: {local_today} | Global today: {global_today} | Remaining: {remaining}')

    if remaining <= 0:
        print('  Cap reached. Skipping draft generation.')
        return

    for lead_type in lead_types:
        if remaining <= 0:
            print(f'\n--- {lead_type} --- SKIPPED (cap reached)')
            continue

        print(f'\n--- {lead_type} ---')
        leads = load_pending_leads(lead_type)
        leads = leads[:remaining]  # Enforce cap
        print(f'  Loaded {len(leads)} pending leads (capped)')

        generator = GENERATORS.get(lead_type)
        if not generator or not leads:
            continue

        count = 0
        for lead in leads:
            try:
                email_data = generator(lead)
                if not args.dry_run:
                    saved = save_draft_to_supabase(lead, email_data, lead_type)
                    if saved:
                        count += 1
                        remaining -= 1
                else:
                    count += 1
                    remaining -= 1
            except Exception as e:
                print(f'  WARN: Failed for lead {lead.get("id", "?")}: {e}')

        print(f'  Generated {count} drafts')
        total_drafts += count
        by_type[lead_type] = count

    # Telegram notification
    notify_outreach_summary(total_drafts, by_type)

    # Log
    log_scan('outreach_drafter', total_drafts, total_drafts, 0)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE — {total_drafts} drafts generated')
    print(f'  Review in Supabase: altara_outreach_drafts')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
