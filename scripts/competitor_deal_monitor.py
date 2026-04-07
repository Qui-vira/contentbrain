"""
KOL Lead Gen — Competitor Deal Monitor
Detects sponsored posts and KOL deals from competitors listed in competitor-watchlist.md.
New projects detected = hot leads (they're spending on KOL marketing).

Sources:
    A) Apify X/Twitter scraper — competitor tweets with sponsored signals (#ad, partner, ambassador, ref links)
    B) Apify Instagram scraper — competitor IG for sponsored posts (weekly)

Schedule: Daily 8AM WAT

Usage:
    python scripts/competitor_deal_monitor.py              # Full run
    python scripts/competitor_deal_monitor.py --dry-run    # Skip Supabase writes
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    fetch_json, fetch_x_user_tweets, search_x_recent, run_apify_actor,
    is_duplicate, upsert_leads, save_csv, log_scan, ensure_dirs, APIFY_KEY,
    VAULT_DIR
)
from kol_telegram import notify_scan_complete, notify_competitor_alert

LEAD_TYPE = 'competitor_deal'
LEAD_TYPE_LEADGEN = 'leadgen_service_client'

CSV_FIELDS = [
    'project_name', 'website', 'twitter_handle', 'competitor_handle',
    'deal_type', 'detected_post_url', 'score', 'priority', 'source',
    'description',
]

# Sponsored content signals
SPONSORED_SIGNALS = [
    '#ad', '#sponsored', '#partner', '#ambassador',
    'partner with', 'partnered with', 'ambassador for',
    'in collaboration with', 'paid partnership',
    'referral link', 'ref link', 'use my code', 'use code',
    'sign up with my link', 'sponsored by',
]

# Referral link patterns (exchange/protocol referral URLs)
REF_LINK_PATTERNS = [
    r'https?://\S+[?&]ref[=_]\S+',
    r'https?://\S+/r/\S+',
    r'https?://\S+/invite/\S+',
]


def load_competitor_handles():
    """Parse competitor-watchlist.md for X handles (Web3/AI pillars only)."""
    watchlist_path = VAULT_DIR / 'competitor-watchlist.md'
    if not watchlist_path.exists():
        print('  WARN: competitor-watchlist.md not found')
        return [], []

    content = watchlist_path.read_text(encoding='utf-8')
    x_handles = []
    ig_handles = []

    current_section = ''
    current_platform = ''

    for line in content.split('\n'):
        line = line.strip()

        if line.startswith('## '):
            current_section = line[3:].strip().lower()
        elif line.startswith('### '):
            current_platform = line[4:].strip().lower()

        # Only monitor Web3/Crypto and AI competitors
        if current_section not in ('ai pillar', 'web3 / crypto pillar', 'web3 / crypto'):
            continue

        if line.startswith('- @'):
            # Extract handle
            match = re.match(r'- @(\w+)', line)
            if match:
                handle = match.group(1)
                if 'x' in current_platform or 'twitter' in current_platform:
                    x_handles.append(handle)
                elif 'instagram' in current_platform:
                    ig_handles.append(handle)

    print(f'  Loaded {len(x_handles)} X handles, {len(ig_handles)} IG handles from watchlist')
    return x_handles, ig_handles


# --- Source A: Apify X/Twitter Competitor Monitoring ---

def monitor_x_competitors(x_handles):
    """Check competitor X accounts for sponsored posts via Apify scraper."""
    if not APIFY_KEY:
        print('\n  [Apify X] Skipped — APIFY_API_KEY not set')
        return []

    if not x_handles:
        return []

    print(f'\n  [Apify X] Monitoring {len(x_handles)} competitor accounts...')

    # Fetch recent tweets from all competitor handles in one batch
    tweets = fetch_x_user_tweets(x_handles, max_per_user=10)
    print(f'  [Apify X] Fetched {len(tweets)} tweets from competitors')

    leads = []
    seen_projects = set()

    for tweet in tweets:
        text = tweet.get('text', '')
        text_lower = text.lower()
        handle = tweet.get('author_username', '')

        # Check for sponsored signals
        is_sponsored = any(s in text_lower for s in SPONSORED_SIGNALS)
        has_ref_link = any(re.search(p, text) for p in REF_LINK_PATTERNS)

        if not is_sponsored and not has_ref_link:
            continue

        # Try to extract project name from tweet
        project_name = extract_project_name(text)
        if not project_name or project_name.lower() in seen_projects:
            continue
        seen_projects.add(project_name.lower())

        # Determine deal type
        deal_type = 'unknown'
        if 'ambassador' in text_lower:
            deal_type = 'ambassador'
        elif '#ad' in text_lower or 'sponsored' in text_lower:
            deal_type = 'sponsored_post'
        elif has_ref_link:
            deal_type = 'referral'
        elif 'partner' in text_lower:
            deal_type = 'partnership'

        # High score — competitor is already spending here
        score = 8.0
        tweet_url = tweet.get('tweet_url', f'https://x.com/{handle}')

        lead = {
            'project_name': project_name,
            'twitter_handle': '',
            'competitor_handle': handle,
            'deal_type': deal_type,
            'detected_post_url': tweet_url,
            'score': score,
            'priority': 'high',
            'source': 'apify_x',
            'description': f'Competitor @{handle} has {deal_type} deal. {text[:150]}',
        }
        leads.append(lead)

        # Send immediate alert
        notify_competitor_alert(project_name, handle, deal_type, tweet_url)

    print(f'  [Apify X] Competitor deals detected: {len(leads)}')
    return leads


def extract_project_name(text):
    """Try to extract a project/protocol name from a sponsored tweet."""
    # Look for @mentions (excluding common accounts)
    mentions = re.findall(r'@(\w+)', text)
    skip = {'binance', 'coinbase', 'bitcoin', 'ethereum', 'solana'}
    for m in mentions:
        if m.lower() not in skip and len(m) > 2:
            return m

    # Look for capitalized words that might be project names
    words = text.split()
    for w in words:
        if w[0:1].isupper() and len(w) > 3 and w.isalpha() and w.lower() not in {
            'This', 'The', 'Just', 'New', 'Check', 'Join', 'Use', 'Get', 'Sign',
            'Today', 'Amazing', 'Huge', 'Breaking', 'Excited',
        }:
            return w

    return ''


# --- Source B: Apify Instagram Monitoring ---

def monitor_ig_competitors(ig_handles):
    """Check competitor IG accounts for sponsored posts via Apify."""
    if not ig_handles:
        print('\n  [Instagram] No IG handles to monitor')
        return []

    # Only run weekly (check day)
    if datetime.now().weekday() != 0:  # Monday only
        print('\n  [Instagram] Skipped — runs weekly on Monday')
        return []

    print(f'\n  [Instagram] Monitoring {len(ig_handles)} competitor accounts...')

    leads = []
    actor_id = 'apify~instagram-post-scraper'

    for handle in ig_handles:
        payload = {
            'username': [handle],
            'resultsLimit': 10,
        }

        results = run_apify_actor(actor_id, payload, label=f'IG:{handle}', timeout_mins=5)

        for post in results:
            caption = (post.get('caption', '') or '').lower()

            is_sponsored = any(s in caption for s in SPONSORED_SIGNALS)
            is_paid = post.get('isPaidPartnership', False)

            if not is_sponsored and not is_paid:
                continue

            # Extract project name from caption
            mentions = re.findall(r'@(\w+)', post.get('caption', ''))
            project_name = mentions[0] if mentions else ''
            if not project_name:
                continue

            leads.append({
                'project_name': project_name,
                'competitor_handle': handle,
                'deal_type': 'paid_partnership' if is_paid else 'sponsored_post',
                'detected_post_url': post.get('url', ''),
                'score': 8.0,
                'priority': 'high',
                'source': 'instagram',
                'description': f'IG @{handle} sponsored post for @{project_name}',
            })

    print(f'  [Instagram] Competitor deals detected: {len(leads)}')
    return leads


# --- Source C: Lead Gen Pain Point Monitor (X) ---

def monitor_leadgen_pain_points():
    """Find founders/sales managers complaining about manual lead gen on X."""
    print('\n  [Apify X] Searching lead gen pain points...')

    queries = [
        '"too much manual prospecting" OR "tired of finding leads" -is:retweet',
        '"need more leads" (founder OR CEO OR sales OR startup) -is:retweet',
        '"cold outreach" (broken OR painful OR waste OR manual) -is:retweet',
        '"lead generation" (struggling OR help OR automate OR broken) -is:retweet',
    ]

    seen = set()
    leads = []

    for query in queries:
        tweets = search_x_recent(query, max_results=15)
        for tweet in tweets:
            text = tweet.get('text', '')
            author = tweet.get('author_username', '')
            author_name = tweet.get('author_name', '')

            if author.lower() in seen:
                continue
            seen.add(author.lower())

            if tweet.get('author_followers', 0) < 300:
                continue

            project_name = author_name or author
            if is_duplicate(project_name):
                continue

            followers = tweet.get('author_followers', 0)
            follower_score = min(followers / 10000, 10)
            likes = tweet.get('metrics', {}).get('like_count', 0)
            engagement_score = min(likes / 10, 10)
            score = round(follower_score * 0.4 + engagement_score * 0.3 + 6 * 0.3, 1)

            leads.append({
                'project_name': project_name,
                'twitter_handle': author,
                'deal_type': 'pain_point',
                'detected_post_url': tweet.get('tweet_url', ''),
                'score': score,
                'priority': 'high' if followers >= 5000 else 'normal',
                'source': 'apify_x',
                'description': text[:200],
            })

    print(f'  [Apify X] Lead gen pain point leads: {len(leads)}')
    return leads


# --- Main ---

def run(dry_run=False):
    """Entry point for cron orchestrator."""
    ensure_dirs()
    all_leads = []
    leadgen_leads = []
    errors = []

    x_handles, ig_handles = load_competitor_handles()

    # Source A: Apify X/Twitter competitor deals
    try:
        all_leads.extend(monitor_x_competitors(x_handles))
    except Exception as e:
        errors.append(f'apify_x: {e}')
        print(f'  ERROR: X monitoring failed: {e}')

    # Source B: Instagram competitor deals
    try:
        all_leads.extend(monitor_ig_competitors(ig_handles))
    except Exception as e:
        errors.append(f'instagram: {e}')
        print(f'  ERROR: IG monitoring failed: {e}')

    # Source C: Lead gen pain point monitoring
    try:
        leadgen_leads.extend(monitor_leadgen_pain_points())
    except Exception as e:
        errors.append(f'leadgen_pain: {e}')
        print(f'  ERROR: Lead gen pain point monitor failed: {e}')

    # Filter out already-contacted projects
    new_leads = [l for l in all_leads if not is_duplicate(l['project_name'])]
    new_leadgen = [l for l in leadgen_leads if not is_duplicate(l['project_name'])]
    print(f'\n  Total new competitor deals: {len(new_leads)} (filtered from {len(all_leads)})')
    print(f'  Total new leadgen pain points: {len(new_leadgen)} (filtered from {len(leadgen_leads)})')

    # Save CSV
    combined = new_leads + new_leadgen
    if combined:
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_csv(combined, f'competitor-deals-{date_str}.csv', CSV_FIELDS)

    # Upsert to Supabase
    saved = 0
    if not dry_run:
        if new_leads:
            saved += upsert_leads(new_leads, LEAD_TYPE)
        if new_leadgen:
            saved += upsert_leads(new_leadgen, LEAD_TYPE_LEADGEN)

    # Log + notify
    error_str = '; '.join(errors) if errors else None
    log_scan('competitor_deal_monitor', len(combined), saved, 0, error_str)
    notify_scan_complete('Competitor Deal Monitor', len(combined), saved, 0, error_str)

    return combined


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — Competitor Deal Monitor')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — Competitor Deal Monitor')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
