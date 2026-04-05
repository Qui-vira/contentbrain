from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1920
canvas = Image.new("RGB", (W, H), (10, 10, 15))

# ── Colors ────────────────────────────────────────────────────────────────────
BG        = (10, 10, 15)
RED       = (230, 57, 70)
GOLD      = (210, 170, 0)
GREEN     = (0, 190, 100)
WHITE     = (255, 255, 255)
LIGHT     = (225, 225, 225)
DIMMED    = (155, 155, 165)
GRAY      = (90, 90, 100)
PANEL     = (17, 17, 28)
PANEL2    = (22, 22, 38)
BORDER    = (42, 42, 70)
RED_DIM   = (55, 15, 18)
GOLD_DIM  = (55, 48, 5)
GREEN_DIM = (8, 50, 28)

# Annotation badge colors (match original image style)
BADGE_COLORS = [
    (34, 100, 60),   # 1 dark green
    (140, 100, 20),  # 2 dark gold
    (140, 100, 20),  # 3 dark gold
    (60, 60, 140),   # 4 blue
    (140, 80, 20),   # 5 orange
    (140, 30, 90),   # 6 pink
    (20, 100, 60),   # 7 teal
    (80, 30, 130),   # 8 purple
]
BADGE_TEXT = [
    (80, 220, 140),
    (255, 210, 80),
    (255, 210, 80),
    (140, 160, 255),
    (255, 170, 80),
    (255, 100, 180),
    (80, 220, 160),
    (180, 120, 255),
]

# ── Fonts ─────────────────────────────────────────────────────────────────────
FD = "C:/Windows/Fonts/"
def fnt(name, size):
    return ImageFont.truetype(FD + name, size)

f_hero    = fnt("arialbd.ttf", 58)
f_section = fnt("arialbd.ttf", 44)
f_label   = fnt("arialbd.ttf", 32)
f_label_sm= fnt("arialbd.ttf", 26)
f_body    = fnt("arial.ttf", 29)
f_body_sm = fnt("arial.ttf", 25)
f_body_xs = fnt("arial.ttf", 21)
f_italic  = fnt("ariali.ttf", 29)
f_italic_sm = fnt("ariali.ttf", 25)
f_tag     = fnt("arialbd.ttf", 22)
f_mono    = fnt("consola.ttf", 24)

# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_obj(img):
    return ImageDraw.Draw(img)

def text_w(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def text_h(d, text, font):
    bb = d.textbbox((0,0), text, font=font)
    return bb[3] - bb[1]

def center_x(d, text, font):
    return (W - text_w(d, text, font)) // 2

def rect(d, x1, y1, x2, y2, fill, radius=12, outline=None, width=1):
    d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill,
                         outline=outline, width=width)

def glow(img, text, x, y, font, color, blur=14, alpha=110):
    g = Image.new("RGBA", img.size, (0,0,0,0))
    gd = ImageDraw.Draw(g)
    gd.text((x, y), text, fill=(*color[:3], alpha), font=font)
    g = g.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")
    ImageDraw.Draw(out).text((x, y), text, fill=color, font=font)
    return out

def glow_center(img, text, y, font, color, blur=14, alpha=110):
    d = ImageDraw.Draw(img)
    x = center_x(d, text, font)
    return glow(img, text, x, y, font, color, blur, alpha)

def orb(img, cx, cy, r, color, alpha=35):
    o = Image.new("RGBA", img.size, (0,0,0,0))
    od = ImageDraw.Draw(o)
    for i in range(20, 0, -1):
        ri = int(r * i / 20)
        ai = int(alpha * (1 - i/20))
        od.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=(*color[:3], ai))
    return Image.alpha_composite(img.convert("RGBA"), o).convert("RGB")

