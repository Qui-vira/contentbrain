"""
Generate a practical PDF guide for animating keyframes on Kling AI.
Uses actual keyframe images from the 4 video projects as examples.
"""
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
        Table, TableStyle, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    os.system("pip install reportlab")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
        Table, TableStyle, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Paths
BASE = Path(r"C:/Users/Bigquiv/onedrive/desktop/contentbrain")
STUDIO = Path(r"C:/Users/Bigquiv/onedrive/desktop/content-studio/public")
OUT_PDF = BASE / "06-Drafts" / "visuals" / "kling-animation-guide.pdf"
THUMB_DIR = BASE / "06-Drafts" / "visuals" / "kling-guide-thumbs"
THUMB_DIR.mkdir(parents=True, exist_ok=True)

# Colors
RED = HexColor("#E63946")
DARK = HexColor("#0A0A0F")
GOLD = HexColor("#FFD700")
GRAY = HexColor("#666666")
LIGHT_GRAY = HexColor("#F5F5F5")
WHITE = HexColor("#FFFFFF")

# Create thumbnail versions of keyframes (smaller for PDF)
def make_thumbnail(src_path, dest_path, size=(200, 356)):
    img = Image.open(src_path)
    img.thumbnail(size, Image.LANCZOS)
    img.save(dest_path, quality=90)
    return dest_path

# Projects data
projects = [
    {
        "name": "20M Bitcoin TikTok",
        "dir": "20m-bitcoin-tiktok",
        "shots": 10,
        "description": "Bitcoin scarcity narrative. 10 shots, 30s.",
    },
    {
        "name": "3 Cleared Tokens Reel",
        "dir": "3-cleared-tokens-reel",
        "shots": 12,
        "description": "SEC-cleared tokens breakdown. 12 shots, 35s.",
    },
    {
        "name": "Day In Life KOL Reel",
        "dir": "day-in-life-kol-reel",
        "shots": 10,
        "description": "Morning routine as a crypto KOL. 10 shots, 35s.",
    },
    {
        "name": "Claude Code Portfolio Reel",
        "dir": "claude-code-portfolio-reel",
        "shots": 8,
        "description": "AI portfolio analysis demo. 8 shots, 30s.",
    },
]

# Load manifests and build shot data
all_shots = []
for proj in projects:
    manifest_path = STUDIO / proj["dir"] / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            data = json.load(f)
        manifest = data.get("manifest", data)
        for shot in manifest.get("shots", []):
            shot_path = STUDIO / proj["dir"] / shot["src"]
            if shot_path.exists() and shot_path.stat().st_size > 100:
                thumb_name = f"{proj['dir']}-{shot['src']}"
                thumb_path = THUMB_DIR / thumb_name
                make_thumbnail(str(shot_path), str(thumb_path))

                duration_s = shot["durationFrames"] / manifest.get("fps", 30)
                all_shots.append({
                    "project": proj["name"],
                    "shot_id": shot["id"],
                    "src": shot["src"],
                    "thumb": str(thumb_path),
                    "effect": shot.get("effect", ""),
                    "text_overlay": shot.get("textOverlay", ""),
                    "duration_s": duration_s,
                    "duration_frames": shot["durationFrames"],
                    "file_path": str(shot_path),
                })

print(f"Prepared {len(all_shots)} shot thumbnails")

# --- Build PDF ---
doc = SimpleDocTemplate(
    str(OUT_PDF),
    pagesize=A4,
    topMargin=0.6*inch,
    bottomMargin=0.6*inch,
    leftMargin=0.7*inch,
    rightMargin=0.7*inch,
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Title"],
    fontSize=28,
    textColor=RED,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)

subtitle_style = ParagraphStyle(
    "CustomSubtitle",
    parent=styles["Normal"],
    fontSize=12,
    textColor=GRAY,
    spaceAfter=20,
)

h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=20,
    textColor=RED,
    spaceBefore=16,
    spaceAfter=8,
    fontName="Helvetica-Bold",
)

