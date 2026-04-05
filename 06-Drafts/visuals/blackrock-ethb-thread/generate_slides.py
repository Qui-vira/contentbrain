"""
BlackRock ETHB Thread — Twitter/X Graphics (Pure Pillow, no fal.ai)
3 graphics: Hook (tweet 1), Comparison (tweet 3), Data Card (tweet 4)
Canvas: 1200x675 (16:9 Twitter standard)
Brand: @big_quiv — dark backgrounds, red accents, gold highlights, premium institutional
"""

import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# === BRAND COLORS ===
DEEP_BLACK = (10, 10, 15)
QUIVIRA_RED = (230, 57, 70)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
DIMMED = (180, 180, 180)
GRAY = (150, 150, 150)
DARK_PANEL = (26, 26, 46)
PANEL_BORDER = (40, 40, 70)
GREEN = (0, 200, 100)
RED_DIM = (180, 40, 50)
NAVY = (12, 14, 35)

W, H = 1200, 675
BASE = os.path.dirname(os.path.abspath(__file__))

# === FONT LOADING ===
def load_font(size, bold=False):
    paths = [
        f"C:/Windows/Fonts/{'arialbd.ttf' if bold else 'arial.ttf'}",
        f"C:/Windows/Fonts/{'calibrib.ttf' if bold else 'calibri.ttf'}",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_HERO = load_font(64, True)
FONT_HEADLINE = load_font(44, True)
FONT_SUBHEAD = load_font(32, True)
FONT_BODY = load_font(26, False)
FONT_BODY_BOLD = load_font(26, True)
FONT_SMALL = load_font(20, False)
FONT_TAG = load_font(18, True)
FONT_STAT_BIG = load_font(52, True)

# === DESIGN HELPERS ===
def create_gradient_bg(colors_stops, angle=135):
    """Create a gradient background with multiple color stops."""
    img = Image.new("RGBA", (W, H), DEEP_BLACK)
    draw = ImageDraw.Draw(img)
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    for y in range(H):
        for x in range(W):
            t = ((x * cos_a + y * sin_a) / (W * abs(cos_a) + H * abs(sin_a))) + 0.5
            t = max(0, min(1, t))
            # Find segment
            for i in range(len(colors_stops) - 1):
                t1, c1 = colors_stops[i]
                t2, c2 = colors_stops[i + 1]
                if t1 <= t <= t2:
                    local_t = (t - t1) / (t2 - t1) if t2 > t1 else 0
                    r = int(c1[0] + (c2[0] - c1[0]) * local_t)
                    g = int(c1[1] + (c2[1] - c1[1]) * local_t)
                    b = int(c1[2] + (c2[2] - c1[2]) * local_t)
                    draw.point((x, y), fill=(r, g, b, 255))
                    break
    return img

def fast_gradient_bg(top_color, bottom_color, mid_color=None):
    """Fast vertical gradient (row-based)."""
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        if mid_color:
            if t < 0.5:
                lt = t * 2
                r = int(top_color[0] + (mid_color[0] - top_color[0]) * lt)
                g = int(top_color[1] + (mid_color[1] - top_color[1]) * lt)
                b = int(top_color[2] + (mid_color[2] - top_color[2]) * lt)
            else:
                lt = (t - 0.5) * 2
                r = int(mid_color[0] + (bottom_color[0] - mid_color[0]) * lt)
                g = int(mid_color[1] + (bottom_color[1] - mid_color[1]) * lt)
                b = int(mid_color[2] + (bottom_color[2] - mid_color[2]) * lt)
        else:
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
    return img

def draw_glow_text(img, text, x, y, font, color, glow_radius=10, glow_alpha=120):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, fill=(*color[:3], glow_alpha), font=font)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, fill=(*color[:3], 255), font=font)
    return img

def draw_gradient_orb(img, cx, cy, radius, color, alpha=40):
    orb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    for i in range(20, 0, -1):
        r = int(radius * i / 20)
        a = int(alpha * (1 - i / 20))
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color[:3], a))
    return Image.alpha_composite(img, orb)

def draw_glass_panel(img, x1, y1, x2, y2, fill_alpha=140, border_color=(255,255,255), border_alpha=30, radius=12):
    panel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=(26, 26, 46, fill_alpha))
    pd.rounded_rectangle([x1, y1, x2, y2], radius=radius, outline=(*border_color[:3], border_alpha), width=1)
    return Image.alpha_composite(img, panel)

