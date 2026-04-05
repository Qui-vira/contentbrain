"""
Generate visual assets for "AI Scans 50 Crypto Pairs" Instagram Reel.
Brand: Quivira (@big_quiv)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

# Brand colors
DEEP_BLACK = (10, 10, 15)
QUIVIRA_RED = (230, 57, 70)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DIMMED = (180, 180, 180)
DARK_PANEL = (26, 26, 46)
PANEL_BORDER = (40, 40, 70)

# Fonts
FONT_HERO = "C:/Windows/Fonts/impact.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def apply_vignette(img, intensity=0.6):
    """Darken edges of image."""
    vig = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)
    cx, cy = img.size[0] // 2, img.size[1] // 2
    max_r = max(cx, cy) * 1.2
    steps = 40
    for i in range(steps):
        r = max_r * (1 - i / steps)
        alpha = int(255 * intensity * (1 - i / steps) ** 0.5)
        x0, y0 = cx - r, cy - r
        x1, y1 = cx + r, cy + r
        draw.ellipse([x0, y0, x1, y1], fill=(0, 0, 0, alpha))
    # Invert: we want edges dark, center clear
    # Actually build it differently - darken from edges
    vig2 = Image.new("RGBA", img.size, (0, 0, 0, int(255 * intensity)))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    # Radial gradient mask - white center, black edges
    for i in range(steps):
        r = max_r * (i / steps)
        brightness = int(255 * (1 - (i / steps) ** 1.5))
        md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=brightness)
    vig2.putalpha(ImageEnhance_invert_mask(mask))
    result = img.copy().convert("RGBA")
    result = Image.alpha_composite(result, vig2)
    return result


def simple_vignette(img, strength=120):
    """Simple vignette using overlay."""
    result = img.convert("RGBA")
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = result.size
    # Draw concentric rectangles with increasing opacity at edges
    border = 200
    for i in range(border):
        alpha = int(strength * (1 - i / border) ** 2)
        draw.rectangle([i, i, w - i, h - i], outline=(0, 0, 0, alpha))
    result = Image.alpha_composite(result, overlay)
    return result


def draw_gradient_orb(img, cx, cy, radius, color, alpha_max=80):
    """Draw a soft radial gradient orb for ambient depth."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    steps = 50
    for i in range(steps):
        r = radius * (1 - i / steps)
        a = int(alpha_max * (i / steps) ** 0.5)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    return Image.alpha_composite(img, overlay)


