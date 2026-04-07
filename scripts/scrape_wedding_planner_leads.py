"""
Altara Aerial — Wedding Planner Finder
Uses Apify Instagram scraper to find wedding planners in Lagos and Abuja.
Scores by follower count and post frequency. Saves to Supabase and CSV.

Usage:
    python scripts/scrape_wedding_planner_leads.py              # All keywords
    python scripts/scrape_wedding_planner_leads.py --dry-run    # Skip Supabase
"""

import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from altara_lead_base import (
    run_apify_actor, save_csv, upsert_leads, promote_to_mql,
    log_scan, ensure_dirs
)
from altara_telegram import notify_scan_complete

# --- Search config ---

HASHTAG_URLS = [
    # Wedding planners Lagos
    'https://www.instagram.com/explore/tags/weddingplannerlagos/',
    'https://www.instagram.com/explore/tags/lagosweddingplanner/',
    'https://www.instagram.com/explore/tags/nigerianweddingplanner/',
    'https://www.instagram.com/explore/tags/weddingplannerinnigeria/',
    'https://www.instagram.com/explore/tags/lagoswedding/',
    'https://www.instagram.com/explore/tags/nigerianeventplanner/',
    # Wedding planners Abuja
    'https://www.instagram.com/explore/tags/abujaweddingplanner/',
    'https://www.instagram.com/explore/tags/eventplannerabuja/',
    'https://www.instagram.com/explore/tags/abujawedding/',
    'https://www.instagram.com/explore/tags/weddingcoordinatorabuja/',
    # Event planners general
    'https://www.instagram.com/explore/tags/eventplannernigeria/',
    'https://www.instagram.com/explore/tags/nigerianweddings/',
    'https://www.instagram.com/explore/tags/weddingvendornigeria/',
    'https://www.instagram.com/explore/tags/lagosweddingvendor/',
    'https://www.instagram.com/explore/tags/nigerianweddingvendors/',
]

WEDDING_TERMS = [
    'wedding planner', 'event planner', 'wedding coordinator',
    'event coordinator', 'wedding decor', 'event decor',
    'wedding planning', 'event planning', 'bridal',
    'weddings', 'event management', 'event designer',
    'party planner', 'event stylist', 'wedding stylist',
    'celebration', 'nuptials', 'destination wedding',
]

NIGERIA_TERMS = [
    'nigeria', 'lagos', 'abuja', 'naija', 'lekki', 'vi',
    'ikeja', 'ikoyi', 'ajah', 'wuse', 'garki', 'maitama',
    'gwarinpa', 'surulere', 'festac', 'port harcourt',
]


def step_1_hashtag_scrape():
    """Scrape hashtag pages for wedding planner posts."""
    print('\n=== Step 1: Hashtag scraping ===')
    profiles = {}

    batch_size = 5
    for i in range(0, len(HASHTAG_URLS), batch_size):
        batch = HASHTAG_URLS[i:i + batch_size]
        results = run_apify_actor('apify~instagram-scraper', {
            'directUrls': batch,
            'resultsType': 'posts',
            'resultsLimit': 30,
        }, label=f'hashtag batch {i // batch_size + 1}')

        for item in results:
            username = item.get('ownerUsername', '')
            if not username:
                continue
            caption = item.get('caption', '') or ''
            timestamp = item.get('timestamp', '')

            if username not in profiles:
                profiles[username] = {
                    'username': username,
                    'full_name': '',
                    'bio': '',
                    'followers': 0,
                    'following': 0,
                    'posts_count': 0,
                    'profile_url': f'https://instagram.com/{username}',
                    'external_url': '',
                    'is_verified': False,
                    'is_business': False,
                    'captions': [caption] if caption else [],
                    'post_dates': [timestamp] if timestamp else [],
                }
            else:
                if caption and caption not in profiles[username]['captions']:
                    profiles[username]['captions'].append(caption)
                if timestamp:
                    profiles[username]['post_dates'].append(timestamp)

    print(f'  Step 1 found {len(profiles)} unique usernames')
    return profiles


def step_2_enrich(profiles):
    """Enrich profiles with full bio, follower data, business status."""
    print(f'\n=== Step 2: Enriching {len(profiles)} profiles ===')
    usernames = list(profiles.keys())

    batch_size = 10
    for i in range(0, len(usernames), batch_size):
        batch = usernames[i:i + batch_size]
        urls = [f'https://www.instagram.com/{u}/' for u in batch]

        results = run_apify_actor('apify~instagram-scraper', {
            'directUrls': urls,
            'resultsType': 'details',
            'resultsLimit': 1,
        }, label=f'enrich batch {i // batch_size + 1}')

        for item in results:
            username = item.get('username', '')
            if username in profiles:
                profiles[username]['bio'] = item.get('biography', '') or ''
                profiles[username]['followers'] = item.get('followersCount', 0) or 0
                profiles[username]['following'] = item.get('followsCount', 0) or 0
                profiles[username]['posts_count'] = item.get('postsCount', 0) or 0
                profiles[username]['full_name'] = item.get('fullName', '') or ''
                profiles[username]['is_verified'] = item.get('verified', False)
                profiles[username]['is_business'] = item.get('isBusinessAccount', False)
                profiles[username]['external_url'] = item.get('externalUrl', '') or ''

    return profiles


