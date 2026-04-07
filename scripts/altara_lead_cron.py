"""
Altara Aerial Lead Cron — Scheduled lead generation wrapper for Railway.

Runs scrapers on schedule and generates outreach drafts.
Follows polymarket_cron.py pattern for Railway deployment.

Usage:
    python scripts/altara_lead_cron.py                     # Run all scrapers + outreach
    python scripts/altara_lead_cron.py --daily              # Real estate only (daily)
    python scripts/altara_lead_cron.py --weekly             # Construction + wedding (weekly)
    python scripts/altara_lead_cron.py --outreach-only      # Generate emails from existing leads
    python scripts/altara_lead_cron.py --dry-run            # Skip Supabase writes

Schedule on Railway:
    Daily (real estate):   CRON_SCHEDULE="0 8 * * *"   python scripts/altara_lead_cron.py --daily
    Weekly (construction): CRON_SCHEDULE="0 8 * * 1"   python scripts/altara_lead_cron.py --weekly
    Full run (manual):     python scripts/altara_lead_cron.py
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

from altara_lead_base import log_scan, ensure_dirs


# --- Phase runners ---

def run_real_estate(dry_run=False):
    """Phase 1: Scrape property listings for agents without aerial photos."""
    print('\n--- Phase 1: Real Estate Agent Finder ---')
    try:
        from scrape_real_estate_leads import main as real_estate_main
        # Simulate CLI args
        sys.argv = ['scrape_real_estate_leads.py']
        if dry_run:
            sys.argv.append('--dry-run')
        real_estate_main()
        return True
    except SystemExit:
        return True  # main() calls sys.exit(0) on success
    except Exception as e:
        print(f'ERROR in real estate scraper: {e}')
        return False


def run_construction(dry_run=False):
    """Phase 2: Scrape Google Maps for construction companies."""
    print('\n--- Phase 2: Construction Company Finder ---')
    try:
        from scrape_construction_leads import main as construction_main
        sys.argv = ['scrape_construction_leads.py']
        if dry_run:
            sys.argv.append('--dry-run')
        construction_main()
        return True
    except SystemExit:
        return True
    except Exception as e:
        print(f'ERROR in construction scraper: {e}')
        return False


def run_wedding(dry_run=False):
    """Phase 3: Scrape Instagram for wedding planners."""
    print('\n--- Phase 3: Wedding Planner Finder ---')
    try:
        from scrape_wedding_planner_leads import main as wedding_main
        sys.argv = ['scrape_wedding_planner_leads.py']
        if dry_run:
            sys.argv.append('--dry-run')
        wedding_main()
        return True
    except SystemExit:
        return True
    except Exception as e:
        print(f'ERROR in wedding planner scraper: {e}')
        return False


def run_outreach():
    """Phase 4: Generate cold outreach emails for all lead types."""
    print('\n--- Phase 4: Outreach Email Generation ---')
    try:
        from generate_altara_outreach import main as outreach_main
        sys.argv = ['generate_altara_outreach.py', '--from-csv']
        outreach_main()
        return True
    except SystemExit:
        return True
    except Exception as e:
        print(f'ERROR in outreach generator: {e}')
        return False


# --- Main cycle ---

def run_full_cycle(daily=False, weekly=False, outreach_only=False, dry_run=False):
    """Run the full lead generation cycle."""
    now = datetime.now(timezone.utc)
    print(f'\n{"=" * 60}')
    print(f'  ALTARA AERIAL LEAD GENERATION')
    print(f'  {now.strftime("%Y-%m-%d %H:%M UTC")}')
    mode = 'DAILY' if daily else 'WEEKLY' if weekly else 'OUTREACH' if outreach_only else 'FULL'
    print(f'  Mode: {mode}')
    if dry_run:
        print(f'  DRY RUN — no Supabase writes')
    print(f'{"=" * 60}')

    ensure_dirs()
    results = {'real_estate': None, 'construction': None, 'wedding': None, 'outreach': None}
    errors = []

    if outreach_only:
        results['outreach'] = run_outreach()
        if not results['outreach']:
            errors.append('outreach failed')

    elif daily:
        # Daily: real estate only
        results['real_estate'] = run_real_estate(dry_run)
        if not results['real_estate']:
            errors.append('real_estate failed')

        # Always generate outreach after scraping
        results['outreach'] = run_outreach()

    elif weekly:
        # Weekly: construction + wedding
        results['construction'] = run_construction(dry_run)
        if not results['construction']:
            errors.append('construction failed')

        results['wedding'] = run_wedding(dry_run)
        if not results['wedding']:
            errors.append('wedding failed')

        results['outreach'] = run_outreach()

    else:
        # Full run: all scrapers + outreach
        results['real_estate'] = run_real_estate(dry_run)
        if not results['real_estate']:
            errors.append('real_estate failed')

        results['construction'] = run_construction(dry_run)
        if not results['construction']:
            errors.append('construction failed')

        results['wedding'] = run_wedding(dry_run)
        if not results['wedding']:
            errors.append('wedding failed')

        results['outreach'] = run_outreach()

    # Summary
    print(f'\n{"=" * 60}')
    print(f'  LEAD GENERATION COMPLETE')
    print(f'  Real Estate:   {"OK" if results["real_estate"] else "SKIPPED" if results["real_estate"] is None else "FAILED"}')
    print(f'  Construction:  {"OK" if results["construction"] else "SKIPPED" if results["construction"] is None else "FAILED"}')
    print(f'  Wedding:       {"OK" if results["wedding"] else "SKIPPED" if results["wedding"] is None else "FAILED"}')
    print(f'  Outreach:      {"OK" if results["outreach"] else "SKIPPED" if results["outreach"] is None else "FAILED"}')
    if errors:
        print(f'  Errors: {", ".join(errors)}')
    print(f'{"=" * 60}\n')


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='Altara Aerial Lead Cron')
    parser.add_argument('--daily', action='store_true', help='Daily run: real estate only')
    parser.add_argument('--weekly', action='store_true', help='Weekly run: construction + wedding')
    parser.add_argument('--outreach-only', action='store_true', help='Generate outreach emails only')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase writes')
    args = parser.parse_args()

    run_full_cycle(
        daily=args.daily,
        weekly=args.weekly,
        outreach_only=args.outreach_only,
        dry_run=args.dry_run,
    )


if __name__ == '__main__':
    main()