def draw_glass_panel(img, bbox, bg_alpha=140, border_alpha=60):
    """Draw a semi-transparent glass panel."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = bbox
    # Panel fill
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16,
                           fill=(*DARK_PANEL, bg_alpha))
    # Border
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16,
                           outline=(*PANEL_BORDER, border_alpha), width=2)
    return Image.alpha_composite(img, overlay)


def draw_glow_text(img, text, position, font, color, glow_radius=14, glow_color=None):
    """Render text with Gaussian blur glow behind crisp text."""
    if glow_color is None:
        glow_color = color

    # Create glow layer
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text(position, text, font=font, fill=(*glow_color, 180))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=glow_radius))

    # Composite glow
    result = Image.alpha_composite(img, glow)

    # Draw crisp text on top
    draw = ImageDraw.Draw(result)
    draw.text(position, text, font=font, fill=(*color, 255))
    return result


def draw_drop_shadow(img, bbox, offset=(6, 6), blur=12, shadow_alpha=160):
    """Drop shadow behind a rectangle region."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = bbox
    sd.rounded_rectangle([x0 + offset[0], y0 + offset[1],
                          x1 + offset[0], y1 + offset[1]],
                         radius=16, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    return Image.alpha_composite(img, shadow)


def draw_dark_overlay(img, alpha=140):
    """Dark overlay on background."""
    overlay = Image.new("RGBA", img.size, (*DEEP_BLACK, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def get_text_bbox(draw, text, font):
    """Get text bounding box dimensions."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def center_x(draw, text, font, canvas_width):
    """Get x position to center text."""
    tw, _ = get_text_bbox(draw, text, font)
    return (canvas_width - tw) // 2


# ============================================================
# ASSET 1: COVER / THUMBNAIL FRAME
# ============================================================
def make_cover():
    bg = Image.open(os.path.join(OUT, "bg_cover_0.png")).convert("RGBA")
    bg = bg.resize((W, H), Image.LANCZOS)

    # Dark overlay (50-55% per framework for cover)
    img = draw_dark_overlay(bg, alpha=140)

    # Vignette
    img = simple_vignette(img, strength=150)

    # Gradient orbs for depth
    img = draw_gradient_orb(img, 200, 600, 400, QUIVIRA_RED, alpha_max=40)
    img = draw_gradient_orb(img, 900, 1400, 350, GOLD, alpha_max=25)

    # Fonts
    hero_font = load_font(FONT_HERO, 80)
    headline_font = load_font(FONT_BOLD, 56)
    body_font = load_font(FONT_REG, 28)
    brand_font = load_font(FONT_BOLD, 24)

    draw = ImageDraw.Draw(img)

    # --- Top area: "AI SCANNER" badge ---
    badge_font = load_font(FONT_BOLD, 22)
    badge_text = "AI SCANNER"
    btw, bth = get_text_bbox(draw, badge_text, badge_font)
    badge_x = (W - btw - 40) // 2
    badge_y = 280
    # Badge background
    img = draw_glass_panel(img, (badge_x, badge_y, badge_x + btw + 40, badge_y + bth + 16),
                           bg_alpha=180, border_alpha=100)
    draw = ImageDraw.Draw(img)
    draw.text((badge_x + 20, badge_y + 8), badge_text, font=badge_font, fill=QUIVIRA_RED)

    # --- Main headline: "50 PAIRS." ---
    y_start = 420
    line1 = "50 PAIRS."
    line2 = "10 MINUTES."
    line3 = "3 SETUPS."

    # Glass panel behind all headline text
    panel_top = y_start - 30
    panel_bottom = y_start + 340
    img = draw_glass_panel(img, (60, panel_top, W - 60, panel_bottom),
                           bg_alpha=100, border_alpha=40)
    draw = ImageDraw.Draw(img)

    # Line 1 - GOLD numbers
    x1 = center_x(draw, line1, hero_font, W)
    # Draw "50" in gold, "PAIRS." in white
    img = draw_glow_text(img, "50", (x1, y_start), hero_font, GOLD, glow_radius=16, glow_color=GOLD)
    draw = ImageDraw.Draw(img)
    w50, _ = get_text_bbox(draw, "50", hero_font)
    # " PAIRS." in white
    img = draw_glow_text(img, " PAIRS.", (x1 + w50, y_start), hero_font, WHITE, glow_radius=10)
    draw = ImageDraw.Draw(img)

    # Line 2
    y2 = y_start + 110
    x2 = center_x(draw, line2, hero_font, W)
    img = draw_glow_text(img, "10", (x2, y2), hero_font, GOLD, glow_radius=16, glow_color=GOLD)
    draw = ImageDraw.Draw(img)
    w10, _ = get_text_bbox(draw, "10", hero_font)
    img = draw_glow_text(img, " MINUTES.", (x2 + w10, y2), hero_font, WHITE, glow_radius=10)
    draw = ImageDraw.Draw(img)

    # Line 3
    y3 = y_start + 220
    x3 = center_x(draw, line3, hero_font, W)
    img = draw_glow_text(img, "3", (x3, y3), hero_font, GOLD, glow_radius=16, glow_color=GOLD)
    draw = ImageDraw.Draw(img)
    w3, _ = get_text_bbox(draw, "3", hero_font)
    img = draw_glow_text(img, " SETUPS.", (x3 + w3, y3), hero_font, WHITE, glow_radius=10)
    draw = ImageDraw.Draw(img)

    # --- Red accent line ---
    accent_y = y_start + 330
    draw.line([(W // 2 - 150, accent_y), (W // 2 + 150, accent_y)],
              fill=(*QUIVIRA_RED, 200), width=3)

    # --- Subtitle ---
    sub_font = load_font(FONT_BOLD, 32)
    sub_text = "While You Sleep"
    xs = center_x(draw, sub_text, sub_font, W)
    draw.text((xs, accent_y + 25), sub_text, font=sub_font, fill=DIMMED)

    # --- Branding bottom-left ---
    draw.text((80, H - 100), "@big_quiv", font=brand_font, fill=(*DIMMED, 180))

    # Save
    out_path = os.path.join(OUT, "01_cover_frame.png")
    img.convert("RGB").save(out_path, quality=95)
    print(f"Saved: {out_path}")
    return out_path


# ============================================================
# ASSET 2-7: TEXT OVERLAY GRAPHICS (transparent PNG)
# ============================================================
def make_overlay(filename, lines, style="default"):
    """
    Create a text overlay on transparent/dark background.
    lines: list of (text, font_path, size, color, glow)
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Semi-dark background for context
    bg = Image.new("RGBA", (W, H), (*DEEP_BLACK, 220))
    img = Image.alpha_composite(img, bg)

    # Vignette
    img = simple_vignette(img, strength=100)

    # Gradient orb
    img = draw_gradient_orb(img, 540, 960, 500, QUIVIRA_RED, alpha_max=30)

    draw = ImageDraw.Draw(img)

    total_height = 0
    rendered_lines = []
    for text, font_path, size, color, glow in lines:
        font = load_font(font_path, size)
        tw, th = get_text_bbox(draw, text, font)
        rendered_lines.append((text, font, tw, th, color, glow))
        total_height += th + 20

    y = (H - total_height) // 2

    for text, font, tw, th, color, glow in rendered_lines:
        x = (W - tw) // 2
        if glow:
            img = draw_glow_text(img, text, (x, y), font, color, glow_radius=12)
            draw = ImageDraw.Draw(img)
        else:
            draw.text((x, y), text, font=font, fill=color)
        y += th + 20

    # Branding
    brand_font = load_font(FONT_BOLD, 24)
    draw.text((80, H - 100), "@big_quiv", font=brand_font, fill=(*DIMMED, 180))

    out_path = os.path.join(OUT, filename)
    img.convert("RGB").save(out_path, quality=95)
    print(f"Saved: {out_path}")
    return out_path


def make_hook_overlay():
    """AI scans 50 pairs while you sleep"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg = Image.new("RGBA", (W, H), (*DEEP_BLACK, 230))
    img = Image.alpha_composite(img, bg)
    img = simple_vignette(img, strength=100)
    img = draw_gradient_orb(img, 300, 800, 400, QUIVIRA_RED, alpha_max=35)
    img = draw_gradient_orb(img, 800, 1100, 300, GOLD, alpha_max=20)

    draw = ImageDraw.Draw(img)

    # Glass panel
    img = draw_glass_panel(img, (80, 780, W - 80, 1140), bg_alpha=120, border_alpha=50)
    draw = ImageDraw.Draw(img)

    hero = load_font(FONT_HERO, 72)
    sub = load_font(FONT_BOLD, 40)

    # "AI SCANS" in red
    t1 = "AI SCANS"
    x1 = center_x(draw, t1, hero, W)
    img = draw_glow_text(img, t1, (x1, 820), hero, QUIVIRA_RED, glow_radius=14)
    draw = ImageDraw.Draw(img)

    # "50 PAIRS" in gold
    t2 = "50 PAIRS"
    x2 = center_x(draw, t2, hero, W)
    img = draw_glow_text(img, t2, (x2, 910), hero, GOLD, glow_radius=14, glow_color=GOLD)
    draw = ImageDraw.Draw(img)

    # "while you sleep" in dimmed
    t3 = "while you sleep"
    x3 = center_x(draw, t3, sub, W)
    draw.text((x3, 1020), t3, font=sub, fill=DIMMED)

    # Accent line
    draw.line([(W // 2 - 120, 1080), (W // 2 + 120, 1080)], fill=QUIVIRA_RED, width=3)

    brand = load_font(FONT_BOLD, 24)
    draw.text((80, H - 100), "@big_quiv", font=brand, fill=(*DIMMED, 180))

    out_path = os.path.join(OUT, "02_hook_overlay.png")
    img.convert("RGB").save(out_path, quality=95)
    print(f"Saved: {out_path}")


def make_indicator_overlays():
    """Individual indicator name overlays for rapid-fire sequence."""
    indicators = [
        ("RSI", QUIVIRA_RED),
        ("MACD", GOLD),
        ("VOLUME", WHITE),
        ("SUPPORT", (0, 200, 100)),
        ("RESISTANCE", QUIVIRA_RED),
    ]

    for idx, (name, color) in enumerate(indicators):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bg = Image.new("RGBA", (W, H), (*DEEP_BLACK, 240))
        img = Image.alpha_composite(img, bg)

        # Orb matching indicator color
        img = draw_gradient_orb(img, W // 2, H // 2, 500, color, alpha_max=40)

        draw = ImageDraw.Draw(img)
        hero = load_font(FONT_HERO, 96)

        # Center the indicator name
        tw, th = get_text_bbox(draw, name, hero)
        x = (W - tw) // 2
        y = (H - th) // 2 - 40

        # Glass panel behind
        pad = 60
        img = draw_glass_panel(img, (x - pad, y - pad // 2, x + tw + pad, y + th + pad // 2),
                               bg_alpha=100, border_alpha=60)
        draw = ImageDraw.Draw(img)

        # Glow text
        img = draw_glow_text(img, name, (x, y), hero, color, glow_radius=18, glow_color=color)
        draw = ImageDraw.Draw(img)

        # Scanning line effect
        scan_y = y + th + pad
        draw.line([(100, scan_y), (W - 100, scan_y)], fill=(*color, 120), width=2)

        # Small label
        label_font = load_font(FONT_REG, 26)
        label = "SCANNING..."
        lw, _ = get_text_bbox(draw, label, label_font)
        draw.text(((W - lw) // 2, scan_y + 15), label, font=label_font, fill=DIMMED)

        out_path = os.path.join(OUT, f"03_{chr(97 + idx)}_{name.lower()}_overlay.png")
        img.convert("RGB").save(out_path, quality=95)
        print(f"Saved: {out_path}")


def make_time_comparison():
    """4 hours -> 10 minutes split comparison."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg = Image.new("RGBA", (W, H), (*DEEP_BLACK, 230))
    img = Image.alpha_composite(img, bg)
    img = simple_vignette(img, strength=100)

    draw = ImageDraw.Draw(img)

    # Left side (old way) - red tint
    img = draw_gradient_orb(img, 270, H // 2, 400, QUIVIRA_RED, alpha_max=25)
    # Right side (new way) - gold tint
    img = draw_gradient_orb(img, 810, H // 2, 400, GOLD, alpha_max=25)

    # Divider line
    draw = ImageDraw.Draw(img)
    draw.line([(W // 2, H // 2 - 200), (W // 2, H // 2 + 200)],
              fill=(*DIMMED, 100), width=2)

    hero = load_font(FONT_HERO, 72)
    sub = load_font(FONT_BOLD, 32)
    label_font = load_font(FONT_REG, 26)

    # Left: "4 HOURS"
    # Glass panel
    img = draw_glass_panel(img, (60, H // 2 - 160, W // 2 - 30, H // 2 + 100),
                           bg_alpha=100, border_alpha=40)
    draw = ImageDraw.Draw(img)
    t_old = "4 HRS"
    tw, th = get_text_bbox(draw, t_old, hero)
    x_old = (W // 4 - tw // 2)
    draw.text((x_old, H // 2 - 120), t_old, font=hero, fill=QUIVIRA_RED)
    # Strikethrough
    draw.line([(x_old - 10, H // 2 - 120 + th // 2),
               (x_old + tw + 10, H // 2 - 120 + th // 2)],
              fill=QUIVIRA_RED, width=4)
    lbl = "MANUAL"
    lw, _ = get_text_bbox(draw, lbl, label_font)
    draw.text(((W // 4 - lw // 2), H // 2 + 20), lbl, font=label_font, fill=DIMMED)

    # Right: "10 MIN"
    img = draw_glass_panel(img, (W // 2 + 30, H // 2 - 160, W - 60, H // 2 + 100),
                           bg_alpha=100, border_alpha=40)
    draw = ImageDraw.Draw(img)
    t_new = "10 MIN"
    tw2, th2 = get_text_bbox(draw, t_new, hero)
    x_new = (3 * W // 4 - tw2 // 2)
    img = draw_glow_text(img, t_new, (x_new, H // 2 - 120), hero, GOLD,
                         glow_radius=14, glow_color=GOLD)
    draw = ImageDraw.Draw(img)
    lbl2 = "AI SCANNER"
    lw2, _ = get_text_bbox(draw, lbl2, label_font)
    draw.text(((3 * W // 4 - lw2 // 2), H // 2 + 20), lbl2, font=label_font, fill=GOLD)

    # Arrow
    arrow_font = load_font(FONT_HERO, 56)
    draw.text((W // 2 - 18, H // 2 - 100), ">", font=arrow_font, fill=WHITE)

    # Title above
    title = "TIME SAVED"
    title_font = load_font(FONT_BOLD, 36)
    tw_t, _ = get_text_bbox(draw, title, title_font)
    draw.text(((W - tw_t) // 2, H // 2 - 240), title, font=title_font, fill=WHITE)

    brand = load_font(FONT_BOLD, 24)
    draw.text((80, H - 100), "@big_quiv", font=brand, fill=(*DIMMED, 180))

    out_path = os.path.join(OUT, "04_time_comparison.png")
    img.convert("RGB").save(out_path, quality=95)
    print(f"Saved: {out_path}")


def make_cta():
    """Comment SIGNAL CTA slam."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg = Image.new("RGBA", (W, H), (*DEEP_BLACK, 240))
    img = Image.alpha_composite(img, bg)
    img = simple_vignette(img, strength=100)
    img = draw_gradient_orb(img, W // 2, H // 2 - 100, 500, QUIVIRA_RED, alpha_max=35)

    draw = ImageDraw.Draw(img)

    # "COMMENT" text
    hero = load_font(FONT_HERO, 64)
    keyword_font = load_font(FONT_HERO, 96)
    sub = load_font(FONT_BOLD, 32)

    t_comment = "COMMENT"
    tw_c, th_c = get_text_bbox(draw, t_comment, hero)
    xc = (W - tw_c) // 2
    yc = H // 2 - 180
    draw.text((xc, yc), t_comment, font=hero, fill=WHITE)

    # "SIGNAL" keyword - big, red, glowing, in a button
    t_kw = "SIGNAL"
    tw_k, th_k = get_text_bbox(draw, t_kw, keyword_font)
    xk = (W - tw_k) // 2
    yk = H // 2 - 60

    # Button background with drop shadow
    btn_pad_x, btn_pad_y = 60, 20
    btn_bbox = (xk - btn_pad_x, yk - btn_pad_y,
                xk + tw_k + btn_pad_x, yk + th_k + btn_pad_y)
    img = draw_drop_shadow(img, btn_bbox, offset=(8, 8), blur=16, shadow_alpha=180)
    draw = ImageDraw.Draw(img)

    # Red button fill
    draw.rounded_rectangle(btn_bbox, radius=16, fill=QUIVIRA_RED)
    # White text on button
    img = draw_glow_text(img, t_kw, (xk, yk), keyword_font, WHITE, glow_radius=8,
                         glow_color=WHITE)
    draw = ImageDraw.Draw(img)

    # Subtitle
    sub_text = "and I'll DM you the scanner"
    tw_s, _ = get_text_bbox(draw, sub_text, sub)
    xs = (W - tw_s) // 2
    draw.text((xs, yk + th_k + btn_pad_y + 40), sub_text, font=sub, fill=DIMMED)

    # Arrow pointing down
    arrow = load_font(FONT_HERO, 48)
    aw, _ = get_text_bbox(draw, "v", arrow)
    draw.text(((W - aw) // 2, yk + th_k + btn_pad_y + 100), "v", font=arrow, fill=QUIVIRA_RED)

    brand = load_font(FONT_BOLD, 24)
    draw.text((80, H - 100), "@big_quiv", font=brand, fill=(*DIMMED, 180))

    out_path = os.path.join(OUT, "05_cta_signal.png")
    img.convert("RGB").save(out_path, quality=95)
    print(f"Saved: {out_path}")


# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("=== Generating Cover Frame ===")
    make_cover()

    print("\n=== Generating Hook Overlay ===")
    make_hook_overlay()

    print("\n=== Generating Indicator Overlays ===")
    make_indicator_overlays()

    print("\n=== Generating Time Comparison ===")
    make_time_comparison()

    print("\n=== Generating CTA Overlay ===")
    make_cta()

    print("\n=== ALL ASSETS GENERATED ===")
