from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
MARGIN = 80
TEXT_W = W - MARGIN * 2

# Colors
BG = (10, 10, 15)
WHITE = (255, 255, 255)
LIGHT = (230, 230, 230)
RED = (230, 57, 70)
GOLD = (255, 215, 0)
DARK_PANEL = (26, 26, 46)
GRAY = (150, 150, 150)

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

font_headline = get_font(52, True)
font_subhead = get_font(38, True)
font_body = get_font(30, False)
font_body_bold = get_font(30, True)
font_small = get_font(24, False)
font_tag = get_font(22, True)
font_cta = get_font(44, True)
font_token = get_font(28, True)
font_big = get_font(72, True)
font_big2 = get_font(60, True)
font_big3 = get_font(48, True)

def new_slide(bg_path=None):
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).resize((W, H))
        overlay = Image.new("RGBA", (W, H), (10, 10, 15, 160))
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
img = new_slide(os.path.join(output_dir, "slide1_cover.png"))
draw = ImageDraw.Draw(img)
y = 280
draw_text_centered(draw, "THE SEC JUST CLEARED", y, font_headline, RED)
y += 70
draw_text_centered(draw, "16 TOKENS", y, font_big, GOLD)
y += 100
draw_red_line(draw, y, 300)
y += 40
draw_text_centered(draw, "HERE'S WHAT IT MEANS", y, font_subhead, WHITE)
y += 50
draw_text_centered(draw, "FOR YOUR BAG.", y, font_subhead, WHITE)
add_branding(draw)
draw_text_centered(draw, "SWIPE >", H - 120, font_tag, GRAY)
img.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("  Saved slide-01.png")


