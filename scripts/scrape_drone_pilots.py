"""
Drone Pilot Recruitment Scraper
Scrapes Instagram hashtags for drone camera pilots in Nigeria using Apify.
Outputs scored CSV to 06-Drafts/drone-pilot-prospects.csv
"""

import os
import sys
import csv
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')
if not API_KEY:
    print('ERROR: APIFY_API_KEY not found in .env')
    sys.exit(1)

HEADERS = {'Authorization': f'Bearer {API_KEY}'}
BASE_URL = 'https://api.apify.com/v2'

# --- Hashtag URLs to scrape for drone pilots in Nigeria ---
HASHTAG_URLS = [
    'https://www.instagram.com/explore/tags/dronepilotlagos/',
    'https://www.instagram.com/explore/tags/dronepilotnaija/',
    'https://www.instagram.com/explore/tags/dronephotonigeria/',
    'https://www.instagram.com/explore/tags/dronephotographylagos/',
    'https://www.instagram.com/explore/tags/dronephotographynigeria/',
    'https://www.instagram.com/explore/tags/aerialphotographylagos/',
    'https://www.instagram.com/explore/tags/aerialphotographynigeria/',
    'https://www.instagram.com/explore/tags/dronevideonigeria/',
    'https://www.instagram.com/explore/tags/dronenigeria/',
    'https://www.instagram.com/explore/tags/dronelagos/',
    'https://www.instagram.com/explore/tags/fpvnigeria/',
    'https://www.instagram.com/explore/tags/fpvlagos/',
    'https://www.instagram.com/explore/tags/djinigeria/',
    'https://www.instagram.com/explore/tags/droneabuja/',
    'https://www.instagram.com/explore/tags/droneportharcourt/',
    'https://www.instagram.com/explore/tags/aeriallagos/',
    'https://www.instagram.com/explore/tags/droneshotlagos/',
    'https://www.instagram.com/explore/tags/dronepilotabuja/',
    'https://www.instagram.com/explore/tags/lagosaerial/',
    'https://www.instagram.com/explore/tags/dronefilminglagos/',
]

DRONE_TERMS = [
    'drone', 'aerial', 'fpv', 'dji', 'mavic', 'phantom', 'mini 3', 'mini 4',
    'air 2s', 'air 3', 'inspire', 'cinematography', 'pilot', 'uav', 'quadcopter',
    'drone operator', 'drone photography', 'drone videography', 'aerial shot',
    'aerial view', 'bird eye', 'sky view', 'flyover',
]