def apply_vignette(img, strength=60):
    vig = Image.new("RGBA", img.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    w, h = img.size
    for i in range(strength):
        alpha = int((strength - i) * 2.5)
        margin = i * max(w, h) // (strength * 2)
        vd.rectangle([0, 0, w, margin], fill=(0, 0, 0, alpha))
        vd.rectangle([0, h-margin, w, h], fill=(0, 0, 0, alpha))
        vd.rectangle([0, 0, margin, h], fill=(0, 0, 0, alpha))
        vd.rectangle([w-margin, 0, w, h], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, vig)

def draw_accent_line(img, y, x_start, width=200, color=QUIVIRA_RED):
    line = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    ld.rectangle([x_start-4, y-3, x_start+width+4, y+6], fill=(*color[:3], 50))
    ld.rectangle([x_start, y, x_start+width, y+3], fill=(*color, 255))
    return Image.alpha_composite(img, line)

def add_branding(img):
    draw = ImageDraw.Draw(img)
    draw.text((60, H - 38), "@big_quiv", fill=(*GRAY, 200), font=FONT_SMALL)
    return img

def tw(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def add_grid_lines(img, spacing=80, color=(255, 255, 255), alpha=6):
    """Subtle grid overlay for institutional feel."""
    grid = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, spacing):
        gd.line([(x, 0), (x, H)], fill=(*color, alpha), width=1)
    for y in range(0, H, spacing):
        gd.line([(0, y), (W, y)], fill=(*color, alpha), width=1)
    return Image.alpha_composite(img, grid)


# =============================================================================
# SLIDE 1 — HOOK (Tweet 1)
# =============================================================================
def build_slide_1():
    print("Building Slide 1 (Hook)...")
    img = fast_gradient_bg((15, 12, 30), DEEP_BLACK, mid_color=(20, 15, 40))
    img = add_grid_lines(img, spacing=60, alpha=5)
    img = apply_vignette(img, strength=50)
    img = draw_gradient_orb(img, 900, 280, 350, QUIVIRA_RED, alpha=25)
    img = draw_gradient_orb(img, 250, 400, 280, GOLD, alpha=12)
    img = draw_gradient_orb(img, 600, 100, 200, (60, 40, 120), alpha=15)

    x = 60
    y = 60

    # Tag badge
    img = draw_glass_panel(img, x, y, x + 220, y + 32, fill_alpha=160, border_color=QUIVIRA_RED, border_alpha=80, radius=6)
    draw = ImageDraw.Draw(img)
    draw.text((x + 12, y + 6), "REGIME SHIFT", fill=QUIVIRA_RED, font=FONT_TAG)
    y += 52

    # Headline
    img = draw_glow_text(img, "BlackRock Made Staking", x, y, FONT_HEADLINE, WHITE, glow_radius=8, glow_alpha=80)
    y += 52
    img = draw_glow_text(img, "Institutional.", x, y, FONT_HEADLINE, QUIVIRA_RED, glow_radius=12, glow_alpha=130)
    y += 65

    img = draw_accent_line(img, y, x, width=160)
    y += 25

    # Body text
    draw = ImageDraw.Draw(img)
    draw.text((x, y), "ETH rallied", fill=LIGHT, font=FONT_BODY)
    w1 = tw(draw, "ETH rallied ", FONT_BODY)
    draw.text((x + w1, y), "20% in 8 days", fill=GOLD, font=FONT_BODY_BOLD)
    w2 = tw(draw, "20% in 8 days ", FONT_BODY_BOLD)
    draw.text((x + w1 + w2, y), "after ETHB launched.", fill=LIGHT, font=FONT_BODY)
    y += 38
    draw.text((x, y), "This is not a coincidence.", fill=DIMMED, font=FONT_BODY)

    # Right side: stat card
    sx, sy = 720, 120
    img = draw_glass_panel(img, sx, sy, sx + 420, sy + 310, fill_alpha=110, border_color=GOLD, border_alpha=45, radius=16)
    img = draw_gradient_orb(img, sx + 210, sy + 155, 160, GOLD, alpha=18)

    draw = ImageDraw.Draw(img)
    draw.text((sx + 30, sy + 22), "ETH SINCE ETHB LAUNCH", fill=DIMMED, font=FONT_TAG)

    img = draw_glow_text(img, "+20%", sx + 70, sy + 60, FONT_HERO, GOLD, glow_radius=16, glow_alpha=150)

    draw = ImageDraw.Draw(img)
    draw.text((sx + 30, sy + 150), "8 DAYS", fill=WHITE, font=FONT_SUBHEAD)
    draw.text((sx + 185, sy + 156), "rally duration", fill=DIMMED, font=FONT_SMALL)

    # Separator
    draw.rectangle([sx + 30, sy + 198, sx + 390, sy + 199], fill=(*PANEL_BORDER, 120))

    draw.text((sx + 30, sy + 215), "ETHB", fill=QUIVIRA_RED, font=FONT_BODY_BOLD)
    draw.text((sx + 100, sy + 217), "First staked ETH ETF", fill=DIMMED, font=FONT_SMALL)

    draw.text((sx + 30, sy + 250), "$14T AUM", fill=GOLD, font=FONT_BODY_BOLD)
    draw.text((sx + 170, sy + 252), "BlackRock", fill=DIMMED, font=FONT_SMALL)

    draw.text((sx + 30, sy + 280), "$107M", fill=WHITE, font=FONT_BODY_BOLD)
    draw.text((sx + 130, sy + 282), "seed assets at launch", fill=DIMMED, font=FONT_SMALL)

    img = add_branding(img)
    out = os.path.join(BASE, "slide-01-hook.png")
    img.save(out, "PNG", quality=95)
    print(f"  [saved] {out}")
    return out


# =============================================================================
# SLIDE 2 — COMPARISON (Tweet 3)
# =============================================================================
def build_slide_2():
    print("Building Slide 2 (Comparison)...")
    img = fast_gradient_bg((18, 10, 25), DEEP_BLACK, mid_color=(12, 12, 28))
    img = add_grid_lines(img, spacing=60, alpha=4)
    img = apply_vignette(img, strength=50)

    # Title
    img = draw_glow_text(img, "What Staked ETH ETFs Change", 60, 30, FONT_SUBHEAD, WHITE, glow_radius=6, glow_alpha=70)
    img = draw_accent_line(img, 72, 60, width=140)

    mid = W // 2
    panel_top = 100
    panel_bottom = 560
    gap = 16

    # BEFORE panel (left)
    img = draw_gradient_orb(img, 290, 340, 220, RED_DIM, alpha=15)
    img = draw_glass_panel(img, 40, panel_top, mid - gap, panel_bottom, fill_alpha=110, border_color=RED_DIM, border_alpha=50, radius=14)

    draw = ImageDraw.Draw(img)
    bx = 70
    by = panel_top + 20

    img = draw_glass_panel(img, bx, by, bx + 110, by + 30, fill_alpha=180, border_color=RED_DIM, border_alpha=100, radius=6)
    draw = ImageDraw.Draw(img)
    draw.text((bx + 14, by + 5), "BEFORE", fill=RED_DIM, font=FONT_TAG)
    by += 50

    img = draw_glow_text(img, "Dead", bx, by, FONT_HERO, RED_DIM, glow_radius=12, glow_alpha=100)
    by += 68
    img = draw_glow_text(img, "Capital", bx, by, FONT_HERO, RED_DIM, glow_radius=12, glow_alpha=100)
    by += 85

    draw = ImageDraw.Draw(img)
    for line in ["Institutions bought spot ETH.", "No yield. No staking.", "Capital sat idle.", "", '"Speculative asset"', "in portfolio models."]:
        if line == "":
            by += 8
            continue
        c = DIMMED if line.startswith('"') else LIGHT
        draw.text((bx, by), line, fill=c, font=FONT_BODY)
        by += 30

    # NOW panel (right)
    img = draw_gradient_orb(img, 910, 340, 220, GOLD, alpha=15)
    img = draw_glass_panel(img, mid + gap, panel_top, W - 40, panel_bottom, fill_alpha=110, border_color=GOLD, border_alpha=50, radius=14)

    draw = ImageDraw.Draw(img)
    nx = mid + gap + 30
    ny = panel_top + 20

    img = draw_glass_panel(img, nx, ny, nx + 80, ny + 30, fill_alpha=180, border_color=GREEN, border_alpha=100, radius=6)
    draw = ImageDraw.Draw(img)
    draw.text((nx + 16, ny + 5), "NOW", fill=GREEN, font=FONT_TAG)
    ny += 50

    img = draw_glow_text(img, "Productive", nx, ny, FONT_HERO, GOLD, glow_radius=12, glow_alpha=100)
    ny += 68
    img = draw_glow_text(img, "Asset", nx, ny, FONT_HERO, GOLD, glow_radius=12, glow_alpha=100)
    ny += 85

    draw = ImageDraw.Draw(img)
    for line in ["Earn ~2.5% net staking yield.", "Price exposure + yield.", "70-95% of holdings staked.", "", '"Productive asset"', "in allocation models."]:
        if line == "":
            ny += 8
            continue
        c = DIMMED if line.startswith('"') else LIGHT
        draw.text((nx, ny), line, fill=c, font=FONT_BODY)
        ny += 30

    # VS circle
    vs_y = (panel_top + panel_bottom) // 2 - 22
    vs_x = mid - 24
    img = draw_glass_panel(img, vs_x - 2, vs_y - 2, vs_x + 48, vs_y + 48, fill_alpha=220, border_color=WHITE, border_alpha=80, radius=24)
    draw = ImageDraw.Draw(img)
    draw.text((vs_x + 8, vs_y + 8), "VS", fill=WHITE, font=FONT_BODY_BOLD)

    # Bottom verdict
    draw.text((60, panel_bottom + 22), "More allocation models = more inflows. Period.", fill=QUIVIRA_RED, font=FONT_BODY_BOLD)

    img = add_branding(img)
    out = os.path.join(BASE, "slide-02-comparison.png")
    img.save(out, "PNG", quality=95)
    print(f"  [saved] {out}")
    return out


# =============================================================================
# SLIDE 3 — DATA CARD (Tweet 4)
# =============================================================================
def build_slide_3():
    print("Building Slide 3 (Data Card)...")
    img = fast_gradient_bg((12, 10, 28), DEEP_BLACK, mid_color=(15, 12, 32))
    img = add_grid_lines(img, spacing=60, alpha=5)
    img = apply_vignette(img, strength=50)
    img = draw_gradient_orb(img, 600, 340, 350, QUIVIRA_RED, alpha=10)
    img = draw_gradient_orb(img, 300, 200, 200, GOLD, alpha=8)

    # Title
    img = draw_glow_text(img, "Where ETH Sits Right Now", 60, 28, FONT_SUBHEAD, QUIVIRA_RED, glow_radius=8, glow_alpha=100)
    img = draw_accent_line(img, 68, 60, width=140)

    # === ROW 1: Price + Fear&Greed + ETHB ===
    # Price card
    img = draw_glass_panel(img, 50, 90, 480, 240, fill_alpha=120, border_color=GOLD, border_alpha=45, radius=14)
    img = draw_gradient_orb(img, 265, 165, 140, GOLD, alpha=15)
    draw = ImageDraw.Draw(img)
    draw.text((75, 104), "ETH / USD", fill=DIMMED, font=FONT_TAG)
    img = draw_glow_text(img, "~$2,180", 75, 135, FONT_HERO, GOLD, glow_radius=14, glow_alpha=130)
    draw = ImageDraw.Draw(img)
    draw.text((75, 210), "Recovery mode. Not a clean breakout.", fill=DIMMED, font=FONT_SMALL)

    # Fear & Greed card
    img = draw_glass_panel(img, 500, 90, 830, 240, fill_alpha=120, border_color=QUIVIRA_RED, border_alpha=55, radius=14)
    draw = ImageDraw.Draw(img)
    draw.text((525, 104), "FEAR & GREED INDEX", fill=DIMMED, font=FONT_TAG)
    img = draw_glow_text(img, "14", 525, 132, FONT_HERO, QUIVIRA_RED, glow_radius=14, glow_alpha=140)
    draw = ImageDraw.Draw(img)
    draw.text((610, 155), "/ 100", fill=DIMMED, font=FONT_SUBHEAD)
    draw.text((525, 210), "EXTREME FEAR", fill=QUIVIRA_RED, font=FONT_BODY_BOLD)

    # ETHB monthly high card
    img = draw_glass_panel(img, 850, 90, 1150, 240, fill_alpha=120, border_color=WHITE, border_alpha=35, radius=14)
    draw = ImageDraw.Draw(img)
    draw.text((875, 104), "SINCE ETHB LAUNCH", fill=DIMMED, font=FONT_TAG)
    img = draw_glow_text(img, "$2,384", 875, 138, FONT_STAT_BIG, WHITE, glow_radius=8, glow_alpha=80)
    draw = ImageDraw.Draw(img)
    draw.text((875, 210), "Monthly high", fill=DIMMED, font=FONT_SMALL)

    # === ROW 2: 52-week range + Key levels ===
    row_y = 265

    # 52-week range card
    img = draw_glass_panel(img, 50, row_y, 580, row_y + 160, fill_alpha=110, border_color=PANEL_BORDER, border_alpha=45, radius=14)
    draw = ImageDraw.Draw(img)
    draw.text((75, row_y + 15), "52-WEEK RANGE", fill=DIMMED, font=FONT_TAG)

    draw.text((75, row_y + 48), "$1,473", fill=QUIVIRA_RED, font=FONT_SUBHEAD)
    draw.text((220, row_y + 54), "Feb 2026 low", fill=DIMMED, font=FONT_SMALL)

    # Range bar
    bar_y = row_y + 100
    draw.rectangle([75, bar_y, 555, bar_y + 8], fill=(*PANEL_BORDER, 200))
    # Gradient fill on bar: red to gold
    for px in range(75, 556):
        t = (px - 75) / 480
        r = int(QUIVIRA_RED[0] + (GOLD[0] - QUIVIRA_RED[0]) * t)
        g = int(QUIVIRA_RED[1] + (GOLD[1] - QUIVIRA_RED[1]) * t)
        b = int(QUIVIRA_RED[2] + (GOLD[2] - QUIVIRA_RED[2]) * t)
        draw.rectangle([px, bar_y + 1, px, bar_y + 7], fill=(r, g, b, 120))

    pct = (2180 - 1473) / (4955 - 1473)
    marker_x = int(75 + pct * 480)
    draw.ellipse([marker_x - 7, bar_y - 5, marker_x + 7, bar_y + 13], fill=WHITE)
    draw.text((marker_x - 25, bar_y - 24), "$2,180", fill=WHITE, font=FONT_TAG)

    draw.text((75, row_y + 122), "$4,955", fill=GOLD, font=FONT_SUBHEAD)
    draw.text((220, row_y + 128), "Oct 2025 high", fill=DIMMED, font=FONT_SMALL)

    # Key levels card
    img = draw_glass_panel(img, 600, row_y, 1150, row_y + 160, fill_alpha=110, border_color=PANEL_BORDER, border_alpha=45, radius=14)
    draw = ImageDraw.Draw(img)
    draw.text((625, row_y + 15), "KEY LEVELS TO WATCH", fill=DIMMED, font=FONT_TAG)

    # Bullish level
    draw.text((625, row_y + 50), "$2,378", fill=GOLD, font=FONT_SUBHEAD)
    draw.text((775, row_y + 56), "R1 pivot. Confirmation level.", fill=LIGHT, font=FONT_SMALL)

    # Separator
    draw.rectangle([625, row_y + 95, 1125, row_y + 96], fill=(*PANEL_BORDER, 100))

    # Bearish level
    draw.text((625, row_y + 110), "$1,990", fill=QUIVIRA_RED, font=FONT_SUBHEAD)
    draw.text((775, row_y + 116), "20-day SMA. Below = weakening.", fill=LIGHT, font=FONT_SMALL)

    # === BOTTOM VERDICT BAR ===
    verdict_y = row_y + 185
    img = draw_glass_panel(img, 50, verdict_y, 1150, verdict_y + 55, fill_alpha=100, border_color=QUIVIRA_RED, border_alpha=35, radius=10)
    draw = ImageDraw.Draw(img)
    draw.text((80, verdict_y + 14), 'This is a "watch and wait" zone, not a "send it" zone.', fill=WHITE, font=FONT_BODY_BOLD)

    img = add_branding(img)
    out = os.path.join(BASE, "slide-03-data.png")
    img.save(out, "PNG", quality=95)
    print(f"  [saved] {out}")
    return out


# =============================================================================
if __name__ == "__main__":
    print("=== BlackRock ETHB Thread Graphics (Gradient Mode) ===\n")
    build_slide_1()
    build_slide_2()
    build_slide_3()
    print("\n=== Done! 3 slides generated. ===")