h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=15,
    textColor=HexColor("#333333"),
    spaceBefore=12,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)

h3_style = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontSize=12,
    textColor=HexColor("#444444"),
    spaceBefore=8,
    spaceAfter=4,
    fontName="Helvetica-Bold",
)

body_style = ParagraphStyle(
    "CustomBody",
    parent=styles["Normal"],
    fontSize=10,
    textColor=HexColor("#333333"),
    spaceAfter=6,
    leading=14,
)

tip_style = ParagraphStyle(
    "Tip",
    parent=styles["Normal"],
    fontSize=10,
    textColor=HexColor("#1a6b3c"),
    backColor=HexColor("#e8f5e9"),
    borderPadding=8,
    spaceAfter=8,
    leading=14,
    fontName="Helvetica-Oblique",
)

warn_style = ParagraphStyle(
    "Warning",
    parent=styles["Normal"],
    fontSize=10,
    textColor=HexColor("#b71c1c"),
    backColor=HexColor("#ffebee"),
    borderPadding=8,
    spaceAfter=8,
    leading=14,
)

prompt_style = ParagraphStyle(
    "Prompt",
    parent=styles["Code"],
    fontSize=9,
    textColor=HexColor("#e0e0e0"),
    backColor=HexColor("#1e1e1e"),
    borderPadding=10,
    spaceAfter=8,
    leading=13,
    fontName="Courier",
)

caption_style = ParagraphStyle(
    "Caption",
    parent=styles["Normal"],
    fontSize=8,
    textColor=GRAY,
    alignment=TA_CENTER,
    spaceAfter=4,
)

elements = []

# === COVER ===
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph("KLING AI", title_style))
elements.append(Paragraph("IMAGE-TO-VIDEO ANIMATION GUIDE", ParagraphStyle(
    "CoverSub", parent=title_style, fontSize=18, textColor=HexColor("#333333"), spaceAfter=20,
)))
elements.append(Paragraph(
    "A practical, step-by-step guide to animating your keyframes on Kling 3.0. "
    "Includes your actual shots with recommended prompts for each.",
    subtitle_style
))
elements.append(Spacer(1, 0.3*inch))

# Show 4 keyframe thumbnails in a row as cover visual
cover_thumbs = []
for proj in projects:
    t = THUMB_DIR / f"{proj['dir']}-shot-01.png"
    if t.exists():
        cover_thumbs.append(RLImage(str(t), width=1.2*inch, height=2.1*inch))
if cover_thumbs:
    cover_table = Table([cover_thumbs], colWidths=[1.4*inch]*len(cover_thumbs))
    cover_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(cover_table)
    elements.append(Paragraph("Your 4 video projects: 40 keyframes ready to animate", caption_style))

elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph("Prepared for @big_quiv | March 27, 2026", caption_style))
elements.append(PageBreak())

# === TABLE OF CONTENTS ===
elements.append(Paragraph("TABLE OF CONTENTS", h1_style))
toc_items = [
    "1. What You Need Before Starting",
    "2. Step-by-Step: Kling Image-to-Video (Website)",
    "3. Settings That Matter",
    "4. Prompt Engineering for Animation",
    "5. Advanced: Motion Brush & Start/End Frames",
    "6. Your 40 Keyframes with Recommended Prompts",
    "7. Workflow: Batch Animate All 40 Shots",
    "8. Tutorial Videos",
    "9. Quick Reference Cheat Sheet",
]
for item in toc_items:
    elements.append(Paragraph(item, body_style))
elements.append(PageBreak())

# === SECTION 1: PREREQUISITES ===
elements.append(Paragraph("1. WHAT YOU NEED BEFORE STARTING", h1_style))
elements.append(Paragraph(
    "Before you open Kling, make sure you have these ready:", body_style
))