def wrap_lines(text, d, font, max_w):
    """Return list of lines that fit within max_w."""
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if text_w(d, test, font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_wrapped(d, text, x, y, max_w, font, color, line_h=38):
    lines = wrap_lines(text, d, font, max_w)
    cy = y
    for l in lines:
        d.text((x, cy), l, fill=color, font=font)
        cy += line_h
    return cy

# ── Prompt input box (mimics Claude Code / chat UI) ───────────────────────────
def prompt_box(img, x1, y1, x2, accent_color, accent_dim, label_text,
               prompt_text, font=None, italic=True):
    """Draws a prompt input box. Returns new y position (bottom of box)."""
    d = ImageDraw.Draw(img)
    if font is None:
        font = f_italic if italic else f_body

    # Measure wrapped prompt text
    pad = 24
    inner_w = (x2 - x1) - pad*2
    lines = wrap_lines(prompt_text, d, font, inner_w)
    line_h = 36
    content_h = len(lines) * line_h + pad*2
    box_h = content_h + 52  # 52 = bottom bar height

    y2 = y1 + box_h

    # Outer border box
    rect(d, x1, y1, x2, y2, PANEL, radius=16, outline=accent_color, width=2)

    # Text area
    cy = y1 + pad
    for l in lines:
        d.text((x1 + pad, cy), l, fill=LIGHT, font=font)
        cy += line_h

    # Bottom bar (model selector)
    bar_y = y2 - 50
    rect(d, x1, bar_y, x2, y2, PANEL2, radius=16)
    rect(d, x1, bar_y, x2, bar_y+4, PANEL2, radius=0)  # flatten top of bar
    d.text((x1 + pad, bar_y + 14), "+", fill=GRAY, font=f_label_sm)
    model_txt = "Sonnet 4.6"
    d.text((x2 - text_w(d, model_txt, f_body_xs) - 52, bar_y + 16),
           model_txt, fill=GRAY, font=f_body_xs)
    # Send button
    btn_x = x2 - 46
    btn_y = bar_y + 8
    d.rounded_rectangle([btn_x, btn_y, btn_x+32, btn_y+32], radius=8,
                         fill=accent_color)
    d.text((btn_x+8, btn_y+6), "↑", fill=WHITE, font=f_label_sm)

    return y2

# ── Section badge ─────────────────────────────────────────────────────────────
def section_badge(img, y, label, color, dim):
    d = ImageDraw.Draw(img)
    bw = text_w(d, label, f_label) + 50
    bx = (W - bw) // 2
    rect(d, bx, y, bx+bw, y+46, dim, radius=23, outline=color, width=2)
    d.text(((W - text_w(d, label, f_label))//2, y+8), label, fill=color, font=f_label)
    return y + 46

# ── Annotation row ────────────────────────────────────────────────────────────
def annotate(d, num, title, sub, y):
    bx = 596
    bg = BADGE_COLORS[(num-1) % len(BADGE_COLORS)]
    tc = BADGE_TEXT[(num-1) % len(BADGE_TEXT)]
    # Badge
    rect(d, bx, y, bx+32, y+32, bg, radius=7)
    nb = str(num)
    nx = bx + (32 - text_w(d, nb, f_tag))//2
    d.text((nx, y+5), nb, fill=tc, font=f_tag)
    # Text
    d.text((bx+42, y+1), title, fill=WHITE, font=f_label_sm)
    d.text((bx+42, y+22), sub, fill=DIMMED, font=f_body_xs)
    return y + 52

# ═════════════════════════════════════════════════════════════════════════════
#  BUILD IMAGE
# ═════════════════════════════════════════════════════════════════════════════
img = canvas.copy()

# Ambient orbs
img = orb(img, W//2, 200, 400, RED, alpha=18)
img = orb(img, W//2, 1100, 500, GREEN, alpha=14)

d = ImageDraw.Draw(img)

# ── HEADER ────────────────────────────────────────────────────────────────────
eyebrow = "EXAMPLE: CREATING A WEEK OF CONTENT FROM A VOICE NOTE"
d.text((center_x(d, eyebrow, f_body_xs), 36), eyebrow, fill=GRAY, font=f_body_xs)

img = glow_center(img, "The AI Prompt", 72, f_hero, WHITE, blur=18, alpha=90)
d = ImageDraw.Draw(img)
# Accent underline
al = 260
d.rectangle([(W-al)//2, 142, (W+al)//2, 146], fill=RED)

# ── BAD PROMPT ────────────────────────────────────────────────────────────────
y = 172
y = section_badge(img, y, "  Bad prompt", RED, RED_DIM) + 20
d = ImageDraw.Draw(img)

y = prompt_box(img, 60, y, W-60, RED, RED_DIM, "Bad",
               "Write me some content about AI.",
               font=f_italic) + 16
d = ImageDraw.Draw(img)

# ── GOOD PROMPT ───────────────────────────────────────────────────────────────
y += 12
y = section_badge(img, y, "  Good prompt", GOLD, GOLD_DIM) + 20
d = ImageDraw.Draw(img)

y = prompt_box(img, 60, y, W-60, GOLD, GOLD_DIM, "Good",
               "Write me a week of social media posts about AI for beginners. "
               "Include Twitter, TikTok, LinkedIn and Instagram.",
               font=f_italic) + 16
d = ImageDraw.Draw(img)

# ── GREAT PROMPT ──────────────────────────────────────────────────────────────
y += 12
y = section_badge(img, y, "  Great prompt", GREEN, GREEN_DIM) + 20
d = ImageDraw.Draw(img)

# Two-column layout: prompt box left (560px wide), annotations right
SPLIT = 570
great_prompt = (
    "Here\u2019s a voice note transcript. "
    "Turn it into a full week of content: "
    "one thread, two TikTok scripts, "
    "one LinkedIn post, one IG caption."
)

box_top = y
y = prompt_box(img, 60, box_top, SPLIT, GREEN, GREEN_DIM, "Great",
               great_prompt, font=f_italic) + 16
d = ImageDraw.Draw(img)

# Annotations (right column, aligned to box top)
ay = box_top + 8
annots = [
    ("Input type",      "Voice note transcript"),
    ("Action verb",     "\"Turn it into\" (not \'write me\')"),
    ("Scope",           "Full week of content"),
    ("Format 1",        "One thread"),
    ("Format 2",        "Two TikTok scripts"),
    ("Format 3",        "One LinkedIn post"),
    ("Format 4",        "One IG caption"),
    ("Why it works",    "Specific counts. Zero ambiguity."),
]
for i, (title, sub) in enumerate(annots):
    ay = annotate(d, i+1, title, sub, ay)

# ── RESULT TAG ────────────────────────────────────────────────────────────────
y = max(y, ay + 10)
img = orb(img, W//2, y + 30, 200, GREEN, alpha=20)
d = ImageDraw.Draw(img)
result_txt = "40 seconds. 5 pieces of content. Done."
img = glow(img, result_txt,
           center_x(d, result_txt, f_label), y,
           f_label, GREEN, blur=12, alpha=120)
d = ImageDraw.Draw(img)

# ── DIVIDER ───────────────────────────────────────────────────────────────────
y += 55
d.rectangle([60, y, W-60, y+1], fill=BORDER)
y += 24

# ── BOTTOM: THE EXACT PROMPT ──────────────────────────────────────────────────
d.text((center_x(d, "The exact prompt from the thread:", f_body_sm), y),
       "The exact prompt from the thread:", fill=DIMMED, font=f_body_sm)
y += 38

# Quoted prompt box
rect(d, 60, y, W-60, y+130, PANEL2, radius=14, outline=BORDER, width=1)
# Left green bar
d.rectangle([60, y+14, 66, y+116], fill=GREEN)
qtext = (
    '"Here\'s a voice note transcript.\n'
    'Turn it into a full week of content:\n'
    'one thread, two TikTok scripts,\n'
    'one LinkedIn post, one IG caption."'
)
cy2 = y + 18
for line in qtext.split("\n"):
    d.text((82, cy2), line, fill=LIGHT, font=f_italic_sm)
    cy2 += 30
y += 144

# ── BRANDING ──────────────────────────────────────────────────────────────────
y += 16
d.text((60, y), "@big_quiv", fill=GRAY, font=f_body_xs)
brtxt = "ContentBrain \u00b7 Claude Code"
d.text((W - text_w(d, brtxt, f_body_xs) - 60, y), brtxt, fill=GRAY, font=f_body_xs)

# ── TRIM TO CONTENT ───────────────────────────────────────────────────────────
final_h = min(y + 40, H)
img = img.crop((0, 0, W, final_h))

# ── SAVE ─────────────────────────────────────────────────────────────────────
out_dir = "C:/Users/Bigquiv/onedrive/desktop/contentbrain/06-Drafts/visuals/prompt-guide"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "contentbrain-command-guide.png")
img.save(out, "PNG", quality=95)
print(f"Saved: {out}  Size: {img.size}")
