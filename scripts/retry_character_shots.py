"""
Retry the 12 failed character shots using fal_client.upload_file for ref images.
"""
import requests, os, time, fal_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

FAL_KEY = os.getenv("FAL_KEY")
headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
BASE = os.path.join(os.path.dirname(__file__), "..")
CHARS = os.path.join(BASE, "08-Media", "characters")
NEG = "blurry, low quality, distorted face, extra fingers, watermark, text, words, letters, cartoon, anime, 3D render, bright cheerful colors, generic stock photo, wrong ethnicity"

# Cache uploaded ref URLs
ref_cache = {}

def get_ref_url(filename):
    if filename not in ref_cache:
        fp = os.path.join(CHARS, filename)
        print(f"  Uploading {filename}...", end=" ", flush=True)
        url = fal_client.upload_file(fp)
        ref_cache[filename] = url
        print(f"OK -> {url[:60]}...")
    return ref_cache[filename]

def generate_character_shot(prompt, filename, output_dir, ref_file):
    fp = os.path.join(output_dir, filename)
    if os.path.exists(fp):
        print(f"  SKIP (exists): {filename}")
        return True

    ref_url = get_ref_url(ref_file)
    model = "fal-ai/nano-banana-pro/edit"
    payload = {
        "prompt": prompt,
        "negative_prompt": NEG,
        "image_size": {"width": 1080, "height": 1920},
        "num_images": 1,
        "guidance_scale": 7.5,
        "num_inference_steps": 30,
        "image_urls": [ref_url]
    }

    for attempt in range(2):
        try:
            resp = requests.post(f"https://queue.fal.run/{model}", json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Use URLs from response (edit variant queues under base model path)
            status_url = data["status_url"]
            response_url = data["response_url"]

            for _ in range(90):
                time.sleep(3)
                st = requests.get(status_url, headers=headers, timeout=15).json()
                if st.get("status") == "COMPLETED":
                    break
                if st.get("status") == "FAILED":
                    raise Exception("Generation failed on server")

            result = requests.get(response_url, headers=headers, timeout=30).json()

            if not result.get("images"):
                raise Exception("No images returned")

            img_url = result["images"][0]["url"]
            img_data = requests.get(img_url, timeout=60).content
            os.makedirs(output_dir, exist_ok=True)
            with open(fp, "wb") as f:
                f.write(img_data)
            print(f"  OK: {filename}")
            return True
        except Exception as e:
            if attempt == 0:
                print(f"  RETRY {filename}: {e}")
                time.sleep(3)
            else:
                print(f"  FAIL: {filename}: {e}")
                return False


# All 12 failed character shots
failed_shots = [
    # Video 1: 20M Bitcoin TikTok
    {"dir": "20m-bitcoin-tiktok", "file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot head and shoulders, looking directly at camera with intense serious expression, dark studio background, single red accent light from behind, dramatic side lighting from camera left, cinematic color grading, photograph ultra realistic 8K resolution, intense atmosphere commanding presence sharp focus, 9:16 vertical"},
    {"dir": "20m-bitcoin-tiktok", "file": "shot-09.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium shot waist up, confident slight smirk, questioning gesture with hands, dark studio background, red accent backlight creating rim light, cinematic color grading, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "20m-bitcoin-tiktok", "file": "shot-10.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, calm confident expression looking directly at camera, dark background with subtle red rim light, warm cinematic tones, photograph ultra realistic 8K, 9:16 vertical"},

    # Video 2: 3 Cleared Tokens Reel
    {"dir": "3-cleared-tokens-reel", "file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, extreme close-up face fills frame, intense focused expression, dark studio, dramatic side lighting with red accent light, cinematic color grading, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "3-cleared-tokens-reel", "file": "shot-10.png", "ref": "img_4656.jpg",
     "prompt": "African man with bold square black-frame glasses, low angle shot from below, powerful commanding stance arms crossed, dark studio, red accent backlight creating rim light, authority energy, shot from below subject appears dominant, cinematic photograph 8K, 9:16 vertical"},
    {"dir": "3-cleared-tokens-reel", "file": "shot-12.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, slight warm smile, inviting approachable expression, dark background with soft golden rim light, warm cinematic tones, photograph ultra realistic 8K, 9:16 vertical"},

    # Video 3: Day In Life KOL Reel
    {"dir": "day-in-life-kol-reel", "file": "shot-01.png", "ref": "img_4671.jpg",
     "prompt": "African man with bold square black-frame glasses, medium shot, sitting up reaching for phone on bedside table, morning golden light streaming from window, cozy modern bedroom, warm amber tones, natural authentic vlog energy, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "day-in-life-kol-reel", "file": "shot-03.png", "ref": "img_4668.jpg",
     "prompt": "African man with bold square black-frame glasses, over-the-shoulder shot from behind, looking at phone screen showing trading signal charts, morning light, relaxed comfortable posture, cozy home environment, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "day-in-life-kol-reel", "file": "shot-08.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium close-up, relaxed confident expression, casual dark hoodie, home office background with plants and monitor, warm natural window light, authentic vlog energy, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "day-in-life-kol-reel", "file": "shot-10.png", "ref": "img_4649.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, genuine warm smile, looking directly at camera, soft golden light, inviting welcoming expression, dark background with warm tones, photograph ultra realistic 8K, 9:16 vertical"},

    # Video 4: Claude Code Portfolio Reel
    {"dir": "claude-code-portfolio-reel", "file": "shot-01.png", "ref": "img_4650.jpg",
     "prompt": "African man with bold square black-frame glasses, close-up shot, eyes slightly wide with discovery expression, face illuminated only by laptop screen glow, completely dark room, blue-green screen reflections on skin, intimate tech mood, photograph ultra realistic 8K, 9:16 vertical"},
    {"dir": "claude-code-portfolio-reel", "file": "shot-08.png", "ref": "img_4655.jpg",
     "prompt": "African man with bold square black-frame glasses, medium close-up, confident knowing expression with slight head tilt, dark background with subtle blue tech glow, approachable authority energy, photograph ultra realistic 8K, 9:16 vertical"},
]

print(f"Retrying {len(failed_shots)} character shots...\n")

# Pre-upload all refs
needed = set(s["ref"] for s in failed_shots)
print(f"Pre-uploading {len(needed)} reference images...")
for ref in sorted(needed):
    get_ref_url(ref)

ok = 0
fail = 0
for shot in failed_shots:
    out_dir = os.path.join(BASE, "06-Drafts", "visuals", shot["dir"])
    print(f"\n[{shot['dir']}] {shot['file']}")
    if generate_character_shot(shot["prompt"], shot["file"], out_dir, shot["ref"]):
        ok += 1
    else:
        fail += 1

print(f"\n{'='*50}")
print(f"DONE: {ok}/{ok+fail} succeeded, {fail} failed")