prereqs = [
    ["Item", "Details"],
    ["Kling Account", "Sign up at klingai.com. Pro plan ($25.99/mo) recommended for priority + no watermark"],
    ["Your Keyframes", "40 PNG files across 4 projects (listed in Section 6)"],
    ["Keyframe Location", "C:\\Users\\Bigquiv\\onedrive\\desktop\\content-studio\\public\\"],
    ["Image Format", "PNG, 1080x1920 (9:16 vertical). Already correct."],
    ["Credits Estimate", "~66 credits for 40 shots at 5s each (Standard mode). ~132 credits at Pro mode."],
    ["Time Estimate", "~2-3 hours to animate all 40 shots manually on the website"],
]
t = Table(prereqs, colWidths=[1.5*inch, 4.5*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), RED),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
elements.append(t)
elements.append(PageBreak())

# === SECTION 2: STEP BY STEP ===
elements.append(Paragraph("2. STEP-BY-STEP: KLING IMAGE-TO-VIDEO", h1_style))

steps = [
    ("Step 1: Open Kling AI",
     "Go to <b>klingai.com</b> and log in. Click <b>'AI Videos'</b> in the top nav, "
     "then select <b>'Image to Video'</b> from the left panel."),

    ("Step 2: Upload Your Keyframe",
     "Click the upload area and select one of your keyframe PNGs. "
     "Example: <b>shot-01.png</b> from the 20M Bitcoin TikTok project. "
     "The image will appear in the preview window."),

    ("Step 3: Write Your Animation Prompt",
     "In the prompt box, describe HOW the image should move. "
     "Do NOT describe what's in the image (Kling already sees it). "
     "Focus on: <b>camera movement + subject motion + atmosphere</b>. "
     "See Section 4 for prompt formulas and Section 6 for shot-specific prompts."),

    ("Step 4: Set Negative Prompt",
     "Click 'Negative Prompt' and enter: <b>morphing, distorted face, sliding feet, "
     "blurry, cartoon, 3D render, text morphing, extra fingers, unnatural movement</b>"),

    ("Step 5: Choose Mode & Duration",
     "<b>Mode:</b> Select 'Professional' for character shots (better face consistency). "
     "Select 'Standard' for non-character shots (charts, screens, abstract).<br/>"
     "<b>Duration:</b> 5 seconds for most shots. 10 seconds only for establishing shots or slow reveals.<br/>"
     "<b>Aspect Ratio:</b> 9:16 (vertical). This matches your keyframes."),

    ("Step 6: Enable 'Bind Subject' (CRITICAL for face shots)",
     "If your shot has a face/character, toggle ON the <b>'Bind Subject'</b> button. "
     "This locks the face and clothing so they don't morph during animation. "
     "This is the #1 setting for character consistency."),

    ("Step 7: Generate",
     "Click <b>'Generate'</b>. Wait ~1-3 minutes (Pro) or ~15 minutes (Free). "
     "Preview the result. If the motion is wrong, adjust the prompt and regenerate. "
     "If the face morphed, make sure 'Bind Subject' is ON and add 'stable face, no morphing' to the prompt."),

    ("Step 8: Download",
     "Click the download icon. Save as MP4. Name it to match: <b>shot-01.mp4</b>, <b>shot-02.mp4</b>, etc. "
     "Save to the same folder as the keyframe PNG."),
]

for title, desc in steps:
    elements.append(Paragraph(title, h2_style))
    elements.append(Paragraph(desc, body_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "TIP: Do character shots first (shots with faces). These need the most iteration. "
    "Non-character shots (charts, screens, abstract backgrounds) are easier and faster.",
    tip_style
))
elements.append(PageBreak())

# === SECTION 3: SETTINGS ===
elements.append(Paragraph("3. SETTINGS THAT MATTER", h1_style))

settings_data = [
    ["Setting", "Options", "When to Use"],
    ["Mode", "Standard / Professional", "Professional for faces. Standard for everything else."],
    ["Duration", "5s / 10s", "5s for most shots. 10s for slow reveals or establishing shots."],
    ["Aspect Ratio", "16:9 / 9:16 / 1:1", "Always 9:16 for your reels (vertical)."],
    ["Bind Subject", "ON / OFF", "ALWAYS ON for character/face shots. OFF for abstract/charts."],
    ["Motion Brush", "Paint areas", "Use when you want ONLY specific parts to move (e.g., hair but not body)."],
    ["Negative Prompt", "Text field", "Always include: morphing, distorted face, blurry, cartoon, text morphing"],
]
t2 = Table(settings_data, colWidths=[1.2*inch, 1.5*inch, 3.3*inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), RED),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
elements.append(t2)
elements.append(PageBreak())

