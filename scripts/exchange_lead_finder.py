"""
KOL Lead Gen — Exchange & Protocol Finder
Discovers new exchanges and DeFi protocols that need KOL marketing.

Sources:
    A) CoinGecko /exchanges — new exchanges (year_established >= 2025)
    B) DeFiLlama /protocols — protocols with TVL > $100K listed recently
    C) CoinMarketCap /exchange/map — optional, requires CMC_API_KEY

Schedule: Daily 6AM WAT

Usage:
    python scripts/exchange_lead_finder.py              # Full run
    python scripts/exchange_lead_finder.py --dry-run    # Skip Supabase writes
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import (
    fetch_json, is_duplicate, upsert_leads, promote_to_mql,
    save_csv, log_scan, ensure_dirs,
    COINGECKO_API_KEY, CMC_API_KEY
)
from kol_telegram import notify_scan_complete

LEAD_TYPE_EXCHANGE = 'new_exchange'
LEAD_TYPE_PROTOCOL = 'defi_protocol'
CURRENT_YEAR = datetime.now().year
FOURTEEN_DAYS_AGO = datetime.now(timezone.utc) - timedelta(days=14)

CSV_FIELDS = [
    'project_name', 'token_symbol', 'website', 'twitter_handle',
    'category', 'score', 'priority', 'trust_score', 'volume_24h',
    'year_established', 'tvl', 'chain', 'source', 'lead_type',
]


# --- Source A: CoinGecko Exchanges ---

def fetch_coingecko_exchanges():
    """Fetch exchanges from CoinGecko, filter for new ones."""
    print('\n  [CoinGecko] Fetching exchanges...')

    headers = {}
    if COINGECKO_API_KEY:
        headers['x-cg-demo-key'] = COINGECKO_API_KEY

    # CoinGecko returns up to 100 per page
    all_exchanges = []
    for page in range(1, 4):  # Up to 300 exchanges
        url = f'https://api.coingecko.com/api/v3/exchanges?per_page=100&page={page}'
        data = fetch_json(url, headers=headers)
        if not data:
            break
        all_exchanges.extend(data)
        if len(data) < 100:
            break

    print(f'  [CoinGecko] Total exchanges: {len(all_exchanges)}')

    leads = []
    for ex in all_exchanges:
        year = ex.get('year_established')
        if not year or year < (CURRENT_YEAR - 1):
            continue

        name = ex.get('name', '').strip()
        if not name or is_duplicate(name):
            continue

        trust = ex.get('trust_score', 0) or 0
        volume = ex.get('trade_volume_24h_btc', 0) or 0

        # Score: trust (0-10) * 0.4 + volume factor * 0.3 + recency * 0.3
        volume_score = min(volume / 1000, 10)  # 1000 BTC = max score
        recency_score = 10 if year >= CURRENT_YEAR else 5
        score = round(trust * 0.4 + volume_score * 0.3 + recency_score * 0.3, 1)

        leads.append({
            'project_name': name,
            'website': ex.get('url', ''),
            'twitter_handle': '',
            'category': 'exchange',
            'trust_score': trust,
            'volume_24h': volume,
            'year_established': year,
            'score': score,
            'priority': 'high' if score >= 7 else 'normal',
            'source': 'coingecko',
            'lead_type': LEAD_TYPE_EXCHANGE,
            'description': f'New exchange (est. {year}), trust score {trust}/10',
        })

    print(f'  [CoinGecko] New exchanges found: {len(leads)}')
    return leads


# --- Source B: DeFiLlama Protocols ---

def fetch_defillama_protocols():
    """Fetch DeFi protocols from DeFiLlama, filter for new high-TVL ones."""
    print('\n  [DeFiLlama] Fetching protocols...')

    data = fetch_json('https://api.llama.fi/protocols')
    if not data:
        return []

    print(f'  [DeFiLlama] Total protocols: {len(data)}')

    leads = []
    for proto in data:
        name = proto.get('name', '').strip()
        tvl = proto.get('tvl', 0) or 0

        if tvl < 100_000:
            continue

        # Check if listed recently (listedAt is unix timestamp)
        listed_at = proto.get('listedAt')
        if listed_at:
            listed_date = datetime.fromtimestamp(listed_at, tz=timezone.utc)
            if listed_date < FOURTEEN_DAYS_AGO:
                continue
        else:
            continue  # Skip if no listing date

        if is_duplicate(name):
            continue

        twitter = proto.get('twitter', '') or ''
        if twitter.startswith('https://twitter.com/'):
            twitter = twitter.split('/')[-1]

        # Score: TVL factor * 0.4 + category match * 0.3 + chain diversity * 0.3
        tvl_score = min(tvl / 10_000_000, 10)  # $10M = max
        category = proto.get('category', '')
        cat_score = 8 if category in ('DEX', 'Lending', 'Yield', 'Bridge', 'Derivatives') else 5
        chains = proto.get('chains', [])
        chain_score = min(len(chains) * 2, 10)
        score = round(tvl_score * 0.4 + cat_score * 0.3 + chain_score * 0.3, 1)

        leads.append({
            'project_name': name,
            'token_symbol': proto.get('symbol', ''),
            'website': proto.get('url', ''),
            'twitter_handle': twitter,
            'category': category,
            'tvl': tvl,
            'chain': ', '.join(chains[:5]),
            'score': score,
            'priority': 'high' if score >= 7 else 'normal',
            'source': 'defillama',
            'lead_type': LEAD_TYPE_PROTOCOL,
            'description': f'DeFi protocol, TVL ${tvl:,.0f}, {category}',
        })

    print(f'  [DeFiLlama] New protocols found: {len(leads)}')
    return leads


# --- Source C: CoinMarketCap Exchanges (optional) ---

def fetch_cmc_exchanges():
    """Fetch new exchanges from CoinMarketCap. Requires CMC_API_KEY."""
    if not CMC_API_KEY:
        print('\n  [CMC] Skipped — CMC_API_KEY not set')
        return []

    print('\n  [CMC] Fetching exchange map...')

    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    data = fetch_json(
        'https://pro-api.coinmarketcap.com/v1/exchange/map',
        headers=headers,
        params={'listing_status': 'active', 'limit': 200, 'sort': 'id'},
    )

    if not data or 'data' not in data:
        print('  [CMC] No data returned')
        return []

    exchanges = data['data']
    print(f'  [CMC] Total exchanges: {len(exchanges)}')

    leads = []
    for ex in exchanges:
        name = ex.get('name', '').strip()
        first_date = ex.get('first_historical_data', '')

        if not first_date:
            continue

        # Filter last 14 days
        try:
            listed = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
            if listed < FOURTEEN_DAYS_AGO:
                continue
        except Exception:
            continue

        if is_duplicate(name):
            continue

        score = 6.0  # CMC-listed = moderate baseline
        leads.append({
            'project_name': name,
            'website': '',
            'category': 'exchange',
            'score': score,
            'priority': 'normal',
            'source': 'coinmarketcap',
            'lead_type': LEAD_TYPE_EXCHANGE,
            'description': f'New CMC-listed exchange, first data {first_date[:10]}',
        })

    print(f'  [CMC] New exchanges found: {len(leads)}')
    return leads


# --- Main ---

def run(dry_run=False):
    """Entry point for cron orchestrator."""
    ensure_dirs()
    all_leads = []
    errors = []

    # Source A: CoinGecko
    try:
        all_leads.extend(fetch_coingecko_exchanges())
    except Exception as e:
        errors.append(f'coingecko: {e}')
        print(f'  ERROR: CoinGecko failed: {e}')

    # Source B: DeFiLlama
    try:
        all_leads.extend(fetch_defillama_protocols())
    except Exception as e:
        errors.append(f'defillama: {e}')
        print(f'  ERROR: DeFiLlama failed: {e}')

    # Source C: CMC
    try:
        all_leads.extend(fetch_cmc_exchanges())
    except Exception as e:
        errors.append(f'cmc: {e}')
        print(f'  ERROR: CMC failed: {e}')

    print(f'\n  Total leads found: {len(all_leads)}')

    # Save CSV
    if all_leads:
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_csv(all_leads, f'exchange-protocol-leads-{date_str}.csv', CSV_FIELDS)

    # Upsert to Supabase
    saved = 0
    promoted = 0
    if not dry_run and all_leads:
        exchange_leads = [l for l in all_leads if l['lead_type'] == LEAD_TYPE_EXCHANGE]
        protocol_leads = [l for l in all_leads if l['lead_type'] == LEAD_TYPE_PROTOCOL]

        if exchange_leads:
            saved += upsert_leads(exchange_leads, LEAD_TYPE_EXCHANGE)
            promoted += promote_to_mql(LEAD_TYPE_EXCHANGE)
        if protocol_leads:
            saved += upsert_leads(protocol_leads, LEAD_TYPE_PROTOCOL)
            promoted += promote_to_mql(LEAD_TYPE_PROTOCOL)

    # Log + notify
    error_str = '; '.join(errors) if errors else None
    log_scan('exchange_lead_finder', len(all_leads), saved, promoted, error_str)
    notify_scan_complete('Exchange & Protocol Finder', len(all_leads), saved, promoted, error_str)

    return all_leads


def main():
    parser = argparse.ArgumentParser(description='KOL Lead Gen — Exchange & Protocol Finder')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    print('=' * 50)
    print('  KOL LEAD GEN — Exchange & Protocol Finder')
    print(f'  Mode: {"DRY RUN" if args.dry_run else "LIVE"}')
    print('=' * 50)

    run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
