"""
KOL Lead Gen — Outreach Drafter
Reads pending leads from kol_leads, generates personalized outreach emails
using Pain-Bridge-Solution framework. Saves drafts to kol_outreach_drafts.

Schedule: Daily 10AM WAT

Usage:
    python scripts/kol_outreach_drafter.py                          # All lead types
    python scripts/kol_outreach_drafter.py --type funded_project    # Single type
    python scripts/kol_outreach_drafter.py --dry-run                # Skip Supabase writes
"""

import os
import sys
import argparse
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    get_supabase, ensure_dirs, TABLE_LEADS, TABLE_DRAFTS, log_scan
)
from kol_telegram import notify_outreach_summary

DATE = datetime.now().strftime('%Y-%m-%d')

# Daily draft cap
DAILY_CAP = 20


# --- Draft cap helpers ---

def get_today_draft_count():
    """Count drafts created today in kol_outreach_drafts."""
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
    for table in ['altara_outreach_drafts', TABLE_DRAFTS]:
        url = f"{sb['url']}/rest/v1/{table}?created_at=gte.{today_start}&select=id"
        resp = requests.get(url, headers={**sb['headers'], 'Prefer': 'count=exact'}, timeout=10)
        if resp.ok:
            total += len(resp.json())
    return total


ALL_LEAD_TYPES = [
    'new_exchange', 'defi_protocol', 'funded_project',
    'ai_consulting', 'competitor_deal', 'leadgen_service_client',
]


# --- Load leads from Supabase ---

def load_pending_leads(lead_type=None):
    """Load leads with outreach_status='not_contacted' from Supabase."""
    sb = get_supabase()
    if not sb:
        return []

    url = f"{sb['url']}/rest/v1/{TABLE_LEADS}"
    query = f"{url}?outreach_status=eq.not_contacted&order=score.desc&limit=30"
    if lead_type:
        query += f'&lead_type=eq.{lead_type}'

    resp = requests.get(query, headers=sb['headers'], timeout=15)
    if resp.ok:
        return resp.json()
    print(f'  WARN: Failed to load leads: {resp.status_code}')
    return []


# --- Email generators (Pain-Bridge-Solution) ---

def generate_exchange_outreach(lead):
    """Pitch to new exchanges: "You need distribution, I bring traders." """
    name = lead.get('project_name', '').strip()
    volume = lead.get('volume_24h', 0)
    trust = lead.get('trust_score', 0)

    volume_note = ''
    if volume and volume < 500:
        volume_note = ' Your 24h volume is still building. That changes with the right voices pushing traders your way.'

    return {
        'subject': f'{name} needs traders. I bring them.',
        'body': f"""Hi {name} team,

New exchanges have one problem. Liquidity. You can build the cleanest UI, the fastest matching engine, the lowest fees. None of it matters if traders don't show up.{volume_note}

I run KOL campaigns for crypto exchanges. My audience is 44K+ traders on X and growing across TikTok, Instagram, and Telegram. Active traders. Not bots. Not engagement farmers. People who actually move volume.

What I bring:
1. Sponsored content across X, TikTok, IG (44K+ combined reach)
2. Trading tutorials filmed on your platform (builds trust, not just awareness)
3. Telegram community push (direct access to active traders)
4. Referral tracking so you see exactly what you're getting

I've worked with exchanges and DeFi protocols in this space. I know what moves the needle and what wastes budget.

Let's do a quick call to discuss a pilot campaign. No long-term commitment. If the numbers don't work after 30 days, we part ways.

Quivira
@_Quivira | bigquivdigitals.com""",
        'channel': 'email',
    }


