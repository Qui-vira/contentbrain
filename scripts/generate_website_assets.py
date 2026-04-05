#!/usr/bin/env python3
"""
Generate visual assets for bigquivdigitals.com website.

Assets:
1. Hero image (Home) — low-angle authority shot, red accent lighting
2. About portrait — confident composed, dark background
3. SignalOS product mockup — trading dashboard
4. ContentBrain product mockup — AI content intelligence dashboard
5. OG image — social sharing card

Uses fal.ai Nano Banana Pro Edit for character shots (with reference images)
and Nano Banana Pro (text-only) for product mockups.
"""

import os
import sys
import json
import time
import requests
import fal_client
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

FAL_KEY = os.getenv("FAL_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Set fal.ai key for fal_client
os.environ["FAL_KEY"] = FAL_KEY

if not FAL_KEY:
    print("ERROR: FAL_KEY not found in .env")
    sys.exit(1)

# Paths
CHARACTERS_DIR = Path(__file__).parent.parent / "08-Media" / "characters"
OUTPUT_DIR = Path(__file__).parent.parent / "06-Drafts" / "visuals" / "website"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# fal.ai headers
FAL_HEADERS = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json",
}

# Character description from character-library.md
QUIVIRA_DESC = "African man, sharp features, short cropped hair, light goatee, bold square black-frame glasses with blue-light lenses, confident commanding expression, Web3 creator aesthetic"

# Negative prompts
NEGATIVE_DEFAULT = "blurry, low quality, distorted face, extra fingers, extra limbs, watermark, text, logo, cartoon, anime, illustration, painting, 3D render, CGI look, overexposed, underexposed, cropped, out of frame, duplicate, disfigured"
NEGATIVE_BRAND = "bright cheerful colors, pastel, generic stock photo, corporate sterile, clip art, childish, unprofessional"
NEGATIVE_CHARACTER = "wrong ethnicity, different person, inconsistent features, morphed face, uncanny valley, plastic skin, wax figure"


def upload_to_fal(local_path: str) -> str:
    """Upload a local file to fal.ai storage and return the public URL."""
    print(f"  Uploading {Path(local_path).name} to fal.ai storage...")
    public_url = fal_client.upload_file(local_path)
    print(f"  Uploaded: {public_url}")
    return public_url


def run_fal(model_id: str, payload: dict) -> dict:
    """Run a fal.ai model using fal_client.subscribe (handles queuing + polling)."""
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            pass  # silently wait

    try:
        result = fal_client.subscribe(
            model_id,
            arguments=payload,
            with_logs=False,
            on_queue_update=on_queue_update,
        )
        return result
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def download_image(url: str, output_path: Path):
    """Download an image from URL to local path."""
    resp = requests.get(url)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    print(f"  Saved: {output_path.name}")


def search_pexels(query: str, per_page: int = 3, orientation: str = "landscape") -> list:
    """Search Pexels for reference images."""
    if not PEXELS_API_KEY:
        print("  WARNING: No PEXELS_API_KEY, skipping reference search")
        return []

    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": per_page, "orientation": orientation},
    )
    resp.raise_for_status()
    data = resp.json()
    return [p["src"]["large2x"] for p in data.get("photos", [])]


def generate_character_shot(
    name: str,
    char_ref_file: str,
    prompt: str,
    width: int = 1080,
    height: int = 1350,
    scene_ref_url: str = None,
):
    """Generate a character shot using Nano Banana Pro Edit with reference images."""
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"{'='*60}")

    # Upload character reference
    char_path = CHARACTERS_DIR / char_ref_file
    if not char_path.exists():
        print(f"  ERROR: Character reference not found: {char_path}")
        return None

    char_url = upload_to_fal(str(char_path))

    # Build image_urls list
    image_urls = [char_url]
    if scene_ref_url:
        image_urls.append(scene_ref_url)

    payload = {
        "prompt": prompt,
        "image_urls": image_urls,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
        "output_format": "png",
    }

    print(f"  Running fal-ai/nano-banana-pro/edit...")
    result = run_fal("fal-ai/nano-banana-pro/edit", payload)
    if not result:
        return None

    # Download the image
    images = result.get("images", [])
    if not images:
        print("  ERROR: No images in result")
        return None

    img_url = images[0].get("url")
    output_path = OUTPUT_DIR / f"{name}.png"
    download_image(img_url, output_path)
    return output_path


def generate_text_only(
    name: str,
    prompt: str,
    width: int = 1200,
    height: int = 630,
):
    """Generate an image using Nano Banana Pro (text-only, no reference images)."""
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"{'='*60}")

    payload = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
        "output_format": "png",
    }

    print(f"  Running fal-ai/nano-banana-pro...")
    result = run_fal("fal-ai/nano-banana-pro", payload)
    if not result:
        return None

    images = result.get("images", [])
    if not images:
        print("  ERROR: No images in result")
        return None

    img_url = images[0].get("url")
    output_path = OUTPUT_DIR / f"{name}.png"
    download_image(img_url, output_path)
    return output_path