NIGERIA_TERMS = [
    'nigeria', 'lagos', 'abuja', 'port harcourt', 'ph', 'naija', 'lekki',
    'vi', 'ikeja', 'ikoyi', 'ajah', 'wuse', 'garki', 'maitama', 'gwarinpa',
    'surulere', 'yaba', 'festac', 'owerri', 'enugu', 'calabar', 'ibadan',
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / '06-Drafts'


def run_actor(actor_id, payload, label=''):
    """Run an Apify actor and return results."""
    url = f'{BASE_URL}/acts/{actor_id}/runs'
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()['data']
            run_id = data['id']
            dataset_id = data['defaultDatasetId']
            print(f'  [{label}] Run started: {run_id}')

            status_url = f'{BASE_URL}/actor-runs/{run_id}'
            for i in range(120):
                time.sleep(5)
                status = requests.get(status_url, headers=HEADERS, timeout=15).json()
                state = status['data']['status']
                if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
                    break
                if i % 12 == 0 and i > 0:
                    print(f'    Still waiting... ({state})')

            if state != 'SUCCEEDED':
                print(f'  WARN: [{label}] ended with {state}')
                if attempt < max_retries:
                    print(f'  Retrying in 10s...')
                    time.sleep(10)
                    continue
                return []

            results_url = f'{BASE_URL}/datasets/{dataset_id}/items'
            results = requests.get(results_url, headers=HEADERS, timeout=30).json()
            if isinstance(results, list):
                print(f'  [{label}] Got {len(results)} results')
                return results
            else:
                print(f'  [{label}] Non-list response: {str(results)[:100]}')
                return []

        except Exception as e:
            print(f'  WARN: [{label}] attempt {attempt+1} failed: {e}')
            if attempt < max_retries:
                time.sleep(10)
                continue
            return []
    return []


def step_1a_hashtag_scrape():
    """Scrape hashtag pages for drone-related posts, extract owner usernames."""
    print('\n=== Step 1A: Hashtag scraping ===')
    profiles = {}

    # Batch hashtags in groups of 5 to reduce API calls
    batch_size = 5
    for i in range(0, len(HASHTAG_URLS), batch_size):
        batch = HASHTAG_URLS[i:i + batch_size]
        results = run_actor('apify~instagram-scraper', {
            'directUrls': batch,
            'resultsType': 'posts',
            'resultsLimit': 30,
        }, label=f'hashtag batch {i // batch_size + 1}')

        for item in results:
            username = item.get('ownerUsername', '')
            if not username:
                continue
            caption = item.get('caption', '') or ''

            if username not in profiles:
                profiles[username] = {
                    'username': username,
                    'full_name': '',
                    'bio': '',
                    'followers': 0,
                    'profile_url': f'https://instagram.com/{username}',
                    'profile_pic': '',
                    'is_verified': False,
                    'external_url': '',
                    'source': 'hashtag_scrape',
                    'captions': [caption] if caption else [],
                }
            else:
                if caption and caption not in profiles[username]['captions']:
                    profiles[username]['captions'].append(caption)

    print(f'\nStep 1A found {len(profiles)} unique usernames from hashtag posts')
    return profiles


def step_1b_enrich(profiles):
    """Enrich profiles with full bio/follower data."""
    print(f'\n=== Step 1B: Enriching {len(profiles)} profiles ===')
    usernames = list(profiles.keys())

    batch_size = 10
    for i in range(0, len(usernames), batch_size):
        batch = usernames[i:i + batch_size]
        urls = [f'https://www.instagram.com/{u}/' for u in batch]

        results = run_actor('apify~instagram-scraper', {
            'directUrls': urls,
            'resultsType': 'details',
            'resultsLimit': 1,
        }, label=f'enrich batch {i // batch_size + 1}')

        for item in results:
            username = item.get('username', '')
            if username in profiles:
                profiles[username]['bio'] = item.get('biography', '') or ''
                profiles[username]['followers'] = item.get('followersCount', 0) or 0
                profiles[username]['full_name'] = item.get('fullName', '') or ''
                profiles[username]['is_verified'] = item.get('verified', False)
                profiles[username]['external_url'] = item.get('externalUrl', '') or ''
                profiles[username]['profile_pic'] = item.get('profilePicUrl', '') or ''

    return profiles


def has_drone_keywords(text):
    text_lower = text.lower()
    return any(term in text_lower for term in DRONE_TERMS)


def has_nigeria_keywords(text):
    text_lower = text.lower()
    return any(term in text_lower for term in NIGERIA_TERMS)


def step_1c_filter_and_score(profiles):
    """Filter for drone + Nigeria relevance and score 1-10."""
    print(f'\n=== Step 1C: Filtering and scoring {len(profiles)} profiles ===')
    scored = []

    for username, p in profiles.items():
        bio = p.get('bio', '') or ''
        captions_text = ' '.join(p.get('captions', []))
        all_text = f"{bio} {captions_text} {p.get('full_name', '')}"
        followers = p.get('followers', 0) or 0

        # Must have some drone signal (from hashtag source, most will)
        drone_match = has_drone_keywords(all_text)
        nigeria_match = has_nigeria_keywords(all_text)

        # Score 1-10
        score = 0

        # Drone relevance (0-3)
        drone_count = sum(1 for term in DRONE_TERMS if term in all_text.lower())
        score += min(drone_count, 3)

        # Nigeria location (0-2)
        if has_nigeria_keywords(bio):
            score += 2
        elif nigeria_match:
            score += 1

        # Followers (0-2)
        if followers >= 5000:
            score += 2
        elif followers >= 1000:
            score += 1.5
        elif followers >= 500:
            score += 1
        elif followers >= 100:
            score += 0.5

        # Professional signals (0-2)
        pro_signals = ['booking', 'hire', 'available', 'services', 'dm for', 'contact',
                       'commercial', 'licensed', 'certified', 'professional', 'for hire']
        pro_count = sum(1 for s in pro_signals if s in all_text.lower())
        score += min(pro_count, 2)

        # Verified bonus (0-1)
        if p.get('is_verified'):
            score += 1

        score = min(round(score, 1), 10)

        # Detect city
        city = 'Unknown'
        for c in ['Lagos', 'Abuja', 'Port Harcourt', 'Ibadan', 'Enugu', 'Calabar', 'Owerri']:
            if c.lower() in all_text.lower():
                city = c
                break

        scored.append({
            'username': username,
            'full_name': p.get('full_name', ''),
            'bio': bio[:200],
            'followers': followers,
            'city': city,
            'profile_url': p.get('profile_url', ''),
            'external_url': p.get('external_url', ''),
            'is_verified': p.get('is_verified', False),
            'drone_match': drone_match,
            'nigeria_match': nigeria_match,
            'score': score,
            'source': p.get('source', ''),
            'sample_captions': captions_text[:300],
        })

    # Sort by score descending, keep top 40
    scored.sort(key=lambda x: x['score'], reverse=True)
    scored = scored[:40]

    print(f'Step 1C: {len(scored)} profiles scored (top 40 kept)')
    return scored


def step_1d_output_csv(scored):
    """Save scored profiles to CSV."""
    print(f'\n=== Step 1D: Writing CSV ===')
    output_path = OUTPUT_DIR / 'drone-pilot-prospects.csv'

    fieldnames = [
        'username', 'full_name', 'bio', 'followers', 'city', 'profile_url',
        'external_url', 'is_verified', 'drone_match', 'nigeria_match',
        'score', 'source', 'sample_captions',
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored)

    print(f'Saved {len(scored)} profiles to {output_path}')
    return output_path


def main():
    print('=== Drone Pilot Recruitment Scraper ===')
    print(f'Output: {OUTPUT_DIR / "drone-pilot-prospects.csv"}')

    # Step 1A: Hashtag scraping
    profiles = step_1a_hashtag_scrape()

    if not profiles:
        print('No profiles found from hashtag scraping.')
        sys.exit(1)

    # Step 1B: Enrich with profile details
    profiles = step_1b_enrich(profiles)

    # Step 1C: Filter and score
    scored = step_1c_filter_and_score(profiles)

    if not scored:
        print('No profiles passed scoring. Outputting all as fallback.')
        scored = [{
            'username': u,
            'full_name': p.get('full_name', ''),
            'bio': (p.get('bio', '') or '')[:200],
            'followers': p.get('followers', 0),
            'city': 'Unknown',
            'profile_url': p.get('profile_url', ''),
            'external_url': p.get('external_url', ''),
            'is_verified': p.get('is_verified', False),
            'drone_match': True,
            'nigeria_match': False,
            'score': 0,
            'source': p.get('source', ''),
            'sample_captions': ' '.join(p.get('captions', []))[:300],
        } for u, p in profiles.items()]

    # Step 1D: Output CSV
    output_path = step_1d_output_csv(scored)
    print(f'\nDone! {len(scored)} prospects saved to {output_path}')


if __name__ == '__main__':
    main()