def generate_funded_project_outreach(lead):
    """Pitch to funded projects: "Post-raise, you need awareness." """
    name = lead.get('project_name', '').strip()
    amount = lead.get('funding_amount', 0)
    round_type = lead.get('funding_round', 'funding round')
    investors = lead.get('investors', '')

    amount_line = ''
    if amount:
        amount_line = f' Congrats on the ${amount/1_000_000:.1f}M {round_type}.'

    investor_line = ''
    if investors:
        investor_line = f' With {investors.split(",")[0].strip()} backing you, the market is watching.'

    return {
        'subject': f'{name} just raised. Now you need distribution.',
        'body': f"""Hi {name} team,{amount_line}{investor_line}

Post-raise is the most critical window for visibility. VCs gave you runway. But runway without users is just a countdown.

Most projects hire a PR agency. Get a few articles on CoinTelegraph. Maybe a Twitter Spaces appearance. Then wonder why nobody's using the product 3 months later.

What actually works is sustained KOL distribution. Real voices. Real traders and builders talking about your product. Not one tweet. A campaign.

Here's what I run:
1. Multi-platform content (X, TikTok, IG, Telegram) — 44K+ engaged followers
2. Technical breakdowns that show builders your product is worth building on
3. Trading community distribution if your project has a token or DeFi angle
4. Ongoing campaign management with transparent metrics

I've shipped production AI systems (PharmaOS, trading signal bots, data pipelines). When I talk about a protocol, my audience knows I actually understand the tech.

Let me put together a campaign proposal for your first 30 days post-raise. 15 minutes on a call to scope it.

Quivira
@_Quivira | bigquivdigitals.com""",
        'channel': 'email',
    }


def generate_ai_consulting_outreach(lead):
    """Pitch to AI consulting clients: "I've shipped PharmaOS, signal bots, AI pipelines." """
    name = lead.get('project_name', '').strip()
    category = lead.get('category', '')
    description = lead.get('description', '')[:150]

    return {
        'subject': f'Re: {name[:50]}',
        'body': f"""Hi,

I saw your project listing for {category.replace('_', ' ')}. I've shipped exactly this kind of work before.

What I've built:
- PharmaOS: Full production AI system for pharmaceutical operations
- Automated trading signal bots: Crypto + forex, live in production with real money
- AI data pipelines: Scraping, analysis, automated reporting at scale
- Content automation systems: AI-powered content production running 24/7

I'm not a freelancer who read a tutorial last week. I build systems that run in production and handle real money.

My rate is competitive and I deliver fast. I can scope your project in a 15-minute call and give you a fixed-price quote same day.

What's your timeline looking like?

Quivira
@_Quivira | bigquivdigitals.com""",
        'channel': 'email',
    }


def generate_competitor_deal_outreach(lead):
    """Pitch to projects already spending on competitor KOLs. No competitor mention."""
    name = lead.get('project_name', '').strip()

    return {
        'subject': f'KOL campaign for {name}',
        'body': f"""Hi {name} team,

I noticed you're investing in KOL marketing. Smart move. Most projects in your space are still relying on organic growth alone.

Quick question: are you getting the metrics you expected? Specifically, are you tracking:
- New users attributed to each KOL
- Trading volume or TVL changes during campaigns
- Retention 30 days after the campaign ends

Most projects don't track beyond impressions. That's why budgets get wasted.

I run KOL campaigns differently:
1. Multi-platform distribution (X, TikTok, IG, Telegram) — not just one tweet
2. Technical content that converts builders and traders, not just viewers
3. Full attribution tracking so you know exactly what you're paying for
4. 30-day performance guarantee

My audience is 44K+ active crypto traders and builders. Not bots. Real engagement. Real conversions.

Let me send you a campaign proposal with projected reach and conversion estimates. 15 minutes on a call to scope it.

Quivira
@_Quivira | bigquivdigitals.com""",
        'channel': 'email',
    }


def generate_leadgen_service_outreach(lead):
    """Pitch to businesses struggling with manual lead gen. Sell the automated pipeline."""
    name = lead.get('project_name', '').strip()
    description = lead.get('description', '')[:100]

    return {
        'subject': f'{name} — what if your lead gen ran on autopilot?',
        'body': f"""Hey {name},

I saw you're dealing with lead generation manually. Real talk, I was in the same spot 3 months ago.

Then I built an automated pipeline. First day it ran, it pulled 83 qualified leads. No manual scraping. No spreadsheet hell. No VA managing 12 tabs.

Here's what the system does:
1. Scrapes leads from multiple sources automatically (Upwork, LinkedIn, X, industry databases)
2. Scores and ranks them by how likely they are to buy
3. Generates personalized outreach drafts (not copy-paste templates)
4. Sends approved emails via Gmail SMTP on schedule
5. Tracks the full pipeline in a live Supabase dashboard
6. Sends daily Telegram review with approve/reject buttons

The whole thing runs on a $5/month Railway server. I built it for my own businesses (KOL deals and drone services). Both pipelines run 24/7 without me touching anything.

I'm now offering this as a service. I'll build your custom lead gen pipeline, deploy it, and hand you the keys. Fixed price. No monthly retainer unless you want managed outreach on top.

15 minutes to scope your pipeline. I'll tell you exactly what it costs.

Quivira
@_Quivira | bigquivdigitals.com""",
        'channel': 'email',
    }


