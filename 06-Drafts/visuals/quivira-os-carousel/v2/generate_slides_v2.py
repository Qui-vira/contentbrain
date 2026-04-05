"""
Quivira OS Carousel — V2 Premium Design
Graphic Designer skill | @big_quiv brand system
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

output_dir = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - MARGIN * 2
TOP_SAFE = 120
BOTTOM_SAFE = 80

# ── Brand Colors ──
BG = (10, 10, 15)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
RED = (230, 57, 70)
GOLD = (255, 215, 0)
DARK_PANEL = (26, 26, 46)
GRAY = (150, 150, 150)
DIMMED = (180, 180, 180)

# ── Fonts ──
def get_font(size, bold=True):
    if bold:
        for p in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    else:
        for p in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()

font_hero     = get_font(76, True)
font_headline = get_font(54, True)
font_subhead  = get_font(40, True)
font_body     = get_font(30, False)
font_body_b   = get_font(30, True)
font_small    = get_font(24, False)
font_tag      = get_font(22, True)
font_cta      = get_font(46, True)
font_big2     = get_font(62, True)
font_big3     = get_font(50, True)
font_token    = get_font(28, True)
font_check    = get_font(36, True)
font_stat     = get_font(44, True)


# ══════════════════════════════════════════════
#  DESIGN SYSTEM FUNCTIONS
# ══════════════════════════════════════════════

def load_bg(filename, overlay_alpha=140):
    """Load AI background with dark overlay. Lower alpha = more art visible."""
    path = os.path.join(output_dir, filename)
    if os.path.exists(path):
        img = Image.open(path).resize((W, H)).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (10, 10, 15, overlay_alpha))
        img = Image.alpha_composite(img, overlay)
        return img
    else:
        img = Image.new("RGBA", (W, H), (*BG, 255))
        draw = ImageDraw.Draw(img)
        for y in range(H):
            r = int(10 + (16 * y / H))
            g = int(10 + (16 * y / H))
            b = int(15 + (31 * y / H))
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        return img


def apply_vignette(img, strength=60):
    """Darken edges to draw focus to the center."""
    w, h = img.size
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    steps = strength
    for i in range(steps):
        alpha = int((steps - i) * 3)
        m = i * max(w, h) // (steps * 2)
        if m < 1:
            m = 1
        vd.rectangle([0, 0, w, m], fill=(0, 0, 0, min(alpha, 255)))
        vd.rectangle([0, h - m, w, h], fill=(0, 0, 0, min(alpha, 255)))
        vd.rectangle([0, 0, m, h], fill=(0, 0, 0, min(alpha, 255)))
        vd.rectangle([w - m, 0, w, h], fill=(0, 0, 0, min(alpha, 255)))
    return Image.alpha_composite(img, vig)


def draw_gradient_orb(img, cx, cy, radius, color, alpha=45):
    """Soft radial gradient circle for ambient depth."""
    orb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    steps = 25
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i / steps))
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color[:3], min(a, 255)))
    return Image.alpha_composite(img, orb)


def draw_glow_text(img, text, x, y, font, color, glow_radius=12, glow_alpha=140):
    """Text with a soft glow halo behind it."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, fill=(*color[:3], glow_alpha), font=font)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, fill=(*color, 255), font=font)
    return img