def main():
    print("=" * 60)
    print("bigquivdigitals.com — Visual Asset Generation")
    print("=" * 60)

    results = {}

    # ──────────────────────────────────────────────
    # 1. HERO IMAGE (Home page)
    # Low-angle authority shot, dark bg, red accent lighting
    # Using: img_4656.jpg (low angle power shot)
    # ──────────────────────────────────────────────
    hero_prompt = (
        f"{QUIVIRA_DESC}, standing with arms slightly open in a commanding pose, "
        f"looking directly at camera with confident intensity, "
        f"low angle shot from below subject appears dominant and powerful, "
        f"dark background (#0A0A0F deep black), single red accent light from behind, "
        f"red rim light on edges, high contrast, brand signature, "
        f"intense atmosphere commanding presence sharp focus, "
        f"photograph ultra realistic editorial quality 8K resolution, "
        f"cinematic color grading, matte finish, high contrast deep blacks selective red highlights, "
        f"clean negative space for typography overlay room for text no clutter in upper 30% of frame"
    )

    results["hero"] = generate_character_shot(
        name="hero-home",
        char_ref_file="img_4656.jpg",
        prompt=hero_prompt,
        width=1080,
        height=1350,
    )

    # ──────────────────────────────────────────────
    # 2. ABOUT PAGE PORTRAIT
    # Confident, composed, dark background
    # Using: img_4674.jpg (arms crossed, authority)
    # ──────────────────────────────────────────────
    about_prompt = (
        f"{QUIVIRA_DESC}, arms crossed, composed and confident expression, "
        f"direct gaze at camera, slight knowing smile, "
        f"medium shot waist up subject centered, "
        f"dark professional studio clean background controlled lighting, "
        f"dark background (#0A0A0F deep black), subtle red accent light from camera left, "
        f"calm serene atmosphere composed and centered, "
        f"photograph ultra realistic editorial quality 8K resolution, "
        f"cinematic color grading, matte finish desaturated editorial, "
        f"high contrast deep blacks"
    )

    results["about"] = generate_character_shot(
        name="portrait-about",
        char_ref_file="img_4674.jpg",
        prompt=about_prompt,
        width=800,
        height=1000,
    )

    # ──────────────────────────────────────────────
    # 3. SIGNALOS PRODUCT MOCKUP
    # Trading dashboard with charts, dark UI, red accents
    # Text-only generation (no character needed)
    # ──────────────────────────────────────────────

    # First, get a reference image from Pexels for the trading dashboard
    print("\n  Searching Pexels for trading dashboard reference...")
    pexels_refs = search_pexels("trading dashboard monitors dark", per_page=1)
    scene_ref = pexels_refs[0] if pexels_refs else None

    signalos_prompt = (
        "Modern trading dashboard UI mockup on a large monitor, dark theme interface (#0A0A0F background), "
        "multiple crypto charts with candlestick patterns in green and red, "
        "sidebar showing signal alerts with approve/reject buttons, "
        "clean minimal UI design, red accent elements (#E63946), "
        "white and gray text on dark background, "
        "data visualization with clean typography, "
        "professional SaaS product screenshot aesthetic, "
        "8K resolution, sharp, clean digital modern, ultra detailed, "
        "no people, no hands, product mockup only"
    )

    results["signalos"] = generate_text_only(
        name="mockup-signalos",
        prompt=signalos_prompt,
        width=1200,
        height=800,
    )

    # ──────────────────────────────────────────────
    # 4. CONTENTBRAIN PRODUCT MOCKUP
    # AI content intelligence dashboard, dark UI
    # ──────────────────────────────────────────────
    contentbrain_prompt = (
        "Modern AI content intelligence dashboard UI mockup, dark theme interface (#0A0A0F background), "
        "showing social media analytics cards for Instagram, TikTok, YouTube, Twitter, "
        "competitor analysis grid with engagement metrics and hook scores, "
        "content calendar view in sidebar, AI-generated insights panel, "
        "clean minimal UI design, red accent elements (#E63946), "
        "white and gray text on dark background, "
        "professional SaaS product screenshot aesthetic, "
        "8K resolution, sharp, clean digital modern, ultra detailed, "
        "no people, no hands, product mockup only"
    )

    results["contentbrain"] = generate_text_only(
        name="mockup-contentbrain",
        prompt=contentbrain_prompt,
        width=1200,
        height=800,
    )

    # ──────────────────────────────────────────────
    # 5. OG IMAGE (Social sharing card)
    # Brand name + tagline on dark background with red accent
    # ──────────────────────────────────────────────
    og_prompt = (
        "Minimalist dark brand card for social media sharing, "
        "solid deep black background (#0A0A0F), "
        "large bold white text 'QUIVIRA' centered, clean sans-serif font, "
        "smaller text below 'Build. Trade. Dominate.', "
        "subtle red accent line (#E63946) between the two text elements, "
        "clean negative space, premium feel, "
        "corporate brand identity card aesthetic, "
        "8K resolution, sharp, clean digital, ultra minimal"
    )

    results["og"] = generate_text_only(
        name="og-image",
        prompt=og_prompt,
        width=1200,
        height=630,
    )

    # ──────────────────────────────────────────────
    # 6. HERO VARIANT — wider format for desktop layout
    # Same character, wider composition for side-by-side with text
    # ──────────────────────────────────────────────
    hero_wide_prompt = (
        f"{QUIVIRA_DESC}, standing confidently, one hand slightly raised in a teaching gesture, "
        f"looking directly at camera, "
        f"medium wide shot knees up subject in context of environment, "
        f"dark background (#0A0A0F deep black), red accent light from behind, "
        f"red rim light on edges, high contrast, "
        f"intense atmosphere commanding presence, "
        f"photograph ultra realistic editorial quality 8K resolution, "
        f"cinematic color grading, matte finish, deep blacks, "
        f"subject positioned on right third of frame leaving space on left for text overlay"
    )

    results["hero_wide"] = generate_character_shot(
        name="hero-home-wide",
        char_ref_file="img_4663.jpg",
        prompt=hero_wide_prompt,
        width=1600,
        height=900,
    )

    # ──────────────────────────────────────────────
    # Summary
    # ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    for name, path in results.items():
        status = f"OK — {path}" if path else "FAILED"
        print(f"  {name}: {status}")

    print(f"\nAll assets saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
