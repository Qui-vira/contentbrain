"""
Batch Graphics Generator — March 26, 2026
8 graphics across 5 posts. AI backgrounds via fal.ai + Pillow compositing.
Canvas: 1200x675 (16:9 Twitter/LinkedIn standard)

Posts:
1. $14B Derivatives Expiry Warning (Tweet) — 1 graphic
2. Bear Market Built The Machine (Tweet) — 1 graphic
3. 30 Hours to 3 Hours — Automation Story (LinkedIn) — 1 graphic
4. Weekly Market Recap Mar 23-28 (Thread) — 3 graphics (hook, ETH, levels)
5. Q2 Preview — Community Tweet — 1 graphic
"""

import requests, os, time, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
load_dotenv()

FAL_KEY = os.getenv("FAL_KEY")
fal_headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

# === BRAND ===
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
ORANGE = (255, 165, 0)

W, H = 1200, 675
BASE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE, "backgrounds")
os.makedirs(BG_DIR, exist_ok=True)

# === FONTS ===
def lf(size, bold=False):
    p = f"C:/Windows/Fonts/{'arialbd.ttf' if bold else 'arial.ttf'}"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

F_HERO = lf(64, True)
F_HEAD = lf(44, True)
F_SUB = lf(32, True)
F_BODY = lf(26, False)
F_BODY_B = lf(26, True)
F_SM = lf(20, False)
F_TAG = lf(18, True)
F_STAT = lf(52, True)
F_MEGA = lf(80, True)

# === HELPERS ===
def glow(img, text, x, y, font, color, r=10, a=120):
    g = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(g).text((x,y), text, fill=(*color[:3],a), font=font)
    g = g.filter(ImageFilter.GaussianBlur(r))
    img = Image.alpha_composite(img, g)
    ImageDraw.Draw(img).text((x,y), text, fill=(*color[:3],255), font=font)
    return img

def orb(img, cx, cy, radius, color, alpha=40):
    o = Image.new("RGBA", img.size, (0,0,0,0))
    od = ImageDraw.Draw(o)
    for i in range(20, 0, -1):
        r = int(radius * i / 20)
        a = int(alpha * (1 - i/20))
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*color[:3],a))
    return Image.alpha_composite(img, o)

def glass(img, x1, y1, x2, y2, fa=140, bc=(255,255,255), ba=30, rad=12):
    p = Image.new("RGBA", img.size, (0,0,0,0))
    pd = ImageDraw.Draw(p)
    pd.rounded_rectangle([x1,y1,x2,y2], radius=rad, fill=(26,26,46,fa))
    pd.rounded_rectangle([x1,y1,x2,y2], radius=rad, outline=(*bc[:3],ba), width=1)
    return Image.alpha_composite(img, p)

def vignette(img, s=60):
    v = Image.new("RGBA", img.size, (0,0,0,0))
    vd = ImageDraw.Draw(v)
    w, h = img.size
    for i in range(s):
        a = int((s-i)*2.5)
        m = i * max(w,h) // (s*2)
        vd.rectangle([0,0,w,m], fill=(0,0,0,a))
        vd.rectangle([0,h-m,w,h], fill=(0,0,0,a))
        vd.rectangle([0,0,m,h], fill=(0,0,0,a))
        vd.rectangle([w-m,0,w,h], fill=(0,0,0,a))
    return Image.alpha_composite(img, v)

def accent(img, y, x, width=200, color=QUIVIRA_RED):
    l = Image.new("RGBA", img.size, (0,0,0,0))
    ld = ImageDraw.Draw(l)
    ld.rectangle([x-4,y-3,x+width+4,y+6], fill=(*color[:3],50))
    ld.rectangle([x,y,x+width,y+3], fill=(*color,255))
    return Image.alpha_composite(img, l)

def brand(img):
    ImageDraw.Draw(img).text((60, H-38), "@big_quiv", fill=(*GRAY,200), font=F_SM)
    return img

def grid(img, sp=60, alpha=5):
    g = Image.new("RGBA", img.size, (0,0,0,0))
    gd = ImageDraw.Draw(g)
    for x in range(0, W, sp): gd.line([(x,0),(x,H)], fill=(255,255,255,alpha), width=1)
    for y in range(0, H, sp): gd.line([(0,y),(W,y)], fill=(255,255,255,alpha), width=1)
    return Image.alpha_composite(img, g)

