"""
Generate all keyframe images for 4 video projects via fal.ai.
Scene-only shots use nano-banana-pro, character shots use nano-banana-pro/edit with reference images.
"""
import requests, os, time, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found in .env")
    sys.exit(1)

headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
BASE = os.path.join(os.path.dirname(__file__), "..")
CHARS = os.path.join(BASE, "08-Media", "characters")

NEG = "blurry, low quality, distorted face, extra fingers, watermark, text, words, letters, cartoon, anime, 3D render, bright cheerful colors, generic stock photo, wrong ethnicity"

# Cache for uploaded reference URLs
ref_cache = {}

def upload_ref(filename):
    if filename in ref_cache:
        return ref_cache[filename]
    fp = os.path.join(CHARS, filename)
    print(f"  Uploading ref: {filename}...", end=" ", flush=True)
    with open(fp, "rb") as f:
        resp = requests.post(
            "https://fal.run/fal-ai/file-upload",
            headers={"Authorization": f"Key {FAL_KEY}"},
            files={"file": (filename, f, "image/jpeg")}
        )
    if resp.status_code != 200:
        # Try alternative upload endpoint
        with open(fp, "rb") as f:
            resp = requests.post(
                "https://rest.alpha.fal.ai/storage/upload",
                headers={"Authorization": f"Key {FAL_KEY}"},
                files={"file": (filename, f, "image/jpeg")}
            )
    url = resp.json().get("url") or resp.json().get("file_url")
    print(f"OK")
    ref_cache[filename] = url
    return url

def generate(prompt, filename, output_dir, ref_urls=None, retries=1):
    fp = os.path.join(output_dir, filename)
    if os.path.exists(fp):
        print(f"  SKIP (exists): {filename}")
        return fp

    model = "fal-ai/nano-banana-pro/edit" if ref_urls else "fal-ai/nano-banana-pro"
    submit_url = f"https://queue.fal.run/{model}"
    payload = {
        "prompt": prompt,
        "negative_prompt": NEG,
        "image_size": {"width": 1080, "height": 1920},
        "num_images": 1,
        "guidance_scale": 7.5,
        "num_inference_steps": 30
    }
    if ref_urls:
        payload["image_urls"] = ref_urls

    for attempt in range(retries + 1):
        try:
            resp = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            request_id = resp.json()["request_id"]

            status_url = f"https://queue.fal.run/{model}/requests/{request_id}/status"
            for _ in range(90):
                time.sleep(3)
                st = requests.get(status_url, headers=headers, timeout=15).json()
                if st.get("status") == "COMPLETED":
                    break
                if st.get("status") == "FAILED":
                    raise Exception("Generation failed")

            result_url = f"https://queue.fal.run/{model}/requests/{request_id}"
            result = requests.get(result_url, headers=headers, timeout=30).json()

            if not result.get("images"):
                raise Exception("No images in result")

            img_url = result["images"][0]["url"]
            img_data = requests.get(img_url, timeout=60).content
            os.makedirs(output_dir, exist_ok=True)
            with open(fp, "wb") as f:
                f.write(img_data)
            print(f"  OK: {filename}")
            return fp
        except Exception as e:
            if attempt < retries:
                print(f"  RETRY {filename}: {e}")
                time.sleep(2)
            else:
                print(f"  FAIL: {filename} - {e}")
                return None


def run_video(name, output_dir, shots):
    print(f"\n{'='*60}")
    print(f"VIDEO: {name}")
    print(f"Output: {output_dir}")
    print(f"Shots: {len(shots)}")
    print(f"{'='*60}")
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    for shot in shots:
        fn = shot["file"]
        prompt = shot["prompt"]
        ref = shot.get("ref")
        ref_urls = None
        if ref:
            ref_url = upload_ref(ref)
            ref_urls = [ref_url]
        print(f"  Generating {fn}...")
        r = generate(prompt, fn, output_dir, ref_urls)
        results[fn] = "OK" if r else "FAIL"
    return results