def _wrap_lines(draw, text, font, max_width):
    """Word-wrap text into lines that fit max_width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def glow_text_centered(img, text, y, font, color, glow_radius=12, glow_alpha=140, max_width=None):
    """Center-aligned text with glow. Returns (img, new_y)."""
    if max_width is None:
        max_width = TEXT_W
    draw = ImageDraw.Draw(img)
    lines = _wrap_lines(draw, text, font, max_width)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        img = draw_glow_text(img, line, x, y, font, color, glow_radius, glow_alpha)
        y += int((bbox[3] - bbox[1]) * 1.3)
    return img, y


def flat_text_centered(img, text, y, font, color=WHITE, max_width=None):
    """Center-aligned text, no glow. Returns (img, new_y)."""
    if max_width is None:
        max_width = TEXT_W
    draw = ImageDraw.Draw(img)
    lines = _wrap_lines(draw, text, font, max_width)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += int((bbox[3] - bbox[1]) * 1.4)
    return img, y


def flat_text_left(img, text, y, font, color=LIGHT, max_width=None):
    """Left-aligned body text, no glow. Returns (img, new_y)."""
    if max_width is None:
        max_width = TEXT_W
    draw = ImageDraw.Draw(img)
    lines = _wrap_lines(draw, text, font, max_width)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text((MARGIN, y), line, fill=color, font=font)
        y += int((bbox[3] - bbox[1]) * 1.45)
    return img, y


def draw_accent_line(img, y, width=220):
    """Red accent separator with subtle glow."""
    x_start = (W - width) // 2
    line = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    ld.rectangle([x_start - 8, y - 5, x_start + width + 8, y + 8], fill=(230, 57, 70, 50))
    ld.rectangle([x_start, y, x_start + width, y + 3], fill=(230, 57, 70, 255))
    return Image.alpha_composite(img, line)


def draw_glass_panel(img, x1, y1, x2, y2, border_color=GOLD, fill_alpha=160):
    """Semi-transparent glass panel with colored border."""
    panel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=(26, 26, 46, fill_alpha))
    pd.rounded_rectangle([x1, y1, x2, y2], radius=16, outline=(*border_color[:3], 120), width=2)
    return Image.alpha_composite(img, panel)


def add_branding(img):
    """Bottom-left @big_quiv + red dot."""
    draw = ImageDraw.Draw(img)
    draw.text((MARGIN, H - 60), "@big_quiv", fill=(*GRAY, 255), font=font_small)
    draw.ellipse([W - MARGIN - 12, H - 52, W - MARGIN, H - 40], fill=(*RED, 255))
    return img


def add_counter(img, current, total=6):
    """Slide counter top-right."""
    draw = ImageDraw.Draw(img)
    text = f"{current}/{total}"
    bbox = draw.textbbox((0, 0), text, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 45), text, fill=(*GRAY, 200), font=font_tag)
    return img


def finalize(img):
    """Convert RGBA to RGB for PNG save."""
    bg = Image.new("RGB", img.size, BG)
    bg.paste(img, mask=img.split()[3])
    return bg


# ══════════════════════════════════════════════
#  SLIDE 1: COVER
# ══════════════════════════════════════════════
print("Slide 1 — Cover")
img = load_bg("bg1_cover.png", overlay_alpha=110)
img = apply_vignette(img, strength=50)
img = draw_gradient_orb(img, W // 2, 420, 380, RED, alpha=35)
img = draw_gradient_orb(img, W // 2, 500, 250, GOLD, alpha=20)

y = 280
img, y = glow_text_centered(img, "I WAS WORKING", y, font_headline, WHITE, glow_radius=8, glow_alpha=100)
y += 10
img, y = glow_text_centered(img, "40 HOURS", y, font_hero, RED, glow_radius=18, glow_alpha=160)
y += 5
img, y = glow_text_centered(img, "A WEEK.", y, font_headline, WHITE, glow_radius=8, glow_alpha=100)
y += 30
img = draw_accent_line(img, y, 300)
y += 50
img, y = glow_text_centered(img, "NOW I WORK 3.", y, font_big3, GOLD, glow_radius=14, glow_alpha=140)
y += 30
img, y = flat_text_centered(img, "Here's the system.", y, font_subhead, DIMMED)

img = add_branding(img)
img, _ = flat_text_centered(img, "SWIPE  >", H - 120, font_tag, GRAY)

img = finalize(img)
img.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("  -> slide-01.png")


# ══════════════════════════════════════════════
#  SLIDE 2: THE PROBLEM
# ══════════════════════════════════════════════
print("Slide 2 — The Problem")
img = load_bg("bg2_problem.png", overlay_alpha=155)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 350, 300, RED, alpha=25)

img, y = glow_text_centered(img, "THE PROBLEM", 220, font_headline, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

# X items
draw = ImageDraw.Draw(img)
pain_points = [
    "Manually charting 50 pairs",
    "Writing content from scratch",
    "Managing 4 platforms",
    "Answering the same questions daily",
]
for p in pain_points:
    draw.text((MARGIN, y), "X", fill=(*RED, 255), font=font_body_b)
    draw.text((MARGIN + 40, y), p, fill=(*LIGHT, 255), font=font_body)
    y += 50

y += 25
# Glass panel with RED border
img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 120, border_color=RED, fill_alpha=170)
img, _ = flat_text_centered(img, "40 hours a week.", y + 22, font_subhead, RED)
img, _ = flat_text_centered(img, "Burning out while looking productive.", y + 72, font_body, DIMMED)

img = add_branding(img)
img = add_counter(img, 2)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("  -> slide-02.png")


# ══════════════════════════════════════════════
#  SLIDE 3: THE BREAKING POINT
# ══════════════════════════════════════════════
print("Slide 3 — Breaking Point")
img = load_bg("bg3_breaking.png", overlay_alpha=145)
img = apply_vignette(img, strength=50)
img = draw_gradient_orb(img, W // 2, 400, 300, RED, alpha=25)

img, y = glow_text_centered(img, "THE BREAKING", 240, font_headline, WHITE, glow_radius=8, glow_alpha=100)
y += 5
img, y = glow_text_centered(img, "POINT", y, font_headline, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

img, y = flat_text_left(img, "I realized I wasn't building a brand.", y, font_body_b, WHITE)
y += 20
img, y = flat_text_left(img, "I was running on a treadmill.", y, font_body, RED)
y += 30
img, y = flat_text_left(img, "Doing the same tasks every week.", y, font_body, LIGHT)
y += 8
img, y = flat_text_left(img, "No leverage. No compounding.", y, font_body, LIGHT)
y += 30
img, y = glow_text_centered(img, "Just effort.", y, font_subhead, RED, glow_radius=10, glow_alpha=120)

img = add_branding(img)
img = add_counter(img, 3)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("  -> slide-03.png")


# ══════════════════════════════════════════════
#  SLIDE 4: THE SYSTEM
# ══════════════════════════════════════════════
print("Slide 4 — The System")
img = load_bg("bg4_system.png", overlay_alpha=155)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 500, 400, GOLD, alpha=20)

img, y = glow_text_centered(img, "THE SYSTEM", 180, font_headline, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 50

img, y = flat_text_centered(img, "Quivira OS replaces the grind with 3 layers.", y, font_body, LIGHT)
y += 30

BLUE = (100, 200, 255)
layers = [
    ("LAYER 1", "AI Signal Scanner", "Scans 50 pairs every 4 hours. Filters for confluence. Sends approval alerts.", RED),
    ("LAYER 2", "Content Engine", "Scouts trends, pulls data, builds weekly plans.", GOLD),
    ("LAYER 3", "Distribution", "Approved signals and content push to Telegram, X, IG, LinkedIn automatically.", BLUE),
]

for label, title, desc, color in layers:
    # Glass panel with colored border
    img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 150, border_color=color, fill_alpha=170)
    draw = ImageDraw.Draw(img)

    # Layer badge
    badge_w = 130
    badge_h = 32
    bx = MARGIN + 18
    by_ = y + 14
    draw.rounded_rectangle([bx, by_, bx + badge_w, by_ + badge_h], radius=8, fill=(*color, 255))
    bbox = draw.textbbox((0, 0), label, font=font_tag)
    tw = bbox[2] - bbox[0]
    label_color = WHITE if color != GOLD else BG
    draw.text((bx + (badge_w - tw) // 2, by_ + 5), label, fill=(*label_color, 255), font=font_tag)

    # Title
    draw.text((MARGIN + 160, y + 16), title, fill=(*WHITE, 255), font=font_body_b)

    # Description with wrapping
    desc_words = desc.split()
    desc_lines = []
    cur = ""
    for w in desc_words:
        test = cur + " " + w if cur else w
        bbox2 = draw.textbbox((0, 0), test, font=font_small)
        if bbox2[2] - bbox2[0] > TEXT_W - 50:
            if cur:
                desc_lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        desc_lines.append(cur)
    dy = y + 58
    for dl in desc_lines:
        draw.text((MARGIN + 28, dy), dl, fill=(*DIMMED, 255), font=font_small)
        dy += 30

    y += 162

img = add_branding(img)
img = add_counter(img, 4)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("  -> slide-04.png")


# ══════════════════════════════════════════════
#  SLIDE 5: THE RESULT
# ══════════════════════════════════════════════
print("Slide 5 — The Result")
img = load_bg("bg5_result.png", overlay_alpha=130)
img = apply_vignette(img, strength=50)
img = draw_gradient_orb(img, W // 2, 550, 350, GOLD, alpha=30)

img, y = glow_text_centered(img, "THE RESULT", 220, font_headline, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

stats = [
    ("30 HOURS", "saved per week"),
    ("DAILY SIGNALS", "without me charting"),
    ("45 MINUTES", "to build content calendar"),
]
for big, small in stats:
    img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 110, border_color=GOLD, fill_alpha=170)
    img, _ = glow_text_centered(img, big, y + 18, font_stat, GOLD, glow_radius=12, glow_alpha=130)
    img, _ = flat_text_centered(img, small, y + 70, font_small, DIMMED)
    y += 130

y += 20
img, _ = flat_text_left(img, "More time for strategy, community, and product building.", y, font_body_b, WHITE)

img = add_branding(img)
img = add_counter(img, 5)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("  -> slide-05.png")


# ══════════════════════════════════════════════
#  SLIDE 6: CTA
# ══════════════════════════════════════════════
print("Slide 6 — CTA")
img = load_bg("bg6_cta.png", overlay_alpha=105)
img = apply_vignette(img, strength=55)
img = draw_gradient_orb(img, W // 2, 520, 400, RED, alpha=30)

img, y = glow_text_centered(img, "WANT THE FULL", 350, font_subhead, WHITE, glow_radius=8, glow_alpha=100)
y += 15
img, y = glow_text_centered(img, "BREAKDOWN?", y, font_big2, RED, glow_radius=18, glow_alpha=160)
y += 45
img = draw_accent_line(img, y, 400)
y += 65

# CTA button with drop shadow
btn_w = 680
btn_h = 95
btn_x = (W - btn_w) // 2
draw = ImageDraw.Draw(img)
# Shadow
draw.rounded_rectangle([btn_x + 5, y + 5, btn_x + btn_w + 5, y + btn_h + 5], radius=18, fill=(80, 15, 20, 200))
# Button
draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h], radius=18, fill=(*RED, 255))
# Button text
bbox = draw.textbbox((0, 0), "COMMENT  OS", font=font_cta)
tw = bbox[2] - bbox[0]
tx = (W - tw) // 2
draw.text((tx, y + 22), "COMMENT  OS", fill=(*WHITE, 255), font=font_cta)

y += btn_h + 45
img, y = flat_text_centered(img, "and I'll send you the full", y, font_body, DIMMED)
y += 5
img, _ = flat_text_centered(img, "breakdown of how Quivira OS works.", y, font_body, DIMMED)

img = add_branding(img)
img = add_counter(img, 6)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-06.png"), quality=95)
print("  -> slide-06.png")


print("\nALL 6 PREMIUM V2 SLIDES GENERATED.")