def step_3_filter_and_score(profiles):
    """Filter for wedding planners in Nigeria and score 0-10."""
    print(f'\n=== Step 3: Filtering and scoring ===')
    scored = []

    for username, p in profiles.items():
        bio = p.get('bio', '') or ''
        captions_text = ' '.join(p.get('captions', []))
        all_text = f"{bio} {captions_text} {p.get('full_name', '')}"
        all_lower = all_text.lower()
        followers = p.get('followers', 0) or 0

        # Must have wedding/event signal
        is_wedding = any(term in all_lower for term in WEDDING_TERMS)
        if not is_wedding:
            continue

        # Must have Nigeria signal
        is_nigeria = any(term in all_lower for term in NIGERIA_TERMS)
        if not is_nigeria:
            continue

        # Score 0-10
        score = 0

        # Wedding relevance (0-3)
        wedding_count = sum(1 for t in WEDDING_TERMS if t in all_lower)
        score += min(wedding_count, 3)

        # Nigeria location confirmed in bio (0-2)
        bio_lower = bio.lower()
        if any(t in bio_lower for t in NIGERIA_TERMS):
            score += 2
        else:
            score += 1

        # Followers (0-2)
        if followers >= 10000:
            score += 2
        elif followers >= 5000:
            score += 1.5
        elif followers >= 1000:
            score += 1
        elif followers >= 500:
            score += 0.5

        # Post frequency — active accounts score higher (0-1.5)
        posts = p.get('posts_count', 0) or 0
        if posts >= 500:
            score += 1.5
        elif posts >= 200:
            score += 1
        elif posts >= 50:
            score += 0.5

        # Business account (0-0.5)
        if p.get('is_business'):
            score += 0.5

        # Professional signals in bio (0-1)
        pro_signals = ['booking', 'book us', 'hire', 'services', 'dm for',
                       'contact', 'available', 'certified', 'for hire', 'inquiries']
        if any(s in bio_lower for s in pro_signals):
            score += 1

        score = min(round(score, 1), 10)

        # Detect city
        city = 'Unknown'
        for c in ['Lagos', 'Abuja', 'Port Harcourt']:
            if c.lower() in all_lower:
                city = c
                break

        scored.append({
            'name': p.get('full_name', ''),
            'company': username,
            'phone': '',
            'email': '',
            'website': p.get('external_url', ''),
            'address': '',
            'city': city,
            'listing_url': p.get('profile_url', ''),
            'instagram': username,
            'followers': followers,
            'score': score,
            'lifecycle_stage': 'subscriber',
            'source': 'Instagram hashtag scrape',
            'notes': f"Posts: {p.get('posts_count', 0)}. "
                     f"Business: {p.get('is_business', False)}. "
                     f"Bio: {bio[:100]}",
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    scored = scored[:50]  # Keep top 50

    print(f'  {len(scored)} wedding planners scored (top 50 kept)')
    return scored


CSV_FIELDS = [
    'name', 'instagram', 'followers', 'city', 'website',
    'score', 'lifecycle_stage', 'source', 'notes',
]


def main():
    parser = argparse.ArgumentParser(description='Altara Aerial — Wedding Planner Finder')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase, CSV only')
    args = parser.parse_args()

    ensure_dirs()

    print('=' * 50)
    print('  ALTARA AERIAL — Wedding Planner Finder')
    print('  Cities: Lagos, Abuja')
    print('=' * 50)

    errors = []

    # Step 1: Hashtag scraping
    try:
        profiles = step_1_hashtag_scrape()
    except Exception as e:
        print(f'ERROR in hashtag scrape: {e}')
        errors.append(f'scrape: {e}')
        profiles = {}

    if not profiles:
        print('No profiles found. Exiting.')
        log_scan('wedding_finder', 0, 0, 0, '; '.join(errors) if errors else 'No profiles')
        sys.exit(1)

    # Step 2: Enrich
    try:
        profiles = step_2_enrich(profiles)
    except Exception as e:
        errors.append(f'enrich: {e}')
        print(f'ERROR in enrichment: {e}')

    # Step 3: Filter and score
    leads = step_3_filter_and_score(profiles)

    # Save CSV
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_csv(leads, f'wedding-planner-leads-{date_str}.csv', CSV_FIELDS)

    # Save to Supabase
    saved = 0
    promoted = 0
    if not args.dry_run:
        saved = upsert_leads(leads, 'wedding')
        promoted = promote_to_mql('wedding')
        print(f'  Supabase: {saved} saved, {promoted} promoted to MQL')

    # Log
    error_str = '; '.join(errors) if errors else None
    log_scan('wedding_finder', len(leads), saved, promoted, error_str)

    # Telegram notification
    notify_scan_complete('Wedding Planner Finder', len(leads), saved, promoted, error_str)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE — {len(leads)} leads found')
    print(f'  Top 5:')
    for lead in leads[:5]:
        print(f'    @{lead["instagram"]} | {lead["followers"]} followers | {lead["city"]} | Score: {lead["score"]}')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