# ============ SLIDE 2: WHAT HAPPENED ============
print("Generating Slide 2 (What Happened)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "WHAT HAPPENED", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
texts = [
    ("On March 17, the SEC classified 16 crypto tokens as", False),
    ('"digital commodities."', True),
    ("", False),
    ("Not securities. Commodities.", True),
    ("", False),
    ("This is the biggest regulatory green light crypto has ever received.", False),
]
for t, bold in texts:
    if t == "":
        y += 20
    else:
        f = font_body_bold if bold else font_body
        c = WHITE if bold else LIGHT
        y = draw_text_left(draw, t, y, f, c)
        y += 10
draw.rounded_rectangle([MARGIN, y + 20, W - MARGIN, y + 100], radius=12, fill=DARK_PANEL, outline=RED)
draw_text_centered(draw, "Commodities = treated like gold or oil", y + 45, font_body_bold, GOLD)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("  Saved slide-02.png")


# ============ SLIDE 3: TOKEN LIST ============
print("Generating Slide 3 (Token List)...")
img = new_slide(os.path.join(output_dir, "slide3_tokens.png"))
draw = ImageDraw.Draw(img)
y = 180
draw_text_centered(draw, "THE FULL LIST", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
tokens = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK",
          "DOT", "LTC", "BCH", "ALGO", "XLM", "FIL", "HBAR", "ICP"]
cols, rows = 4, 4
badge_w, badge_h = 190, 60
gap_x, gap_y = 30, 25
start_x = (W - (cols * badge_w + (cols - 1) * gap_x)) // 2
for i, token in enumerate(tokens):
    row = i // cols
    col = i % cols
    x = start_x + col * (badge_w + gap_x)
    by = y + row * (badge_h + gap_y)
    draw.rounded_rectangle([x, by, x + badge_w, by + badge_h], radius=10, fill=DARK_PANEL, outline=GOLD, width=2)
    bbox = draw.textbbox((0, 0), token, font=font_token)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (badge_w - tw) // 2
    ty = by + (badge_h - th) // 2 - 2
    draw.text((tx, ty), token, fill=GOLD, font=font_token)
y += rows * (badge_h + gap_y) + 40
draw_text_centered(draw, "If you hold any of these,", y, font_body, LIGHT)
y += 40
draw_text_centered(draw, "your bags just got legal clarity.", y, font_body_bold, WHITE)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("  Saved slide-03.png")


# ============ SLIDE 4: COMMODITY MEANING ============
print("Generating Slide 4 (Commodity Meaning)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "WHAT DOES", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, '"COMMODITY" MEAN?', y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
benefits = [
    ("Treated like gold or oil", "under US law"),
    ("No more securities lawsuits", "against these tokens"),
    ("Exchanges can list them", "freely without fear"),
    ("Funds can buy them", "without legal risk"),
]
for title, subtitle in benefits:
    draw.text((MARGIN, y - 4), "\u2713", fill=RED, font=font_subhead)
    draw.text((MARGIN + 45, y), title, fill=WHITE, font=font_body_bold)
    y += 38
    draw.text((MARGIN + 45, y), subtitle, fill=(180, 180, 180), font=font_small)
    y += 50
add_branding(draw)
img.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("  Saved slide-04.png")


# ============ SLIDE 5: STAKING UNLOCK ============
print("Generating Slide 5 (Staking Unlock)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "THE STAKING", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, "UNLOCK", y, font_big2, GOLD)
y += 90
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "Staking and airdrops are officially cleared under federal law.", y, font_body, LIGHT)
y += 30
y = draw_text_left(draw, "Projects can now distribute rewards without triggering SEC enforcement.", y, font_body, LIGHT)
y += 40
draw.rounded_rectangle([MARGIN, y, W - MARGIN, y + 120], radius=12, fill=DARK_PANEL, outline=RED)
draw_text_centered(draw, "This is massive for DeFi.", y + 20, font_subhead, RED)
draw_text_centered(draw, "Innovation is unblocked.", y + 70, font_body_bold, WHITE)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("  Saved slide-05.png")


# ============ SLIDE 6: PRICE IMPACT ============
print("Generating Slide 6 (Price Impact)...")
img = new_slide(os.path.join(output_dir, "slide6_price.png"))
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "WHAT IT MEANS", y, font_headline, WHITE)
y += 60
draw_text_centered(draw, "FOR PRICE", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "Less regulatory fear = more institutional flow.", y, font_body_bold, WHITE)
y += 30
y = draw_text_left(draw, "BlackRock already launched a staked ETH ETF on March 12.", y, font_body, LIGHT)
y += 30
draw.rounded_rectangle([MARGIN, y + 10, W - MARGIN, y + 130], radius=16, fill=DARK_PANEL, outline=GOLD, width=2)
draw_text_centered(draw, "ETH UP 20%", y + 30, font_big3, GOLD)
draw_text_centered(draw, "in just 10 days", y + 85, font_body, LIGHT)
y += 160
draw_text_left(draw, "Follow the money.", y, font_subhead, RED)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-06.png"), quality=95)
print("  Saved slide-06.png")


# ============ SLIDE 7: WHAT'S NEXT ============
print("Generating Slide 7 (What's Next)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 200
draw_text_centered(draw, "WHAT'S NEXT?", y, font_headline, RED)
y += 80
draw_red_line(draw, y)
y += 50
y = draw_text_left(draw, "The CLARITY Act is finalizing stablecoin yield rules.", y, font_body, LIGHT)
y += 30
y = draw_text_left(draw, "Regulation is becoming a foundation, not a threat.", y, font_body_bold, WHITE)
y += 40
y = draw_text_left(draw, "Builders win from here.", y, font_subhead, GOLD)
y += 60
items = [
    ("Q2 2026", "CLARITY Act vote"),
    ("90 DAYS", "Liquidity deepens on all 16"),
    ("NOW", "Institutional staking live"),
]
for label, desc in items:
    draw.rounded_rectangle([MARGIN, y, MARGIN + 130, y + 45], radius=8, fill=RED)
    bbox = draw.textbbox((0, 0), label, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + (130 - tw) // 2, y + 10), label, fill=WHITE, font=font_tag)
    draw.text((MARGIN + 150, y + 10), desc, fill=LIGHT, font=font_body)
    y += 65
add_branding(draw)
img.save(os.path.join(output_dir, "slide-07.png"), quality=95)
print("  Saved slide-07.png")


# ============ SLIDE 8: CTA ============
print("Generating Slide 8 (CTA)...")
img = new_slide()
draw = ImageDraw.Draw(img)
y = 320
draw_text_centered(draw, "WANT THE FULL", y, font_subhead, WHITE)
y += 50
draw_text_centered(draw, "BREAKDOWN?", y, font_big2, RED)
y += 100
draw_red_line(draw, y, 400)
y += 60
btn_w = 700
btn_h = 90
btn_x = (W - btn_w) // 2
draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h], radius=16, fill=RED)
draw_text_centered(draw, "COMMENT  CLEARED", y + 20, font_cta, WHITE)
y += btn_h + 40
draw_text_centered(draw, "and I'll send you the full", y, font_body, LIGHT)
y += 40
draw_text_centered(draw, "breakdown with tokens to watch next.", y, font_body, LIGHT)
add_branding(draw)
img.save(os.path.join(output_dir, "slide-08.png"), quality=95)
print("  Saved slide-08.png")

print()
print("ALL 8 SLIDES GENERATED SUCCESSFULLY.")
