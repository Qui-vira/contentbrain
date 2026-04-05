"""
Generate the Keyframe Prompt & Camera Angle Guide PDF.
A comprehensive reference for manually creating keyframes from video scripts.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT_PATH = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain\08-Templates\keyframe-prompt-guide.pdf"

# Brand colors
DARK_BG = HexColor("#0A0A0F")
RED_ACCENT = HexColor("#E63946")
TEAL = HexColor("#0EA5E9")
GOLD = HexColor("#FFD700")
DARK_NAVY = HexColor("#0C0C1E")
LIGHT_GRAY = HexColor("#F5F5F5")
MED_GRAY = HexColor("#E0E0E0")
DARK_TEXT = HexColor("#1A1A2E")
SECTION_BG = HexColor("#F8F9FA")

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
        leftMargin=0.7*inch,
        rightMargin=0.7*inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=24, leading=28, textColor=DARK_TEXT,
        spaceAfter=6, fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, leading=14, textColor=HexColor("#666666"),
        spaceAfter=20
    )
    h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=18, leading=22, textColor=RED_ACCENT,
        spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold"
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=14, leading=17, textColor=DARK_TEXT,
        spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"
    )
    h3 = ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontSize=12, leading=15, textColor=HexColor("#333333"),
        spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold"
    )
    body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=13, textColor=DARK_TEXT,
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        "Code", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=HexColor("#2D3748"),
        fontName="Courier", backColor=LIGHT_GRAY,
        leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4,
        borderPadding=(6, 6, 6, 6)
    )
    tip_style = ParagraphStyle(
        "Tip", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=HexColor("#1A5276"),
        backColor=HexColor("#EBF5FB"), leftIndent=12, rightIndent=12,
        spaceBefore=4, spaceAfter=8, borderPadding=(8, 8, 8, 8)
    )

    elements = []

    def add_table(data, col_widths=None):
        """Helper to add a styled table."""
        if col_widths is None:
            col_widths = [doc.width / len(data[0])] * len(data[0])
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), RED_ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8.5),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("BACKGROUND", (0, 1), (-1, -1), white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, MED_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════
    # COVER / TITLE
    # ═══════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("Keyframe Prompt &<br/>Camera Angle Guide", title_style))
    elements.append(Paragraph(
        "A complete reference for creating AI-generated keyframes from video scripts. "
        "Works with any image generator: fal.ai, Midjourney, DALL-E, Ideogram, Leonardo, ChatGPT, or local Flux.",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=RED_ACCENT))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "<b>For:</b> @big_quiv / Quivira video production pipeline<br/>"
        "<b>Version:</b> 1.0 — March 2026<br/>"
        "<b>Use when:</b> fal.ai credits are exhausted, or you want manual control over keyframe generation",
        body
    ))
    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: HOW THE PIPELINE WORKS
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("1. How the Production Pipeline Works", h1))
    elements.append(Paragraph(
        "The video production pipeline converts a script into a finished video through 6 steps. "
        "Keyframe generation happens at Step 3 (Generate Visuals). Understanding the full flow "
        "helps you create better keyframes manually.",
        body
    ))

    add_table([
        ["Step", "Name", "What Happens", "Output"],
        ["1", "Art Direction", "Define visual language: palette, mood, lighting, environment", "Art direction brief"],
        ["2", "Storyboard", "Break script into shots with timing, types, effects, SFX", "Shot deck table"],
        ["3", "Generate Visuals", "Create keyframe images for each AI shot in the deck", "Keyframe images (shot-01.png...)"],
        ["4", "Voice & Audio", "Generate voiceover from script using MiniMax voice clone", "voiceover.mp3"],
        ["5", "Assemble", "Combine keyframes + voice + SFX + effects in Remotion", "Draft video"],
        ["6", "Final Render", "Apply final adjustments, render at 1080x1920 30fps", "Final .mp4"],
    ], col_widths=[0.4*inch, 1.0*inch, 2.8*inch, 1.6*inch])

    elements.append(Paragraph("How Camera Angles Are Selected", h2))
    elements.append(Paragraph(
        "The pipeline selects camera angles based on the <b>emotional intent</b> of each shot. "
        "During Step 2 (Storyboard), each shot is assigned an angle from the prompt library "
        "that matches what the shot needs to communicate. The rule: <b>never use the same angle "
        "for 3+ consecutive shots</b> — variety keeps the viewer engaged.",
        body
    ))

    add_table([
        ["Shot Intent", "Camera Angle", "Why This Angle"],
        ["Hook / scroll-stop", "Extreme close-up or Low angle", "Maximum visual impact, forces attention"],
        ["Bold claim / flex", "Low angle (power)", "Subject appears dominant, authoritative"],
        ["Teaching / explaining", "Medium shot or Medium close-up", "Room for text overlays, approachable feel"],
        ["Story / vulnerability", "High angle or Close-up", "Intimacy, emotional connection"],
        ["Tension / controversy", "Dutch angle", "Visual unease matches provocative content"],
        ["Demo / showing process", "POV first-person or Over-shoulder", "Viewer feels involved, immersive"],
        ["Reveal / surprise", "Macro-to-wide reveal", "Starts tight, pulls back for context"],
        ["Before/after comparison", "Split screen comparison", "Side-by-side visual impact"],
        ["Establishing / context", "Wide / establishing", "Sets the scene, shows full environment"],
        ["Transition / breather", "Profile / side", "Cinematic pause between sections"],
        ["CTA / closing", "Three-quarter or Medium close-up", "Editorial, direct, personal connection"],
        ["Authority / expert", "Close-up + Dramatic side light", "Confidence, expertise, credibility"],
    ], col_widths=[1.4*inch, 1.8*inch, 2.6*inch])

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: COMPLETE CAMERA ANGLE LIBRARY
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("2. Complete Camera Angle Library", h1))
    elements.append(Paragraph(
        "Copy these prompt blocks exactly when building keyframe prompts. Each block is optimized "
        "for AI image generators and produces consistent results across tools.",
        body
    ))

    camera_angles = [
        ("Extreme close-up", "extreme close-up, face fills frame, eyes and expression dominant, shallow depth of field f/1.4", "Hook shots, dramatic reveals, emotional moments"),
        ("Close-up", "close-up shot, head and shoulders, subject fills 70% of frame, shallow depth of field", "Authority, talking head, CTA, confidence"),
        ("Medium close-up", "medium close-up, chest up, room for text overlay on sides, balanced framing", "Narration, body language visible, text space"),
        ("Medium shot", "medium shot, waist up, subject centered, environment partially visible", "Standard talking head, teaching, explaining"),
        ("Medium wide", "medium wide shot, knees up, subject in context of environment, natural framing", "Context + subject, natural conversation"),
        ("Wide / establishing", "wide establishing shot, full body visible, environment dominant, subject placed on rule of thirds", "Scene-setting, environment reveals, establishing"),
        ("Bird's eye", "bird's eye view, directly overhead, flat layout perspective, geometric composition", "Process shots, desk layouts, before/after"),
        ("Low angle (power)", "low angle shot from below, subject appears dominant and powerful, sky or ceiling visible behind", "Authority, bold claims, flex moments"),
        ("High angle (vulnerability)", "high angle looking down on subject, appears smaller, introspective feeling", "Story beats, vulnerability, reflection"),
        ("Dutch angle (tension)", "Dutch angle tilted 20 degrees, creates visual tension and unease, dynamic composition", "Controversy, tension, disruption"),
        ("Over-the-shoulder", "over-the-shoulder shot, back of head visible, subject looking at screen/object, depth layers", "Trading desk, screen demos, watching data"),
        ("POV first-person", "first-person POV, hands visible in frame, looking at laptop/phone/charts, immersive perspective", "Demos, chart analysis, process walkthroughs"),
        ("Profile / side", "profile shot, subject facing left/right, silhouette-ready, clean background separation", "Transitions, cinematic pauses, editorial"),
        ("Three-quarter", "three-quarter angle, face turned 45 degrees from camera, dimensional and editorial", "CTA, editorial feel, casual authority"),
        ("Macro-to-wide reveal", "extreme macro close-up transitioning to wide shot, starts on small detail then pulls back to reveal full context, cinematic rack focus", "Reveals, surprises, plot twists"),
        ("Hand-in-frame action", "first-person view with hands visible performing an action, natural movement, immersive crafting perspective", "Process demos, hands-on tutorials"),
        ("Split screen comparison", "split screen side-by-side composition, left panel vs right panel, clean dividing line, before-and-after energy", "Before/after, comparison, contrast"),
        ("Green screen overlay", "creator composited over reference footage or screenshots, picture-in-picture with background content visible", "Demos with visual context, reactions"),
    ]

    for name, prompt, use_for in camera_angles:
        elements.append(Paragraph(f"<b>{name}</b>", h3))
        elements.append(Paragraph(f"<i>Prompt:</i> <font face='Courier' size='8'>{prompt}</font>", body))
        elements.append(Paragraph(f"<i>Best for:</i> {use_for}", body))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: LIGHTING STYLES
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("3. Lighting Styles", h1))

    lighting_styles = [
        ("Dramatic side light", "single key light from camera left at 45 degrees, deep shadows on right side, noir-style contrast, dramatic mood"),
        ("Neon crypto", "neon blue and purple backlighting, dark room, face lit by soft screen glow, cyberpunk-adjacent, tech aesthetic"),
        ("Red accent (Quivira brand)", "dark background, single red accent light from behind, red rim light on edges, high contrast, brand signature"),
        ("Golden hour", "warm golden light streaming from window at low angle, long soft shadows, cinematic warmth, orange-amber tones"),
        ("Screen glow only", "face illuminated only by monitor light, completely dark room, green and blue screen reflections on skin, intimate tech mood"),
        ("Clean studio", "soft even studio lighting, white or neutral background, minimal shadows, professional headshot quality"),
        ("Silhouette", "strong backlight, subject in full silhouette, rim light on edges only, mysterious and powerful"),
        ("Split light", "light hitting exactly half the face, other half in complete shadow, Rembrandt-style, high drama"),
        ("Overhead / top light", "light source directly above, shadows under eyes and chin, editorial fashion style, moody"),
        ("Practical lights", "lit only by practical sources in scene — desk lamp, monitor, candles — naturalistic, warm, authentic"),
        ("Dark-to-spotlight reveal", "starts in near-total darkness, single spotlight snaps on to illuminate subject or object, dramatic contrast shift, visual hook energy"),
        ("Single candle glow", "one candle flame illuminating face in darkness, warm flicker on skin, everything else black, intimate and raw"),
    ]

    add_table(
        [["Style", "Prompt Block"]] + [[name, prompt] for name, prompt in lighting_styles],
        col_widths=[1.5*inch, 4.3*inch]
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: ENVIRONMENTS / SCENES
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("4. Environments / Scenes", h1))

    environments = [
        ("Trading desk", "modern trading desk with multiple monitors showing crypto charts, dark room, ambient screen glow, professional setup"),
        ("Studio (dark)", "dark professional studio, clean background, controlled lighting, content creator setup"),
        ("Studio (bright)", "bright clean studio, white walls, soft diffused light, modern minimalist"),
        ("Urban rooftop", "city rooftop at night, skyline in background, ambient city lights, urban atmosphere"),
        ("Conference stage", "professional conference stage, spotlight on speaker, dark audience in background, authority positioning"),
        ("Abstract void", "pure black void background, subject floating in darkness, isolated focus, cinematic"),
        ("Digital space", "abstract digital environment, data streams, blockchain nodes, floating code, matrix-inspired"),
        ("Home office", "clean home office, natural light from window, plants, personal touches, authentic workspace"),
        ("Luxury interior", "high-end interior, marble surfaces, dark wood, ambient lighting, premium atmosphere"),
        ("Street / outdoor", "urban street environment, concrete walls, natural light, candid feel, real world"),
        ("Whiteboard / teaching", "clean whiteboard or glass board in background, marker annotations visible, educational setup, authority positioning"),
        ("Multi-monitor command center", "wall of monitors showing charts, data, and dashboards, command center aesthetic, ambient multi-screen glow, high-stakes operation feel"),
    ]

    add_table(
        [["Environment", "Prompt Block"]] + [[name, prompt] for name, prompt in environments],
        col_widths=[1.5*inch, 4.3*inch]
    )

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: MOODS / ATMOSPHERE
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("5. Moods / Atmosphere", h1))

    moods = [
        ("Intense / powerful", "intense atmosphere, commanding presence, sharp focus, high contrast, every detail deliberate"),
        ("Calm / wise", "calm serene atmosphere, composed and centered, soft tones, unhurried energy, meditative quality"),
        ("Chaotic / urgent", "chaotic energy, multiple data streams, fast-moving particles, screen glitches, information overload aesthetic"),
        ("Luxurious / premium", "luxury aesthetic, rich textures, matte surfaces, gold and dark tones, aspirational quality"),
        ("Gritty / streetwise", "raw gritty aesthetic, urban textures, concrete and steel, imperfect surfaces, authentic not polished"),
        ("Clean / minimal", "ultra clean minimalist aesthetic, negative space, single focal point, modern design sensibility"),
        ("Mysterious", "mysterious atmosphere, fog or haze, partial visibility, questions unanswered, intrigue"),
        ("Futuristic", "futuristic environment, holographic elements, floating data, clean lines, advanced technology"),
        ("Warm / personal", "warm personal atmosphere, soft light, comfortable environment, approachable and relatable"),
        ("Dark / ominous", "dark ominous atmosphere, deep shadows, sense of warning, something at stake, tension"),
        ("Pattern interrupt", "jarring visual contrast, unexpected composition, something visually wrong that forces a second look, scroll-stopping energy"),
        ("Demo energy", "hands-on active demonstration in progress, tools visible, mid-action frozen moment, workshop feel"),
        ("Reveal moment", "split-second of discovery, curtain-pull energy, the exact moment something hidden becomes visible, dramatic unveiling"),
    ]

    add_table(
        [["Mood", "Prompt Block"]] + [[name, prompt] for name, prompt in moods],
        col_widths=[1.5*inch, 4.3*inch]
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: HOW TO BUILD A KEYFRAME PROMPT
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("6. How to Build a Keyframe Prompt from a Script", h1))
    elements.append(Paragraph(
        "Follow this step-by-step process for every shot in your shot deck. "
        "The result is a complete prompt you can paste into any AI image generator.",
        body
    ))

    elements.append(Paragraph("Step-by-Step Assembly", h2))

    steps = [
        ("1. Read the script line", "Look at what is being said/shown in this shot. What emotion? What action? What's the point?"),
        ("2. Pick the camera angle", "Use the Camera Angle Selection Guide (Section 1). Match the shot's emotional intent to the right angle."),
        ("3. Pick the lighting", "Match the overall art direction. Use Red accent for brand shots, Screen glow for tech, Dramatic side for authority."),
        ("4. Pick the environment", "Where does this scene take place? Trading desk, studio, abstract void, street?"),
        ("5. Pick the mood", "What should the viewer FEEL? Intense, calm, chaotic, mysterious?"),
        ("6. Add the character", "Copy the character description from character-library.md. Add the pose/action for this specific shot."),
        ("7. Add quality tags", "Always end with: photograph, ultra realistic, editorial quality, 8K resolution"),
        ("8. Add negative prompt", "Always include: blurry, low quality, distorted face, extra fingers, watermark, cartoon, anime"),
        ("9. Set aspect ratio", "9:16 for TikTok/Reels, 16:9 for YouTube, 1:1 for Instagram feed"),
    ]

    add_table(
        [["Step", "Action"]] + [[s, a] for s, a in steps],
        col_widths=[0.4*inch, 5.4*inch]
    )

    elements.append(Paragraph("Prompt Assembly Formula", h2))
    elements.append(Paragraph(
        "<font face='Courier' size='9'>[Character description], [Action/Pose], [Environment block], "
        "[Lighting block], [Camera angle block], [Style modifiers], [Mood block], [Aspect ratio]</font>",
        code_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Example: Script Line to Keyframe Prompt", h2))
    elements.append(Paragraph(
        "<b>Script line:</b> \"I built my entire system during a bear market. Now I just approve signals.\"<br/>"
        "<b>Shot intent:</b> Authority + story (bold claim about past achievement)",
        body
    ))
    elements.append(Paragraph(
        "<b>Assembled prompt:</b>",
        body
    ))
    elements.append(Paragraph(
        "Confident African man in dark premium hoodie, slight smirk, arms crossed, "
        "looking directly at camera, modern trading desk with multiple monitors showing crypto charts "
        "dark room ambient screen glow, single key light from camera left at 45 degrees deep shadows "
        "on right side noir-style contrast, low angle shot from below subject appears dominant and powerful, "
        "photograph ultra realistic editorial quality 8K resolution, intense atmosphere commanding presence "
        "sharp focus, 9:16 vertical format",
        code_style
    ))
    elements.append(Paragraph(
        "<b>Negative prompt:</b> blurry, low quality, distorted face, extra fingers, watermark, cartoon, anime, "
        "3D render, bright cheerful colors, wrong ethnicity, different person",
        code_style
    ))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 7: MANUAL KEYFRAME WORKFLOW
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("7. Manual Keyframe Workflow (No fal.ai Credits)", h1))
    elements.append(Paragraph(
        "When fal.ai credits are exhausted, the pipeline still generates all prompts. "
        "You just generate the images manually instead of through the API.",
        body
    ))

    elements.append(Paragraph("Workflow", h2))
    manual_steps = [
        ("1", "Run the pipeline through Steps 1-2 normally (Art Direction + Storyboard)"),
        ("2", "At Step 3, the pipeline outputs a Keyframe Prompt Sheet with numbered prompts"),
        ("3", "Open your image generator of choice (see tool comparison below)"),
        ("4", "Paste each prompt directly — they are tool-agnostic"),
        ("5", "Generate 2-3 variations per shot, pick the best"),
        ("6", "For character consistency: use the best result from shot 1 as reference for shot 2, etc."),
        ("7", "Save images as shot-01.png, shot-02.png in the project visuals folder"),
        ("8", "Continue the pipeline from Step 4 (Voice) onward normally"),
    ]
    add_table(
        [["#", "Action"]] + manual_steps,
        col_widths=[0.4*inch, 5.4*inch]
    )

    elements.append(Paragraph("Tool Comparison for Manual Generation", h2))
    add_table([
        ["Tool", "Best For", "Character Consistency", "Cost"],
        ["ChatGPT (GPT-4o)", "Quick, conversational, iterative", "Good with reference images", "ChatGPT Plus ($20/mo)"],
        ["Midjourney", "Highest aesthetic quality", "Moderate (use --cref flag)", "Basic $10/mo"],
        ["DALL-E 3", "Text-accurate, literal prompts", "Moderate", "Via ChatGPT or API"],
        ["Ideogram", "Text in images, logos", "Low", "Free tier available"],
        ["Leonardo AI", "Style consistency, ControlNet", "Good with model training", "Free tier + paid"],
        ["Local Flux/SD", "Unlimited, private, LoRA support", "Best with trained LoRA", "Free (GPU required)"],
    ], col_widths=[1.1*inch, 1.5*inch, 1.5*inch, 1.7*inch])

    elements.append(Paragraph(
        "<b>Tip:</b> For best character consistency without fal.ai, use ChatGPT image gen with the character "
        "reference photo attached. Say: \"Keep this exact person's face and features in all images I ask for.\" "
        "Then paste each keyframe prompt one by one.",
        tip_style
    ))

    # ═══════════════════════════════════════════════════════════════
    # SECTION 8: CAROUSEL FIRST-SLIDE RULE
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("8. Carousel Production: Aesthetic First Slide Rule", h1))
    elements.append(Paragraph(
        "Data from high-performing carousel posts (2,000+ likes) shows that carousels with "
        "aesthetically pleasing first slides consistently outperform text-heavy openers. "
        "The first slide acts as a visual hook — it must stop the scroll before the viewer reads anything.",
        body
    ))
    elements.append(Paragraph(
        "<b>Rule:</b> Every carousel's first slide must be a visually striking, aesthetically crafted image "
        "— not a text-heavy title card. Use the keyframe prompt system to generate it.",
        tip_style
    ))

    add_table([
        ["Element", "Do This", "Not This"],
        ["First slide", "Beautiful visual with minimal text (3-5 words max)", "Wall of text, generic title card"],
        ["Colors", "Rich, branded, high contrast", "Flat, low-contrast, generic"],
        ["Typography", "Large, bold, clean — overlaid on visual", "Small text, multiple fonts, cluttered"],
        ["Composition", "Subject-focused, rule of thirds, breathing room", "Centered text block, no visual hierarchy"],
        ["Mood", "Aspirational, premium, or emotionally striking", "Informational, corporate, bland"],
    ], col_widths=[1.0*inch, 2.4*inch, 2.4*inch])

    elements.append(Paragraph(
        "Generate the first carousel slide using the same keyframe prompt system: pick a camera angle, "
        "lighting, mood, and environment that matches the carousel's topic. The remaining slides can be "
        "text-heavy educational content — but slide 1 is a visual hook.",
        body
    ))

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 9: QUICK REFERENCE CHEAT SHEET
    # ═══════════════════════════════════════════════════════════════
    elements.append(Paragraph("9. Quick Reference Cheat Sheet", h1))
    elements.append(Paragraph(
        "Cut out and keep next to your workstation. Maps script moments directly to prompt choices.",
        body
    ))

    add_table([
        ["When the script says...", "Use this angle", "Use this lighting", "Use this mood"],
        ["\"I built / I created / My system\"", "Low angle (power)", "Red accent", "Intense / powerful"],
        ["\"Here's what happened / Story time\"", "Close-up", "Golden hour", "Warm / personal"],
        ["\"Let me show you / Watch this\"", "POV first-person", "Screen glow", "Demo energy"],
        ["\"The truth is / Nobody talks about\"", "Dutch angle", "Split light", "Dark / ominous"],
        ["\"3 things / 5 steps / Framework\"", "Medium shot", "Clean studio", "Clean / minimal"],
        ["\"What if / Imagine / Picture this\"", "Wide / establishing", "Neon crypto", "Futuristic"],
        ["\"Comment / Follow / DM me\"", "Three-quarter", "Practical lights", "Warm / personal"],
        ["\"Before vs After / Old way vs New\"", "Split screen", "Dramatic side", "Pattern interrupt"],
        ["\"I was scared / I failed / Vulnerable\"", "High angle", "Single candle", "Calm / wise"],
        ["\"Breaking / Just happened / Alert\"", "Extreme close-up", "Dark-to-spotlight", "Reveal moment"],
        ["Charts / Data / Numbers", "Over-the-shoulder", "Screen glow", "Intense / powerful"],
        ["Opening hook (first 3 seconds)", "Extreme close-up OR Low angle", "Red accent or Neon", "Pattern interrupt"],
    ], col_widths=[1.8*inch, 1.3*inch, 1.2*inch, 1.5*inch])

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Quivira Brand Tags (add to every brand-consistent shot)", h2))
    elements.append(Paragraph(
        "<font face='Courier' size='8'>dark background (#0A0A0F deep black), red accent lighting (#E63946), "
        "cinematic color grading, warm shadows</font>",
        code_style
    ))
    elements.append(Paragraph(
        "<font face='Courier' size='8'>Negative: blurry, low quality, distorted face, extra fingers, "
        "watermark, cartoon, anime, 3D render, bright cheerful colors, generic stock photo, wrong ethnicity</font>",
        code_style
    ))

    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=MED_GRAY))
    elements.append(Paragraph(
        "<i>Keyframe Prompt &amp; Camera Angle Guide v1.0 — Quivira Production System — March 2026</i>",
        ParagraphStyle("Footer", parent=body, fontSize=8, textColor=HexColor("#999999"), alignment=TA_CENTER)
    ))

    doc.build(elements)
    print(f"PDF generated: {OUTPUT_PATH}")
    print(f"Pages: ~10")


if __name__ == "__main__":
    build_pdf()
