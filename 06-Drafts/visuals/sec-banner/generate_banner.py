"""
SEC Twitter/X Banner Generator
Aspect ratio: 5:2 (1500x600)
Theme: Regulation, hidden signals, market intelligence
"""
import requests, os, time, json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────
W, H = 1500, 600
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(OUT_DIR, "backgrounds")
os.makedirs(BG_DIR, exist_ok=True)

# Colors
DEEP_BLACK = (10, 10, 15)
DEEP_NAVY = (8, 12, 28)
NEON_BLUE = (0, 180, 255)
SAFE_GREEN = (0, 230, 118)
RISK_RED = (230, 57, 70)
WHITE = (255, 255, 255)
LIGHT = (210, 215, 225)
DIMMED = (140, 150, 170)
GOLD = (255, 215, 0)

# Fonts
FONT_DIR = "C:/Windows/Fonts"
FONT_BOLD = os.path.join(FONT_DIR, "arialbd.ttf")
FONT_REG = os.path.join(FONT_DIR, "arial.ttf")
FONT_SEGOE_BOLD = os.path.join(FONT_DIR, "segoeuib.ttf")
FONT_IMPACT = os.path.join(FONT_DIR, "impact.ttf")

# ── fal.ai Background Generation ───────────────────────────────────────
FAL_KEY = os.getenv("FAL_KEY")