def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def overlay(img, opacity=160):
    ov = Image.new("RGBA", img.size, (*DEEP_BLACK, opacity))
    return Image.alpha_composite(img, ov)

# === FAL.AI ===
def gen_bg(prompt, filename):
    fp = os.path.join(BG_DIR, filename)
    if os.path.exists(fp):
        print(f"  [cached] {filename}")
        return fp
    print(f"  [gen] {filename}...")
    payload = {
        "prompt": prompt,
        "negative_prompt": "text, words, letters, numbers, watermark, logo, blurry, low quality, cartoon, anime, distorted, bright cheerful, flat lighting",
        "image_size": {"width": 1200, "height": 675},
        "num_images": 1, "guidance_scale": 7.5, "num_inference_steps": 30
    }
    resp = requests.post("https://queue.fal.run/fal-ai/nano-banana-pro", json=payload, headers=fal_headers, timeout=30)
    resp.raise_for_status()
    rid = resp.json()["request_id"]
    for _ in range(60):
        time.sleep(3)
        st = requests.get(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}/status", headers=fal_headers, timeout=15).json()
        if st.get("status") == "COMPLETED": break
    result = requests.get(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}", headers=fal_headers, timeout=30).json()
    if "images" not in result or not result["images"]:
        print(f"  [retry] {filename} - no images in result, retrying...")
        time.sleep(5)
        # Retry once
        resp2 = requests.post("https://queue.fal.run/fal-ai/nano-banana-pro", json=payload, headers=fal_headers, timeout=30)
        resp2.raise_for_status()
        rid2 = resp2.json()["request_id"]
        for _ in range(60):
            time.sleep(3)
            st2 = requests.get(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid2}/status", headers=fal_headers, timeout=15).json()
            if st2.get("status") == "COMPLETED": break
        result = requests.get(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid2}", headers=fal_headers, timeout=30).json()
        if "images" not in result or not result["images"]:
            print(f"  [fallback] {filename} - using gradient background")
            # Create gradient fallback
            from PIL import Image as PILImage, ImageDraw as PILDraw
            fallback = PILImage.new("RGBA", (1200, 675))
            fd = PILDraw.Draw(fallback)
            for y in range(675):
                t = y / 675
                r = int(10 + 15 * t); g = int(10 + 5 * t); b = int(15 + 25 * t)
                fd.line([(0,y),(1200,y)], fill=(r,g,b,255))
            fallback.save(fp, "PNG")
            return fp
    img_url = result["images"][0]["url"]
    data = requests.get(img_url, timeout=60).content
    with open(fp, "wb") as f: f.write(data)
    print(f"  [saved] {filename}")
    return fp