GENERATORS = {
    'new_exchange': generate_exchange_outreach,
    'defi_protocol': generate_exchange_outreach,
    'funded_project': generate_funded_project_outreach,
    'ai_consulting': generate_ai_consulting_outreach,
    'competitor_deal': generate_competitor_deal_outreach,
    'leadgen_service_client': generate_leadgen_service_outreach,
}


# --- Save drafts to Supabase ---

def save_draft_to_supabase(lead, email_data, lead_type):
    """Save an outreach draft to kol_outreach_drafts table."""
    sb = get_supabase()
    if not sb:
        return False

    url = f"{sb['url']}/rest/v1/{TABLE_DRAFTS}"
    row = {
        'lead_id': lead.get('id', ''),
        'lead_type': lead_type,
        'lead_name': lead.get('project_name', ''),
        'lead_contact': lead.get('email', '') or lead.get('twitter_handle', ''),
        'channel': email_data.get('channel', 'email'),
        'subject': email_data.get('subject', ''),
        'body': email_data.get('body', ''),
        'status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    resp = requests.post(url, json=row, headers=sb['headers'], timeout=10)
    if resp.status_code in (200, 201, 204):
        # Mark lead as drafted
        lead_url = f"{sb['url']}/rest/v1/{TABLE_LEADS}?id=eq.{lead.get('id', '')}"
        requests.patch(
            lead_url,
            json={'outreach_status': 'draft_ready', 'updated_at': datetime.now(timezone.utc).isoformat()},
            headers=sb['headers'], timeout=10
        )
        return True

    print(f'  WARN: Draft save failed: {resp.status_code} {resp.text[:100]}')
    return False


# --- Main ---

def run(dry_run=False, lead_type=None):
    """Entry point for cron orchestrator."""
    ensure_dirs()

    lead_types = [lead_type] if lead_type else ALL_LEAD_TYPES

    print(f'\n  Lead types: {", ".join(lead_types)}')

    total_drafts = 0
    by_type = {}

    # Enforce daily cap
    local_today = get_today_draft_count()
    global_today = get_global_draft_count()
    remaining_local = max(DAILY_CAP - local_today, 0)
    remaining_global = max(40 - global_today, 0)
    remaining = min(remaining_local, remaining_global)
    print(f'\n  Daily cap: {DAILY_CAP} | KOL today: {local_today} | Global today: {global_today} | Remaining: {remaining}')

    if remaining <= 0:
        print('  Cap reached. Skipping draft generation.')
        return 0

    for lt in lead_types:
        if remaining <= 0:
            print(f'\n--- {lt} --- SKIPPED (cap reached)')
            continue

        print(f'\n--- {lt} ---')
        leads = load_pending_leads(lt)
        leads = leads[:remaining]  # Enforce cap
        print(f'  Loaded {len(leads)} pending leads (capped)')

        generator = GENERATORS.get(lt)
        if not generator or not leads:
            continue

        count = 0
        for lead in leads:
            try:
                email_data = generator(lead)
                if not dry_run:
                    saved = save_draft_to_supabase(lead, email_data, lt)
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
        by_type[lt] = count

    # Telegram notification
    notify_outreach_summary(total_drafts, by_type)

    # Log
    log_scan('kol_outreach_drafter', total_drafts, total_drafts, 0)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE — {total_drafts} drafts generated')
    print(f'  Review in Supabase: kol_outreach_drafts')
    print(f'{"=" * 50}')

    return total_drafts


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — Outreach Drafter')
    parser.add_argument('--type', choices=ALL_LEAD_TYPES)
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — Outreach Drafter')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run, lead_type=args.type)


if __name__ == '__main__':
    main()