# ============================================================
# VIDEO 1: 20M Bitcoin TikTok
# ============================================================
v1_dir = os.path.join(BASE, "06-Drafts", "visuals", "20m-bitcoin-tiktok")
v1_shots = [
    {"file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot head and shoulders, looking directly at camera with intense serious expression, dark studio background, single red accent light from behind, dramatic side lighting from camera left, cinematic color grading, photograph ultra realistic 8K resolution, intense atmosphere commanding presence sharp focus, 9:16 vertical"},
    {"file": "shot-02.png",
     "prompt": "Giant golden Bitcoin coin floating in dark void, glowing ethereal volumetric light, the number 20000000 faintly etched on surface, dark moody atmosphere, cinematic, photorealistic 8K quality, 9:16 vertical"},
    {"file": "shot-03.png",
     "prompt": "Futuristic Bitcoin mining facility interior, rows of mining rigs with blinking blue and orange LED lights, dark industrial environment, steam rising from machines, cinematic wide shot, photorealistic 8K quality, 9:16 vertical"},
    {"file": "shot-04.png",
     "prompt": "Digital hourglass with golden Bitcoin-colored sand flowing slowly, almost empty top chamber, dark background, volumetric golden light rays, time running out concept, cinematic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-05.png",
     "prompt": "Abstract visualization of Bitcoin supply halving, golden bar chart with each bar half the size of the previous, decreasing pattern, dark background with subtle red accent lighting, clean financial data visualization aesthetic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-06.png",
     "prompt": "Wall Street trading floor with Bloomberg terminals showing Bitcoin charts, institutional traders in suits watching screens, dark moody dramatic lighting, cinematic color grading, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-07.png",
     "prompt": "Supply and demand economics chart visualization, shrinking gold supply curve meeting rising green demand curve, clean lines on dark background, financial chart professional style, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-08.png",
     "prompt": "Bitcoin price chart showing dramatic green candle breakout on dark background, price smashing through resistance level with golden particle explosion effect, cinematic trading chart aesthetic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-09.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium shot waist up, confident slight smirk, questioning gesture with hands, dark studio background, red accent backlight creating rim light, cinematic color grading, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-10.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, calm confident expression looking directly at camera, dark background with subtle red rim light, warm cinematic tones, photograph ultra realistic 8K, 9:16 vertical"},
]

# ============================================================
# VIDEO 2: 3 Cleared Tokens Reel
# ============================================================
v2_dir = os.path.join(BASE, "06-Drafts", "visuals", "3-cleared-tokens-reel")
v2_shots = [
    {"file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, extreme close-up face fills frame, intense focused expression, dark studio, dramatic side lighting with red accent light, cinematic color grading, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-02.png",
     "prompt": "SEC government building facade with dramatic spotlight illumination, official classical architecture columns, dark moody storm sky, red and gold accent lighting, authority and power atmosphere, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-03.png",
     "prompt": "16 cryptocurrency coins arranged in 4x4 grid pattern glowing golden on dark background, some coins brighter than others indicating selection, official regulatory cleared concept, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-04.png",
     "prompt": "Avalanche AVAX cryptocurrency concept, glowing red triangular logo in dark space, subnet network visualization with blue and red node connections behind it, futuristic institutional aesthetic, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-05.png",
     "prompt": "Institutional building facade transforming into digital tokenized assets, physical architecture dissolving into glowing data particles, blue and gold lighting, futuristic metamorphosis concept, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-06.png",
     "prompt": "Chainlink LINK concept, glowing blue hexagonal logo with oracle network connections radiating outward, DeFi protocol connections shown as golden chain links, dark background, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-07.png",
     "prompt": "Enterprise server room with blockchain integration visualization, green status lights indicating regulatory approval, clean technology aesthetic, dark environment with blue accent lighting, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-08.png",
     "prompt": "Polkadot DOT concept, circular multi-colored logo emerging from dark shadows, parachain connections lighting up sequentially, dark background with purple and pink accents, sleeper awakening energy, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-09.png",
     "prompt": "Blockchain protocol upgrade visualization, interconnected nodes pulsing with energy upgrade wave, purple and gold lighting, futuristic network transformation, dark background, cinematic photorealistic 8K, 9:16 vertical"},
    {"file": "shot-10.png", "ref": "img_4656.jpg",
     "prompt": "African man with bold square black-frame glasses, low angle shot from below, powerful commanding stance arms crossed, dark studio, red accent backlight creating rim light, authority energy, shot from below subject appears dominant, cinematic photograph 8K, 9:16 vertical"},
    {"file": "shot-11.png",
     "prompt": "The word ALPHA floating in dark cinematic space with golden metallic glow, comment speech bubble aesthetic around it, dark background with red and gold accent lighting, bold CTA energy, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-12.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, slight warm smile, inviting approachable expression, dark background with soft golden rim light, warm cinematic tones, photograph ultra realistic 8K, 9:16 vertical"},
]

