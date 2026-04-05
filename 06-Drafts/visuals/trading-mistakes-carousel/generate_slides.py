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
font_cta = get_font(40, True)
font_big = get_font(64, True)
font_big2 = get_font(56, True)
font_mistake_num = get_font(20, True)

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
img = new_slide(os.path.join(output_dir, "mistakes_cover.png"))
draw = ImageDraw.Draw(img)
y = 300
draw_text_centered(draw, "5 MISTAKES", y, font_big, RED)
y += 80
draw_text_centered(draw, "THAT COST BEGINNERS", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, "$10K+", y, font_big, GOLD)
y += 100
draw_red_line(draw, y, 300)
y += 40
draw_text_centered(draw, "I made all of them", y, font_body, DIMMED)
y += 38
draw_text_centered(draw, "so you don't have to.", y, font_body, DIMMED)
add_branding(draw)
draw_text_centered(draw, "SWIPE >", H - 120, font_tag, GRAY)
img.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("  Saved slide-01.png")


# ============ SLIDE 2: MISTAKE 1 — No Stop Loss ============
print("Generating Slide 2 (No Stop Loss)...")
img = new_slide()
draw = ImageDraw.Draw(img)
# Mistake badge
draw.rounded_rectangle([MARGIN, 160, MARGIN + 220, 205], radius=8, fill=RED)
draw.text((MARGIN + 15, 168), "MISTAKE 1 OF 5", fill=WHITE, font=font_mistake_num)
y = 240
draw_text_centered(draw, "NO STOP LOSS", y, font_big2, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "You're not being patient.", y, font_body_bold, WHITE)
y += 15
y = draw_text_left(draw, "You're being reckless.", y, font_body_bold, RED)
y += 30
y = draw_text_left(draw, "Every trade without a stop loss is an invitation for the market to take your whole bag.", y, font_body, LIGHT)
y += 40
draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 80], radius=12, fill=DARK_PANEL, outline=GOLD, width=2)
draw_text_centered(draw, "Set the SL before you enter. No exceptions.", y + 22, font_body_bold, GOLD)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("  Saved slide-02.png")