# =============================================================================
# 1. $14B DERIVATIVES EXPIRY WARNING
# =============================================================================
def build_derivs_expiry(bg_path):
    print("  Compositing: derivs-expiry...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 155)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 850, 300, 350, QUIVIRA_RED, 25)
    img = orb(img, 250, 350, 250, ORANGE, 12)

    x = 60; y = 55
    img = glass(img, x, y, x+280, y+32, fa=160, bc=QUIVIRA_RED, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "OPTIONS EXPIRY ALERT", fill=QUIVIRA_RED, font=F_TAG)
    y += 50

    img = glow(img, "$14 Billion", x, y, F_HERO, GOLD, r=16, a=150)
    y += 75
    img = glow(img, "BTC Options Expire Tomorrow", x, y, F_SUB, WHITE, r=6, a=70)
    y += 48
    img = accent(img, y, x, 160)
    y += 22
    d = ImageDraw.Draw(img)
    d.text((x, y), "Largest quarterly expiry of 2026.", fill=LIGHT, font=F_BODY)
    y += 32
    d.text((x, y), "Nobody's talking about what happens next.", fill=DIMMED, font=F_BODY)

    # Right: stat cards
    sx = 700; sy = 80
    img = glass(img, sx, sy, sx+440, sy+130, fa=120, bc=GOLD, ba=50, rad=14)
    img = orb(img, sx+220, sy+65, 100, GOLD, 15)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy+15), "MAX PAIN", fill=DIMMED, font=F_TAG)
    img = glow(img, "$75K", sx+25, sy+42, F_STAT, GOLD, r=12, a=130)
    d = ImageDraw.Draw(img)
    d.text((sx+220, sy+55), "BTC hovers at $70K", fill=LIGHT, font=F_SM)
    d.text((sx+220, sy+80), "7% gap begging to close", fill=GOLD, font=F_SM)

    sy2 = sy + 150
    img = glass(img, sx, sy2, sx+440, sy2+130, fa=120, bc=QUIVIRA_RED, ba=50, rad=14)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy2+15), "GAMMA EFFECT", fill=DIMMED, font=F_TAG)
    img = glow(img, "60%", sx+25, sy2+42, F_STAT, QUIVIRA_RED, r=12, a=130)
    d = ImageDraw.Draw(img)
    d.text((sx+180, sy2+55), "of quarterly expiries", fill=LIGHT, font=F_SM)
    d.text((sx+180, sy2+80), "pull price toward max pain", fill=LIGHT, font=F_SM)

    sy3 = sy2 + 150
    img = glass(img, sx, sy3, sx+440, sy3+95, fa=100, bc=ORANGE, ba=40, rad=14)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy3+12), "RISK STACK", fill=DIMMED, font=F_TAG)
    d.text((sx+25, sy3+40), "Options + PCE Data + Iran", fill=ORANGE, font=F_BODY_B)
    d.text((sx+25, sy3+68), "All in one 24-hour window", fill=DIMMED, font=F_SM)

    img = brand(img)
    out = os.path.join(BASE, "01-derivs-expiry.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 2. BEAR MARKET BUILT THE MACHINE
# =============================================================================
def build_bear_machine(bg_path):
    print("  Compositing: bear-machine...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 150)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 300, 340, 300, QUIVIRA_RED, 20)
    img = orb(img, 900, 300, 250, GOLD, 15)

    x = 60; y = 80
    img = glass(img, x, y, x+180, y+32, fa=160, bc=QUIVIRA_RED, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "BEAR MARKET", fill=QUIVIRA_RED, font=F_TAG)
    y += 55

    img = glow(img, "Built The", x, y, F_HEAD, WHITE, r=8, a=80)
    y += 52
    img = glow(img, "Machine.", x, y, F_HEAD, GOLD, r=10, a=120)
    y += 65
    img = accent(img, y, x, 140)
    y += 25
    d = ImageDraw.Draw(img)
    d.text((x, y), "While everyone doom-scrolled in 2023,", fill=LIGHT, font=F_BODY)
    y += 32
    d.text((x, y), "I was writing scripts and testing scanners.", fill=LIGHT, font=F_BODY)
    y += 40
    d.text((x, y), "Today my AI scans", fill=DIMMED, font=F_BODY)
    w1 = tw(d, "Today my AI scans ", F_BODY)
    d.text((x+w1, y), "50 pairs every 4 hours.", fill=GOLD, font=F_BODY_B)
    y += 32
    d.text((x, y), "I wake up. Review. Approve. Done.", fill=WHITE, font=F_BODY_B)

    # Right: before/after stat
    sx = 720; sy = 130
    img = glass(img, sx, sy, sx+420, sy+180, fa=110, bc=RED_DIM, ba=50, rad=14)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy+15), "BEFORE", fill=RED_DIM, font=F_TAG)
    img = glow(img, "4 hrs/day", sx+25, sy+45, F_SUB, RED_DIM, r=8, a=90)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy+90), "Manual charting", fill=DIMMED, font=F_SM)
    d.rectangle([sx+25, sy+120, sx+395, sy+121], fill=(*PANEL_BORDER, 100))
    d.text((sx+25, sy+130), "NOW", fill=GREEN, font=F_TAG)
    img = glow(img, "10 min/day", sx+25, sy+155, F_SUB, GREEN, r=8, a=90)

    sy2 = sy + 200
    img = glass(img, sx, sy2, sx+420, sy2+120, fa=110, bc=GOLD, ba=45, rad=14)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy2+15), "THE RESULT", fill=DIMMED, font=F_TAG)
    img = glow(img, "50 pairs", sx+25, sy2+42, F_SUB, GOLD, r=8, a=100)
    d = ImageDraw.Draw(img)
    d.text((sx+220, sy2+48), "scanned automatically", fill=DIMMED, font=F_SM)
    d.text((sx+25, sy2+85), "Every 4 hours. Zero manual work.", fill=LIGHT, font=F_SM)

    img = brand(img)
    out = os.path.join(BASE, "02-bear-machine.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 3. 30 HOURS TO 3 HOURS — LINKEDIN
# =============================================================================
def build_automation_linkedin(bg_path):
    print("  Compositing: automation-linkedin...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 155)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 600, 340, 350, GOLD, 15)

    x = 60; y = 50
    img = glass(img, x, y, x+200, y+32, fa=160, bc=GOLD, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "AUTOMATION STORY", fill=GOLD, font=F_TAG)
    y += 55

    # Big before/after numbers side by side
    img = glow(img, "30", x, y, F_MEGA, RED_DIM, r=16, a=120)
    d = ImageDraw.Draw(img)
    w30 = tw(d, "30", F_MEGA)
    d.text((x+w30+10, y+30), "hrs/week", fill=DIMMED, font=F_SUB)

    # Arrow
    arrow_x = x + w30 + 200
    d.text((arrow_x, y+20), "→", fill=GOLD, font=F_HERO)

    img = glow(img, "3", arrow_x + 80, y, F_MEGA, GREEN, r=16, a=120)
    d = ImageDraw.Draw(img)
    w3 = tw(d, "3", F_MEGA)
    d.text((arrow_x + 80 + w3 + 10, y+30), "hrs/week", fill=DIMMED, font=F_SUB)
    y += 100

    img = accent(img, y, x, 500)
    y += 22
    d = ImageDraw.Draw(img)
    d.text((x, y), "27 hours saved weekly. Redirected to strategy.", fill=WHITE, font=F_BODY_B)
    y += 38
    d.text((x, y), "Automation doesn't replace effort. It redirects it.", fill=GOLD, font=F_BODY_B)

    # Bottom cards row
    cy = 340
    cards = [
        ("SIGNALS", "50 pairs / 4 hrs", "10 min vs 4 hrs", QUIVIRA_RED),
        ("CONTENT", "AI-drafted calendar", "45 min vs 8 hrs", GOLD),
        ("FREED TIME", "Strategy & building", "27 hrs/week saved", GREEN),
    ]
    cw = 350
    for i, (label, line1, line2, color) in enumerate(cards):
        cx = 60 + i * (cw + 20)
        img = glass(img, cx, cy, cx+cw, cy+180, fa=110, bc=color, ba=50, rad=14)
        img = orb(img, cx+175, cy+90, 100, color, 12)
        d = ImageDraw.Draw(img)
        d.text((cx+20, cy+15), label, fill=color, font=F_TAG)
        img = glow(img, line1, cx+20, cy+50, F_BODY_B, WHITE, r=4, a=60)
        d = ImageDraw.Draw(img)
        d.text((cx+20, cy+90), line2, fill=DIMMED, font=F_BODY)

        # Mini bar
        bar_y = cy + 130
        d.rectangle([cx+20, bar_y, cx+cw-20, bar_y+6], fill=(*PANEL_BORDER, 150))
        fill_pct = [0.04, 0.09, 1.0][i]
        d.rectangle([cx+20, bar_y, cx+20+int((cw-40)*fill_pct), bar_y+6], fill=(*color, 200))

    img = brand(img)
    out = os.path.join(BASE, "03-automation-linkedin.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 4a. WEEKLY RECAP — HOOK (Tweet 1)
# =============================================================================
def build_recap_hook(bg_path):
    print("  Compositing: recap-hook...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 155)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 600, 340, 400, QUIVIRA_RED, 15)

    x = 60; y = 50
    img = glass(img, x, y, x+280, y+32, fa=160, bc=QUIVIRA_RED, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "WEEKLY MARKET RECAP", fill=QUIVIRA_RED, font=F_TAG)
    y += 50

    img = glow(img, "March 23-28, 2026", x, y, F_HEAD, WHITE, r=8, a=80)
    y += 58
    img = accent(img, y, x, 160)
    y += 22
    d = ImageDraw.Draw(img)
    d.text((x, y), "The biggest week in crypto regulation history.", fill=DIMMED, font=F_BODY)

    # Stat cards grid (2x2)
    stats = [
        ("16", "Tokens cleared\nby the SEC", GOLD, "REGULATION"),
        ("$708M", "BTC ETF\noutflows in 1 day", QUIVIRA_RED, "ETF FLOWS"),
        ("+20%", "ETH rally since\nETHB launch", GREEN, "ETH MOMENTUM"),
        ("$13.5B", "Options expired\non Deribit", ORANGE, "DERIVATIVES"),
    ]
    for i, (val, desc, color, label) in enumerate(stats):
        col = i % 2
        row = i // 2
        cx = 620 + col * 285
        cy = 60 + row * 195
        img = glass(img, cx, cy, cx+270, cy+180, fa=115, bc=color, ba=50, rad=14)
        img = orb(img, cx+135, cy+90, 80, color, 12)
        d = ImageDraw.Draw(img)
        d.text((cx+18, cy+12), label, fill=DIMMED, font=F_TAG)
        img = glow(img, val, cx+18, cy+38, F_SUB, color, r=8, a=100)
        d = ImageDraw.Draw(img)
        for j, line in enumerate(desc.split("\n")):
            d.text((cx+18, cy+85+j*24), line, fill=LIGHT, font=F_SM)

    # Bottom bar
    img = glass(img, 60, H-95, W-60, H-45, fa=100, bc=QUIVIRA_RED, ba=35, rad=10)
    d = ImageDraw.Draw(img)
    d.text((85, H-82), "Fed held rates. Smart money repositioned. What comes next matters more.", fill=WHITE, font=F_BODY_B)

    img = brand(img)
    out = os.path.join(BASE, "04a-recap-hook.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 4b. WEEKLY RECAP — ETH STORY (Tweet 4)
# =============================================================================
def build_recap_eth(bg_path):
    print("  Compositing: recap-eth...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 155)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 400, 300, 300, GOLD, 20)

    x = 60; y = 55
    img = glass(img, x, y, x+220, y+32, fa=160, bc=GOLD, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "ETH IS THE STORY", fill=GOLD, font=F_TAG)
    y += 50

    img = glow(img, "ETH +20%", x, y, F_HERO, GOLD, r=16, a=150)
    y += 78
    img = glow(img, "Since ETHB Launch", x, y, F_SUB, WHITE, r=6, a=70)
    y += 45
    img = accent(img, y, x, 160)
    y += 22
    d = ImageDraw.Draw(img)
    d.text((x, y), "Institutional money doesn't just want ETH exposure.", fill=LIGHT, font=F_BODY)
    y += 30
    d.text((x, y), "They want", fill=LIGHT, font=F_BODY)
    w1 = tw(d, "They want ", F_BODY)
    d.text((x+w1, y), "yield on that exposure.", fill=GOLD, font=F_BODY_B)

    # Right card
    sx = 700; sy = 100
    img = glass(img, sx, sy, sx+440, sy+250, fa=115, bc=GOLD, ba=50, rad=14)
    img = orb(img, sx+220, sy+125, 130, GOLD, 15)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy+18), "BLACKROCK ETHB", fill=DIMMED, font=F_TAG)
    img = glow(img, "Staked ETH ETF", sx+25, sy+48, F_SUB, GOLD, r=8, a=90)
    d = ImageDraw.Draw(img)
    d.text((sx+25, sy+95), "Launched March 12 on Nasdaq", fill=LIGHT, font=F_SM)
    d.rectangle([sx+25, sy+125, sx+415, sy+126], fill=(*PANEL_BORDER, 100))
    d.text((sx+25, sy+140), "~2.5% net staking yield", fill=GREEN, font=F_BODY_B)
    d.text((sx+25, sy+170), "+ price appreciation", fill=GREEN, font=F_BODY_B)
    d.rectangle([sx+25, sy+205, sx+415, sy+206], fill=(*PANEL_BORDER, 100))
    d.text((sx+25, sy+215), "ETHB changes the calculus for every", fill=DIMMED, font=F_SM)
    d.text((sx+25, sy+238), "portfolio manager on the sidelines.", fill=DIMMED, font=F_SM)

    img = brand(img)
    out = os.path.join(BASE, "04b-recap-eth.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 4c. WEEKLY RECAP — LEVELS TO WATCH (Tweet 6)
# =============================================================================
def build_recap_levels(bg_path):
    print("  Compositing: recap-levels...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 175)
    img = vignette(img, 50)
    img = grid(img, 60, 5)
    img = orb(img, 600, 340, 300, QUIVIRA_RED, 10)

    x = 60; y = 35
    img = glow(img, "Next Week: 3 Levels to Watch", x, y, F_SUB, QUIVIRA_RED, r=8, a=100)
    img = accent(img, 75, x, 140)

    # 3 large cards for BTC, ETH, SOL
    tokens = [
        ("BTC", "$71.1K", "support confirmed", "$73K → $78K", "Break above opens new range", GOLD),
        ("ETH", "$4,200", "new floor if ETHB holds", "Staking inflows", "Institutional momentum", GREEN),
        ("SOL", "$185", "close above = new highs", "Watch daily close", "Breakout confirmation", QUIVIRA_RED),
    ]
    cw = 360
    for i, (token, level, desc, target, target_desc, color) in enumerate(tokens):
        cx = 50 + i * (cw + 20)
        cy = 95
        img = glass(img, cx, cy, cx+cw, cy+340, fa=115, bc=color, ba=50, rad=14)
        img = orb(img, cx+180, cy+170, 120, color, 12)
        d = ImageDraw.Draw(img)
        d.text((cx+20, cy+15), token, fill=color, font=F_TAG)
        img = glow(img, level, cx+20, cy+45, F_STAT, color, r=12, a=120)
        d = ImageDraw.Draw(img)
        d.text((cx+20, cy+110), desc, fill=LIGHT, font=F_BODY)
        d.rectangle([cx+20, cy+150, cx+cw-20, cy+151], fill=(*PANEL_BORDER, 100))
        d.text((cx+20, cy+165), "TARGET", fill=DIMMED, font=F_TAG)
        d.text((cx+20, cy+195), target, fill=WHITE, font=F_BODY_B)
        d.text((cx+20, cy+230), target_desc, fill=DIMMED, font=F_SM)

        # Visual bar
        bar_y = cy + 280
        d.rectangle([cx+20, bar_y, cx+cw-20, bar_y+8], fill=(*PANEL_BORDER, 150))
        d.rectangle([cx+20, bar_y, cx+20+int((cw-40)*0.6), bar_y+8], fill=(*color, 180))

    # Bottom CTA
    img = glass(img, 50, H-80, W-50, H-30, fa=100, bc=GOLD, ba=35, rad=10)
    d = ImageDraw.Draw(img)
    d.text((75, H-66), "Krib members get this analysis before it hits the timeline. DM 'KRIB' for access.", fill=WHITE, font=F_BODY_B)

    img = brand(img)
    out = os.path.join(BASE, "04c-recap-levels.png")
    img.save(out, "PNG", quality=95)
    return out

# =============================================================================
# 5. Q2 PREVIEW — COMMUNITY TWEET
# =============================================================================
def build_q2_preview(bg_path):
    print("  Compositing: q2-preview...")
    bg = Image.open(bg_path).resize((W,H)).convert("RGBA")
    img = overlay(bg, 155)
    img = vignette(img, 50)
    img = grid(img, 60, 4)
    img = orb(img, 600, 340, 350, GOLD, 18)
    img = orb(img, 200, 200, 200, GREEN, 10)

    x = 60; y = 55
    img = glass(img, x, y, x+180, y+32, fa=160, bc=GREEN, ba=80, rad=6)
    ImageDraw.Draw(img).text((x+12, y+6), "Q2 OUTLOOK", fill=GREEN, font=F_TAG)
    y += 50

    img = glow(img, "Q2 Is Setting Up", x, y, F_HEAD, WHITE, r=8, a=80)
    y += 52
    img = glow(img, "To Be Violent.", x, y, F_HEAD, GOLD, r=10, a=120)
    y += 60
    img = accent(img, y, x, 140)
    y += 22
    d = ImageDraw.Draw(img)
    d.text((x, y), "In a good way.", fill=DIMMED, font=F_BODY)

    # Right: 3 catalyst cards stacked
    sx = 650; sy = 70
    catalysts = [
        ("CLARITY ACT", "Stablecoin vote next week", "Yield regulation, not a ban", GREEN),
        ("BTC BREAKOUT", "$73K resistance in play", "$71.1K support held through expiry", GOLD),
        ("ETH MOMENTUM", "Institutional staking live", "ETHB driving 20% rally", QUIVIRA_RED),
    ]
    for i, (label, line1, line2, color) in enumerate(catalysts):
        cy = sy + i * 145
        img = glass(img, sx, cy, sx+490, cy+130, fa=115, bc=color, ba=50, rad=14)
        d = ImageDraw.Draw(img)
        d.text((sx+20, cy+12), label, fill=color, font=F_TAG)
        d.text((sx+20, cy+42), line1, fill=WHITE, font=F_BODY_B)
        d.text((sx+20, cy+75), line2, fill=DIMMED, font=F_BODY)

    # Bottom bar
    img = glass(img, 60, H-80, W-60, H-30, fa=100, bc=GOLD, ba=35, rad=10)
    d = ImageDraw.Draw(img)
    d.text((85, H-66), "Reply with your top hold going into Q2.", fill=WHITE, font=F_BODY_B)

    img = brand(img)
    out = os.path.join(BASE, "05-q2-preview.png")
    img.save(out, "PNG", quality=95)
    return out


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=== Batch Graphics: 8 slides, 5 posts ===\n")

    print("[1/2] Generating AI backgrounds via fal.ai...\n")

    prompts = {
        "bg_derivs.png": "Massive Deribit trading terminal screens glowing in dark room, red warning indicators flashing, billions in crypto options contracts visible as abstract light streams, dark moody atmosphere #0A0A0F, #E63946 red warning glow, #FFD700 gold price tickers, cinematic wide angle, volumetric fog, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_bear.png": "Lone figure standing before massive industrial machine made of light and code, dark factory environment transforming from rust and decay into golden glowing circuits, bear transforming into bull silhouette, dark moody atmosphere #0A0A0F, #E63946 red sparks, #FFD700 gold energy, cinematic, volumetric lighting, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_auto.png": "Split scene showing chaotic cluttered desk with papers and charts on left dissolving into clean minimalist workstation with holographic AI dashboard on right, productivity transformation, dark moody atmosphere #0A0A0F, warm golden light on right side #FFD700, cool blue-red on left, cinematic, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_recap.png": "Massive holographic globe showing crypto market data flows between continents, institutional buildings connected by golden light streams, dark moody atmosphere #0A0A0F, #E63946 red data points, #FFD700 gold flow lines, cinematic wide establishing shot, volumetric lighting, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_eth.png": "Ethereum crystal floating above institutional vault, staking energy flowing as golden spirals around the crystal, dark moody atmosphere #0A0A0F, #FFD700 gold energy streams, #E63946 red ambient glow, cinematic close-up, shallow depth of field, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_levels.png": "Dark trading command center with three large holographic displays showing price charts, military-grade precision aesthetic, dark moody atmosphere #0A0A0F, #E63946 red indicators, #FFD700 gold price levels, cinematic, volumetric fog, 8k quality, no text, no words, no letters, no watermark, photorealistic",
        "bg_q2.png": "Dramatic sunrise breaking through storm clouds over futuristic cityscape, golden light rays piercing dark atmosphere, crypto bull emerging from shadows into light, dark to golden transition, #0A0A0F to #FFD700 gradient, cinematic, epic scale, volumetric god rays, 8k quality, no text, no words, no letters, no watermark, photorealistic",
    }

    bg_paths = {}
    for fname, prompt in prompts.items():
        bg_paths[fname] = gen_bg(prompt, fname)

    print("\n[2/2] Compositing all slides...\n")

    results = []
    results.append(("$14B Derivs Expiry", build_derivs_expiry(bg_paths["bg_derivs.png"])))
    results.append(("Bear Market Machine", build_bear_machine(bg_paths["bg_bear.png"])))
    results.append(("30-to-3 Hours LinkedIn", build_automation_linkedin(bg_paths["bg_auto.png"])))
    results.append(("Recap Hook", build_recap_hook(bg_paths["bg_recap.png"])))
    results.append(("Recap ETH", build_recap_eth(bg_paths["bg_eth.png"])))
    results.append(("Recap Levels", build_recap_levels(bg_paths["bg_levels.png"])))
    results.append(("Q2 Preview", build_q2_preview(bg_paths["bg_q2.png"])))

    print("\n=== Done! 7 slides generated ===")
    for name, path in results:
        print(f"  {name}: {path}")
