"""
Birthday Photoshoot: 3-step fal.ai pipeline
Step 1: Generate environment (nano-banana-pro)
Step 2: Composite character (nano-banana-pro/edit)
Step 3: Face swap (face-swap)
"""

import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ["FAL_KEY"] = os.getenv("FAL_KEY")

import fal_client

BASE = Path(r"C:/Users/Bigquiv/onedrive/desktop/contentbrain")
CHARS = BASE / "08-Media" / "characters"
OUT = BASE / "06-Drafts" / "visuals" / "birthday-photoshoot"
OUT.mkdir(parents=True, exist_ok=True)


def download(url: str, dest: Path):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"  Saved: {dest}  ({dest.stat().st_size:,} bytes)")


# ── STEP 1: Environment ──────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Generating environment (nano-banana-pro)...")
print("=" * 60)

env_path = OUT / "step1-environment.png"

result1 = fal_client.subscribe(
    "fal-ai/nano-banana-pro",
    arguments={
        "prompt": (
            "A sleek black and red Ducati Panigale V4 superbike parked on a rooftop "
            "at golden hour, city skyline in the background, dramatic golden sunset light, "
            "wet concrete floor with reflections, cinematic atmosphere, hyper-realistic "
            "film photograph, 8K quality, no text, no words, no letters, no watermark, "
            "9:16 vertical"
        ),
        "image_size": {"width": 1080, "height": 1920},
        "num_images": 1,
    },
    with_logs=True,
)

env_url = result1["images"][0]["url"]
print(f"  Environment URL: {env_url}")
download(env_url, env_path)
print("  STEP 1 COMPLETE\n")


# ── STEP 2: Character composite ─────────────────────────────────────
print("=" * 60)
print("STEP 2: Uploading references & compositing character...")
print("=" * 60)

comp_path = OUT / "step2-composite.png"

ref_files = {
    "fullbody": CHARS / "img_4675.jpg",
    "front":    CHARS / "img_4650.jpg",
    "left":     CHARS / "img_4673.jpg",
    "right":    CHARS / "img_4678.jpg",
}

uploaded = {}
# Upload environment from step 1
print("  Uploading environment image...")
env_upload = fal_client.upload_file(str(env_path))
uploaded["environment"] = env_upload
print(f"    environment -> {env_upload}")

for name, path in ref_files.items():
    print(f"  Uploading {name} ({path.name})...")
    url = fal_client.upload_file(str(path))
    uploaded[name] = url
    print(f"    {name} -> {url}")

image_urls = [
    uploaded["environment"],
    uploaded["fullbody"],
    uploaded["front"],
    uploaded["left"],
    uploaded["right"],
]

print("  Submitting composite request...")

# Use submit + poll pattern for /edit model
handle = fal_client.submit(
    "fal-ai/nano-banana-pro/edit",
    arguments={
        "prompt": (
            "African man with sharp features, short cropped hair, light goatee, "
            "bold square black-frame glasses with blue-light lenses, wearing an "
            "all-black leather jacket over a black fitted t-shirt and black slim fit jeans, "
            "sitting confidently on the Ducati superbike with one foot on the ground, "
            "relaxed powerful pose facing the camera, golden hour sunset light illuminating "
            "from behind creating a warm rim light, city skyline background, wet rooftop "
            "reflections, hyper-realistic film photograph, cinematic color grading, "
            "ultra realistic 8K, 9:16 vertical"
        ),
        "negative_prompt": (
            "blurry, low quality, distorted face, extra fingers, watermark, text, words, "
            "letters, cartoon, anime, 3D render, bright cheerful colors, wrong ethnicity, "
            "white skin"
        ),
        "image_urls": image_urls,
        "image_size": {"width": 1080, "height": 1920},
        "num_images": 1,
    },
)

print("  Polling for result...")
result2 = handle.get()

comp_url = result2["images"][0]["url"]
print(f"  Composite URL: {comp_url}")
download(comp_url, comp_path)
print("  STEP 2 COMPLETE\n")


# ── STEP 3: Face swap ───────────────────────────────────────────────
print("=" * 60)
print("STEP 3: Face swap...")
print("=" * 60)

final_path = OUT / "step3-final.png"

# Upload composite as base
print("  Uploading composite for face swap...")
comp_upload = fal_client.upload_file(str(comp_path))
print(f"    base -> {comp_upload}")

# Upload front face as swap source
print("  Uploading face reference...")
face_upload = fal_client.upload_file(str(CHARS / "img_4650.jpg"))
print(f"    swap -> {face_upload}")

result3 = fal_client.subscribe(
    "fal-ai/face-swap",
    arguments={
        "base_image_url": comp_upload,
        "swap_image_url": face_upload,
    },
    with_logs=True,
)

final_url = result3["image"]["url"]
print(f"  Final URL: {final_url}")
download(final_url, final_path)
print("  STEP 3 COMPLETE\n")


# ── Summary ──────────────────────────────────────────────────────────
print("=" * 60)
print("SUMMARY")
print("=" * 60)
for step, path in [
    ("Step 1 - Environment", env_path),
    ("Step 2 - Composite", comp_path),
    ("Step 3 - Final", final_path),
]:
    size = path.stat().st_size
    print(f"  {step}: {path}  ({size:,} bytes)")
print("\nDone!")
