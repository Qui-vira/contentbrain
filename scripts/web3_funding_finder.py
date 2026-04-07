"""
KOL Lead Gen — Web3 Funding Finder
Discovers recently funded/launched Web3 projects that need KOL marketing.

Sources:
    A) CoinGecko trending + recently listed coins (free, no auth)
    B) Apify X/Twitter scraper — funding announcement tweets (via apidojo/tweet-scraper)

Note: No free API exists for crypto funding round data (CryptoRank, DeFiLlama
raises, and Messari are all paywalled). CoinGecko trending is the best free
proxy — projects that just raised appear as trending/new listings.

Schedule: Mon/Thu 7AM WAT

Usage:
    python scripts/web3_funding_finder.py              # Full run
    python scripts/web3_funding_finder.py --dry-run    # Skip Supabase writes
"""

import os
import sys
import re
import argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    fetch_json, search_x_recent, is_duplicate, upsert_leads,
    promote_to_mql, save_csv, log_scan, ensure_dirs,
    COINGECKO_API_KEY
)
from kol_telegram import notify_scan_complete

LEAD_TYPE = 'funded_project'

CSV_FIELDS = [
    'project_name', 'token_symbol', 'website', 'twitter_handle',
    'category', 'funding_amount', 'funding_round', 'investors',
    'score', 'priority', 'source', 'description',
]


# --- Source A: CoinGecko Trending + New Coins ---

def fetch_coingecko_trending():
    """Fetch trending coins from CoinGecko. Trending = recently hyped = often just funded."""
    print('\n  [CoinGecko] Fetching trending coins...')

    headers = {}
    if COINGECKO_API_KEY:
        headers['x-cg-demo-key'] = COINGECKO_API_KEY

    data = fetch_json('https://api.coingecko.com/api/v3/search/trending', headers=headers)
    if not data or 'coins' not in data:
        print('  [CoinGecko] No trending data')
        return []

    coins = data.get('coins', [])
    print(f'  [CoinGecko] Trending coins: {len(coins)}')

    leads = []
    for coin in coins:
        item = coin.get('item', {})
        name = item.get('name', '').strip()
        if not name or is_duplicate(name):
            continue

        symbol = item.get('symbol', '')
        market_cap_rank = item.get('market_cap_rank') or 9999
        score_val = item.get('score', 0)

        # Score: lower market cap rank = newer/smaller = better KOL target
        # Projects ranked 200+ are the sweet spot (need marketing most)
        if market_cap_rank and market_cap_rank < 100:
            rank_score = 3  # Too established
        elif market_cap_rank and market_cap_rank < 500:
            rank_score = 7  # Sweet spot
        else:
            rank_score = 9  # New, needs marketing badly

        # Trending position bonus
        position_score = max(10 - score_val, 5)
        final_score = round(rank_score * 0.6 + position_score * 0.4, 1)

        leads.append({
            'project_name': name,
            'token_symbol': symbol,
            'website': '',
            'twitter_handle': '',
            'category': 'trending',
            'funding_amount': 0,
            'funding_round': '',
            'investors': '',
            'score': final_score,
            'priority': 'high' if final_score >= 7 else 'normal',
            'source': 'coingecko_trending',
            'description': f'Trending #{score_val + 1} on CoinGecko, rank #{market_cap_rank}',
        })

    print(f'  [CoinGecko] Trending leads: {len(leads)}')
    return leads


def fetch_coingecko_new_coins():
    """Fetch recently added coins from CoinGecko markets sorted by newest."""
    print('\n  [CoinGecko] Fetching recently listed coins...')

    headers = {}
    if COINGECKO_API_KEY:
        headers['x-cg-demo-key'] = COINGECKO_API_KEY

    # Get coins sorted by newest (lowest gecko rank = newest additions)
    data = fetch_json(
        'https://api.coingecko.com/api/v3/coins/markets',
        headers=headers,
        params={
            'vs_currency': 'usd',
            'order': 'gecko_asc',
            'per_page': 50,
            'page': 1,
            'sparkline': 'false',
        }
    )

    if not data:
        print('  [CoinGecko] No new coins data')
        return []

    print(f'  [CoinGecko] New coins fetched: {len(data)}')

    leads = []
    for coin in data:
        name = coin.get('name', '').strip()
        mcap = coin.get('market_cap') or 0

        # Filter: only coins with some market cap (not dead) but not huge (already established)
        if mcap < 100_000 or mcap > 500_000_000:
            continue

        if is_duplicate(name):
            continue

        symbol = coin.get('symbol', '').upper()

        # Score: smaller mcap = needs more marketing
        if mcap < 1_000_000:
            mcap_score = 9
        elif mcap < 10_000_000:
            mcap_score = 8
        elif mcap < 50_000_000:
            mcap_score = 7
        elif mcap < 100_000_000:
            mcap_score = 6
        else:
            mcap_score = 4

        # Volume factor
        volume = coin.get('total_volume') or 0
        vol_ratio = volume / mcap if mcap > 0 else 0
        vol_score = min(vol_ratio * 20, 10)  # High volume/mcap = active community

        score = round(mcap_score * 0.6 + vol_score * 0.4, 1)

        leads.append({
            'project_name': name,
            'token_symbol': symbol,
            'website': '',
            'twitter_handle': '',
            'category': 'new_listing',
            'funding_amount': 0,
            'funding_round': '',
            'investors': '',
            'score': score,
            'priority': 'high' if score >= 7 else 'normal',
            'source': 'coingecko_new',
            'description': f'Recently listed, mcap ${mcap:,.0f}, vol ${volume:,.0f}',
        })

    print(f'  [CoinGecko] New coin leads: {len(leads)}')
    return leads