# ============================================================
# VIDEO 3: Day In Life KOL Reel
# ============================================================
v3_dir = os.path.join(BASE, "06-Drafts", "visuals", "day-in-life-kol-reel")
v3_shots = [
    {"file": "shot-01.png", "ref": "img_4671.jpg",
     "prompt": "African man with bold square black-frame glasses, medium shot, sitting up reaching for phone on bedside table, morning golden light streaming from window, cozy modern bedroom, warm amber tones, natural authentic vlog energy, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-02.png",
     "prompt": "Smartphone screen close-up showing Telegram app with 3 signal notification alerts, dark mode UI, green checkmarks next to each alert, morning light reflecting on phone glass, clean mobile interface, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-03.png", "ref": "img_4668.jpg",
     "prompt": "African man with bold square black-frame glasses, over-the-shoulder shot from behind, looking at phone screen showing trading signal charts, morning light, relaxed comfortable posture, cozy home environment, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-04.png",
     "prompt": "Multiple trading monitors showing clean chart setups with technical indicators, RSI MACD support levels highlighted, dark professional trading desk, blue screen glow illuminating the setup, professional trader aesthetic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-05.png",
     "prompt": "Digital clock display showing 4:00 AM with AI scanner visualization running behind it, automated crypto pair scanning across multiple charts, dark room, blue and green data stream particles, autonomous system concept, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-06.png",
     "prompt": "Content calendar displayed on large monitor, posts mapped out for the week with color-coded categories, clean dark mode productivity UI, organized grid layout, professional content creator workspace, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-07.png",
     "prompt": "AI trend analysis dashboard on screen, data visualizations showing trending topics and performance metrics, dark mode interface, purple and blue accent colors, futuristic productivity tool aesthetic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-08.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium close-up, relaxed confident expression, casual dark hoodie, home office background with plants and monitor, warm natural window light, authentic vlog energy, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-09.png",
     "prompt": "Split composition comparison, left side chaotic cluttered desk with scattered papers charts coffee cups, right side clean minimal desk with single laptop and coffee mug, before-after transformation concept, dark cinematic lighting, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-10.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, genuine warm smile, looking directly at camera, soft golden light, inviting welcoming expression, dark background with warm tones, photograph ultra realistic 8K, 9:16 vertical"},
]

# ============================================================
# VIDEO 4: Claude Code Portfolio Reel
# ============================================================
v4_dir = os.path.join(BASE, "06-Drafts", "visuals", "claude-code-portfolio-reel")
v4_shots = [
    {"file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, eyes slightly wide with discovery expression, face illuminated only by laptop screen glow, completely dark room, blue-green screen reflections on skin, intimate tech mood, photograph ultra realistic 8K, 9:16 vertical"},
    {"file": "shot-02.png",
     "prompt": "Clean terminal interface showing code execution output, dark terminal theme with green and white monospace text on pure black background, portfolio analysis data scrolling, professional developer aesthetic, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-03.png",
     "prompt": "Portfolio pie chart visualization breaking apart to reveal risk exposure underneath, one large 40 percent segment highlighted in red showing concentration risk, dark background, clean financial data visualization style, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-04.png",
     "prompt": "Terminal output showing analysis results with risk flags highlighted in yellow and red warning colors, concentration warning text, correlation overlap detected notification, clean code monospace aesthetic, dark terminal theme, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-05.png",
     "prompt": "DeFi stablecoin yield visualization, protocol logos with APY percentages displayed in green, regulatory document faded in background, financial opportunity concept, dark background with gold accent highlights, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-06.png",
     "prompt": "Terminal screen showing suggested portfolio rebalance output, before and after allocation horizontal bars, green indicators showing improvements, professional data output format, dark terminal theme, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-07.png",
     "prompt": "Stopwatch showing 2 minutes on left side glowing gold next to spreadsheet showing 1 hour on right side in dim gray, time efficiency comparison concept, dark background, dramatic contrast between the two sides, photorealistic 8K, 9:16 vertical"},
    {"file": "shot-08.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium close-up, confident knowing expression with slight head tilt, dark background with subtle blue tech glow, approachable authority energy, photograph ultra realistic 8K, 9:16 vertical"},
]

# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    all_results = {}

    # Pre-upload all needed reference images
    needed_refs = set()
    for shots in [v1_shots, v2_shots, v3_shots, v4_shots]:
        for s in shots:
            if s.get("ref"):
                needed_refs.add(s["ref"])

    print(f"Pre-uploading {len(needed_refs)} character reference images...")
    for ref in sorted(needed_refs):
        try:
            upload_ref(ref)
        except Exception as e:
            print(f"  WARN: Could not upload {ref}: {e}")

    # Generate all videos
    all_results["20M Bitcoin TikTok"] = run_video("20M Bitcoin TikTok", v1_dir, v1_shots)
    all_results["3 Cleared Tokens Reel"] = run_video("3 Cleared Tokens Reel", v2_dir, v2_shots)
    all_results["Day In Life KOL Reel"] = run_video("Day In Life KOL Reel", v3_dir, v3_shots)
    all_results["Claude Code Portfolio Reel"] = run_video("Claude Code Portfolio Reel", v4_dir, v4_shots)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total_ok = 0
    total_fail = 0
    for video, results in all_results.items():
        ok = sum(1 for v in results.values() if v == "OK")
        fail = sum(1 for v in results.values() if v == "FAIL")
        total_ok += ok
        total_fail += fail
        status = "ALL OK" if fail == 0 else f"{fail} FAILED"
        print(f"  {video}: {ok}/{len(results)} ({status})")
        if fail > 0:
            for fn, st in results.items():
                if st == "FAIL":
                    print(f"    - {fn}")
    print(f"\nTOTAL: {total_ok}/{total_ok+total_fail} generated")