def generate_background():
    """Generate cinematic SEC-themed background via fal.ai."""
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

    prompt = (
        "A glowing official government document labeled SEC emitting ethereal blue light rays, "
        "partially revealing cryptocurrency symbols and blockchain nodes fading into deep shadows, "
        "dark environment with faint holographic candlestick charts in background, "
        "digital data streams flowing outward from the document, "
        "matrix-style code rain faintly visible, subtle blockchain grid pattern, "
        "deep black and dark navy color palette with neon blue light accents and subtle green highlights, "
        "volumetric lighting, cinematic atmosphere, ultra detailed, 8k quality, "
        "mysterious elite intelligence aesthetic, photorealistic digital art, "
        "no text, no words, no letters, no numbers, no watermark, no logo"
    )

    submit_url = "https://queue.fal.run/fal-ai/nano-banana-pro"
    payload = {
        "prompt": prompt,
        "negative_prompt": "text, words, letters, numbers, watermark, logo, blurry, low quality, cartoon, anime, distorted, bright cheerful colors, flat lighting, generic stock photo, faces, people, hands",
        "image_size": {"width": 1500, "height": 600},
        "num_images": 1,
        "guidance_scale": 7.5,
        "num_inference_steps": 30
    }

    print("Submitting background generation to fal.ai...")
    resp = requests.post(submit_url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    request_id = data["request_id"]
    print(f"Request ID: {request_id}")

    status_url = f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{request_id}/status"
    for i in range(60):
        time.sleep(3)
        status = requests.get(status_url, headers=headers, timeout=15).json()
        s = status.get("status", "UNKNOWN")
        print(f"  Poll {i+1}: {s}")
        if s == "COMPLETED":
            break

    result_url = f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{request_id}"
    result = requests.get(result_url, headers=headers, timeout=30).json()
    image_url = result["images"][0]["url"]

    bg_path = os.path.join(BG_DIR, "bg_sec_banner.png")
    img_data = requests.get(image_url, timeout=60).content
    with open(bg_path, "wb") as f:
        f.write(img_data)
    print(f"Background saved: {bg_path}")
    return bg_path


# ── Compositing Helpers ─────────────────────────────────────────────────

def draw_glow_text(img, text, x, y, font, color, glow_radius=12, glow_alpha=120):
    """Render text with soft glow halo."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, fill=(*color[:3], glow_alpha), font=font)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, fill=(*color, 255), font=font)
    return img


def draw_gradient_orb(img, cx, cy, radius, color, alpha=40):
    """Soft radial gradient for ambient depth."""
    orb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    for i in range(20, 0, -1):
        r = int(radius * i / 20)
        a = int(alpha * (1 - i / 20))
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color[:3], a))
    return Image.alpha_composite(img.convert("RGBA"), orb)


def apply_vignette(img, strength=100):
    """Darken edges for focus."""
    vig = Image.new("RGBA", img.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    w, h = img.size
    for i in range(strength):
        alpha = int((strength - i) * 2.0)
        margin = i * max(w, h) // (strength * 2)
        vd.rectangle([0, 0, w, margin], fill=(0, 0, 0, alpha))
        vd.rectangle([0, h - margin, w, h], fill=(0, 0, 0, alpha))
        vd.rectangle([0, 0, margin, h], fill=(0, 0, 0, alpha))
        vd.rectangle([w - margin, 0, w, h], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), vig)


def draw_accent_line(img, x, y, width=260, thickness=3, color=NEON_BLUE):
    """Horizontal accent line with glow."""
    line = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    # Glow
    ld.rectangle([x - 4, y - 3, x + width + 4, y + thickness + 3], fill=(*color[:3], 50))
    # Core
    ld.rectangle([x, y, x + width, y + thickness], fill=(*color, 220))
    return Image.alpha_composite(img.convert("RGBA"), line)


def draw_scan_lines(img, spacing=6, alpha=12):
    """Subtle horizontal scan lines for digital feel."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, img.size[1], spacing):
        od.rectangle([0, y, img.size[0], y + 1], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_grid_pattern(img, spacing=80, color=NEON_BLUE, alpha=8):
    """Faint blockchain grid overlay."""
    grid = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    w, h = img.size
    for x in range(0, w, spacing):
        gd.line([(x, 0), (x, h)], fill=(*color[:3], alpha), width=1)
    for y in range(0, h, spacing):
        gd.line([(0, y), (w, y)], fill=(*color[:3], alpha), width=1)
    return Image.alpha_composite(img.convert("RGBA"), grid)


def draw_data_particles(img, count=40, color=NEON_BLUE, seed=42):
    """Scatter faint data point particles."""
    random.seed(seed)
    particles = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(particles)
    w, h = img.size
    for _ in range(count):
        px = random.randint(0, w)
        py = random.randint(0, h)
        size = random.randint(1, 3)
        a = random.randint(20, 60)
        c = random.choice([NEON_BLUE, SAFE_GREEN, (100, 140, 200)])
        pd.ellipse([px, py, px + size, py + size], fill=(*c[:3], a))
    return Image.alpha_composite(img.convert("RGBA"), particles)


# ── Word-level highlight rendering ──────────────────────────────────────

def draw_headline_highlighted(img, text_parts, x, y, font, default_color=WHITE, glow_radius=10):
    """
    Render headline with per-word color highlights.
    text_parts: list of (word, color, do_glow) tuples
    """
    cursor_x = x
    for word, color, do_glow in text_parts:
        if do_glow:
            img = draw_glow_text(img, word, cursor_x, y, font, color, glow_radius=glow_radius, glow_alpha=100)
        else:
            draw = ImageDraw.Draw(img)
            draw.text((cursor_x, y), word, fill=(*color, 255), font=font)
        bbox = font.getbbox(word)
        word_w = bbox[2] - bbox[0]
        cursor_x += word_w
    return img


# ── Main Compositing ───────────────────────────────────────────────────

def composite_banner(bg_path):
    """Build the final banner."""
    print("Compositing banner...")

    # Load background
    bg = Image.open(bg_path).convert("RGBA").resize((W, H), Image.LANCZOS)

    # Darken background with gradient overlay (darker on left for text readability)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(W):
        # Left side darker (alpha ~170), right side lighter (alpha ~90)
        progress = x / W
        alpha = int(175 - progress * 85)
        od.line([(x, 0), (x, H)], fill=(8, 12, 28, alpha))
    bg = Image.alpha_composite(bg, overlay)

    # Apply vignette
    bg = apply_vignette(bg, strength=80)

    # Add subtle grid pattern
    bg = draw_grid_pattern(bg, spacing=60, alpha=6)

    # Add scan lines for digital texture
    bg = draw_scan_lines(bg, spacing=4, alpha=8)

    # Add gradient orbs for depth
    bg = draw_gradient_orb(bg, cx=300, cy=280, radius=350, color=NEON_BLUE, alpha=18)
    bg = draw_gradient_orb(bg, cx=1100, cy=250, radius=300, color=SAFE_GREEN, alpha=10)
    bg = draw_gradient_orb(bg, cx=900, cy=400, radius=200, color=RISK_RED, alpha=8)

    # Add data particles
    bg = draw_data_particles(bg, count=50)

    # ── Typography ──────────────────────────────────────────────────

    # Load fonts
    font_headline = ImageFont.truetype(FONT_BOLD, 52)
    font_sub = ImageFont.truetype(FONT_REG, 26)
    font_brand = ImageFont.truetype(FONT_SEGOE_BOLD, 18)
    font_hidden = ImageFont.truetype(FONT_REG, 13)
    font_tag = ImageFont.truetype(FONT_SEGOE_BOLD, 15)

    # Text positioning (left-heavy, center-left)
    text_x = 90
    headline_y = 175

    # ── Headline: "The SEC just told you which tokens are safe." ──
    # Highlight "SEC" in neon blue, "safe" in green
    headline_parts = [
        ('"The ', WHITE, False),
        ('SEC', NEON_BLUE, True),
        (' just told you', WHITE, False),
    ]
    bg = draw_headline_highlighted(bg, headline_parts, text_x, headline_y, font_headline, glow_radius=12)

    # Second line of headline
    headline2_parts = [
        ('which tokens are ', WHITE, False),
        ('safe', SAFE_GREEN, True),
        ('."', WHITE, False),
    ]
    bg = draw_headline_highlighted(bg, headline2_parts, text_x, headline_y + 68, font_headline, glow_radius=10)

    # ── Accent line ──
    bg = draw_accent_line(bg, text_x, headline_y + 155, width=300, thickness=2, color=NEON_BLUE)

    # ── Subheadline ──
    sub_y = headline_y + 175
    bg = draw_glow_text(bg, "Most people missed the real signal.", text_x, sub_y, font_sub, DIMMED, glow_radius=6, glow_alpha=40)

    # ── Small tag: intel feel ──
    tag_y = headline_y - 50
    # Draw a subtle tag/badge
    tag_text = "CLASSIFIED  //  MARKET INTELLIGENCE"
    tag = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    tag_bbox = font_tag.getbbox(tag_text)
    tag_w = tag_bbox[2] - tag_bbox[0]
    # Subtle background pill
    td.rounded_rectangle([text_x - 8, tag_y - 4, text_x + tag_w + 12, tag_y + 20], radius=4, fill=(0, 180, 255, 25))
    td.text((text_x, tag_y), tag_text, fill=(*NEON_BLUE[:3], 140), font=font_tag)
    bg = Image.alpha_composite(bg, tag)

    # ── Brand watermark bottom-left ──
    brand_y = H - 45
    draw = ImageDraw.Draw(bg)
    draw.text((text_x, brand_y), "@big_quiv", fill=(*DIMMED[:3], 120), font=font_brand)

    # ── Hidden question (easter egg, bottom-right, very faint) ──
    hidden_x = W - 250
    hidden_y = H - 30
    draw.text((hidden_x, hidden_y), "Did you notice?", fill=(*DIMMED[:3], 35), font=font_hidden)

    # ── Right side: faint token indicator dots (safe vs ignored) ──
    # Represent "safe" tokens as green-glowing dots, "risk" as fading red
    right_x_start = 950
    dot_y_base = 200

    token_dots = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(token_dots)

    # Safe tokens (brighter, green glow)
    safe_positions = [(980, 180), (1080, 230), (1150, 160), (1250, 280), (1050, 340)]
    for sx, sy in safe_positions:
        # Outer glow
        for r in range(18, 0, -2):
            a = int(25 * (1 - r / 18))
            dd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(*SAFE_GREEN[:3], a))
        # Core dot
        dd.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(*SAFE_GREEN[:3], 160))

    # Risk/ignored tokens (dimmer, red, fading)
    risk_positions = [(1320, 200), (1380, 350), (1200, 400), (1050, 420), (1350, 140)]
    for rx, ry in risk_positions:
        for r in range(12, 0, -2):
            a = int(15 * (1 - r / 12))
            dd.ellipse([rx - r, ry - r, rx + r, ry + r], fill=(*RISK_RED[:3], a))
        dd.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=(*RISK_RED[:3], 60))

    # Neutral/unknown tokens (blue, very faint)
    neutral_positions = [(1300, 260), (1100, 120), (960, 350), (1400, 430)]
    for nx, ny in neutral_positions:
        for r in range(10, 0, -2):
            a = int(10 * (1 - r / 10))
            dd.ellipse([nx - r, ny - r, nx + r, ny + r], fill=(*NEON_BLUE[:3], a))
        dd.ellipse([nx - 2, ny - 2, nx + 2, ny + 2], fill=(*NEON_BLUE[:3], 45))

    bg = Image.alpha_composite(bg, token_dots)

    # ── Faint connecting lines between token dots (data stream feel) ──
    connections = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(connections)
    # Connect some safe tokens
    pairs = [(safe_positions[0], safe_positions[1]),
             (safe_positions[1], safe_positions[3]),
             (safe_positions[2], safe_positions[4]),
             (safe_positions[3], safe_positions[4])]
    for (x1, y1), (x2, y2) in pairs:
        cd.line([(x1, y1), (x2, y2)], fill=(*SAFE_GREEN[:3], 18), width=1)
    # Connect some risk tokens (even fainter)
    risk_pairs = [(risk_positions[0], risk_positions[1]),
                  (risk_positions[2], risk_positions[3])]
    for (x1, y1), (x2, y2) in risk_pairs:
        cd.line([(x1, y1), (x2, y2)], fill=(*RISK_RED[:3], 10), width=1)
    bg = Image.alpha_composite(bg, connections)

    # ── Final export ────────────────────────────────────────────────
    output_path = os.path.join(OUT_DIR, "sec-banner.png")
    bg.save(output_path, "PNG", quality=95)
    print(f"Banner saved: {output_path}")
    return output_path


# ── Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bg_path = os.path.join(BG_DIR, "bg_sec_banner.png")

    # Generate background if not exists
    if not os.path.exists(bg_path):
        bg_path = generate_background()
    else:
        print(f"Using existing background: {bg_path}")

    # Composite final banner
    output = composite_banner(bg_path)
    print(f"\nDone! Final banner: {output}")
