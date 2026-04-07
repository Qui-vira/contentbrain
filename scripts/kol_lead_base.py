"""
KOL & Consulting Lead Generation — Shared utilities.
Supabase client, CSV writer, lead scoring, dedup, Apify X/Twitter scraper.
Separate from altara_lead_base.py — different dedup logic, scoring, tables.
"""

import os
import sys
import csv
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Config ---

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
APIFY_KEY = os.getenv('APIFY_API_KEY')
APIFY_BASE = 'https://api.apify.com/v2'
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
CMC_API_KEY = os.getenv('CMC_API_KEY', '')

# X/Twitter scraping via Apify (apidojo/tweet-scraper) — no API key needed
APIFY_TWEET_ACTOR = 'apidojo~tweet-scraper'

VAULT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = VAULT_DIR / '06-Drafts' / 'kol-leads'
LOG_DIR = VAULT_DIR / '07-Analytics' / 'kol-pipeline'
PARTNERSHIPS_DIR = VAULT_DIR / '10-Niche-Knowledge' / 'partnerships'
TABLE_LEADS = 'kol_leads'
TABLE_DRAFTS = 'kol_outreach_drafts'

LIFECYCLE_STAGES = ['subscriber', 'mql', 'sql', 'opportunity', 'customer']

# MQL scoring thresholds by lead type
MQL_THRESHOLDS = {
    'new_exchange': 5.0,
    'new_token': 6.0,
    'defi_protocol': 5.0,
    'funded_project': 4.0,
    'ai_consulting': 5.0,
    'competitor_deal': 3.0,
    'leadgen_service_client': 4.0,
}


def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


# --- Supabase ---

