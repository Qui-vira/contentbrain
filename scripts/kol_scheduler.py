"""
KOL & Consulting — Railway Scheduler
Long-running service that runs all KOL lead gen scripts on schedule.
Single Railway deployment.

Schedule (WAT = UTC+1):
    06:00 Daily       — exchange_lead_finder.py (new exchanges + protocols)
    07:00 Mon/Thu     — web3_funding_finder.py (funded projects)
    06:00 Wednesday   — ai_client_finder.py (AI consulting leads)
    08:00 Daily       — competitor_deal_monitor.py (competitor KOL deals)
    10:00 Daily       — kol_outreach_drafter.py (draft emails)
    14:00 Daily       — kol_outreach_sender.py (send approved)

Usage:
    python scripts/kol_scheduler.py           # Run scheduler (Railway entry point)
    python scripts/kol_scheduler.py --now     # Run all jobs immediately (testing)
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
WAT_OFFSET = timedelta(hours=1)  # WAT = UTC+1

# Job definitions: (script, hour_wat, days)
# days: 'daily', 'mon_thu', 'wednesday', 'monday'
JOBS = [
    {
        'name': 'Exchange & Protocol Finder',
        'script': 'exchange_lead_finder.py',
        'hour_wat': 6,
        'days': 'daily',
    },
    {
        'name': 'Web3 Funding Finder',
        'script': 'web3_funding_finder.py',
        'hour_wat': 7,
        'days': 'mon_thu',
    },
    {
        'name': 'AI Client Finder',
        'script': 'ai_client_finder.py',
        'hour_wat': 6,
        'days': 'wednesday',
    },
    {
        'name': 'Competitor Deal Monitor',
        'script': 'competitor_deal_monitor.py',
        'hour_wat': 8,
        'days': 'daily',
    },
    {
        'name': 'KOL Outreach Drafter',
        'script': 'kol_outreach_drafter.py',
        'hour_wat': 10,
        'days': 'daily',
    },
    {
        'name': 'KOL Outreach Sender',
        'script': 'kol_outreach_sender.py',
        'hour_wat': 14,
        'days': 'daily',
    },
]

# Track which jobs ran today to avoid duplicates
jobs_ran_today = {}
running = True


def get_wat_now():
    """Get current time in WAT (UTC+1)."""
    return datetime.now(timezone.utc) + WAT_OFFSET


def should_run(job, now_wat):
    """Check if a job should run based on current WAT time."""
    weekday = now_wat.weekday()  # 0=Mon, 6=Sun

    # Check day
    days = job['days']
    if days == 'monday' and weekday != 0:
        return False
    elif days == 'mon_thu' and weekday not in (0, 3):
        return False
    elif days == 'wednesday' and weekday != 2:
        return False
    # 'daily' runs every day

    # Check hour
    if now_wat.hour != job['hour_wat']:
        return False

    # Check if already ran this hour
    key = f"{job['name']}_{now_wat.strftime('%Y-%m-%d_%H')}"
    if key in jobs_ran_today:
        return False

    return True


def run_job(job):
    """Execute a job script as a subprocess."""
    script_path = os.path.join(SCRIPTS_DIR, job['script'])
    if not os.path.exists(script_path):
        print(f'  ERROR: Script not found: {script_path}')
        return False

    now_wat = get_wat_now()
    print(f'\n{"=" * 60}')
    print(f'  RUNNING: {job["name"]}')
    print(f'  Script: {job["script"]}')
    print(f'  Time: {now_wat.strftime("%Y-%m-%d %H:%M WAT")}')
    print(f'{"=" * 60}\n')

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(SCRIPTS_DIR),  # Run from vault root
            capture_output=False,
            timeout=600,  # 10 minute timeout per job
        )

        # Mark as ran
        key = f"{job['name']}_{now_wat.strftime('%Y-%m-%d_%H')}"
        jobs_ran_today[key] = True

        if result.returncode == 0:
            print(f'\n  {job["name"]} completed successfully.')
            return True
        else:
            print(f'\n  {job["name"]} exited with code {result.returncode}')
            return False

    except subprocess.TimeoutExpired:
        print(f'\n  {job["name"]} timed out after 10 minutes.')
        return False
    except Exception as e:
        print(f'\n  {job["name"]} failed: {e}')
        return False


def cleanup_old_keys():
    """Remove job keys from previous days."""
    global jobs_ran_today
    today = get_wat_now().strftime('%Y-%m-%d')
    jobs_ran_today = {k: v for k, v in jobs_ran_today.items() if today in k}


def handle_shutdown(signum, frame):
    """Graceful shutdown on SIGTERM/SIGINT."""
    global running
    print('\nShutdown signal received. Stopping scheduler...')
    running = False


def run_all_now():
    """Run all jobs immediately (for testing)."""
    print('=' * 60)
    print('  RUNNING ALL KOL JOBS NOW (test mode)')
    print('=' * 60)

    for job in JOBS:
        run_job(job)

    print('\n  All jobs complete.')


def scheduler_loop():
    """Main scheduler loop. Checks every 60 seconds."""
    global running

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    now_wat = get_wat_now()
    print('=' * 60)
    print('  KOL & CONSULTING — Lead Generation Scheduler')
    print(f'  Started: {now_wat.strftime("%Y-%m-%d %H:%M WAT")}')
    print(f'  Jobs configured: {len(JOBS)}')
    print('')
    for job in JOBS:
        day_str = job['days'].replace('_', '/').title()
        print(f'    {job["hour_wat"]:02d}:00 {day_str:12s} — {job["name"]}')
    print('=' * 60)

    while running:
        now_wat = get_wat_now()

        # Clean up old keys at midnight
        if now_wat.hour == 0 and now_wat.minute < 2:
            cleanup_old_keys()

        # Check each job
        for job in JOBS:
            if should_run(job, now_wat):
                run_job(job)

        # Sleep 60 seconds between checks
        time.sleep(60)

    print('Scheduler stopped.')


def main():
    parser = argparse.ArgumentParser(description='KOL & Consulting — Railway Scheduler')
    parser.add_argument('--now', action='store_true', help='Run all jobs immediately')
    args = parser.parse_args()

    if args.now:
        run_all_now()
    else:
        scheduler_loop()


if __name__ == '__main__':
    main()
