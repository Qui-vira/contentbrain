"""
Altara Aerial Lead Generation — Shared utilities.
Supabase client, CSV writer, Apify runner, lead scoring, lifecycle stages.
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

APIFY_KEY = os.getenv('APIFY_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
APIFY_BASE = 'https://api.apify.com/v2'

VAULT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = VAULT_DIR / '06-Drafts' / 'altara-leads'
LOG_DIR = VAULT_DIR / '07-Analytics' / 'altara-aerial'
TABLE_CLIENTS = 'altara_client_leads'
TABLE_PILOTS = 'altara_pilot_prospects'
TABLE_DRAFTS = 'altara_outreach_drafts'

LIFECYCLE_STAGES = ['subscriber', 'mql', 'sql', 'opportunity', 'customer']

CITIES = ['Lagos', 'Abuja', 'Port Harcourt']

# MQL scoring thresholds by lead type
MQL_THRESHOLDS = {
    'real_estate': 5.0,
    'construction': 4.0,
    'wedding': 5.0,
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
    """Insert or update leads in Supabase. Dedupes on phone + lead_type."""
    sb = get_supabase()
    if not sb:
        return 0

    url = f"{sb['url']}/rest/v1/{TABLE_CLIENTS}"
    inserted = 0

    for lead in leads:
        row = {
            'lead_type': lead_type,
            'name': lead.get('name', ''),
            'company': lead.get('company', ''),
            'phone': lead.get('phone', ''),
            'email': lead.get('email', ''),
            'website': lead.get('website', ''),
            'address': lead.get('address', ''),
            'city': lead.get('city', ''),
            'listing_url': lead.get('listing_url', ''),
            'instagram': lead.get('instagram', ''),
            'followers': lead.get('followers', 0),
            'score': lead.get('score', 0),
            'lifecycle_stage': lead.get('lifecycle_stage', 'subscriber'),
            'outreach_status': 'not_contacted',
            'source': lead.get('source', ''),
            'notes': lead.get('notes', ''),
            'scraped_at': datetime.now(timezone.utc).isoformat(),
        }

        # Check for existing lead (dedup on phone + lead_type)
        phone = row['phone']
        if phone:
            check_url = f"{url}?phone=eq.{phone}&lead_type=eq.{lead_type}&select=id"
            resp = requests.get(check_url, headers=sb['headers'], timeout=10)
            if resp.ok and resp.json():
                # Update existing
                lead_id = resp.json()[0]['id']
                update_url = f"{url}?id=eq.{lead_id}"
                row['updated_at'] = datetime.now(timezone.utc).isoformat()
                requests.patch(update_url, json=row, headers=sb['headers'], timeout=10)
                inserted += 1
                continue

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
    url = f"{sb['url']}/rest/v1/{TABLE_CLIENTS}"

    # Find subscribers above threshold
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


# --- CSV ---

def save_csv(leads, filename, fieldnames):
    """Save leads to CSV in altara-leads folder."""
    ensure_dirs()
    path = OUTPUT_DIR / filename
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(leads)
    print(f'  CSV saved: {path} ({len(leads)} rows)')
    return path


# --- Apify ---

def run_apify_actor(actor_id, payload, label='', timeout_mins=10):
    """Run an Apify actor and return results. Follows scrape_drone_pilots.py pattern."""
    if not APIFY_KEY:
        print('ERROR: APIFY_API_KEY not set in .env')
        sys.exit(1)

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
            max_polls = timeout_mins * 12  # poll every 5s
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


# --- Logging ---

def log_scan(script_name, leads_found, leads_saved, leads_promoted, errors=None):
    """Append scan results to altara-aerial scan log."""
    ensure_dirs()
    log_path = LOG_DIR / 'lead-scan-log.md'

    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y-%m-%d %H:%M UTC')

    if not log_path.exists():
        header = """# Altara Aerial Lead Scan Log

> Automated lead generation runs logged here.

| Timestamp | Script | Found | Saved | Promoted to MQL | Errors |
|-----------|--------|-------|-------|-----------------|--------|
"""
        log_path.write_text(header, encoding='utf-8')

    error_str = str(errors) if errors else '—'
    row = f'| {timestamp} | {script_name} | {leads_found} | {leads_saved} | {leads_promoted} | {error_str} |\n'

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(row)
