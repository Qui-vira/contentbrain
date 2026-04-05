"""
Birthday Photoshoot V2: 4 camera angles, each with 3-step pipeline
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
OUT = BASE / "06-Drafts" / "visuals" / "birthday-photoshoot-v2"
OUT.mkdir(parents=True, exist_ok=True)


def download(url: str, dest: Path):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"  Saved: {dest.name}  ({dest.stat().st_size:,} bytes)")


# Character references
ref_files = {
    "fullbody": CHARS / "img_4675.jpg",
    "front":    CHARS / "img_4650.jpg",
    "left":     CHARS / "img_4673.jpg",
    "right":    CHARS / "img_4678.jpg",
}

# Upload character references once
print("Uploading character references...")
uploaded_refs = {}
for name, path in ref_files.items():
    print(f"  {name} ({path.name})...")
    uploaded_refs[name] = fal_client.upload_file(str(path))
print("  Done.\n")


# 4 camera angles with different environment prompts and character prompts
angles = [
    {
        "name": "front-hero",
        "env_prompt": (
            "A sleek black and red Ducati Panigale V4 superbike parked on a rooftop "
            "at golden hour, shot from directly in front at eye level, city skyline in "
            "the background, dramatic golden sunset light, wet concrete floor with "
            "reflections, cinematic atmosphere, hyper-realistic film photograph, "
            "8K quality, no text, no words, no letters, no watermark, 9:16 vertical"
        ),
        "char_prompt": (
            "African man with sharp features, short cropped hair, light goatee, "
            "bold square black-frame glasses with blue-light lenses, wearing an "
            "all-black leather jacket over a black fitted t-shirt and black slim fit jeans, "
            "sitting confidently on the Ducati superbike facing the camera, one foot on "
            "the ground, relaxed powerful pose, front-facing shot at eye level, "
            "golden hour sunset light illuminating from behind creating a warm rim light, "
            "city skyline background, wet rooftop reflections, hyper-realistic film "
            "photograph, cinematic color grading, ultra realistic 8K, 9:16 vertical"
        ),
    },
    {
        "name": "low-angle",
        "env_prompt": (
            "A sleek black and red Ducati Panigale V4 superbike parked on a rooftop "
            "at golden hour, dramatic low angle shot looking upward, city skyline and "
            "golden sky behind, wet concrete floor with reflections, lens flare from "
            "the setting sun, cinematic atmosphere, hyper-realistic film photograph, "
            "8K quality, no text, no words, no letters, no watermark, 9:16 vertical"
        ),
        "char_prompt": (
            "African man with sharp features, short cropped hair, light goatee, "
            "bold square black-frame glasses with blue-light lenses, wearing an "
            "all-black leather jacket over a black fitted t-shirt and black slim fit jeans, "
            "standing next to the Ducati superbike with one hand on the handlebar, "
            "confident stance looking down at the camera, dramatic low angle shot "
            "looking up at him, golden hour sunset light from behind, city skyline, "
            "wet rooftop reflections, hyper-realistic film photograph, cinematic "
            "color grading, ultra realistic 8K, 9:16 vertical"
        ),
    },
    {
        "name": "three-quarter",
        "env_prompt": (
            "A sleek black and red Ducati Panigale V4 superbike parked on a rooftop "
            "at golden hour, three-quarter angle view from the left side, city skyline "
            "panorama in the background, warm golden light casting long shadows, "
            "wet concrete floor with reflections, cinematic atmosphere, hyper-realistic "
            "film photograph, 8K quality, no text, no words, no letters, no watermark, "
            "9:16 vertical"
        ),
        "char_prompt": (
            "African man with sharp features, short cropped hair, light goatee, "
            "bold square black-frame glasses with blue-light lenses, wearing an "
            "all-black leather jacket over a black fitted t-shirt and black slim fit jeans, "
            "leaning against the Ducati superbike with arms crossed, three-quarter angle "
            "from the left, looking at the camera with a confident subtle smile, "
            "golden hour warm light from the right side, city skyline panorama, "
            "wet rooftop reflections, hyper-realistic film photograph, cinematic "
            "color grading, ultra realistic 8K, 9:16 vertical"
        ),
    },
    {
        "name": "profile-silhouette",
        "env_prompt": (
            "A sleek black and red Ducati Panigale V4 superbike parked on a rooftop "
            "at golden hour, side profile view, massive golden sun setting directly "
            "behind creating a dramatic silhouette edge lighting, city skyline "
            "silhouette, wet concrete floor with golden reflections, cinematic "
            "atmosphere, hyper-realistic film photograph, 8K quality, no text, "
            "no words, no letters, no watermark, 9:16 vertical"
        ),
        "char_prompt": (
            "African man with sharp features, short cropped hair, light goatee, "
            "bold square black-frame glasses with blue-light lenses, wearing an "
            "all-black leather jacket over a black fitted t-shirt and black slim fit jeans, "
            "sitting on the Ducati superbike in side profile, looking toward the sunset, "
            "dramatic golden rim lighting from the setting sun behind him creating edge "
            "light on his silhouette, city skyline silhouette, wet rooftop with golden "
            "reflections, hyper-realistic film photograph, cinematic color grading, "
            "ultra realistic 8K, 9:16 vertical"
        ),
    },
]

neg_prompt = (
    "blurry, low quality, distorted face, extra fingers, watermark, text, words, "
    "letters, cartoon, anime, 3D render, bright cheerful colors, wrong ethnicity, "
    "white skin, brown trousers, khaki pants"
)

for i, angle in enumerate(angles, 1):
    print("=" * 60)
    print(f"ANGLE {i}/4: {angle['name']}")
    print("=" * 60)

    env_path = OUT / f"angle{i}-{angle['name']}-env.png"
    comp_path = OUT / f"angle{i}-{angle['name']}-comp.png"
    final_path = OUT / f"angle{i}-{angle['name']}-final.png"

    # ── STEP 1: Environment ──
    print(f"  Step 1: Generating environment...")
    result1 = fal_client.subscribe(
        "fal-ai/nano-banana-pro",
        arguments={
            "prompt": angle["env_prompt"],
            "image_size": {"width": 1080, "height": 1920},
            "num_images": 1,
        },
        with_logs=True,
    )
    env_url = result1["images"][0]["url"]
    download(env_url, env_path)

    # ── STEP 2: Composite ──
    print(f"  Step 2: Compositing character...")
    env_upload = fal_client.upload_file(str(env_path))

    image_urls = [
        env_upload,
        uploaded_refs["fullbody"],
        uploaded_refs["front"],
        uploaded_refs["left"],
        uploaded_refs["right"],
    ]

    handle = fal_client.submit(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": angle["char_prompt"],
            "negative_prompt": neg_prompt,
            "image_urls": image_urls,
            "image_size": {"width": 1080, "height": 1920},
            "num_images": 1,
        },
    )
    print("  Polling for composite result...")
    result2 = handle.get()
    comp_url = result2["images"][0]["url"]
    download(comp_url, comp_path)

    # ── STEP 3: Face swap ──
    print(f"  Step 3: Face swap...")
    comp_upload = fal_client.upload_file(str(comp_path))

    result3 = fal_client.subscribe(
        "fal-ai/face-swap",
        arguments={
            "base_image_url": comp_upload,
            "swap_image_url": uploaded_refs["front"],
        },
        with_logs=True,
    )
    final_url = result3["image"]["url"]
    download(final_url, final_path)
    print(f"  ANGLE {i} COMPLETE\n")


# ── Summary ──
print("=" * 60)
print("SUMMARY — 4 ANGLES")
print("=" * 60)
for i, angle in enumerate(angles, 1):
    final = OUT / f"angle{i}-{angle['name']}-final.png"
    if final.exists():
        print(f"  Angle {i} ({angle['name']}): {final}  ({final.stat().st_size:,} bytes)")
    else:
        print(f"  Angle {i} ({angle['name']}): MISSING")
print("\nDone!")