# === SECTION 4: PROMPT ENGINEERING ===
elements.append(Paragraph("4. PROMPT ENGINEERING FOR ANIMATION", h1_style))

elements.append(Paragraph("The Golden Rule", h2_style))
elements.append(Paragraph(
    "Your image already shows WHAT exists. Your prompt describes HOW it MOVES. "
    "Never describe the image contents. Only describe motion, camera, and atmosphere changes.",
    body_style
))

elements.append(Paragraph("The 5-Layer Prompt Formula", h2_style))
elements.append(Paragraph(
    "<b>Camera Movement</b> + <b>Subject Motion</b> + <b>Environment Motion</b> + "
    "<b>Lighting Changes</b> + <b>Mood/Atmosphere</b>",
    body_style
))

elements.append(Paragraph("Camera Movement Vocabulary", h3_style))
camera_moves = [
    ["Camera Term", "What It Does", "Best For"],
    ["Slow push in", "Gradually zooms toward subject", "Dramatic reveals, close-up emphasis"],
    ["Dolly push", "Camera physically moves forward", "Immersive approach shots"],
    ["Slow pull back", "Camera retreats from subject", "Establishing context, reveals"],
    ["Tracking shot left/right", "Camera slides sideways", "Following motion, panning scenes"],
    ["Crane up", "Camera rises upward", "Establishing shots, dramatic reveals"],
    ["Handheld slight sway", "Subtle natural camera shake", "Documentary feel, raw energy"],
    ["Rack focus", "Focus shifts between planes", "Drawing attention to specific element"],
    ["Static, locked tripod", "No camera movement", "Letting subject motion carry the shot"],
]
t3 = Table(camera_moves, colWidths=[1.5*inch, 2*inch, 2.5*inch])
t3.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#333333")),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
elements.append(t3)

elements.append(Paragraph("Subject Motion Vocabulary", h3_style))
subject_moves = [
    ["Motion Type", "Example Prompt Language"],
    ["Subtle breathing", "\"chest rises and falls with natural breathing\""],
    ["Head turn", "\"slowly turns head to face camera\""],
    ["Blinking", "\"natural eye blinks, steady gaze\""],
    ["Hair/clothing movement", "\"hair gently moves in the breeze, jacket fabric shifts\""],
    ["Hand gesture", "\"hand slowly rises, fingers spread\""],
    ["Body shift", "\"weight shifts slightly, relaxed confident posture\""],
    ["Walking", "\"takes slow deliberate steps forward\""],
    ["Screen glow flicker", "\"screen light flickers and pulses on face\""],
]
t4 = Table(subject_moves, colWidths=[1.5*inch, 4.5*inch])
t4.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#333333")),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
elements.append(t4)

elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph("Example: Weak vs Strong Prompts", h2_style))

weak_strong = [
    ["Weak Prompt", "Strong Prompt"],
    ["\"Man looking at camera\"", "\"Slow push in, subtle breathing, confident gaze directly into lens, ambient light shifts slightly, cinematic shallow depth of field\""],
    ["\"Camera moves\"", "\"Handheld shoulder-cam drifts behind subject with subtle sway, rack focus from foreground to face\""],
    ["\"Dramatic lighting\"", "\"Flickering red neon light pulses across face from camera left, casting shifting shadows\""],
]
t5 = Table(weak_strong, colWidths=[2*inch, 4*inch])
t5.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), RED),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
elements.append(t5)

elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    "ALWAYS include in negative prompt: morphing, distorted face, sliding feet, "
    "blurry, cartoon, 3D render, smooth plastic skin, floating limbs, text morphing, extra fingers",
    warn_style
))
elements.append(PageBreak())

