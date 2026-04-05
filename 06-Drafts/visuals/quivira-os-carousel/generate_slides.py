from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - MARGIN * 2

BG = (10, 10, 15)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
RED = (230, 57, 70)
GOLD = (255, 215, 0)
DARK_PANEL = (26, 26, 46)
GRAY = (150, 150, 150)
DIMMED = (180, 180, 180)

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

font_headline = get_font(50, True)
font_subhead = get_font(36, True)
font_body = get_font(28, False)
font_body_bold = get_font(28, True)
font_small = get_font(24, False)
font_tag = get_font(22, True)
font_cta = get_font(42, True)
font_big = get_font(64, True)
font_big2 = get_font(56, True)
font_big3 = get_font(48, True)
font_stat = get_font(44, True)

def new_slide(bg_path=None):
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).resize((W, H))
        overlay = Image.new("RGBA", (W, H), (10, 10, 15, 170))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")
    else:
        img = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(img)
        for y in range(H):
            r = int(10 + (16 * y / H))
            g = int(10 + (16 * y / H))
            b = int(15 + (31 * y / H))
            draw.line([(0, y), (W, y)], fill=(r, g, b))
        return img

def draw_red_line(draw, y, width=200):
    x_start = (W - width) // 2
    draw.rectangle([x_start, y, x_start + width, y + 3], fill=RED)

def draw_text_centered(draw, text, y, font, color=WHITE, max_width=None):
    if max_width is None:
        max_width = TEXT_W
    words = text.split()
    lines = []
    current = ""
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
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), line, fill=color, font=font)
        y += bbox[3] - bbox[1] + 10
    return y

def draw_text_left(draw, text, y, font, color=LIGHT, max_width=None):
    if max_width is None:
        max_width = TEXT_W
    words = text.split()
    lines = []
    current = ""
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
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text((MARGIN, y), line, fill=color, font=font)
        y += bbox[3] - bbox[1] + 8
    return y

def add_branding(draw):
    draw.text((MARGIN, H - 60), "@big_quiv", fill=GRAY, font=font_small)
    draw.ellipse([W - MARGIN - 12, H - 52, W - MARGIN, H - 40], fill=RED)


# ============ SLIDE 1: COVER ============
print("Generating Slide 1 (Cover)...")
img = new_slide(os.path.join(output_dir, "os_cover.png"))
draw = ImageDraw.Draw(img)
y = 280
draw_text_centered(draw, "I WAS WORKING", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, "40 HOURS", y, font_big, RED)
y += 80
draw_text_centered(draw, "A WEEK.", y, font_headline, WHITE)
y += 70
draw_red_line(draw, y, 300)
y += 40
draw_text_centered(draw, "NOW I WORK 3.", y, font_big3, GOLD)
y += 70
draw_text_centered(draw, "Here's the system.", y, font_subhead, DIMMED)
add_branding(draw)
draw_text_centered(draw, "SWIPE >", H - 120, font_tag, GRAY)
img.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("  Saved slide-01.png")