# --- Source B: Apify X/Twitter Funding Announcements ---

def fetch_x_funding_tweets():
    """Search X for funding announcement tweets via Apify scraper."""
    print('\n  [Apify X] Searching funding announcements...')

    queries = [
        '"raised" "million" (crypto OR web3 OR defi OR blockchain) -is:retweet',
        '"funding round" (crypto OR web3 OR defi) -is:retweet',
        '"seed round" (crypto OR web3) -is:retweet',
    ]

    seen_projects = set()
    leads = []

    for query in queries:
        tweets = search_x_recent(query, max_results=30)
        for tweet in tweets:
            text = tweet.get('text', '')

            # Skip low-follower accounts (noise filter)
            if tweet.get('author_followers', 0) < 1000:
                continue

            # Try to extract project name from tweet (first @mention)
            project_name = ''
            for w in text.split():
                if w.startswith('@') and len(w) > 2:
                    project_name = w[1:]
                    break

            if not project_name:
                project_name = tweet.get('author_name', tweet.get('author_username', ''))

            if not project_name or project_name.lower() in seen_projects:
                continue
            seen_projects.add(project_name.lower())

            if is_duplicate(project_name):
                continue

            # Extract amount if mentioned
            amount = 0
            words = text.split()
            for i, w in enumerate(words):
                w_clean = w.replace('$', '').replace(',', '')
                try:
                    num = float(w_clean.replace('M', '').replace('m', ''))
                    if 'M' in w or 'm' in w or 'million' in text.lower():
                        amount = num * 1_000_000
                    elif num > 100_000:
                        amount = num
                    break
                except ValueError:
                    continue

            if amount < 500_000:
                continue

            # Extract round type
            round_type = ''
            text_lower = text.lower()
            for rt in ['series c', 'series b', 'series a', 'seed', 'pre-seed', 'strategic', 'private']:
                if rt in text_lower:
                    round_type = rt
                    break

            amount_score = min(amount / 20_000_000, 10)
            follower_score = min(tweet.get('author_followers', 0) / 50000, 10)
            score = round(amount_score * 0.5 + follower_score * 0.3 + 5 * 0.2, 1)

            leads.append({
                'project_name': project_name,
                'token_symbol': '',
                'twitter_handle': tweet.get('author_username', ''),
                'website': '',
                'category': 'funded',
                'funding_amount': amount,
                'funding_round': round_type,
                'investors': '',
                'score': score,
                'priority': 'high' if amount >= 5_000_000 else 'normal',
                'source': 'x_api',
                'description': text[:200],
            })

    print(f'  [Apify X] Funding leads from tweets: {len(leads)}')
    return leads


# --- Main ---

def run(dry_run=False):
    """Entry point for cron orchestrator."""
    ensure_dirs()
    all_leads = []
    errors = []

    # Source A1: CoinGecko Trending
    try:
        all_leads.extend(fetch_coingecko_trending())
    except Exception as e:
        errors.append(f'coingecko_trending: {e}')
        print(f'  ERROR: CoinGecko trending failed: {e}')

    # Source A2: CoinGecko New Coins
    try:
        new_coins = fetch_coingecko_new_coins()
        existing_names = {l['project_name'].lower() for l in all_leads}
        for lead in new_coins:
            if lead['project_name'].lower() not in existing_names:
                all_leads.append(lead)
    except Exception as e:
        errors.append(f'coingecko_new: {e}')
        print(f'  ERROR: CoinGecko new coins failed: {e}')

    # Source B: Apify X/Twitter
    try:
        x_leads = fetch_x_funding_tweets()
        existing_names = {l['project_name'].lower() for l in all_leads}
        for lead in x_leads:
            if lead['project_name'].lower() not in existing_names:
                all_leads.append(lead)
    except Exception as e:
        errors.append(f'apify_x: {e}')
        print(f'  ERROR: Apify X scraper failed: {e}')

    print(f'\n  Total funded/new project leads: {len(all_leads)}')

    # Save CSV
    if all_leads:
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_csv(all_leads, f'funded-project-leads-{date_str}.csv', CSV_FIELDS)

    # Upsert to Supabase
    saved = 0
    promoted = 0
    if not dry_run and all_leads:
        saved = upsert_leads(all_leads, LEAD_TYPE)
        promoted = promote_to_mql(LEAD_TYPE)

    # Log + notify
    error_str = '; '.join(errors) if errors else None
    log_scan('web3_funding_finder', len(all_leads), saved, promoted, error_str)
    notify_scan_complete('Web3 Funding Finder', len(all_leads), saved, promoted, error_str)

    return all_leads


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — Web3 Funding Finder')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — Web3 Funding Finder')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