# === SECTION 5: ADVANCED ===
elements.append(Paragraph("5. ADVANCED: MOTION BRUSH & START/END FRAMES", h1_style))

elements.append(Paragraph("Motion Brush", h2_style))
elements.append(Paragraph(
    "Motion Brush lets you paint over specific areas to control what moves and what stays still. "
    "This is perfect for shots where you want the character to move but the background to stay locked.",
    body_style
))
elements.append(Paragraph("How to use:", h3_style))
motion_brush_steps = [
    "1. After uploading your keyframe, click the 'Motion Brush' button",
    "2. Use the brush tool to paint over the areas you want to animate (e.g., hair, clothing, hands)",
    "3. Leave unpainted areas static (e.g., background, fixed objects)",
    "4. Draw motion arrows to indicate direction of movement",
    "5. Combine with your text prompt for best results",
]
for step in motion_brush_steps:
    elements.append(Paragraph(step, body_style))

elements.append(Paragraph(
    "TIP: For portrait shots, paint only the face area and upper body. "
    "This prevents the background from warping while the character breathes and blinks naturally.",
    tip_style
))

elements.append(Paragraph("Start & End Frames", h2_style))
elements.append(Paragraph(
    "Upload TWO images: a start frame and an end frame. Kling generates the motion between them. "
    "This gives you maximum control over the animation arc.",
    body_style
))
elements.append(Paragraph(
    "Use case for your projects: Upload shot-01.png as start frame and a slightly zoomed/cropped "
    "version as the end frame to create a controlled push-in effect.",
    body_style
))
elements.append(PageBreak())

# === SECTION 6: YOUR 40 KEYFRAMES WITH PROMPTS ===
elements.append(Paragraph("6. YOUR 40 KEYFRAMES WITH RECOMMENDED PROMPTS", h1_style))
elements.append(Paragraph(
    "Below is every keyframe from your 4 video projects with a recommended Kling animation prompt. "
    "Use these prompts directly on klingai.com. Adjust based on results.",
    body_style
))

# Prompt recommendations per shot type
def get_animation_prompt(shot, project_name):
    """Generate a Kling animation prompt based on the shot's effect and context."""
    effect = shot.get("effect", "")
    text = shot.get("text_overlay", "")

    # Character/face shots (hook shots, CTA shots)
    if shot["shot_id"] == 1:  # Hook shots
        return (
            "Slow cinematic push in toward subject, subtle natural breathing, "
            "slight head movement, confident steady gaze, ambient light shifts gently, "
            "shallow depth of field, cinematic film grain"
        )

    if "COMMENT" in text or "FOLLOW" in text:  # CTA shots
        return (
            "Static locked shot, subtle breathing motion, slight confident nod, "
            "ambient light pulses gently, cinematic atmosphere, steady gaze into camera"
        )

    if effect == "SlamIn":
        return (
            "Quick dramatic push in, subject remains still with subtle breathing, "
            "background slightly shifts, atmospheric particles drift, "
            "cinematic shallow depth of field, dramatic lighting holds steady"
        )

    if effect == "PunchZoom":
        return (
            "Slow deliberate push in toward center of frame, subtle environmental motion, "
            "light particles drift in atmosphere, dramatic tension builds, "
            "shallow depth of field sharpens"
        )

    if effect == "KenBurns":
        return (
            "Gentle slow drift, subtle atmospheric movement, light shifts naturally, "
            "particles float in the air, ambient environment breathes, "
            "cinematic color temperature holds steady"
        )

    if effect == "CameraShake":
        return (
            "Handheld camera slight shake, urgent energy, subject remains sharp, "
            "background vibrates subtly, dramatic atmospheric tension"
        )

    if effect == "CameraTrack":
        return (
            "Slow tracking shot drifting sideways, parallax depth between foreground "
            "and background, atmospheric haze shifts, cinematic pacing"
        )

    return (
        "Subtle ambient motion, gentle atmospheric drift, natural light shifts, "
        "cinematic film quality, shallow depth of field"
    )