# ============ SLIDE 2: THE PROBLEM ============
print("Generating Slide 2 (The Problem)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "THE PROBLEM", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
pain_points = [
    "Manually charting 50 pairs",
    "Writing content from scratch",
    "Managing 4 platforms",
    "Answering the same questions daily",
]
for p in pain_points:
    draw.text((MARGIN, y), "X", fill=RED, font=font_body_bold)
    draw.text((MARGIN + 35, y), p, fill=LIGHT, font=font_body)
    y += 45
y += 20
draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 100], radius=12, fill=(40, 15, 15), outline=RED)
draw_text_centered(draw, "40 hours a week.", y + 15, font_subhead, RED)
draw_text_centered(draw, "Burning out while looking productive.", y + 58, font_body, DIMMED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("  Saved slide-02.png")


# ============ SLIDE 3: THE BREAKING POINT ============
print("Generating Slide 3 (Breaking Point)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 220
draw_text_centered(draw, "THE BREAKING", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, "POINT", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "I realized I wasn't building a brand.", y, font_body_bold, WHITE)
y += 20
y = draw_text_left(draw, "I was running on a treadmill.", y, font_body, RED)
y += 30
y = draw_text_left(draw, "Doing the same tasks every week.", y, font_body, LIGHT)
y += 15
y = draw_text_left(draw, "No leverage. No compounding.", y, font_body, LIGHT)
y += 30
y = draw_text_left(draw, "Just effort.", y, font_subhead, RED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("  Saved slide-03.png")


# ============ SLIDE 4: THE SYSTEM ============
print("Generating Slide 4 (The System)...")
img = new_slide(os.path.join(output_dir, "os_system.png"))
draw = ImageDraw.Draw(img)
y = 160
draw_text_centered(draw, "THE SYSTEM", y, font_headline, RED)
y += 70
draw_red_line(draw, y)
y += 40
draw_text_centered(draw, "Quivira OS replaces the grind", y, font_body, LIGHT)
y += 35
draw_text_centered(draw, "with 3 layers.", y, font_body_bold, WHITE)
y += 50

layers = [
    ("LAYER 1", "AI Signal Scanner", "Scans 50 pairs every 4 hours. Filters for confluence. Sends approval alerts.", RED),
    ("LAYER 2", "Content Engine", "Scouts trends, pulls data, builds weekly plans.", GOLD),
    ("LAYER 3", "Distribution", "Approved signals and content push to Telegram, X, IG, LinkedIn automatically.", (100, 200, 255)),
]
for label, title, desc, color in layers:
    draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 140], radius=12, fill=DARK_PANEL, outline=color, width=2)
    draw.rounded_rectangle([MARGIN + 15, y + 12, MARGIN + 135, y + 42], radius=6, fill=color)
    bbox = draw.textbbox((0, 0), label, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + 15 + (120 - tw) // 2, y + 16), label, fill=WHITE if color != GOLD else BG, font=font_tag)
    draw.text((MARGIN + 150, y + 15), title, fill=WHITE, font=font_body_bold)
    # Desc with wrapping inside box
    desc_words = desc.split()
    desc_lines = []
    cur = ""
    for w in desc_words:
        test = cur + " " + w if cur else w
        bbox2 = draw.textbbox((0, 0), test, font=font_small)
        if bbox2[2] - bbox2[0] > TEXT_W - 40:
            if cur: desc_lines.append(cur)
            cur = w
        else:
            cur = test
    if cur: desc_lines.append(cur)
    dy = y + 55
    for dl in desc_lines:
        draw.text((MARGIN + 25, dy), dl, fill=DIMMED, font=font_small)
        dy += 28
    y += 155

add_branding(draw)
img.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("  Saved slide-04.png")


# ============ SLIDE 5: THE RESULT ============
print("Generating Slide 5 (The Result)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "THE RESULT", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50

stats = [
    ("30 HOURS", "saved per week"),
    ("DAILY SIGNALS", "without me charting"),
    ("45 MINUTES", "to build content calendar"),
]
for big, small in stats:
    draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 100], radius=12, fill=DARK_PANEL, outline=GOLD, width=2)
    draw_text_centered(draw, big, y + 15, font_stat, GOLD)
    draw_text_centered(draw, small, y + 62, font_small, DIMMED)
    y += 120

y += 10
y = draw_text_left(draw, "More time for strategy, community, and product building.", y, font_body_bold, WHITE)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("  Saved slide-05.png")


# ============ SLIDE 6: CTA ============
print("Generating Slide 6 (CTA)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 300
draw_text_centered(draw, "WANT THE FULL", y, font_subhead, WHITE)
y += 50
draw_text_centered(draw, "BREAKDOWN?", y, font_big2, RED)
y += 90
draw_red_line(draw, y, 400)
y += 60
btn_w = 600
btn_h = 85
btn_x = (W - btn_w) // 2
draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h], radius=16, fill=RED)
draw_text_centered(draw, "COMMENT  OS", y + 18, font_cta, WHITE)
y += btn_h + 40
draw_text_centered(draw, "and I'll send you the full", y, font_body, DIMMED)
y += 38
draw_text_centered(draw, "breakdown of how Quivira OS works.", y, font_body, DIMMED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-06.png"), quality=95)
print("  Saved slide-06.png")

print("\nALL 6 QUIVIRA OS SLIDES GENERATED.")
