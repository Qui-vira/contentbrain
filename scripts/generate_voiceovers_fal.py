"""
Generate voiceover audio for 4 videos via fal.ai MiniMax voice clone.
Uses Quivira source audio for cloning.
"""
import requests, os, time, fal_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

FAL_KEY = os.getenv("FAL_KEY")
headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
BASE = os.path.join(os.path.dirname(__file__), "..")

# Upload source audio once
SOURCE_AUDIO = "C:/Users/Bigquiv/Downloads/Alimosho 29.m4a"
print("Uploading source audio for voice cloning...")
AUDIO_URL = fal_client.upload_file(SOURCE_AUDIO)
print(f"  OK: {AUDIO_URL[:60]}...\n")


def generate_voiceover(text, output_path, speed=1.0):
    if os.path.exists(output_path):
        print(f"  SKIP (exists): {os.path.basename(output_path)}")
        return True

    payload = {
        "text": text,
        "audio_url": AUDIO_URL,
        "speed": speed
    }

    try:
        resp = requests.post("https://queue.fal.run/fal-ai/minimax/voice-clone",
                             json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status_url = data["status_url"]
        response_url = data["response_url"]

        for _ in range(60):
            time.sleep(3)
            st = requests.get(status_url, headers=headers, timeout=15).json()
            if st.get("status") == "COMPLETED":
                break
            if st.get("status") == "FAILED":
                raise Exception("Voice generation failed on server")

        result = requests.get(response_url, headers=headers, timeout=30).json()
        audio_info = result.get("audio", {})
        audio_download_url = audio_info.get("url") if isinstance(audio_info, dict) else None

        if not audio_download_url:
            raise Exception(f"No audio URL in result. Keys: {list(result.keys())}")

        audio_data = requests.get(audio_download_url, timeout=60).content
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_data)

        size_kb = len(audio_data) / 1024
        print(f"  OK: {os.path.basename(output_path)} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


# Scripts
v1_script = """There are only 1 million Bitcoin left. Ever.

The 20 millionth Bitcoin was just mined on March 10th. That means 95% of all Bitcoin that will ever exist is already out there.

The remaining 1 million? That's going to take 114 years to mine. Every 4 years the supply gets cut in half. That's the halving.

So while the supply is slowing down to almost nothing, demand from ETFs, institutions, and governments is going up. Basic economics. Less supply, more demand. You know what happens next.

The question isn't whether Bitcoin hits 100K. The question is whether you own any when it does.

Follow for crypto clarity, not noise."""

v2_script = """The SEC cleared 16 tokens. Everyone's watching BTC and ETH. Nobody's watching these 3.

Number one. AVAX. Avalanche just got cleared as a commodity while their subnet architecture is getting picked up by institutions for tokenized assets. Regulatory clarity plus real utility. Pay attention.

Number two. LINK. Chainlink is the backbone of every DeFi protocol that matters. Now it's officially not a security. Institutions can integrate without legal risk. Green light for enterprise adoption.

Number three. DOT. Polkadot's been quiet. But cleared commodity status plus their new JAM protocol upgrade coming in Q2 makes this a sleeper. Low attention, high optionality.

Comment ALPHA and I'll DM you my full watchlist for Q2."""

v3_script = """I woke up to 3 approved signals and a full content calendar.

Every morning, my scanner has already done the work. I just check the setups and hit approve.

These took me zero screen time to find. The system scans every 4 hours while I sleep.

Content? Same thing. AI scouted trends, pulled the data, and built the plan. I just edit.

People think running signals and content is a full-time grind. It was. Until I built the machine. Now my mornings look like this.

Comment OS if you want to see how the system works."""

v4_script = """I just asked AI to analyze my portfolio. It found 3 things I missed.

I gave Claude Code my portfolio allocation and told it to check for concentration risk, correlation overlap, and sector imbalance.

It flagged that 40% of my portfolio is correlated to ETH ecosystem tokens. I didn't even realize. It also caught that I had zero stablecoin yield exposure, which is free money after the CLARITY Act passes.

In 2 minutes I got a full risk report that would have taken me an hour with a spreadsheet.

Comment PORTFOLIO and I'll send you the exact prompt I used."""


videos = [
    ("20M Bitcoin TikTok", "20m-bitcoin-tiktok", v1_script, 1.0),
    ("3 Cleared Tokens Reel", "3-cleared-tokens-reel", v2_script, 1.0),
    ("Day In Life KOL Reel", "day-in-life-kol-reel", v3_script, 0.95),
    ("Claude Code Portfolio Reel", "claude-code-portfolio-reel", v4_script, 1.0),
]

print("Generating voiceovers via fal.ai MiniMax voice clone...\n")
results = []
for name, folder, script, speed in videos:
    print(f"{name}:")
    out = os.path.join(BASE, "06-Drafts", "visuals", folder, "voiceover.mp3")
    ok = generate_voiceover(script, out, speed)
    results.append((name, ok))

print(f"\n{'='*50}")
print("SUMMARY")
for name, ok in results:
    print(f"  {name}: {'OK' if ok else 'FAILED'}")