# Negative prompt (same for all)
neg_prompt = (
    "morphing, distorted face, sliding feet, blurry, cartoon, 3D render, "
    "smooth plastic skin, floating limbs, text morphing, extra fingers, unnatural movement"
)

for proj in projects:
    elements.append(Paragraph(f"PROJECT: {proj['name']}", h2_style))
    elements.append(Paragraph(
        f"{proj['description']}<br/>"
        f"<b>Folder:</b> content-studio/public/{proj['dir']}/",
        body_style
    ))

    proj_shots = [s for s in all_shots if s["project"] == proj["name"]]

    for shot in proj_shots:
        prompt = get_animation_prompt(shot, proj["name"])
        has_face = shot["shot_id"] in [1, 2, 8, 10] or "COMMENT" in shot.get("text_overlay", "") or "FOLLOW" in shot.get("text_overlay", "")

        # Build shot card
        shot_elements = []
        shot_elements.append(Paragraph(
            f"<b>Shot {shot['shot_id']}</b> | {shot['src']} | "
            f"{shot['duration_s']:.1f}s | Effect: {shot['effect']}"
            f"{' | TEXT: ' + shot['text_overlay'] if shot['text_overlay'] else ''}",
            h3_style
        ))

        # Image + prompt side by side
        thumb_path = shot["thumb"]
        if os.path.exists(thumb_path):
            img_cell = RLImage(thumb_path, width=0.9*inch, height=1.6*inch)
        else:
            img_cell = Paragraph("[Image missing]", body_style)

        prompt_text = Paragraph(
            f"<b>Prompt:</b><br/>{prompt}<br/><br/>"
            f"<b>Settings:</b> {'Professional' if has_face else 'Standard'} mode | "
            f"5s | 9:16 | Bind Subject: {'ON' if has_face else 'OFF'}<br/><br/>"
            f"<b>Negative:</b> {neg_prompt}",
            ParagraphStyle("ShotPrompt", parent=body_style, fontSize=8, leading=11)
        )

        shot_table = Table(
            [[img_cell, prompt_text]],
            colWidths=[1.1*inch, 4.9*inch],
        )
        shot_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
        ]))
        shot_elements.append(shot_table)

        elements.append(KeepTogether(shot_elements))
        elements.append(Spacer(1, 0.08*inch))

    elements.append(PageBreak())

# === SECTION 7: BATCH WORKFLOW ===
elements.append(Paragraph("7. WORKFLOW: BATCH ANIMATE ALL 40 SHOTS", h1_style))

workflow_steps = [
    ("Phase 1: Character Shots First (Priority)",
     "Do all shots that have your face/character FIRST. These need 'Bind Subject' ON "
     "and Professional mode. If the face morphs, iterate the prompt. Count: ~15 shots."),
    ("Phase 2: Environment/Abstract Shots",
     "Charts, screens, abstract backgrounds. Standard mode, no Bind Subject needed. "
     "These are faster and rarely need re-generation. Count: ~25 shots."),
    ("Phase 3: Download & Rename",
     "Download each MP4 and rename to match: shot-01.mp4, shot-02.mp4, etc. "
     "Save to the same folder as the PNG keyframes."),
    ("Phase 4: Replace in Remotion",
     "Once all 40 shots are animated MP4s, update the manifest.json for each project: "
     "change \"type\": \"image\" to \"type\": \"video\" and \"src\": \"shot-01.png\" to "
     "\"src\": \"shot-01.mp4\". Then re-render in Remotion."),
]

for title, desc in workflow_steps:
    elements.append(Paragraph(title, h2_style))
    elements.append(Paragraph(desc, body_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "TIP: Open multiple Kling tabs. Submit 3-4 generations at once (if Pro plan). "
    "While one generates, set up the next. This cuts total time from 3 hours to ~1.5 hours.",
    tip_style
))
elements.append(PageBreak())

