"""Generate LinkedIn carousel: What I Built While Everyone Thought I Quit"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1350
BG = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (255, 51, 51)
GREY = (160, 160, 160)
output_dir = os.path.join(os.path.dirname(__file__), "..", "06-Drafts", "visuals", "linkedin-carousel-silence")
os.makedirs(output_dir, exist_ok=True)

# Fonts
title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 52)
body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 38)
small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
big_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 64)
accent_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44)

# ── SLIDE 1: Poolside photo with text overlay ──
poolside = Image.open("C:/Users/Bigquiv/Downloads/b4dd2655-861c-4174-9acc-2985d851b37b.png").convert("RGBA")
ratio = max(W / poolside.width, H / poolside.height)
poolside = poolside.resize((int(poolside.width * ratio), int(poolside.height * ratio)), Image.LANCZOS)
left = (poolside.width - W) // 2
top = (poolside.height - H) // 2
poolside = poolside.crop((left, top, left + W, top + H))

slide1 = poolside.convert("RGB")
# Dark gradient overlay at bottom
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
odraw = ImageDraw.Draw(overlay)
for y in range(H - 400, H):
    alpha = int(220 * (y - (H - 400)) / 400)
    odraw.line([(0, y), (W, y)], fill=(0, 0, 0, min(alpha, 220)))

slide1_rgba = slide1.convert("RGBA")
slide1_rgba = Image.alpha_composite(slide1_rgba, overlay)
slide1 = slide1_rgba.convert("RGB")
draw = ImageDraw.Draw(slide1)

draw.text((80, H - 200), "What I Built", font=big_font, fill=WHITE)
draw.text((80, H - 120), "While Everyone Thought I Quit", font=accent_font, fill=WHITE)
draw.rectangle([(80, H - 65), (440, H - 58)], fill=RED)
slide1.save(os.path.join(output_dir, "slide-01.png"), quality=95)
print("Slide 1 done")

# ── SLIDE 2: BEFORE ──
slide2 = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(slide2)
draw.rectangle([(0, 0), (W, 8)], fill=RED)
draw.text((80, 120), "BEFORE", font=big_font, fill=RED)
draw.rectangle([(80, 200), (250, 204)], fill=RED)

y = 280
for line, font, color in [
    ("Posting every day.", body_font, WHITE),
    ("Grinding threads at midnight.", body_font, WHITE),
    ("Running a signal channel manually.", body_font, WHITE),
    ("", None, None),
    ("", None, None),
    ("Engagement: 0.03%", accent_font, RED),
    ("Revenue from content: $0", accent_font, RED),
    ("", None, None),
    ("", None, None),
    ("I was a content machine", accent_font, GREY),
    ("with no engine.", accent_font, GREY),
]:
    if line == "":
        y += 30
        continue
    draw.text((80, y), line, font=font, fill=color)
    bbox = draw.textbbox((0, 0), line, font=font)
    y += (bbox[3] - bbox[1]) + 18

slide2.save(os.path.join(output_dir, "slide-02.png"), quality=95)
print("Slide 2 done")

# ── SLIDE 3: THE PIVOT ──
slide3 = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(slide3)
draw.rectangle([(0, 0), (W, 8)], fill=RED)
draw.text((80, 120), "THE PIVOT", font=big_font, fill=WHITE)
draw.rectangle([(80, 200), (320, 204)], fill=RED)

y = 280
for line, font, color in [
    ("I stopped posting.", body_font, WHITE),
    ("I stopped performing.", body_font, WHITE),
    ("I stopped chasing the algorithm.", body_font, WHITE),
    ("", None, None),
    ("", None, None),
    ("And I started engineering.", accent_font, RED),
    ("", None, None),
    ("", None, None),
    ("The hardest part was not building.", body_font, GREY),
    ("It was choosing silence", body_font, GREY),
    ("over visibility.", body_font, GREY),
]:
    if line == "":
        y += 30
        continue
    draw.text((80, y), line, font=font, fill=color)
    bbox = draw.textbbox((0, 0), line, font=font)
    y += (bbox[3] - bbox[1]) + 18

slide3.save(os.path.join(output_dir, "slide-03.png"), quality=95)
print("Slide 3 done")

# ── SLIDE 4: WHAT I BUILT ──
slide4 = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(slide4)
draw.rectangle([(0, 0), (W, 8)], fill=RED)
draw.text((80, 120), "WHAT I BUILT", font=big_font, fill=WHITE)
draw.rectangle([(80, 200), (380, 204)], fill=RED)

y = 280
sections = [
    ("AI Signal Scanner", ["25 crypto pairs + 8 forex pairs", "Scanned every 4 hours automatically"]),
    ("Content Production Pipeline", ["Research > Write > Design > Schedule", "Across 5 platforms. Zero manual work."]),
    ("Distribution System", ["Signals, posts, and content", "Running 24/7 without me touching it"]),
]
for title, bullets in sections:
    draw.text((80, y), f"> {title}", font=accent_font, fill=RED)
    bbox = draw.textbbox((0, 0), f"> {title}", font=accent_font)
    y += (bbox[3] - bbox[1]) + 15
    for bullet in bullets:
        draw.text((120, y), bullet, font=body_font, fill=GREY)
        bbox = draw.textbbox((0, 0), bullet, font=body_font)
        y += (bbox[3] - bbox[1]) + 12
    y += 40

y += 20
draw.text((80, y), "One system replaced", font=accent_font, fill=WHITE)
bbox = draw.textbbox((0, 0), "One system replaced", font=accent_font)
y += (bbox[3] - bbox[1]) + 12
draw.text((80, y), "6 hours of daily work.", font=accent_font, fill=RED)

slide4.save(os.path.join(output_dir, "slide-04.png"), quality=95)
print("Slide 4 done")

# ── SLIDE 5: THE LESSON ──
slide5 = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(slide5)
draw.rectangle([(0, 0), (W, 8)], fill=RED)
draw.text((80, 120), "THE LESSON", font=big_font, fill=WHITE)
draw.rectangle([(80, 200), (340, 204)], fill=RED)

y = 320
draw.text((80, y), "Systems beat", font=big_font, fill=WHITE)
y += 80
draw.text((80, y), "willpower.", font=big_font, fill=RED)
y += 100
draw.text((80, y), "Every single time.", font=accent_font, fill=GREY)
y += 100
draw.rectangle([(80, y), (W - 80, y + 2)], fill=(50, 50, 50))
y += 50

for line, color in [
    ("If you are grinding without a system,", WHITE),
    ("you do not have a business.", WHITE),
    ("", None),
    ("You have a job that does not", GREY),
    ("pay overtime.", GREY),
]:
    if line == "":
        y += 25
        continue
    draw.text((80, y), line, font=body_font, fill=color)
    bbox = draw.textbbox((0, 0), line, font=body_font)
    y += (bbox[3] - bbox[1]) + 15

# CTA button
y = H - 180
draw.rectangle([(80, y), (W - 80, y + 80)], fill=RED)
cta = "DM me SYSTEM for the framework"
bbox = draw.textbbox((0, 0), cta, font=accent_font)
draw.text(((W - (bbox[2] - bbox[0])) // 2, y + 18), cta, font=accent_font, fill=WHITE)
draw.text((80, H - 70), "Save this.", font=small_font, fill=GREY)

slide5.save(os.path.join(output_dir, "slide-05.png"), quality=95)
print("Slide 5 done")

# ── COMBINE INTO PDF ──
slides = [Image.open(os.path.join(output_dir, f"slide-0{i}.png")).convert("RGB") for i in range(1, 6)]
pdf_path = os.path.join(output_dir, "linkedin-carousel-silence.pdf")
slides[0].save(pdf_path, save_all=True, append_images=slides[1:], resolution=150)
print(f"\nPDF saved: {pdf_path}")
print("All 5 slides + PDF ready!")
