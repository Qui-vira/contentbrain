"""
April New Month Graphic — @big_quiv
Ornamental decorative serif typography with platform icon grid.
Outputs: 1080x1350 (IG post) and 1080x1920 (IG story)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, math

# === PATHS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_IMG = r"C:\Users\Bigquiv\Downloads\hf_20260401_061135_49a22d29-5f99-404f-98eb-54fd168225cb.png"

# === BRAND COLORS ===
DEEP_BLACK = (10, 10, 15)
QUIVIRA_RED = (230, 57, 70)
GOLD = (255, 215, 0)
WARM_GOLD = (218, 165, 32)
LIGHT_GOLD = (255, 223, 100)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
DIMMED = (180, 180, 180)
GRAY = (150, 150, 150)
SILVER = (200, 200, 210)

# Platform brand colors
IG_COLORS = [(252, 175, 69), (214, 41, 118), (150, 47, 191), (79, 91, 213)]
X_BLACK = (0, 0, 0)
TT_RED = (254, 44, 85)
TT_CYAN = (37, 244, 238)
LI_BLUE = (10, 102, 194)

# === FONTS ===
FONT_DECORATIVE = "C:/Windows/Fonts/gabriola.ttf"
FONT_SCRIPT = "C:/Windows/Fonts/VIVALDII.TTF"
FONT_SERIF_BOLD = "C:/Windows/Fonts/palabi.ttf"
FONT_SERIF = "C:/Windows/Fonts/pala.ttf"
FONT_BOLD = "C:/Windows/Fonts/bahnschrift.ttf"
FONT_LIGHT = "C:/Windows/Fonts/segoeui.ttf"


# === ICON GENERATION ===

def create_ig_icon(size=120):
    """Instagram icon: gradient rounded square with camera outline."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 5  # corner radius

    # Gradient background (diagonal)
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            if t < 0.33:
                s = t / 0.33
                color = tuple(int(IG_COLORS[0][i] * (1 - s) + IG_COLORS[1][i] * s) for i in range(3))
            elif t < 0.66:
                s = (t - 0.33) / 0.33
                color = tuple(int(IG_COLORS[1][i] * (1 - s) + IG_COLORS[2][i] * s) for i in range(3))
            else:
                s = (t - 0.66) / 0.34
                color = tuple(int(IG_COLORS[2][i] * (1 - s) + IG_COLORS[3][i] * s) for i in range(3))
            img.putpixel((x, y), (*color, 255))

    # Apply rounded corner mask
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    img.putalpha(mask)

    # Camera outline (white)
    draw = ImageDraw.Draw(img)
    margin = size // 4
    # Outer rounded rect
    draw.rounded_rectangle([margin, margin, size - margin, size - margin],
                           radius=size // 8, outline=WHITE, width=max(3, size // 30))
    # Center circle
    c = size // 2
    cr = size // 6
    draw.ellipse([c - cr, c - cr, c + cr, c + cr], outline=WHITE, width=max(3, size // 30))
    # Top-right dot
    dot_r = size // 20
    dot_x = size - margin - size // 8
    dot_y = margin + size // 8
    draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=WHITE)

    return img


def create_x_icon(size=120):
    """X (Twitter) icon: black rounded square with white X."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 5
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(*X_BLACK, 255))
    # White border for visibility on dark backgrounds
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r,
                           outline=(255, 255, 255, 100), width=2)

    # Draw X letter
    font_size = int(size * 0.55)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    bbox = draw.textbbox((0, 0), "X", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "X", fill=WHITE, font=font)
    return img


def create_tt_icon(size=120):
    """TikTok icon: black rounded square with stylized music note."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 5
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(*X_BLACK, 255))
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r,
                           outline=(255, 255, 255, 100), width=2)

    # Draw stylized music note (TikTok-like)
    cx = size // 2
    # Note head (bottom circle)
    note_r = size // 8
    note_cx = cx - size // 10
    note_cy = size - size // 3

    # Cyan layer (offset left)
    draw.ellipse([note_cx - note_r - 2, note_cy - note_r - 2,
                  note_cx + note_r - 2, note_cy + note_r - 2],
                 fill=(*TT_CYAN, 200))
    # Red layer (offset right)
    draw.ellipse([note_cx - note_r + 2, note_cy - note_r + 2,
                  note_cx + note_r + 2, note_cy + note_r + 2],
                 fill=(*TT_RED, 200))
    # White center
    draw.ellipse([note_cx - note_r, note_cy - note_r,
                  note_cx + note_r, note_cy + note_r], fill=WHITE)

    # Stem
    stem_x = note_cx + note_r - 2
    stem_top = size // 4
    w = max(3, size // 25)
    # Cyan stem (offset)
    draw.rectangle([stem_x - 2, stem_top, stem_x + w - 2, note_cy], fill=(*TT_CYAN, 200))
    # Red stem (offset)
    draw.rectangle([stem_x + 2, stem_top, stem_x + w + 2, note_cy], fill=(*TT_RED, 200))
    # White stem
    draw.rectangle([stem_x, stem_top, stem_x + w, note_cy], fill=WHITE)

    # Top wave curve (simplified)
    for i in range(size // 4):
        t = i / (size // 4)
        wave_y = int(stem_top + math.sin(t * math.pi * 0.8) * size // 10)
        wave_x = stem_x + w + int(t * size // 4)
        if wave_x < size - 5:
            draw.ellipse([wave_x - 2, wave_y - 2, wave_x + 2, wave_y + 2], fill=WHITE)

    return img


def create_li_icon(size=120):
    """LinkedIn icon: blue rounded square with white 'in'."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 5
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(*LI_BLUE, 255))

    # "in" text
    font_size = int(size * 0.5)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    bbox = draw.textbbox((0, 0), "in", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - bbox[1] + size // 12
    draw.text((x, y), "in", fill=WHITE, font=font)
    return img


# === DESIGN HELPERS ===

def draw_glow_text(img, text, x, y, font, color, glow_radius=12, glow_alpha=120):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), text, fill=(*color[:3], glow_alpha), font=font)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, fill=(*color[:3], 255), font=font)
    return img


def draw_gradient_orb(img, cx, cy, radius, color, alpha=40):
    orb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    for i in range(20, 0, -1):
        r = int(radius * i / 20)
        a = int(alpha * (1 - i / 20))
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color[:3], a))
    return Image.alpha_composite(img.convert("RGBA"), orb)


def draw_accent_line(img, y, width=220, color=QUIVIRA_RED, thickness=3):
    w = img.size[0]
    x_start = (w - width) // 2
    line = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    ld.rectangle([x_start - 8, y - 5, x_start + width + 8, y + thickness + 5],
                 fill=(*color[:3], 50))
    glow_line = line.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), glow_line)
    line2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld2 = ImageDraw.Draw(line2)
    ld2.rectangle([x_start, y, x_start + width, y + thickness], fill=(*color, 255))
    return Image.alpha_composite(img, line2)


def apply_gradient_overlay(img, top_strength=0.7, bottom_strength=0.85, bottom_start=0.55):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    top_zone = int(h * 0.30)
    for i in range(top_zone):
        progress = 1.0 - (i / top_zone)
        alpha = int(255 * top_strength * progress * progress)
        od.line([(0, i), (w, i)], fill=(10, 10, 15, alpha))
    bottom_zone_start = int(h * bottom_start)
    bottom_zone = h - bottom_zone_start
    for i in range(bottom_zone):
        progress = i / bottom_zone
        alpha = int(255 * bottom_strength * progress * progress)
        od.line([(0, bottom_zone_start + i), (w, bottom_zone_start + i)],
                fill=(10, 10, 15, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def center_text_x(draw, text, font, canvas_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    return (canvas_width - text_width) // 2


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def draw_icon_grid(img, x_start, y_start, icon_size=48, gap=12, handle_font_size=18):
    """Draw a 2x2 grid of platform icons with handles next to each."""
    icons = [
        (create_ig_icon(icon_size), "@big_quiv"),
        (create_x_icon(icon_size), "@_Quivira"),
        (create_tt_icon(icon_size), "@big_quiv"),
        (create_li_icon(icon_size), "@bigquiv"),
    ]
    font = ImageFont.truetype(FONT_LIGHT, handle_font_size)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    row_height = icon_size + gap
    col_width = icon_size + gap

    for idx, (icon, handle) in enumerate(icons):
        row = idx // 2
        col = idx % 2

        # Calculate position (right-aligned grid)
        # Each cell: icon + handle text
        handle_w = text_width(ld, handle, font)
        cell_w = icon_size + 8 + handle_w

        ix = x_start + col * (cell_w + gap * 2)
        iy = y_start + row * row_height

        # Paste icon
        layer.paste(icon, (ix, iy), icon)

        # Handle text next to icon, vertically centered
        text_y = iy + (icon_size - handle_font_size) // 2
        ld.text((ix + icon_size + 8, text_y), handle, fill=(*LIGHT[:3], 220), font=font)

    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_diagonal_ribbon(img, text, cx, cy, angle=-25, ribbon_color=WARM_GOLD,
                         text_color=WHITE, font_size=28, padding_x=60, padding_y=14):
    """Diagonal gold ribbon with text."""
    font = ImageFont.truetype(FONT_SERIF_BOLD, font_size)
    temp = Image.new("RGBA", (800, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(temp)
    tw = text_width(td, text, font)
    th = text_height(td, text, font)
    rw = tw + padding_x * 2
    rh = th + padding_y * 2
    ribbon_x = (800 - rw) // 2
    ribbon_y = (200 - rh) // 2
    points_bg = [
        (ribbon_x, ribbon_y), (ribbon_x + rw, ribbon_y),
        (ribbon_x + rw + 15, ribbon_y + rh // 2),
        (ribbon_x + rw, ribbon_y + rh), (ribbon_x, ribbon_y + rh),
        (ribbon_x - 15, ribbon_y + rh // 2),
    ]
    td.polygon(points_bg, fill=(*ribbon_color[:3], 230))
    highlight = [(ribbon_x, ribbon_y), (ribbon_x + rw, ribbon_y),
                 (ribbon_x + rw, ribbon_y + 4), (ribbon_x, ribbon_y + 4)]
    td.polygon(highlight, fill=(*LIGHT_GOLD[:3], 120))
    tx = (800 - tw) // 2
    ty = ribbon_y + padding_y - 2
    td.text((tx, ty), text, fill=(*text_color[:3], 255), font=font)
    rotated = temp.rotate(angle, expand=True, resample=Image.BICUBIC)
    rw2, rh2 = rotated.size
    paste_x = max(0, min(cx - rw2 // 2, img.size[0] - rw2))
    paste_y = max(0, min(cy - rh2 // 2, img.size[1] - rh2))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(rotated, (paste_x, paste_y), rotated)
    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_decorative_flourish(img, cx, y, width=300, color=SILVER, alpha=120):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    half_w = width // 2
    for i in range(half_w):
        t = i / half_w
        curve_y = int(math.sin(t * math.pi) * 8)
        a = int(alpha * (1 - t * 0.5))
        ld.ellipse([cx - half_w + i - 1, y + curve_y - 1,
                     cx - half_w + i + 1, y + curve_y + 1], fill=(*color[:3], a))
    for i in range(half_w):
        t = i / half_w
        curve_y = int(math.sin(t * math.pi) * 8)
        a = int(alpha * (1 - t * 0.5))
        ld.ellipse([cx + i - 1, y + curve_y - 1,
                     cx + i + 1, y + curve_y + 1], fill=(*color[:3], a))
    d = 4
    ld.polygon([(cx, y - d), (cx + d, y), (cx, y + d), (cx - d, y)], fill=(*color[:3], alpha))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def prepare_base(source_path, target_w, target_h):
    img = Image.open(source_path).convert("RGBA")
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        offset = (src_w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        offset = max(0, int((src_h - new_h) * 0.15))
        img = img.crop((0, offset, src_w, offset + new_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)
    return img


# =============================================================
# VERSION 1: Instagram Post (1080 x 1350)
# =============================================================
def generate_post():
    W, H = 1080, 1350
    img = prepare_base(SOURCE_IMG, W, H)

    enhancer = ImageEnhance.Contrast(img.convert("RGB"))
    img = enhancer.enhance(1.1).convert("RGBA")

    img = apply_gradient_overlay(img, top_strength=0.75, bottom_strength=0.9, bottom_start=0.6)
    img = draw_gradient_orb(img, W // 2, 250, 350, WARM_GOLD, alpha=15)
    img = draw_gradient_orb(img, W // 2, H - 200, 300, GOLD, alpha=12)

    # Icon grid (top-right, 2x2) — pushed to top corner
    img = draw_icon_grid(img, x_start=W - 420, y_start=30, icon_size=44, gap=10,
                         handle_font_size=18)

    draw = ImageDraw.Draw(img)

    # === "Welcome" in elegant script — pushed down to separate from icons ===
    font_welcome = ImageFont.truetype(FONT_SCRIPT, 80)
    welcome_text = "Welcome"
    x_w = center_text_x(draw, welcome_text, font_welcome, W)
    draw.text((x_w + 2, 162), welcome_text, fill=(0, 0, 0, 80), font=font_welcome)
    draw.text((x_w, 160), welcome_text, fill=LIGHT, font=font_welcome)

    # === "to" ===
    font_to = ImageFont.truetype(FONT_SCRIPT, 54)
    to_text = "to"
    x_to = center_text_x(draw, to_text, font_to, W)
    draw.text((x_to, 245), to_text, fill=DIMMED, font=font_to)

    # === "April" ornamental — BIG ===
    font_april = ImageFont.truetype(FONT_DECORATIVE, 260)
    april_text = "April"
    x_april = center_text_x(draw, april_text, font_april, W)
    img = draw_glow_text(img, april_text, x_april, 240, font_april, SILVER,
                         glow_radius=22, glow_alpha=80)

    # Flourish
    img = draw_decorative_flourish(img, W // 2, 560, width=320, color=SILVER, alpha=100)

    # Gold ribbon
    img = draw_diagonal_ribbon(img, "Happy New Month", cx=W // 2 + 140, cy=580,
                               angle=-18, ribbon_color=WARM_GOLD, text_color=WHITE,
                               font_size=32, padding_x=60, padding_y=16)

    # === Bottom ===
    draw = ImageDraw.Draw(img)
    font_tagline = ImageFont.truetype(FONT_SERIF_BOLD, 36)
    tagline = "New month, new focus, endless possibilities."
    x_tag = center_text_x(draw, tagline, font_tagline, W)
    img = draw_glow_text(img, tagline, x_tag, H - 280, font_tagline, WHITE,
                         glow_radius=8, glow_alpha=70)

    img = draw_accent_line(img, H - 230, width=200, color=QUIVIRA_RED)

    draw = ImageDraw.Draw(img)
    font_brand = ImageFont.truetype(FONT_LIGHT, 28)
    brand_text = "@big_quiv"
    x_brand = center_text_x(draw, brand_text, font_brand, W)
    draw.text((x_brand, H - 200), brand_text, fill=GRAY, font=font_brand)

    font_quote = ImageFont.truetype(FONT_SCRIPT, 34)
    quote = "Clarity over noise."
    x_q = center_text_x(draw, quote, font_quote, W)
    draw.text((x_q, H - 160), quote, fill=(*DIMMED[:3], 180), font=font_quote)

    out_path = os.path.join(BASE_DIR, "april-new-month-post.png")
    img.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Saved: {out_path}")
    return out_path


# =============================================================
# VERSION 2: Instagram Story (1080 x 1920)
# =============================================================
def generate_story():
    W, H = 1080, 1920
    img = prepare_base(SOURCE_IMG, W, H)

    enhancer = ImageEnhance.Contrast(img.convert("RGB"))
    img = enhancer.enhance(1.1).convert("RGBA")

    img = apply_gradient_overlay(img, top_strength=0.8, bottom_strength=0.9, bottom_start=0.55)
    img = draw_gradient_orb(img, W // 2, 320, 400, WARM_GOLD, alpha=15)
    img = draw_gradient_orb(img, W // 2, H - 300, 350, GOLD, alpha=10)

    # Icon grid (top-right, 2x2) — pushed to top corner
    img = draw_icon_grid(img, x_start=W - 440, y_start=40, icon_size=50, gap=12,
                         handle_font_size=20)

    draw = ImageDraw.Draw(img)

    # === "Welcome" — pushed down for separation ===
    font_welcome = ImageFont.truetype(FONT_SCRIPT, 90)
    welcome_text = "Welcome"
    x_w = center_text_x(draw, welcome_text, font_welcome, W)
    draw.text((x_w + 2, 212), welcome_text, fill=(0, 0, 0, 80), font=font_welcome)
    draw.text((x_w, 210), welcome_text, fill=LIGHT, font=font_welcome)

    # === "to" ===
    font_to = ImageFont.truetype(FONT_SCRIPT, 58)
    to_text = "to"
    x_to = center_text_x(draw, to_text, font_to, W)
    draw.text((x_to, 305), to_text, fill=DIMMED, font=font_to)

    # === "April" ornamental — BIG ===
    font_april = ImageFont.truetype(FONT_DECORATIVE, 300)
    april_text = "April"
    x_april = center_text_x(draw, april_text, font_april, W)
    img = draw_glow_text(img, april_text, x_april, 300, font_april, SILVER,
                         glow_radius=24, glow_alpha=80)

    # Flourish
    img = draw_decorative_flourish(img, W // 2, 650, width=350, color=SILVER, alpha=100)

    # Gold ribbon
    img = draw_diagonal_ribbon(img, "Happy New Month", cx=W // 2 + 150, cy=670,
                               angle=-18, ribbon_color=WARM_GOLD, text_color=WHITE,
                               font_size=34, padding_x=65, padding_y=16)

    # === Bottom ===
    draw = ImageDraw.Draw(img)
    font_tagline = ImageFont.truetype(FONT_SERIF_BOLD, 38)
    tagline = "New month, new focus, endless possibilities."
    x_tag = center_text_x(draw, tagline, font_tagline, W)
    img = draw_glow_text(img, tagline, x_tag, H - 400, font_tagline, WHITE,
                         glow_radius=8, glow_alpha=70)

    img = draw_accent_line(img, H - 345, width=220, color=QUIVIRA_RED)

    draw = ImageDraw.Draw(img)
    font_brand = ImageFont.truetype(FONT_LIGHT, 30)
    brand_text = "@big_quiv"
    x_brand = center_text_x(draw, brand_text, font_brand, W)
    draw.text((x_brand, H - 315), brand_text, fill=GRAY, font=font_brand)

    font_quote = ImageFont.truetype(FONT_SCRIPT, 36)
    quote = "Clarity over noise."
    x_q = center_text_x(draw, quote, font_quote, W)
    draw.text((x_q, H - 270), quote, fill=(*DIMMED[:3], 180), font=font_quote)

    out_path = os.path.join(BASE_DIR, "april-new-month-story.png")
    img.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    post_path = generate_post()
    story_path = generate_story()
    print("\nDone! Generated:")
    print(f"  Post (1080x1350): {post_path}")
    print(f"  Story (1080x1920): {story_path}")
