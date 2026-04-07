"""
Altara Aerial — Construction Company Finder
Scrapes Google Maps for construction and building companies in Lagos, Abuja,
and Port Harcourt. Extracts company name, phone, website, address.
Saves to Supabase and CSV. Weekly cron.

Usage:
    python scripts/scrape_construction_leads.py                # All cities
    python scripts/scrape_construction_leads.py --city Lagos    # Single city
    python scripts/scrape_construction_leads.py --dry-run       # Skip Supabase
"""

import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from altara_lead_base import (
    run_apify_actor, save_csv, upsert_leads, promote_to_mql,
    log_scan, ensure_dirs, CITIES
)
from altara_telegram import notify_scan_complete

# --- Search queries by city ---

SEARCH_QUERIES = {
    'Lagos': [
        'construction companies in Lagos',
        'building construction Lagos Nigeria',
        'real estate developers Lagos',
        'civil engineering companies Lagos',
        'property developers Lagos',
        'construction firms Lekki Lagos',
        'building contractors Lagos',
    ],
    'Abuja': [
        'construction companies in Abuja',
        'building construction Abuja Nigeria',
        'real estate developers Abuja',
        'civil engineering companies Abuja',
        'property developers Abuja',
        'building contractors Abuja',
    ],
    'Port Harcourt': [
        'construction companies in Port Harcourt',
        'building construction Port Harcourt Nigeria',
        'real estate developers Port Harcourt',
        'civil engineering companies Port Harcourt',
        'building contractors Port Harcourt',
    ],
}


def scrape_google_maps(city):
    """Scrape Google Maps for construction companies in a city."""
    queries = SEARCH_QUERIES.get(city, [])
    if not queries:
        return []

    print(f'\n  Scraping Google Maps — {city} ({len(queries)} queries)...')

    all_results = []
    for query in queries:
        results = run_apify_actor('compass~crawler-google-places', {
            'searchStringsArray': [query],
            'maxCrawledPlacesPerSearch': 20,
            'language': 'en',
            'includeWebResults': False,
        }, label=f'gmaps-{city}-{query[:30]}', timeout_mins=8)

        all_results.extend(results)

    return all_results


def extract_leads(results, city):
    """Extract and deduplicate construction company leads."""
    leads = []
    seen = set()

    for r in results:
        name = r.get('title', '').strip()
        phone = r.get('phone', '').strip()
        website = r.get('website', '').strip()
        address = r.get('address', '').strip()
        rating = r.get('totalScore', 0) or 0
        reviews = r.get('reviewsCount', 0) or 0
        category = r.get('categoryName', '').lower()

        if not name:
            continue

        # Dedup on name + city
        key = f'{name.lower()}_{city.lower()}'
        if key in seen:
            continue
        seen.add(key)

        # Filter for construction-related businesses
        construction_terms = [
            'construction', 'building', 'contractor', 'civil',
            'engineering', 'developer', 'real estate', 'architect',
            'property', 'structural', 'surveyor',
        ]
        name_lower = name.lower()
        cat_lower = category.lower() if category else ''
        is_construction = any(t in name_lower or t in cat_lower for t in construction_terms)

        # If Google Maps category doesn't match, skip
        if not is_construction:
            continue

        score = score_construction_lead(name, phone, website, rating, reviews, address)

        leads.append({
            'name': '',
            'company': name,
            'phone': phone,
            'email': '',
            'website': website,
            'address': address,
            'city': city,
            'listing_url': r.get('url', ''),
            'instagram': '',
            'followers': 0,
            'score': score,
            'lifecycle_stage': 'subscriber',
            'source': 'Google Maps scrape',
            'notes': f'Rating: {rating}/5 ({reviews} reviews). Category: {category}',
        })

    return leads


def score_construction_lead(name, phone, website, rating, reviews, address):
    """Score a construction company lead 0-10."""
    score = 0

    # Has phone (critical for outreach)
    if phone:
        score += 2

    # Has website (indicates established business)
    if website:
        score += 1.5

    # Google rating quality
    if rating >= 4.5:
        score += 2
    elif rating >= 4.0:
        score += 1.5
    elif rating >= 3.5:
        score += 1

    # Review count (proxy for business size/activity)
    if reviews >= 50:
        score += 2
    elif reviews >= 20:
        score += 1.5
    elif reviews >= 10:
        score += 1
    elif reviews >= 5:
        score += 0.5

    # Company name signals (established firms)
    name_lower = name.lower()
    premium_signals = ['limited', 'ltd', 'plc', 'international', 'group', 'associates']
    if any(s in name_lower for s in premium_signals):
        score += 1

    # Has address (verifiable)
    if address:
        score += 0.5

    return min(round(score, 1), 10)


CSV_FIELDS = [
    'company', 'phone', 'website', 'address', 'city',
    'score', 'lifecycle_stage', 'source', 'notes',
]


def main():
    parser = argparse.ArgumentParser(description='Altara Aerial — Construction Company Finder')
    parser.add_argument('--city', choices=CITIES, help='Scrape single city')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase, CSV only')
    args = parser.parse_args()

    cities = [args.city] if args.city else CITIES
    ensure_dirs()

    print('=' * 50)
    print('  ALTARA AERIAL — Construction Lead Finder')
    print(f'  Cities: {", ".join(cities)}')
    print('=' * 50)

    all_leads = []
    errors = []

    for city in cities:
        try:
            results = scrape_google_maps(city)
            leads = extract_leads(results, city)
            all_leads.extend(leads)
            print(f'  {city}: {len(leads)} construction companies found')
        except Exception as e:
            errors.append(f'{city}: {e}')
            print(f'  ERROR: {city}: {e}')

    # Sort by score
    all_leads.sort(key=lambda x: x['score'], reverse=True)
    print(f'\n  Total leads: {len(all_leads)}')

    # Save CSV
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_csv(all_leads, f'construction-leads-{date_str}.csv', CSV_FIELDS)

    # Save to Supabase
    saved = 0
    promoted = 0
    if not args.dry_run:
        saved = upsert_leads(all_leads, 'construction')
        promoted = promote_to_mql('construction')
        print(f'  Supabase: {saved} saved, {promoted} promoted to MQL')

    # Log
    error_str = '; '.join(errors) if errors else None
    log_scan('construction_finder', len(all_leads), saved, promoted, error_str)

    # Telegram notification
    notify_scan_complete('Construction Finder', len(all_leads), saved, promoted, error_str)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE — {len(all_leads)} leads found')
    print(f'  Top 5:')
    for lead in all_leads[:5]:
        print(f'    {lead["company"]} | {lead["phone"]} | {lead["city"]} | Score: {lead["score"]}')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
