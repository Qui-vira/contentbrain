"""
KOL & Consulting Lead Cron — CLI orchestrator for all KOL lead gen scripts.

Usage:
    python scripts/kol_lead_cron.py                     # Full pipeline
    python scripts/kol_lead_cron.py --exchange           # Exchange + protocol finder only
    python scripts/kol_lead_cron.py --funding            # Web3 funding finder only
    python scripts/kol_lead_cron.py --ai-clients         # AI client finder only
    python scripts/kol_lead_cron.py --competitors        # Competitor deal monitor only
    python scripts/kol_lead_cron.py --outreach           # Outreach drafter only
    python scripts/kol_lead_cron.py --sender             # Outreach sender only
    python scripts/kol_lead_cron.py --daily              # Exchange + competitors + outreach + sender
    python scripts/kol_lead_cron.py --full               # All scrapers + outreach + sender
    python scripts/kol_lead_cron.py --dry-run            # Skip Supabase writes
"""

import os
import sys
import argparse
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(__file__))
from kol_lead_base import log_scan, ensure_dirs


# --- Phase runners ---

def run_exchange(dry_run=False):
    """Phase 1: Exchange & protocol finder."""
    print('\n--- Phase 1: Exchange & Protocol Finder ---')
    try:
        from exchange_lead_finder import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in exchange finder: {e}')
        return False


def run_funding(dry_run=False):
    """Phase 2: Web3 funding finder."""
    print('\n--- Phase 2: Web3 Funding Finder ---')
    try:
        from web3_funding_finder import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in funding finder: {e}')
        return False


def run_ai_clients(dry_run=False):
    """Phase 3: AI consulting client finder."""
    print('\n--- Phase 3: AI Client Finder ---')
    try:
        from ai_client_finder import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in AI client finder: {e}')
        return False


def run_competitors(dry_run=False):
    """Phase 4: Competitor deal monitor."""
    print('\n--- Phase 4: Competitor Deal Monitor ---')
    try:
        from competitor_deal_monitor import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in competitor monitor: {e}')
        return False


def run_outreach(dry_run=False):
    """Phase 5: Outreach drafter."""
    print('\n--- Phase 5: Outreach Drafter ---')
    try:
        from kol_outreach_drafter import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in outreach drafter: {e}')
        return False


def run_sender(dry_run=False):
    """Phase 6: Outreach sender."""
    print('\n--- Phase 6: Outreach Sender ---')
    try:
        from kol_outreach_sender import run
        run(dry_run=dry_run)
        return True
    except Exception as e:
        print(f'ERROR in outreach sender: {e}')
        return False


# --- Main cycle ---

def run_full_cycle(args):
    """Run the lead generation cycle based on CLI flags."""
    now = datetime.now(timezone.utc)
    dry_run = args.dry_run

    # Determine mode
    if args.full:
        mode = 'FULL'
    elif args.daily:
        mode = 'DAILY'
    elif any([args.exchange, args.funding, args.ai_clients, args.competitors, args.outreach, args.sender]):
        mode = 'SELECTIVE'
    else:
        mode = 'FULL'

    print(f'\n{"=" * 60}')
    print(f'  KOL & CONSULTING LEAD GENERATION')
    print(f'  {now.strftime("%Y-%m-%d %H:%M UTC")}')
    print(f'  Mode: {mode}')
    if dry_run:
        print(f'  DRY RUN — no Supabase writes')
    print(f'{"=" * 60}')

    ensure_dirs()
    results = {
        'exchange': None, 'funding': None, 'ai_clients': None,
        'competitors': None, 'outreach': None, 'sender': None,
    }
    errors = []

    # Determine which phases to run
    run_all = mode == 'FULL'
    run_daily_mode = mode == 'DAILY'

    if run_all or run_daily_mode or args.exchange:
        results['exchange'] = run_exchange(dry_run)
        if not results['exchange']:
            errors.append('exchange failed')

    if run_all or args.funding:
        results['funding'] = run_funding(dry_run)
        if not results['funding']:
            errors.append('funding failed')

    if run_all or args.ai_clients:
        results['ai_clients'] = run_ai_clients(dry_run)
        if not results['ai_clients']:
            errors.append('ai_clients failed')

    if run_all or run_daily_mode or args.competitors:
        results['competitors'] = run_competitors(dry_run)
        if not results['competitors']:
            errors.append('competitors failed')

    if run_all or run_daily_mode or args.outreach:
        results['outreach'] = run_outreach(dry_run)
        if not results['outreach']:
            errors.append('outreach failed')

    if run_all or run_daily_mode or args.sender:
        results['sender'] = run_sender(dry_run)
        if not results['sender']:
            errors.append('sender failed')

    # Summary
    print(f'\n{"=" * 60}')
    print(f'  KOL LEAD GENERATION COMPLETE')
    for key, val in results.items():
        status = 'OK' if val else 'SKIPPED' if val is None else 'FAILED'
        print(f'  {key:15s}: {status}')
    if errors:
        print(f'  Errors: {", ".join(errors)}')
    print(f'{"=" * 60}\n')


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='KOL & Consulting Lead Cron')
    parser.add_argument('--exchange', action='store_true', help='Run exchange finder')
    parser.add_argument('--funding', action='store_true', help='Run funding finder')
    parser.add_argument('--ai-clients', action='store_true', help='Run AI client finder')
    parser.add_argument('--competitors', action='store_true', help='Run competitor monitor')
    parser.add_argument('--outreach', action='store_true', help='Run outreach drafter')
    parser.add_argument('--sender', action='store_true', help='Run outreach sender')
    parser.add_argument('--daily', action='store_true', help='Daily run: exchange + competitors + outreach + sender')
    parser.add_argument('--full', action='store_true', help='Full run: all scrapers + outreach + sender')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    run_full_cycle(args)


if __name__ == '__main__':
    main()