# ============ SLIDE 3: MISTAKE 2 — Oversizing ============
print("Generating Slide 3 (Oversizing)...")
img = new_slide()
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([MARGIN, 160, MARGIN + 220, 205], radius=8, fill=RED)
draw.text((MARGIN + 15, 168), "MISTAKE 2 OF 5", fill=WHITE, font=font_mistake_num)
y = 240
draw_text_centered(draw, "OVERSIZING", y, font_big2, RED)
y += 65
draw_text_centered(draw, "POSITIONS", y, font_big2, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "Risking 20% of your portfolio on one trade is not conviction.", y, font_body, LIGHT)
y += 20
y = draw_text_left(draw, "It's gambling.", y, font_body_bold, RED)
y += 30
y = draw_text_left(draw, "Professional traders risk 1-2% per trade. That's how you survive long enough to win.", y, font_body, LIGHT)
y += 40
# Comparison boxes
box_w = (TEXT_W - 20) // 2
draw.rounded_rectangle([MARGIN, y, MARGIN + box_w, y + 90], radius=10, fill=(60, 20, 20), outline=RED)
draw_text_centered(draw, "Beginner", y + 10, font_tag, RED, max_width=box_w)
draw_text_centered(draw, "20% risk", y + 45, font_body_bold, WHITE, max_width=box_w)
draw.rounded_rectangle([MARGIN + box_w + 20, y, W - MARGIN, y + 90], radius=10, fill=(20, 40, 20), outline=(80, 200, 80))
x2_center = MARGIN + box_w + 20 + box_w // 2
draw.text((MARGIN + box_w + 20 + (box_w - draw.textbbox((0,0), "Pro", font=font_tag)[2]) // 2, y + 10), "Pro", fill=(80, 200, 80), font=font_tag)
draw.text((MARGIN + box_w + 20 + (box_w - draw.textbbox((0,0), "1-2% risk", font=font_body_bold)[2]) // 2, y + 45), "1-2% risk", fill=WHITE, font=font_body_bold)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("  Saved slide-03.png")


# ============ SLIDE 4: MISTAKE 3 — Revenge Trading ============
print("Generating Slide 4 (Revenge Trading)...")
img = new_slide(os.path.join(output_dir, "mistakes_revenge.png"))
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([MARGIN, 160, MARGIN + 220, 205], radius=8, fill=RED)
draw.text((MARGIN + 15, 168), "MISTAKE 3 OF 5", fill=WHITE, font=font_mistake_num)
y = 240
draw_text_centered(draw, "REVENGE", y, font_big2, RED)
y += 65
draw_text_centered(draw, "TRADING", y, font_big2, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "You lost. Now you want it back immediately.", y, font_body, LIGHT)
y += 20
y = draw_text_left(draw, "So you take a bigger position on a worse setup.", y, font_body, LIGHT)
y += 30
y = draw_text_left(draw, "This is how $500 losses become $5,000 losses.", y, font_body_bold, RED)
y += 40
draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 80], radius=12, fill=DARK_PANEL, outline=GOLD, width=2)
draw_text_centered(draw, "Walk away. The market will be here tomorrow.", y + 22, font_body_bold, GOLD)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("  Saved slide-04.png")


# ============ SLIDE 5: MISTAKE 4 — Ignoring Confluence ============
print("Generating Slide 5 (Ignoring Confluence)...")
img = new_slide()
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([MARGIN, 160, MARGIN + 220, 205], radius=8, fill=RED)
draw.text((MARGIN + 15, 168), "MISTAKE 4 OF 5", fill=WHITE, font=font_mistake_num)
y = 240
draw_text_centered(draw, "IGNORING", y, font_big2, RED)
y += 65
draw_text_centered(draw, "CONFLUENCE", y, font_big2, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "One indicator is not a signal.", y, font_body_bold, WHITE)
y += 20
y = draw_text_left(draw, "You need confluence.", y, font_body, LIGHT)
y += 30
# Three pillars
pillars = ["Structure", "Volume", "Momentum"]
pill_w = (TEXT_W - 40) // 3
for i, p in enumerate(pillars):
    px = MARGIN + i * (pill_w + 20)
    draw.rounded_rectangle([px, y, px + pill_w, y + 70], radius=10, fill=DARK_PANEL, outline=GOLD, width=2)
    bbox = draw.textbbox((0, 0), p, font=font_body_bold)
    tw = bbox[2] - bbox[0]
    draw.text((px + (pill_w - tw) // 2, y + 20), p, fill=GOLD, font=font_body_bold)
y += 100
y = draw_text_left(draw, "All three must agree.", y, font_body_bold, WHITE)
y += 20
y = draw_text_left(draw, "If they don't, you don't trade.", y, font_body, RED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("  Saved slide-05.png")


# ============ SLIDE 6: MISTAKE 5 — No System ============
print("Generating Slide 6 (No System)...")
img = new_slide()
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([MARGIN, 160, MARGIN + 220, 205], radius=8, fill=RED)
draw.text((MARGIN + 15, 168), "MISTAKE 5 OF 5", fill=WHITE, font=font_mistake_num)
y = 240
draw_text_centered(draw, "TRADING WITHOUT", y, font_big2, RED)
y += 65
draw_text_centered(draw, "A SYSTEM", y, font_big2, RED)
y += 80
draw_red_line(draw, y)
y += 50
items = ["No journal.", "No rules.", "No risk parameters.", "Just vibes."]
for item in items:
    draw.text((MARGIN, y), "X", fill=RED, font=font_body_bold)
    draw.text((MARGIN + 35, y), item, fill=LIGHT, font=font_body)
    y += 42
y += 20
y = draw_text_left(draw, "That's not trading.", y, font_body_bold, WHITE)
y += 15
y = draw_text_left(draw, "That's scrolling charts with money on the line.", y, font_body, RED)
y += 30
draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 70], radius=12, fill=DARK_PANEL, outline=GOLD, width=2)
draw_text_centered(draw, "A system removes emotion.", y + 18, font_body_bold, GOLD)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-06.png"), quality=95)
print("  Saved slide-06.png")


# ============ SLIDE 7: CTA ============
print("Generating Slide 7 (CTA)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 250
draw_text_centered(draw, "WANT THE", y, font_subhead, WHITE)
y += 50
draw_text_centered(draw, "FULL SYSTEM?", y, font_big2, RED)
y += 90
draw_red_line(draw, y, 400)
y += 50
y = draw_text_centered(draw, "I teach risk management,", y, font_body, LIGHT)
y += 5
y = draw_text_centered(draw, "confluence trading, and position sizing", y, font_body, LIGHT)
y += 5
y = draw_text_centered(draw, "in Week 1.", y, font_body_bold, WHITE)
y += 40
btn_w = 700
btn_h = 85
btn_x = (W - btn_w) // 2
draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h], radius=16, fill=RED)
draw_text_centered(draw, "COMMENT CHECKLIST", y + 18, font_cta, WHITE)
y += btn_h + 30
draw_text_centered(draw, "and I'll send you the free", y, font_body, DIMMED)
y += 38
draw_text_centered(draw, "risk management guide.", y, font_body, DIMMED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-07.png"), quality=95)
print("  Saved slide-07.png")

print("\nALL 7 TRADING MISTAKES SLIDES GENERATED.")
