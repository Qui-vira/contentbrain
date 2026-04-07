"""
KOL Lead Gen — AI Consulting Client Finder
Discovers businesses looking for AI automation, trading bots, SaaS development.

Sources:
    A) Apify Upwork scraper — keywords: AI automation, trading bot, SaaS
    B) Apify X/Twitter scraper — hiring/building requests (via apidojo/tweet-scraper)

Schedule: Wednesday 6AM WAT

Usage:
    python scripts/ai_client_finder.py              # Full run
    python scripts/ai_client_finder.py --dry-run    # Skip Supabase writes
"""

import os
import sys
import re
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    fetch_json, search_x_recent, run_apify_actor, is_duplicate,
    upsert_leads, promote_to_mql, save_csv, log_scan, ensure_dirs
)
from kol_telegram import notify_scan_complete

LEAD_TYPE = 'ai_consulting'
LEAD_TYPE_LEADGEN = 'leadgen_service_client'

CSV_FIELDS = [
    'project_name', 'website', 'twitter_handle', 'email',
    'contact_name', 'category', 'description', 'score',
    'priority', 'source', 'lead_type',
]

# Keywords for Upwork search — AI consulting
UPWORK_KEYWORDS = [
    'AI automation',
    'trading bot crypto',
    'SaaS development AI',
    'blockchain development',
    'AI data pipeline',
    'AI chatbot business',
]

# Keywords for Upwork search — lead gen service clients
UPWORK_LEADGEN_KEYWORDS = [
    'lead generation automation',
    'automated outreach system',
    'sales pipeline automation',
    'build me a lead gen bot',
    'scraping and outreach',
    'CRM pipeline developer',
    'cold outreach automation',
    'growth hacking developer',
]

# Budget ranges that indicate serious clients
MIN_BUDGET_USD = 500


# --- Source A: Apify Upwork Scraper ---

LEADGEN_MATCH_WORDS = ['lead gen', 'leadgen', 'outreach', 'scraping', 'crm', 'pipeline', 'prospecting', 'cold email']

def _classify_lead_type(keyword, title):
    """Determine if a job is ai_consulting or leadgen_service_client."""
    title_lower = title.lower()
    if keyword in UPWORK_LEADGEN_KEYWORDS:
        return LEAD_TYPE_LEADGEN
    if any(w in title_lower for w in LEADGEN_MATCH_WORDS):
        return LEAD_TYPE_LEADGEN
    return LEAD_TYPE


def fetch_upwork_jobs():
    """Scrape Upwork for AI consulting + lead gen service opportunities."""
    print('\n  [Upwork] Fetching AI consulting + lead gen opportunities...')

    actor_id = 'neatrat~upwork-job-scraper'
    all_keywords = UPWORK_KEYWORDS + UPWORK_LEADGEN_KEYWORDS

    all_leads = []
    for keyword in all_keywords:
        encoded_kw = keyword.replace(' ', '+')
        search_url = f'https://www.upwork.com/nx/search/jobs/?q={encoded_kw}&sort=recency'

        payload = {
            'urls': [search_url],
            'maxItems': 20,
        }

        results = run_apify_actor(actor_id, payload, label=f'Upwork:{keyword}', timeout_mins=5)

        for job in results:
            title = job.get('title', '').strip()
            if not title:
                continue

            budget_str = str(job.get('budget', '') or '')
            amount = 0
            if budget_str and budget_str != 'N/A':
                clean = budget_str.replace('$', '').replace(',', '').strip()
                try:
                    amount = float(clean)
                except ValueError:
                    pass

            if not amount:
                avg_rate_str = str(job.get('clientAvgHourlyRate', '') or '')
                if avg_rate_str and avg_rate_str != 'N/A':
                    clean = avg_rate_str.replace('$', '').replace(',', '').strip()
                    try:
                        amount = float(clean) * 40
                    except ValueError:
                        pass

            project_name = re.sub(r'[^\w\s\-]', '', title)[:80].strip()
            if not project_name or is_duplicate(project_name):
                continue

            description = job.get('description', '')[:300]
            client_location = job.get('clientLocation', '')
            lead_type = _classify_lead_type(keyword, title)

            budget_score = min(amount / 5000, 10) if amount else 3
            urgency = 8 if any(w in title.lower() for w in ['urgent', 'asap', 'immediately']) else 5
            match_words = ['ai', 'bot', 'automation', 'blockchain', 'saas'] if lead_type == LEAD_TYPE else LEADGEN_MATCH_WORDS
            type_match = 8 if any(w in title.lower() for w in match_words) else 5
            score = round(budget_score * 0.4 + urgency * 0.3 + type_match * 0.3, 1)

            all_leads.append({
                'project_name': project_name,
                'website': job.get('url', ''),
                'category': keyword,
                'description': description,
                'score': score,
                'priority': 'high' if amount >= 3000 else 'normal',
                'source': 'upwork',
                'lead_type': lead_type,
                'notes': f'Budget: ${amount:.0f}, Client: {client_location}',
            })

    print(f'  [Upwork] Total opportunities: {len(all_leads)}')
    return all_leads


