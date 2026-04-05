"""
5 Trading Mistakes Carousel — V2 Premium Design
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

# -- Brand Colors --
BG = (10, 10, 15)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
RED = (230, 57, 70)
GOLD = (255, 215, 0)
DARK_PANEL = (26, 26, 46)
GRAY = (150, 150, 150)
DIMMED = (180, 180, 180)
GREEN = (80, 200, 80)

# -- Fonts --
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
font_mistake  = get_font(20, True)


# ======================================================
#  DESIGN SYSTEM FUNCTIONS
# ======================================================

def load_bg(filename, overlay_alpha=140):
    """Load AI background with dark overlay."""
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


def draw_mistake_badge(img, num, y_pos=160):
    """Draw a red rounded rectangle badge with 'MISTAKE N OF 5' text."""
    draw = ImageDraw.Draw(img)
    text = f"MISTAKE {num} OF 5"
    bbox = draw.textbbox((0, 0), text, font=font_mistake)
    tw = bbox[2] - bbox[0]
    badge_w = tw + 30
    badge_h = 42
    # Shadow
    draw.rounded_rectangle([MARGIN + 3, y_pos + 3, MARGIN + badge_w + 3, y_pos + badge_h + 3],
                           radius=10, fill=(80, 15, 20, 200))
    # Badge
    draw.rounded_rectangle([MARGIN, y_pos, MARGIN + badge_w, y_pos + badge_h],
                           radius=10, fill=(*RED, 255))
    draw.text((MARGIN + 15, y_pos + 10), text, fill=(*WHITE, 255), font=font_mistake)
    return img


def add_branding(img):
    """Bottom-left @big_quiv + red dot."""
    draw = ImageDraw.Draw(img)
    draw.text((MARGIN, H - 60), "@big_quiv", fill=(*GRAY, 255), font=font_small)
    draw.ellipse([W - MARGIN - 12, H - 52, W - MARGIN, H - 40], fill=(*RED, 255))
    return img


def add_counter(img, current, total=7):
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


# ======================================================
#  SLIDE 1: COVER
# ======================================================
print("Slide 1 - Cover")
img = load_bg("bg1_cover.png", overlay_alpha=110)
img = apply_vignette(img, strength=50)
img = draw_gradient_orb(img, W // 2, 420, 380, RED, alpha=35)
img = draw_gradient_orb(img, W // 2, 500, 250, GOLD, alpha=20)

y = 300
img, y = glow_text_centered(img, "5 MISTAKES", y, font_hero, RED, glow_radius=16, glow_alpha=150)
y += 10
img, y = glow_text_centered(img, "THAT COST BEGINNERS", y, font_headline, WHITE, glow_radius=10, glow_alpha=100)
y += 10
img, y = glow_text_centered(img, "$10K+", y, font_hero, GOLD, glow_radius=18, glow_alpha=160)
y += 30
img = draw_accent_line(img, y, 320)
y += 50
img, y = flat_text_centered(img, "I made all of them", y, font_body, DIMMED)
y += 5
img, y = flat_text_centered(img, "so you don't have to.", y, font_body, DIMMED)

img = add_branding(img)
img, _ = flat_text_centered(img, "SWIPE  >", H - 120, font_tag, GRAY)

img = finalize(img)
img.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("  -> slide-01.png")


# ======================================================
#  SLIDE 2: MISTAKE 1 - NO STOP LOSS
# ======================================================
print("Slide 2 - No Stop Loss")
img = load_bg("bg2_stoploss.png", overlay_alpha=155)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 350, 300, RED, alpha=25)

img = draw_mistake_badge(img, 1, y_pos=160)

y = 230
img, y = glow_text_centered(img, "NO STOP LOSS", y, font_big2, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

img, y = flat_text_left(img, "You're not being patient.", y, font_body_b, WHITE)
y += 15
img, y = flat_text_left(img, "You're being reckless.", y, font_body_b, RED)
y += 30
img, y = flat_text_left(img, "Every trade without a stop loss is an invitation for the market to take your whole bag.", y, font_body, LIGHT)
y += 40

img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 85, border_color=GOLD, fill_alpha=170)
img, _ = flat_text_centered(img, "Set the SL before you enter.", y + 18, font_body_b, GOLD)
img, _ = flat_text_centered(img, "No exceptions.", y + 52, font_body_b, GOLD)

img = add_branding(img)
img = add_counter(img, 2)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("  -> slide-02.png")


# ======================================================
#  SLIDE 3: MISTAKE 2 - OVERSIZING POSITIONS
# ======================================================
print("Slide 3 - Oversizing Positions")
img = load_bg("bg3_oversize.png", overlay_alpha=155)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 400, 300, RED, alpha=20)

img = draw_mistake_badge(img, 2, y_pos=160)

y = 230
img, y = glow_text_centered(img, "OVERSIZING", y, font_big2, RED, glow_radius=14)
y += 5
img, y = glow_text_centered(img, "POSITIONS", y, font_big2, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

img, y = flat_text_left(img, "Risking 20% of your portfolio on one trade is not conviction.", y, font_body, LIGHT)
y += 20
img, y = flat_text_left(img, "It's gambling.", y, font_body_b, RED)
y += 30
img, y = flat_text_left(img, "Professional traders risk 1-2% per trade. That's how you survive long enough to win.", y, font_body, LIGHT)
y += 40

# Comparison boxes
box_w = (TEXT_W - 30) // 2
# Beginner box (red border)
img = draw_glass_panel(img, MARGIN, y, MARGIN + box_w, y + 95, border_color=RED, fill_alpha=170)
img, _ = flat_text_centered(img, "Beginner", y + 12, font_tag, RED, max_width=box_w)
# Center "20% risk" within the left box
draw = ImageDraw.Draw(img)
bbox = draw.textbbox((0, 0), "20% risk", font=font_body_b)
tw = bbox[2] - bbox[0]
tx = MARGIN + (box_w - tw) // 2
draw.text((tx, y + 50), "20% risk", fill=(*WHITE, 255), font=font_body_b)

# Pro box (green border)
img = draw_glass_panel(img, MARGIN + box_w + 30, y, W - MARGIN, y + 95, border_color=GREEN, fill_alpha=170)
draw = ImageDraw.Draw(img)
bbox_pro = draw.textbbox((0, 0), "Pro", font=font_tag)
tw_pro = bbox_pro[2] - bbox_pro[0]
tx_pro = MARGIN + box_w + 30 + (box_w - tw_pro) // 2
draw.text((tx_pro, y + 12), "Pro", fill=(*GREEN, 255), font=font_tag)
bbox_risk = draw.textbbox((0, 0), "1-2% risk", font=font_body_b)
tw_risk = bbox_risk[2] - bbox_risk[0]
tx_risk = MARGIN + box_w + 30 + (box_w - tw_risk) // 2
draw.text((tx_risk, y + 50), "1-2% risk", fill=(*WHITE, 255), font=font_body_b)

img = add_branding(img)
img = add_counter(img, 3)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("  -> slide-03.png")


# ======================================================
#  SLIDE 4: MISTAKE 3 - REVENGE TRADING
# ======================================================
print("Slide 4 - Revenge Trading")
img = load_bg("bg4_revenge.png", overlay_alpha=150)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 400, 320, RED, alpha=30)

img = draw_mistake_badge(img, 3, y_pos=160)

y = 230
img, y = glow_text_centered(img, "REVENGE TRADING", y, font_big2, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

img, y = flat_text_left(img, "You lost. Now you want it back immediately.", y, font_body, LIGHT)
y += 20
img, y = flat_text_left(img, "So you take a bigger position on a worse setup.", y, font_body, LIGHT)
y += 30
img, y = flat_text_left(img, "This is how $500 losses become $5,000 losses.", y, font_body_b, RED)
y += 40

img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 85, border_color=GOLD, fill_alpha=170)
img, _ = flat_text_centered(img, "Walk away. The market will", y + 18, font_body_b, GOLD)
img, _ = flat_text_centered(img, "be here tomorrow.", y + 52, font_body_b, GOLD)

img = add_branding(img)
img = add_counter(img, 4)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("  -> slide-04.png")


# ======================================================
#  SLIDE 5: MISTAKE 4 - IGNORING CONFLUENCE
# ======================================================
print("Slide 5 - Ignoring Confluence")
img = load_bg("bg5_confluence.png", overlay_alpha=155)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 450, 350, GOLD, alpha=20)

img = draw_mistake_badge(img, 4, y_pos=160)

y = 230
img, y = glow_text_centered(img, "IGNORING", y, font_big2, RED, glow_radius=14)
y += 5
img, y = glow_text_centered(img, "CONFLUENCE", y, font_big2, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

img, y = flat_text_left(img, "One indicator is not a signal.", y, font_body_b, WHITE)
y += 20
img, y = flat_text_left(img, "You need confluence.", y, font_body, LIGHT)
y += 35

# Three pillars
pillars = ["Structure", "Volume", "Momentum"]
pill_w = (TEXT_W - 40) // 3
for i, p in enumerate(pillars):
    px = MARGIN + i * (pill_w + 20)
    img = draw_glass_panel(img, px, y, px + pill_w, y + 75, border_color=GOLD, fill_alpha=180)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), p, font=font_body_b)
    tw = bbox[2] - bbox[0]
    draw.text((px + (pill_w - tw) // 2, y + 22), p, fill=(*GOLD, 255), font=font_body_b)

y += 110
img, y = flat_text_left(img, "All three must agree.", y, font_body_b, WHITE)
y += 20
img, y = flat_text_left(img, "If they don't, you don't trade.", y, font_body_b, RED)

img = add_branding(img)
img = add_counter(img, 5)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("  -> slide-05.png")


# ======================================================
#  SLIDE 6: MISTAKE 5 - TRADING WITHOUT A SYSTEM
# ======================================================
print("Slide 6 - No System")
img = load_bg("bg6_nosystem.png", overlay_alpha=160)
img = apply_vignette(img, strength=45)
img = draw_gradient_orb(img, W // 2, 400, 300, RED, alpha=20)

img = draw_mistake_badge(img, 5, y_pos=160)

y = 230
img, y = glow_text_centered(img, "TRADING WITHOUT", y, font_big2, RED, glow_radius=14)
y += 5
img, y = glow_text_centered(img, "A SYSTEM", y, font_big2, RED, glow_radius=14)
y += 25
img = draw_accent_line(img, y)
y += 55

# X items
x_items = ["No journal.", "No rules.", "No risk parameters.", "Just vibes."]
draw = ImageDraw.Draw(img)
for item in x_items:
    draw.text((MARGIN, y), "X", fill=(*RED, 255), font=font_body_b)
    draw.text((MARGIN + 40, y), item, fill=(*LIGHT, 255), font=font_body)
    y += 45

y += 20
img, y = flat_text_left(img, "That's not trading.", y, font_body_b, WHITE)
y += 15
img, y = flat_text_left(img, "That's scrolling charts with money on the line.", y, font_body, RED)
y += 35

img = draw_glass_panel(img, MARGIN, y, W - MARGIN, y + 75, border_color=GOLD, fill_alpha=170)
img, _ = flat_text_centered(img, "A system removes emotion.", y + 20, font_body_b, GOLD)

img = add_branding(img)
img = add_counter(img, 6)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-06.png"), quality=95)
print("  -> slide-06.png")


# ======================================================
#  SLIDE 7: CTA
# ======================================================
print("Slide 7 - CTA")
img = load_bg("bg7_cta.png", overlay_alpha=105)
img = apply_vignette(img, strength=55)
img = draw_gradient_orb(img, W // 2, 520, 400, RED, alpha=30)

y = 340
img, y = glow_text_centered(img, "WANT THE", y, font_subhead, WHITE, glow_radius=8, glow_alpha=100)
y += 15
img, y = glow_text_centered(img, "FULL SYSTEM?", y, font_big2, RED, glow_radius=18, glow_alpha=160)
y += 40
img = draw_accent_line(img, y, 400)
y += 60

img, y = flat_text_centered(img, "I teach risk management,", y, font_body_b, WHITE)
y += 5
img, y = flat_text_centered(img, "confluence trading, and position sizing", y, font_body_b, WHITE)
y += 5
img, y = flat_text_centered(img, "in Week 1.", y, font_body_b, WHITE)
y += 40

# CTA button with drop shadow
btn_w = 720
btn_h = 95
btn_x = (W - btn_w) // 2
draw = ImageDraw.Draw(img)
# Shadow
draw.rounded_rectangle([btn_x + 5, y + 5, btn_x + btn_w + 5, y + btn_h + 5],
                       radius=18, fill=(80, 15, 20, 200))
# Button
draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h],
                       radius=18, fill=(*RED, 255))
# Button text
bbox = draw.textbbox((0, 0), "COMMENT CHECKLIST", font=font_cta)
tw = bbox[2] - bbox[0]
tx = (W - tw) // 2
draw.text((tx, y + 22), "COMMENT CHECKLIST", fill=(*WHITE, 255), font=font_cta)

y += btn_h + 40
img, y = flat_text_centered(img, "and I'll send you the free", y, font_body, DIMMED)
y += 5
img, _ = flat_text_centered(img, "risk management guide.", y, font_body, DIMMED)

img = add_branding(img)
img = add_counter(img, 7)
img = finalize(img)
img.save(os.path.join(output_dir, "slide-07.png"), quality=95)
print("  -> slide-07.png")


print("\nALL 7 PREMIUM V2 SLIDES GENERATED.")
