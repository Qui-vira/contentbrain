"""
Schedule 4 static posts to Typefully with images, according to their Notion post dates.
"""
import requests, os, time, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

API_KEY = os.getenv("TYPEFULLY_API_KEY")
BASE_URL = "https://api.typefully.com/v2"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Social set IDs (from memory)
X_SET = 61071
LI_SET = 292564

BASE = os.path.join(os.path.dirname(__file__), "..")
VIS = os.path.join(BASE, "06-Drafts", "visuals")


def upload_image(filepath, social_set_id):
    """Upload image to Typefully via presigned URL and return media_id."""
    fname = os.path.basename(filepath)
    ext = fname.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")

    # Step 1: Create upload -> get presigned URL
    resp = requests.post(f"{BASE_URL}/social-sets/{social_set_id}/media/upload", json={
        "file_name": fname,
        "content_type": mime
    }, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    upload_url = data["upload_url"]
    media_id = data["media_id"]

    # Step 2: PUT raw bytes to presigned URL
    with open(filepath, "rb") as f:
        put_resp = requests.put(upload_url, data=f.read(), timeout=60)
        put_resp.raise_for_status()

    # Step 3: Poll for ready
    for _ in range(30):
        time.sleep(1)
        st = requests.get(f"{BASE_URL}/social-sets/{social_set_id}/media/{media_id}", headers=headers, timeout=10)
        if st.status_code == 200 and st.json().get("status") == "ready":
            break

    print(f"  Uploaded: {fname} -> media_id={media_id}")
    return media_id


def schedule_tweet(social_set_id, posts, publish_at, platform="x"):
    """Create a draft on Typefully and schedule it."""
    payload = {
        "platforms": {
            platform: {
                "enabled": True,
                "posts": posts
            }
        },
        "publish_at": publish_at
    }
    resp = requests.post(f"{BASE_URL}/social-sets/{social_set_id}/drafts",
                         json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    draft = resp.json()
    print(f"  Scheduled for {publish_at} -> draft_id={draft.get('id', 'ok')}")
    return draft


# ============================================================
# POST 1: Bear Market Built The Machine (X/Twitter, Mar 27 09:00 UTC)
# ============================================================
print("\n1. Bear Market Built The Machine")
bear_img = os.path.join(VIS, "bear-machine-mar27", "slide-01.png")
bear_media = upload_image(bear_img, X_SET)
schedule_tweet(X_SET, [
    {
        "text": "I built my entire system during a bear market. Now I don't work harder in a bull. I just approve signals.\n\nWhile everyone was doom-scrolling in 2023, I was writing scripts, testing scanners, and losing sleep over confluence filters.\n\nToday my AI scans 50 pairs every 4 hours. I wake up, review, approve, done.\n\nThe bear didn't break me. It built the machine.",
        "media_ids": [bear_media]
    }
], "2026-03-27T09:00:00Z")

# ============================================================
# POST 2: 30 Hours to 3 Hours (LinkedIn, Mar 27 10:00 UTC)
# ============================================================
print("\n2. 30 Hours to 3 Hours — LinkedIn")
auto_img = os.path.join(VIS, "automation-linkedin-mar27", "slide-01.png")
auto_media = upload_image(auto_img, LI_SET)
schedule_tweet(LI_SET, [
    {
        "text": """6 months ago I spent 30 hours a week charting and researching content. This week I spent 3.

Not because I stopped caring. Because I built systems that care for me.

Here's what changed.

I automated my trading signals. Built a scanner that checks 50 crypto pairs every 4 hours. It filters for confluence across 5 indicators. If the setup is clean, it sends it to my phone for approval.

That used to take me 4 hours a day. Now it takes 10 minutes.

Then I automated content research. AI scouts trends, pulls data, and drafts a weekly content calendar. I edit and approve. What used to take 8 hours every Sunday now takes 45 minutes.

Total weekly time saved: roughly 27 hours.

But here's the part nobody talks about. The freed-up time didn't go to a beach. It went to thinking. Strategy. Product building. Community calls. The things that actually compound.

Automation doesn't replace effort. It redirects it.

If you're still doing everything manually, you're not dedicated. You're just busy. There's a difference.

I didn't build this system to be lazy. I built it because I realized the smartest traders and creators aren't the ones who grind the longest. They're the ones who build the machine, then improve the machine.

What would you automate if you could? Curious to hear.""",
        "media_ids": [auto_media]
    }
], "2026-03-27T10:00:00Z", platform="linkedin")

# ============================================================
# POST 3: Weekly Market Recap (X/Twitter Thread, Mar 28 10:00 UTC)
# Images: hook -> tweet 1, eth -> tweet 4, levels -> tweet 6
# ============================================================
print("\n3. Weekly Market Recap — Thread")
recap_hook_img = os.path.join(VIS, "weekly-recap-mar28", "slide-01-hook.png")
recap_eth_img = os.path.join(VIS, "weekly-recap-mar28", "slide-02-eth.png")
recap_levels_img = os.path.join(VIS, "weekly-recap-mar28", "slide-03-levels.png")
hook_media = upload_image(recap_hook_img, X_SET)
eth_media = upload_image(recap_eth_img, X_SET)
levels_media = upload_image(recap_levels_img, X_SET)

schedule_tweet(X_SET, [
    {
        "text": "This week: SEC cleared 16 tokens as commodities. Fed held rates. $708M in ETF outflows. ETH up 20%. $14B in options just expired.\n\nHere's what it all means and what to watch next week.",
        "media_ids": [hook_media]
    },
    {
        "text": "The SEC ruling is the biggest clarity event crypto has ever had.\n\n16 tokens. Officially not securities. Staking cleared. Airdrops cleared.\n\nThis isn't just good news. It's the foundation for the next wave of institutional products. More ETFs are coming. Count on it."
    },
    {
        "text": "The Fed held at 3.5-3.75% with a hawkish dot plot.\n\n$708M left BTC ETFs in one day. BTC tested $71.1K and held.\n\nThat support level is now confirmed. Smart money didn't panic. They accumulated. ETF inflows quietly resumed by Thursday."
    },
    {
        "text": "ETH is the real story this week.\n\nUp 20% since BlackRock's staked ETH ETF launched on March 12. Trading around $2,180 now. Still in recovery mode, not a clean breakout.\n\nBut ETHB changes the calculus. Institutions now earn ~2.5% yield just by holding. That shifts ETH from speculative to productive in portfolio models.",
        "media_ids": [eth_media]
    },
    {
        "text": "$14B in derivatives expired on Deribit this week. Largest quarterly expiry of 2026.\n\nMax pain sat at $75K. BTC hovered at $70K. Gamma hedging, PCE data, and Iran negotiations all stacked on the same 24-hour window.\n\nIf you survived that without panic selling, you understand the game."
    },
    {
        "text": "Next week: 3 levels to watch.\n\nBTC: $71.1K support confirmed. Break above $73K opens $78K.\nETH: Watch $2,378 pivot (R1) for confirmation. Below $1,990 (20-day SMA), structure weakens.\nSOL: Watch $185. A close above it means new highs.\n\nEvery week, Krib members get this analysis before it hits the timeline. DM 'KRIB' for access.",
        "media_ids": [levels_media]
    }
], "2026-03-28T10:00:00Z")

# ============================================================
# POST 4: Q2 Preview (X/Twitter, Mar 29 11:00 UTC)
# ============================================================
print("\n4. Q2 Preview — Community Tweet")
q2_img = os.path.join(VIS, "q2-preview-mar29", "slide-01.png")
q2_media = upload_image(q2_img, X_SET)
schedule_tweet(X_SET, [
    {
        "text": "Next week: CLARITY Act vote, Q1 close, and a potential BTC breakout above $73K.\n\nWe just got the clearest regulatory signal in crypto history. ETH has institutional staking momentum. BTC support at $71.1K held through $14B in options expiry.\n\nQ2 is setting up to be violent. In a good way.\n\nReply with your top hold going into Q2.",
        "media_ids": [q2_media]
    }
], "2026-03-29T11:00:00Z")

print("\nAll 4 posts scheduled on Typefully.")
