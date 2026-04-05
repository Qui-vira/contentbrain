"""Post Claude Code Portfolio reel at 18:30 UTC (7:30pm WAT)."""
import subprocess, sys, time
from datetime import datetime, timezone, timedelta

WAT = timezone(timedelta(hours=1))
target_h, target_m = 18, 30

now = datetime.now(timezone.utc)
target = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
if target > now:
    delta = (target - now).total_seconds()
    print(f"Sleeping {delta/60:.0f} min until 7:30pm WAT...")
    time.sleep(delta)

print(f"Posting at {datetime.now(WAT).strftime('%I:%M %p WAT')}...")
result = subprocess.run(
    [sys.executable, "C:/Users/Bigquiv/onedrive/desktop/contentbrain/scripts/post_reel.py",
     "C:/Users/Bigquiv/Downloads/claude-code-portfolio.mp4",
     "AI found 3 things I missed in my own portfolio.\n\n"
     "40% correlation risk. Free yield unclaimed on 2 positions. A concentration cluster I thought was diversified.\n\n"
     "2 minutes of AI analysis vs 1 hour of manual spreadsheets.\n\n"
     "I am not saying trust AI blindly. I am saying use it as a second pair of eyes.\n\n"
     "It catches what your ego misses.\n\n"
     "Comment \"PORTFOLIO\" for the step-by-step AI audit guide.\n\n"
     "Run your own AI audit: https://bigquivdigitals.com/doc/portfolio-ai-audit\n\n"
     "#crypto #ai #portfolio #trading #riskmanagement #web3 #defi #claudecode #cryptoeducation"],
    capture_output=True, text=True, timeout=600,
    cwd="C:/Users/Bigquiv/onedrive/desktop/contentbrain",
)
print(result.stdout)
if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
else:
    print("SUCCESS: Last reel posted!")