# === SECTION 8: TUTORIAL VIDEOS ===
elements.append(Paragraph("8. TUTORIAL VIDEOS & RESOURCES", h1_style))

elements.append(Paragraph(
    "These resources walk through the exact same process visually:", body_style
))

resources = [
    ["Resource", "URL", "What You'll Learn"],
    ["Kling Official Guide", "klingai.com/quickstart/image-to-video-guide", "Official step-by-step with UI screenshots"],
    ["Segmind Tutorial", "blog.segmind.com/how-to-animate-an-image-with-kling-ai-step-by-step-guide/", "Full walkthrough with prompt examples and parameter settings"],
    ["Kling 3.0 Prompt Guide (fal.ai)", "blog.fal.ai/kling-3-0-prompting-guide/", "Advanced prompt engineering: camera moves, multi-shot, dialogue"],
    ["Atlabs Prompt Guide", "atlabs.ai/blog/kling-3-0-prompting-guide-master-ai-video-generation", "5-layer prompt formula, weak vs strong examples"],
    ["CyberLink Full Review", "cyberlink.com/blog/trending-topics/3881/kling-ai-guide", "Pricing breakdown, free vs Pro comparison, limitations"],
    ["Artlist Kling 3.0 Overview", "artlist.io/blog/new-kling-3/", "4K capabilities, multi-shot narratives, cinematic features"],
]
t6 = Table(resources, colWidths=[1.3*inch, 2.7*inch, 2*inch])
t6.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), RED),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
elements.append(t6)
elements.append(PageBreak())

# === SECTION 9: CHEAT SHEET ===
elements.append(Paragraph("9. QUICK REFERENCE CHEAT SHEET", h1_style))

elements.append(Paragraph("Copy-paste these for every shot:", h2_style))

elements.append(Paragraph("Default Negative Prompt (use for ALL shots):", h3_style))
elements.append(Paragraph(neg_prompt, prompt_style))

elements.append(Paragraph("Character Shot Template:", h3_style))
elements.append(Paragraph(
    "Slow cinematic push in, subtle natural breathing, confident steady gaze, "
    "[specific motion], ambient light shifts gently, shallow depth of field, "
    "cinematic film grain, hyper-realistic",
    prompt_style
))

elements.append(Paragraph("Environment Shot Template:", h3_style))
elements.append(Paragraph(
    "Gentle atmospheric drift, [camera movement], subtle light particles float, "
    "ambient haze shifts naturally, cinematic color grading, "
    "shallow depth of field, film quality",
    prompt_style
))

elements.append(Paragraph("Action Shot Template:", h3_style))
elements.append(Paragraph(
    "Quick dramatic [camera movement], subject [action], background parallax shift, "
    "atmospheric particles scatter, cinematic tension, sharp focus on subject",
    prompt_style
))

elements.append(Spacer(1, 0.3*inch))

# Settings cheat sheet
settings_cheat = [
    ["Shot Type", "Mode", "Duration", "Bind Subject", "Motion Brush"],
    ["Face/character close-up", "Professional", "5s", "ON", "Optional"],
    ["Full body character", "Professional", "5s", "ON", "Paint body only"],
    ["Screen recording style", "Standard", "5s", "OFF", "Not needed"],
    ["Chart/data visual", "Standard", "5s", "OFF", "Not needed"],
    ["Abstract/atmospheric", "Standard", "5s", "OFF", "Optional"],
    ["Establishing/wide shot", "Professional", "10s", "OFF", "Not needed"],
    ["CTA/ending shot", "Professional", "5s", "ON", "Not needed"],
]
t7 = Table(settings_cheat, colWidths=[1.5*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch])
t7.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#333333")),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
]))
elements.append(t7)

elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph(
    "Once all 40 shots are animated, come back and say 'replace the reels' "
    "and I'll update the manifests and re-render all 4 videos with actual motion.",
    tip_style
))

# Build PDF
doc.build(elements)
print(f"\nPDF generated: {OUT_PDF}")
print(f"Size: {OUT_PDF.stat().st_size:,} bytes")