# --- Source B: Apify X/Twitter Hiring/Building Requests ---

def fetch_x_ai_requests():
    """Search X for businesses looking for AI/automation/leadgen help via Apify scraper."""
    print('\n  [Apify X] Searching AI + lead gen hiring requests...')

    queries = [
        '"looking for" (AI OR automation OR "trading bot") (developer OR engineer OR builder) -is:retweet',
        '"need someone" (AI OR chatbot OR SaaS OR blockchain) (build OR develop) -is:retweet',
        '"hiring" (AI engineer OR ML engineer OR blockchain developer) -is:retweet',
        '"too much manual prospecting" OR "need more leads" OR "cold outreach automation" -is:retweet',
        '"lead generation" (automation OR bot OR developer OR build) -is:retweet',
    ]

    seen = set()
    leads = []

    for query in queries:
        tweets = search_x_recent(query, max_results=20)
        for tweet in tweets:
            text = tweet.get('text', '')
            author = tweet.get('author_username', '')
            author_name = tweet.get('author_name', '')

            if author.lower() in seen:
                continue
            seen.add(author.lower())

            if tweet.get('author_followers', 0) < 500:
                continue

            project_name = author_name or author
            if is_duplicate(project_name):
                continue

            # Score based on follower count and engagement
            followers = tweet.get('author_followers', 0)
            follower_score = min(followers / 10000, 10)
            likes = tweet.get('metrics', {}).get('like_count', 0)
            engagement_score = min(likes / 10, 10)
            score = round(follower_score * 0.5 + engagement_score * 0.3 + 5 * 0.2, 1)

            # Classify: leadgen if text mentions lead gen keywords
            text_lower = text.lower()
            is_leadgen = any(w in text_lower for w in LEADGEN_MATCH_WORDS + ['need more leads', 'manual prospecting'])
            lead_type = LEAD_TYPE_LEADGEN if is_leadgen else LEAD_TYPE

            leads.append({
                'project_name': project_name,
                'twitter_handle': author,
                'category': 'leadgen_service' if is_leadgen else 'ai_consulting',
                'description': text[:300],
                'score': score,
                'priority': 'normal',
                'source': 'x_api',
                'lead_type': lead_type,
            })

    print(f'  [Apify X] AI consulting leads: {len(leads)}')
    return leads


# --- Main ---

def run(dry_run=False):
    """Entry point for cron orchestrator."""
    ensure_dirs()
    all_leads = []
    errors = []

    # Source A: Upwork
    try:
        all_leads.extend(fetch_upwork_jobs())
    except Exception as e:
        errors.append(f'upwork: {e}')
        print(f'  ERROR: Upwork failed: {e}')

    # Source B: Apify X/Twitter
    try:
        x_leads = fetch_x_ai_requests()
        existing_names = {l['project_name'].lower() for l in all_leads}
        for lead in x_leads:
            if lead['project_name'].lower() not in existing_names:
                all_leads.append(lead)
    except Exception as e:
        errors.append(f'apify_x: {e}')
        print(f'  ERROR: Apify X scraper failed: {e}')

    # Split by lead type
    ai_leads = [l for l in all_leads if l.get('lead_type') != LEAD_TYPE_LEADGEN]
    lg_leads = [l for l in all_leads if l.get('lead_type') == LEAD_TYPE_LEADGEN]
    print(f'\n  Total leads: {len(all_leads)} (AI consulting: {len(ai_leads)}, Lead gen service: {len(lg_leads)})')

    # Save CSV
    if all_leads:
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_csv(all_leads, f'ai-consulting-leads-{date_str}.csv', CSV_FIELDS)

    # Upsert to Supabase — each lead_type separately
    saved = 0
    promoted = 0
    if not dry_run:
        if ai_leads:
            saved += upsert_leads(ai_leads, LEAD_TYPE)
            promoted += promote_to_mql(LEAD_TYPE)
        if lg_leads:
            saved += upsert_leads(lg_leads, LEAD_TYPE_LEADGEN)
            promoted += promote_to_mql(LEAD_TYPE_LEADGEN)

    # Log + notify
    error_str = '; '.join(errors) if errors else None
    log_scan('ai_client_finder', len(all_leads), saved, promoted, error_str)
    notify_scan_complete('AI Client Finder', len(all_leads), saved, promoted, error_str)

    return all_leads


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — AI Client Finder')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — AI Client Finder')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