def get_supabase():
    """Return Supabase REST headers. No SDK dependency."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print('WARN: SUPABASE_URL or SUPABASE_ANON_KEY not set. CSV-only mode.')
        return None
    return {
        'url': SUPABASE_URL,
        'headers': {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        }
    }


def upsert_leads(leads, lead_type):
    """Insert or update leads in Supabase. Dedupes on project_name + lead_type."""
    sb = get_supabase()
    if not sb:
        return 0

    url = f"{sb['url']}/rest/v1/{TABLE_LEADS}"
    inserted = 0

    for lead in leads:
        project_name = lead.get('project_name', '').strip()
        if not project_name:
            continue

        row = {
            'lead_type': lead_type,
            'project_name': project_name,
            'token_symbol': lead.get('token_symbol', ''),
            'website': lead.get('website', ''),
            'twitter_handle': lead.get('twitter_handle', ''),
            'email': lead.get('email', ''),
            'contact_name': lead.get('contact_name', ''),
            'category': lead.get('category', ''),
            'description': lead.get('description', ''),
            'score': lead.get('score', 0),
            'priority': lead.get('priority', 'normal'),
            'funding_amount': lead.get('funding_amount', 0),
            'funding_round': lead.get('funding_round', ''),
            'investors': lead.get('investors', ''),
            'trust_score': lead.get('trust_score', 0),
            'volume_24h': lead.get('volume_24h', 0),
            'year_established': lead.get('year_established', 0),
            'tvl': lead.get('tvl', 0),
            'chain': lead.get('chain', ''),
            'competitor_handle': lead.get('competitor_handle', ''),
            'deal_type': lead.get('deal_type', ''),
            'detected_post_url': lead.get('detected_post_url', ''),
            'lifecycle_stage': lead.get('lifecycle_stage', 'subscriber'),
            'outreach_status': 'not_contacted',
            'source': lead.get('source', ''),
            'notes': lead.get('notes', ''),
            'scraped_at': datetime.now(timezone.utc).isoformat(),
        }

        # Check for existing lead (dedup on project_name + lead_type)
        check_url = (
            f"{url}?project_name=eq.{requests.utils.quote(project_name)}"
            f"&lead_type=eq.{lead_type}&select=id"
        )
        try:
            resp = requests.get(check_url, headers=sb['headers'], timeout=10)
            if resp.ok and resp.json():
                # Update existing — don't overwrite outreach_status
                lead_id = resp.json()[0]['id']
                update_url = f"{url}?id=eq.{lead_id}"
                row.pop('outreach_status', None)
                row['updated_at'] = datetime.now(timezone.utc).isoformat()
                requests.patch(update_url, json=row, headers=sb['headers'], timeout=10)
                inserted += 1
                continue
        except Exception as e:
            print(f'  WARN: Dedup check failed for {project_name}: {e}')

        # Insert new
        resp = requests.post(url, json=row, headers=sb['headers'], timeout=10)
        if resp.status_code in (200, 201, 204):
            inserted += 1
        else:
            print(f'  WARN: Supabase insert failed: {resp.status_code} {resp.text[:100]}')

    return inserted


def promote_to_mql(lead_type):
    """Promote leads above MQL threshold from subscriber to mql."""
    sb = get_supabase()
    if not sb:
        return 0

    threshold = MQL_THRESHOLDS.get(lead_type, 5.0)
    url = f"{sb['url']}/rest/v1/{TABLE_LEADS}"

    query = f"{url}?lead_type=eq.{lead_type}&lifecycle_stage=eq.subscriber&score=gte.{threshold}&select=id"
    resp = requests.get(query, headers=sb['headers'], timeout=10)
    if not resp.ok:
        return 0

    ids = [r['id'] for r in resp.json()]
    promoted = 0
    for lead_id in ids:
        patch_url = f"{url}?id=eq.{lead_id}"
        resp = requests.patch(
            patch_url,
            json={'lifecycle_stage': 'mql', 'updated_at': datetime.now(timezone.utc).isoformat()},
            headers=sb['headers'], timeout=10
        )
        if resp.status_code in (200, 204):
            promoted += 1

    return promoted


# --- Dedup against existing contacts ---

_existing_contacts = None


def load_existing_contacts():
    """Load all project names from partnership CSVs to prevent duplicate outreach."""
    global _existing_contacts
    if _existing_contacts is not None:
        return _existing_contacts

    contacts = set()
    if not PARTNERSHIPS_DIR.exists():
        _existing_contacts = contacts
        return contacts

    for csv_path in PARTNERSHIPS_DIR.glob('*.csv'):
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check common column names for project/company names
                    for col in ['project', 'project_name', 'name', 'company', 'exchange', 'platform']:
                        val = row.get(col, '').strip().lower()
                        if val:
                            contacts.add(val)
        except Exception:
            continue

    print(f'  Loaded {len(contacts)} existing contacts from CSVs')
    _existing_contacts = contacts
    return contacts


def is_duplicate(project_name):
    """Check if project already exists in CSV contacts or Supabase."""
    contacts = load_existing_contacts()
    name_lower = project_name.strip().lower()
    if name_lower in contacts:
        return True

    # Also check Supabase
    sb = get_supabase()
    if sb:
        url = f"{sb['url']}/rest/v1/{TABLE_LEADS}"
        check_url = f"{url}?project_name=eq.{requests.utils.quote(project_name)}&select=id&limit=1"
        try:
            resp = requests.get(check_url, headers=sb['headers'], timeout=10)
            if resp.ok and resp.json():
                return True
        except Exception:
            pass

    return False


# --- HTTP helpers ---

def fetch_json(url, headers=None, params=None, retries=2, timeout=15):
    """GET request with retry. Returns parsed JSON or None."""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = int(resp.headers.get('Retry-After', 30))
                print(f'  Rate limited. Waiting {wait}s...')
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            print(f'  WARN: fetch_json failed for {url}: {e}')
            return None
    return None


def search_x_recent(query, max_results=20):
    """Search recent tweets via Apify apidojo/tweet-scraper. No X API key needed."""
    if not APIFY_KEY:
        print('  INFO: APIFY_API_KEY not set. Skipping X search.')
        return []

    payload = {
        'searchTerms': [query],
        'maxTweets': max_results,
        'searchMode': 'live',
    }

    results = run_apify_actor(APIFY_TWEET_ACTOR, payload, label=f'X:{query[:40]}', timeout_mins=3)

    tweets = []
    for item in results:
        if item.get('type') != 'tweet':
            continue
        author = item.get('author', {})
        tweets.append({
            'text': item.get('text', '') or item.get('fullText', ''),
            'created_at': item.get('createdAt', ''),
            'metrics': {
                'like_count': item.get('likeCount', 0),
                'retweet_count': item.get('retweetCount', 0),
                'reply_count': item.get('replyCount', 0),
                'view_count': item.get('viewCount', 0),
            },
            'author_username': author.get('userName', ''),
            'author_name': author.get('name', ''),
            'author_followers': author.get('followers', 0),
            'tweet_url': item.get('url', ''),
        })

    return tweets


def fetch_x_user_tweets(handles, max_per_user=10):
    """Fetch recent tweets from specific X handles via Apify. No X API key needed."""
    if not APIFY_KEY:
        print('  INFO: APIFY_API_KEY not set. Skipping X user fetch.')
        return []

    payload = {
        'twitterHandles': handles,
        'maxTweets': max_per_user * len(handles),
        'searchMode': 'live',
    }

    results = run_apify_actor(APIFY_TWEET_ACTOR, payload, label=f'X:users({len(handles)})', timeout_mins=5)

    tweets = []
    for item in results:
        if item.get('type') != 'tweet':
            continue
        author = item.get('author', {})
        tweets.append({
            'text': item.get('text', '') or item.get('fullText', ''),
            'created_at': item.get('createdAt', ''),
            'metrics': {
                'like_count': item.get('likeCount', 0),
                'retweet_count': item.get('retweetCount', 0),
                'reply_count': item.get('replyCount', 0),
                'view_count': item.get('viewCount', 0),
            },
            'author_username': author.get('userName', ''),
            'author_name': author.get('name', ''),
            'author_followers': author.get('followers', 0),
            'tweet_url': item.get('url', ''),
        })

    return tweets


# --- Apify ---

def run_apify_actor(actor_id, payload, label='', timeout_mins=10):
    """Run an Apify actor and return results."""
    if not APIFY_KEY:
        print(f'  WARN: APIFY_API_KEY not set. Skipping {label}.')
        return []

    headers = {'Authorization': f'Bearer {APIFY_KEY}'}
    url = f'{APIFY_BASE}/acts/{actor_id}/runs'

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()['data']
            run_id = data['id']
            dataset_id = data['defaultDatasetId']
            print(f'  [{label}] Run started: {run_id}')

            status_url = f'{APIFY_BASE}/actor-runs/{run_id}'
            max_polls = timeout_mins * 12
            for i in range(max_polls):
                time.sleep(5)
                status = requests.get(status_url, headers=headers, timeout=15).json()
                state = status['data']['status']
                if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
                    break
                if i % 12 == 0 and i > 0:
                    print(f'    Still waiting... ({state})')

            if state != 'SUCCEEDED':
                print(f'  WARN: [{label}] ended with {state}')
                if attempt < max_retries:
                    print('  Retrying in 10s...')
                    time.sleep(10)
                    continue
                return []

            results_url = f'{APIFY_BASE}/datasets/{dataset_id}/items'
            results = requests.get(results_url, headers=headers, timeout=30).json()
            if isinstance(results, list):
                print(f'  [{label}] Got {len(results)} results')
                return results
            return []

        except Exception as e:
            print(f'  WARN: [{label}] attempt {attempt+1} failed: {e}')
            if attempt < max_retries:
                time.sleep(10)
                continue
            return []
    return []


# --- CSV ---

def save_csv(leads, filename, fieldnames):
    """Save leads to CSV in kol-leads folder."""
    ensure_dirs()
    path = OUTPUT_DIR / filename
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(leads)
    print(f'  CSV saved: {path} ({len(leads)} rows)')
    return path


# --- Logging ---

def log_scan(script_name, leads_found, leads_saved, leads_promoted, errors=None):
    """Append scan results to kol-pipeline scan log."""
    ensure_dirs()
    log_path = LOG_DIR / 'lead-scan-log.md'

    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y-%m-%d %H:%M UTC')

    if not log_path.exists():
        header = """# KOL Lead Scan Log

> Automated KOL/consulting lead generation runs logged here.

| Timestamp | Script | Found | Saved | Promoted to MQL | Errors |
|-----------|--------|-------|-------|-----------------|--------|
"""
        log_path.write_text(header, encoding='utf-8')

    error_str = str(errors) if errors else '\u2014'
    row = f'| {timestamp} | {script_name} | {leads_found} | {leads_saved} | {leads_promoted} | {error_str} |\n'

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(row)
