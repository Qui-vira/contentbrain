#!/usr/bin/env python3
"""
Generate remaining 5 website assets using Gemini 3.1 Flash Image (free).
Same prompts as generate_website_assets.py but via google-genai directly.

Assets:
1. portrait-about — confident composed, dark background (edit with char ref)
2. mockup-signalos — trading dashboard UI
3. mockup-contentbrain — AI content intelligence dashboard
4. og-image — social sharing card
5. hero-home-wide — wider hero variant (edit with char ref)
"""

import os
import sys
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDes9riKiUkLZLZaKRaHPEUQKP16WJislE")
if not GEMINI_KEY:
    print("ERROR: GEMINI_API_KEY not found")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_KEY)
MODEL = "gemini-2.5-flash-image"

# Paths
CHARACTERS_DIR = Path(__file__).parent.parent / "08-Media" / "characters"
OUTPUT_DIR = Path(__file__).parent.parent / "06-Drafts" / "visuals" / "website"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Character description
QUIVIRA_DESC = (
    "African man, sharp features, short cropped hair, light goatee, "
    "bold square black-frame glasses with blue-light lenses, "
    "confident commanding expression, Web3 creator aesthetic"
)


def extract_image(response, name):
    """Extract image from Gemini response and save it."""
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            img_data = part.inline_data.data
            ext = "png" if "png" in part.inline_data.mime_type else "jpg"
            output_path = OUTPUT_DIR / f"{name}.{ext}"
            output_path.write_bytes(img_data)
            print(f"  Saved: {output_path.name} ({len(img_data)} bytes)")
            return output_path
    print("  ERROR: No image in response")
    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"  Text: {part.text[:200]}")
    return None


def call_with_retry(contents, name, max_retries=5):
    """Call Gemini API with retry on rate limit errors."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            return extract_image(response, name)
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                # Extract retry delay from error
                import re
                match = re.search(r'retry in ([\d.]+)s', err)
                wait = float(match.group(1)) + 5 if match else 65
                print(f"  Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait:.0f}s...")
                time.sleep(wait)
            else:
                print(f"  ERROR: {e}")
                return None
    print(f"  ERROR: Max retries ({max_retries}) exhausted")
    return None


def generate_text_only(name: str, prompt: str):
    """Generate an image from text prompt only."""
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"{'='*60}")
    return call_with_retry(prompt, name)


def generate_with_reference(name: str, char_ref_file: str, prompt: str):
    """Generate an image using a character reference image."""
    print(f"\n{'='*60}")
    print(f"Generating: {name} (with reference: {char_ref_file})")
    print(f"{'='*60}")

    char_path = CHARACTERS_DIR / char_ref_file
    if not char_path.exists():
        print(f"  ERROR: Reference not found: {char_path}")
        return None

    # Read and encode the reference image
    img_bytes = char_path.read_bytes()
    print(f"  Loaded reference: {char_ref_file} ({len(img_bytes)} bytes)")

    contents = [
        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
        types.Part.from_text(text=prompt),
    ]
    return call_with_retry(contents, name)


def main():
    print("=" * 60)
    print("bigquivdigitals.com — Website Assets (Gemini Free)")
    print(f"Model: {MODEL}")
    print("=" * 60)

    results = {}

    # ── 1. ABOUT PAGE PORTRAIT ──
    about_prompt = (
        f"Generate a new editorial portrait photo based on this reference person. "
        f"{QUIVIRA_DESC}, arms crossed, composed and confident expression, "
        f"direct gaze at camera, slight knowing smile, "
        f"medium shot waist up subject centered, "
        f"dark professional studio clean background controlled lighting, "
        f"dark background deep black (#0A0A0F), subtle red accent light from camera left, "
        f"calm serene atmosphere composed and centered, "
        f"photograph ultra realistic editorial quality 8K resolution, "
        f"cinematic color grading, matte finish desaturated editorial, "
        f"high contrast deep blacks"
    )
    results["about"] = generate_with_reference(
        name="portrait-about",
        char_ref_file="img_4674.jpg",
        prompt=about_prompt,
    )
    time.sleep(30)  # Rate limit buffer

    # ── 2. SIGNALOS PRODUCT MOCKUP ──
    signalos_prompt = (
        "Modern trading dashboard UI mockup on a large monitor, dark theme interface "
        "(#0A0A0F background), multiple crypto charts with candlestick patterns in green "
        "and red, sidebar showing signal alerts with approve/reject buttons, "
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
    )
    time.sleep(2)

    # ── 3. CONTENTBRAIN PRODUCT MOCKUP ──
    contentbrain_prompt = (
        "Modern AI content intelligence dashboard UI mockup, dark theme interface "
        "(#0A0A0F background), showing social media analytics cards for Instagram, "
        "TikTok, YouTube, Twitter, competitor analysis grid with engagement metrics "
        "and hook scores, content calendar view in sidebar, AI-generated insights panel, "
        "clean minimal UI design, red accent elements (#E63946), "
        "white and gray text on dark background, "
        "professional SaaS product screenshot aesthetic, "
        "8K resolution, sharp, clean digital modern, ultra detailed, "
        "no people, no hands, product mockup only"
    )
    results["contentbrain"] = generate_text_only(
        name="mockup-contentbrain",
        prompt=contentbrain_prompt,
    )
    time.sleep(2)

    # ── 4. OG IMAGE ──
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
    )
    time.sleep(2)

    # ── 5. HERO WIDE VARIANT ──
    hero_wide_prompt = (
        f"Generate a new editorial photo based on this reference person. "
        f"{QUIVIRA_DESC}, standing confidently, one hand slightly raised in a "
        f"teaching gesture, looking directly at camera, "
        f"medium wide shot knees up subject in context of environment, "
        f"dark background deep black (#0A0A0F), red accent light from behind, "
        f"red rim light on edges, high contrast, "
        f"intense atmosphere commanding presence, "
        f"photograph ultra realistic editorial quality 8K resolution, "
        f"cinematic color grading, matte finish, deep blacks, "
        f"subject positioned on right third of frame leaving space on left for text overlay"
    )
    results["hero_wide"] = generate_with_reference(
        name="hero-home-wide",
        char_ref_file="img_4663.jpg",
        prompt=hero_wide_prompt,
    )

    # ── Summary ──
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    ok = 0
    for name, path in results.items():
        status = f"OK — {path}" if path else "FAILED"
        if path:
            ok += 1
        print(f"  {name}: {status}")

    print(f"\n{ok}/{len(results)} assets generated successfully")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
