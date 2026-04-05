"""
Background scheduler: posts 3 remaining IG reels at 2hr intervals (WAT).
Schedule:
  3:30pm WAT (14:30 UTC) — 3 Cleared Tokens + ALPHA doc link
  5:30pm WAT (16:30 UTC) — Day In Life KOL + OS doc link
  7:30pm WAT (18:30 UTC) — Claude Code Portfolio + PORTFOLIO doc link
"""

import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

WAT = timezone(timedelta(hours=1))
DOWNLOADS = "C:/Users/Bigquiv/Downloads"
SCRIPTS = "C:/Users/Bigquiv/onedrive/desktop/contentbrain/scripts/post_reel.py"
DOC_BASE = "https://bnoqtghdptobbtrssmdj.supabase.co/functions/v1/doc"

reels = [
    {
        "time_utc": "14:30",
        "video": f"{DOWNLOADS}/3-cleared-tokens.mp4",
        "caption": (
            "3 tokens nobody is watching just cleared the SEC.\n\n"
            "AVAX. LINK. DOT.\n\n"
            "Institutional money needs regulatory clarity before it enters. These three just got it.\n\n"
            "While everyone chases noise, the smart money is quietly positioning.\n\n"
            "This is not about hype. This is about who passes the compliance filter.\n\n"
            "Comment \"ALPHA\" and I will send you the full breakdown.\n\n"
            f"Read the full analysis: {DOC_BASE}/alpha-3-cleared-tokens\n\n"
            "#crypto #avax #chainlink #polkadot #sec #altcoins #web3 #cryptoeducation #trading"
        ),
    },
    {
        "time_utc": "16:30",
        "video": f"{DOWNLOADS}/day-in-life-kol.mp4",
        "caption": (
            "My morning as a crypto trader.\n\n"
            "3 signals approved before breakfast. AI scans 50 pairs every 4 hours. I review. I decide. I move on.\n\n"
            "I spent months building the system so I would not have to be glued to charts.\n\n"
            "Most traders burn out. I built the machine instead.\n\n"
            "Comment \"OS\" and I will show you how it works.\n\n"
            f"See how the system works: {DOC_BASE}/os-trading-system\n\n"
            "#crypto #trading #dayinthelife #morningroutine #trader #ai #signals #web3 #cryptotrader"
        ),
    },
    {
        "time_utc": "18:30",
        "video": f"{DOWNLOADS}/claude-code-portfolio.mp4",
        "caption": (
            "AI found 3 things I missed in my own portfolio.\n\n"
            "40% correlation risk. Free yield unclaimed on 2 positions. A concentration cluster I thought was diversified.\n\n"
            "2 minutes of AI analysis vs 1 hour of manual spreadsheets.\n\n"
            "I am not saying trust AI blindly. I am saying use it as a second pair of eyes.\n\n"
            "It catches what your ego misses.\n\n"
            "Comment \"PORTFOLIO\" for the step-by-step AI audit guide.\n\n"
            f"Run your own AI audit: {DOC_BASE}/portfolio-ai-audit\n\n"
            "#crypto #ai #portfolio #trading #riskmanagement #web3 #defi #claudecode #cryptoeducation"
        ),
    },
]


def wait_until(target_utc_str: str):
    """Sleep until HH:MM UTC today."""
    now = datetime.now(timezone.utc)
    h, m = map(int, target_utc_str.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if target <= now:
        print(f"  Target {target_utc_str} UTC already passed, posting immediately.")
        return
    delta = (target - now).total_seconds()
    wat_time = target.astimezone(WAT).strftime("%I:%M %p WAT")
    print(f"  Sleeping {delta/60:.0f} min until {wat_time} ({target_utc_str} UTC)...")
    time.sleep(delta)


def main():
    print(f"IG Reel Scheduler started at {datetime.now(WAT).strftime('%I:%M %p WAT')}")
    print(f"Posting {len(reels)} reels at 2hr intervals\n")

    for i, reel in enumerate(reels, 1):
        print(f"--- Reel {i}/{len(reels)}: {reel['video'].split('/')[-1]} ---")
        wait_until(reel["time_utc"])

        print(f"  Posting at {datetime.now(WAT).strftime('%I:%M %p WAT')}...")
        try:
            result = subprocess.run(
                [sys.executable, SCRIPTS, reel["video"], reel["caption"]],
                capture_output=True,
                text=True,
                timeout=600,
                cwd="C:/Users/Bigquiv/onedrive/desktop/contentbrain",
            )
            print(result.stdout)
            if result.returncode != 0:
                print(f"  ERROR: {result.stderr}")
            else:
                print(f"  SUCCESS: Reel {i} posted!")
        except Exception as e:
            print(f"  EXCEPTION: {e}")

    print(f"\nAll reels posted. Finished at {datetime.now(WAT).strftime('%I:%M %p WAT')}")


if __name__ == "__main__":
    main()
