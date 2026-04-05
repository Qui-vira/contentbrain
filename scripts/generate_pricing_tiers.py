"""Generate Pricing Tiers PDF for Quivira AI Course Launch."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', '06-Drafts')
OUT_PATH = os.path.join(OUT_DIR, 'pricing-tiers.pdf')

DARK = HexColor('#1a1a2e')
RED = HexColor('#e94560')
GRAY = HexColor('#444444')
LIGHT = HexColor('#f5f5f5')
WHITE = HexColor('#ffffff')
MID = HexColor('#cccccc')
GREEN = HexColor('#2d6a4f')
GOLD = HexColor('#b5862a')

styles = getSampleStyleSheet()

def S(name, **kw):
    try:
        styles.add(ParagraphStyle(name, **kw))
    except KeyError:
        pass

S('CoverTitle', parent=styles['Title'], fontSize=30, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=10)
S('CoverSub', parent=styles['Normal'], fontSize=12, textColor=MID,
  alignment=TA_CENTER, spaceAfter=5)
S('SectionHead', parent=styles['Heading1'], fontSize=16, textColor=DARK,
  fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=6)
S('SubHead', parent=styles['Heading2'], fontSize=12, textColor=RED,
  fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
S('TierTitle', parent=styles['Heading1'], fontSize=18, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceBefore=0, spaceAfter=0)
S('TierPrice', parent=styles['Normal'], fontSize=28, textColor=RED,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
S('TierSub', parent=styles['Normal'], fontSize=10, textColor=MID,
  alignment=TA_CENTER, spaceAfter=0)
S('Body2', parent=styles['Normal'], fontSize=9, textColor=GRAY, leading=13, spaceAfter=5)
S('BulletP', parent=styles['Normal'], fontSize=9, textColor=GRAY,
  leading=13, leftIndent=12, spaceAfter=2)
S('TableHead3', parent=styles['Normal'], fontSize=8, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER)
S('TableCell3', parent=styles['Normal'], fontSize=8, textColor=GRAY, leading=11)
S('Note2', parent=styles['Normal'], fontSize=8, textColor=GRAY,
  fontName='Helvetica-Oblique', leftIndent=10, spaceAfter=4)
S('Check', parent=styles['Normal'], fontSize=9, textColor=GREEN,
  fontName='Helvetica-Bold', leading=13, leftIndent=12, spaceAfter=2)
S('Cross', parent=styles['Normal'], fontSize=9, textColor=MID,
  leading=13, leftIndent=12, spaceAfter=2)

def hr():
    return HRFlowable(width='100%', thickness=1, color=RED, spaceAfter=6, spaceBefore=2)

W = A4[0] - 3.6*cm

def tier_header(label, price, subtitle, color):
    block = Table([
        [Paragraph(label, styles['TierTitle'])],
        [Paragraph(price, styles['TierPrice'])],
        [Paragraph(subtitle, styles['TierSub'])],
    ], colWidths=[W])
    block.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), color),
        ('BACKGROUND', (0,1), (-1,1), DARK),
        ('BACKGROUND', (0,2), (-1,2), DARK),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return block

def make_table3(headers, rows, col_widths):
    data = [[Paragraph(h, styles['TableHead3']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCell3']) for c in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='Quivira AI Course Pricing Tiers', author='@big_quiv'
    )
    story = []

    # COVER
    cover = Table([
        [Paragraph('QUIVIRA AI COURSE', styles['CoverTitle'])],
        [Paragraph('Pricing Architecture & Promotion Strategy', styles['CoverSub'])],
        [Paragraph('Phase 3  ·  April 2026  ·  @big_quiv', styles['CoverSub'])],
    ], colWidths=[W])
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
    ]))
    story += [cover, Spacer(1, 20)]

    # PRICING RATIONALE
    story.append(Paragraph('Pricing Rationale', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'The $15–$50 range is priced below market rate for live cohort delivery (industry benchmark: $97–$500) '
        'to maximise first-cohort enrolment, collect testimonials at scale, and build proof of community '
        'before raising prices in future cohorts. This is a deliberate land-and-expand strategy, not a '
        'reflection of course value. Each tier has a clear, tangible deliverable difference — not just "more access."',
        styles['Body2']))
    story.append(Spacer(1, 10))

    # TIER COMPARISON TABLE
    story.append(Paragraph('Tier Comparison', styles['SectionHead']))
    story.append(hr())

    comp_rows = [
        ['Deliverable', 'Starter ($15)', 'Builder ($30)', 'Full Access ($50)'],
        ['Pre-recorded modules for your track', 'YES', 'YES', 'YES'],
        ['Telegram community access (30 days)', 'YES', 'YES', 'YES'],
        ['Live session attendance (2x/week)', 'NO', 'YES', 'YES'],
        ['Google Meet live builds', 'NO', 'YES', 'YES'],
        ['Live Q&A with instructor', 'NO', 'YES', 'YES'],
        ['Resource templates (prompts, frameworks, SOPs)', 'PDF only', 'YES — all formats', 'YES — all formats'],
        ['Demo Day participation (May 31)', 'View only', 'YES', 'YES'],
        ['Completion certificate (PDF)', 'NO', 'YES', 'YES'],
        ['Direct instructor DM access (1 question per week)', 'NO', 'NO', 'YES'],
        ['Bonus: ContentBrain System Walkthrough', 'NO', 'NO', 'YES'],
        ['Bonus: Trigon Labs Signal Setup Guide', 'NO', 'NO', 'YES'],
        ['Lifetime access to recordings after cohort', 'NO', 'YES', 'YES'],
        ['All 3 course topics (multi-topic access)', 'NO — 1 topic only', 'NO — 1 topic only', 'YES — all 3 topics'],
    ]

    data = [[Paragraph(h, styles['TableHead3']) for h in comp_rows[0]]]
    for row in comp_rows[1:]:
        styled = []
        for i, cell in enumerate(row):
            if i == 0:
                styled.append(Paragraph(cell, styles['TableCell3']))
            elif cell == 'YES':
                styled.append(Paragraph(f'<font color="#2d6a4f"><b>✓ YES</b></font>', styles['TableCell3']))
            elif cell == 'NO':
                styled.append(Paragraph(f'<font color="#aaaaaa">— NO</font>', styles['TableCell3']))
            else:
                styled.append(Paragraph(cell, styles['TableCell3']))
        data.append(styled)

    comp_t = Table(data, colWidths=[W*0.42, W*0.18, W*0.18, W*0.22])
    comp_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('BACKGROUND', (2,0), (2,0), HexColor('#1d4e89')),
        ('BACKGROUND', (3,0), (3,0), GREEN),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story += [comp_t, Spacer(1, 14)]

    # TIER 1
    story.append(PageBreak())
    story.append(tier_header('TIER 1 — STARTER', '$15', 'One-time payment · Self-paced · Pre-recorded only', RED))
    story.append(Spacer(1, 10))

    story.append(Paragraph('What They Get', styles['SubHead']))
    for item in [
        'Access to all pre-recorded modules for their selected course topic and audience track',
        'PDF resource pack: prompt templates, workflow checklists, tool comparison guide',
        'Telegram community access for 30 days (read + post, not live class)',
        'Access to replay recordings after Demo Day (not during the live cohort)',
    ]:
        story.append(Paragraph(f'• {item}', styles['BulletP']))

    story.append(Paragraph('Who This Is For', styles['SubHead']))
    story.append(Paragraph(
        'Students who are unsure about committing to live classes, are in tight budgets, or prefer '
        'fully asynchronous learning. Also ideal for people who want to test the content quality '
        'before upgrading to Builder or Full Access.',
        styles['Body2']))

    story.append(Paragraph('Conversion Hook', styles['SubHead']))
    story.append(Paragraph(
        '"$15 and you get the full system — pre-recorded so you watch at your own pace, '
        'plus the templates we built it with. No live commitment required."',
        styles['Body2']))

    story.append(Paragraph('Organic Promotion Strategies', styles['SubHead']))
    for strat in [
        'X/Twitter: "I\'m charging $15 for this. I know what you\'re thinking. Here\'s why." (thread, no link — DM for access)',
        'Telegram: Announce to your community with a 30-second demo clip of one pre-recorded module',
        'Instagram: "I spent 2 years building this system. You\'re getting it for $15. Not a typo." (visual text card)',
        'LinkedIn: Value post on AI automation savings → CTA at end "I built a course around this — $15, DM me STARTER"',
        'Free freebie drop: Give away Module 1 of any track for free. Make people feel the quality before paying.',
    ]:
        story.append(Paragraph(f'• {strat}', styles['BulletP']))

    story.append(Paragraph('Paid Ad Options (Future Use)', styles['SubHead']))
    for ad in [
        'Meta (Facebook/Instagram): Video ad — 30s demo of pre-recorded module. Target: 18–34, interests "AI tools" + "online learning". CPM est. $8–$12 (Nigeria/Africa), $20–$30 (US/UK). Budget: $50–$100 for 5–10 conversions at $15 price point.',
        'TikTok Ads: Screen recording of AI automation in action → "This course is $15" text overlay. CPM est. $5–$8. Budget: $30–$50 for test run.',
        'X/Twitter Ads: Promoted post (thread intro). Target: followers of @naval, @levelsio, @alexhormozi. CPM est. $8–$15. Budget: $50 minimum.',
    ]:
        story.append(Paragraph(f'• {ad}', styles['BulletP']))

    story.append(Spacer(1, 12))

    # TIER 2
    story.append(tier_header('TIER 2 — BUILDER', '$30', 'One-time payment · Live classes + recordings · 1 topic', HexColor('#1d4e89')))
    story.append(Spacer(1, 10))

    story.append(Paragraph('What They Get', styles['SubHead']))
    for item in [
        'Everything in Starter',
        'Live session attendance (2× per week, 7–9 PM WAT, Tuesday + Thursday)',
        'Google Meet live build-alongs with screen share and real-time Q&A',
        'Resource templates in all formats (Notion, PDF, Google Doc, raw prompts)',
        'Demo Day participation — present your work, get instructor feedback',
        'Completion certificate (branded Quivira PDF)',
        'Lifetime access to all recordings after the cohort closes',
    ]:
        story.append(Paragraph(f'• {item}', styles['BulletP']))

    story.append(Paragraph('Who This Is For', styles['SubHead']))
    story.append(Paragraph(
        'Students who want accountability, real-time help, and the live classroom dynamic. '
        'The majority of students should land here — it is the best value-to-price ratio in the stack.',
        styles['Body2']))

    story.append(Paragraph('Conversion Hook', styles['SubHead']))
    story.append(Paragraph(
        '"$30 and you get the pre-recorded modules, live classes twice a week, Q&A, and a certificate '
        'when you finish. I\'ve seen people pay $300 for less. This is the first cohort — '
        'the price will not stay here."',
        styles['Body2']))

    story.append(Paragraph('Organic Promotion Strategies', styles['SubHead']))
    for strat in [
        'X/Twitter: Thread — "Here\'s exactly what happens in Week 1 of the Builder track." Walk through Day 1 content in the thread as a teaser. CTA: DM BUILDER for link.',
        'Telegram: Post a 60-second Kling video showing the live session setup — real screen, real build, real output.',
        'Instagram: Carousel — "What $30 gets you in the Quivira AI course" — one slide per deliverable.',
        'LinkedIn: Case study angle — "I used to spend $2,000/month on a developer. Then I taught myself to build with AI in 30 days. Here\'s the course I wish existed." CTA buried in comments.',
        'Validation post (Day 7 from today): "Would you pay $30 for live AI classes twice a week? What would make it worth it to you?" — use replies to refine messaging.',
    ]:
        story.append(Paragraph(f'• {strat}', styles['BulletP']))

    story.append(Paragraph('Paid Ad Options (Future Use)', styles['SubHead']))
    for ad in [
        'Meta: Retargeting campaign — target people who viewed Starter content/page but did not convert. Angle: "You\'ve seen what\'s inside. $30 gets you the live experience." Est. CPL: $8–$15.',
        'Google Search: Target "AI automation course", "learn Claude Code", "vibe coding course". CPC est. $1.50–$3.00 (non-branded). Budget: $100/week minimum to test.',
        'LinkedIn Ads: Sponsored post targeting Web3 professionals, solopreneurs, marketers aged 25–40. CPM est. $25–$40 (expensive but high-intent). Budget: $100 minimum test.',
    ]:
        story.append(Paragraph(f'• {ad}', styles['BulletP']))

    story.append(Spacer(1, 12))

    # TIER 3
    story.append(PageBreak())
    story.append(tier_header('TIER 3 — FULL ACCESS', '$50', 'One-time payment · Everything · All 3 topics · Direct access', GREEN))
    story.append(Spacer(1, 10))

    story.append(Paragraph('What They Get', styles['SubHead']))
    for item in [
        'Everything in Builder',
        'Access to ALL THREE course topics (AI Automation + AI Video Creation + Coding with AI)',
        'Direct DM access to instructor — 1 question per week, guaranteed response within 24 hrs',
        'BONUS: Full ContentBrain System Walkthrough — the complete AI content OS @big_quiv runs daily',
        'BONUS: Trigon Labs Signal Setup Guide — how the AI trading signal system was built from scratch',
        'Priority seating in all live sessions',
        'First access to next cohort at founder rate (if you refer one student)',
    ]:
        story.append(Paragraph(f'• {item}', styles['BulletP']))

    story.append(Paragraph('Who This Is For', styles['SubHead']))
    story.append(Paragraph(
        'Serious builders who want the full system, the direct access, and the bonuses. '
        'Also the right tier for business owners who want to extract maximum ROI in 30 days. '
        'The bonuses alone (ContentBrain + Trigon signal guide) would sell separately at $30+ each.',
        styles['Body2']))

    story.append(Paragraph('Conversion Hook', styles['SubHead']))
    story.append(Paragraph(
        '"$50. Three courses. Direct access to me. Two bonuses that I have never published anywhere. '
        'This is only possible because it\'s the first cohort and I want proof that this works. '
        'The next cohort will not be $50."',
        styles['Body2']))

    story.append(Paragraph('Organic Promotion Strategies', styles['SubHead']))
    for strat in [
        'X/Twitter: "I\'m giving away the ContentBrain system as a bonus inside the Full Access tier. I built this over 18 months. It has never been published. You get it for $50." (one tweet, no thread — let the brevity do the work)',
        'Telegram: "Full Access buyers get direct DM access to me. 1 question a week. This is the closest thing to 1-on-1 coaching I\'ve ever offered at this price." Pin this message.',
        'Instagram: Reel — "Here\'s what the ContentBrain system looks like." Show the vault, the skills, the signal pipeline. Do NOT explain it fully. End with "This is inside the Full Access tier."',
        'LinkedIn: "I spent 18 months building an AI content OS. I use it every day. I\'m including it as a bonus in a $50 course. Full breakdown in the comments." (link in first comment)',
        'Scarcity mechanism: "Full Access is capped at 20 students per cohort. This is not fake scarcity — I can only DM 20 people per week at quality." Post a live seat counter.',
    ]:
        story.append(Paragraph(f'• {strat}', styles['BulletP']))

    story.append(Paragraph('Paid Ad Options (Future Use)', styles['SubHead']))
    for ad in [
        'Meta: Lookalike audience from email list of existing community. "You\'re in the community. This is the next level." CPL target: $15–$25 at $50 price = 2–3× ROAS minimum.',
        'YouTube pre-roll: 30-second "watch me build X in 10 minutes" hook → CTA to Full Access landing page. CPV est. $0.03–$0.08. Budget: $100 buys 1,250–3,300 views.',
        'Influencer/KOL: Offer one Full Access seat to a relevant micro-creator (5K–50K followers) in exchange for an honest review post. Cost: $50 in course value. Potential reach: 5K–50K at zero cash spend.',
    ]:
        story.append(Paragraph(f'• {ad}', styles['BulletP']))

    # REVENUE PROJECTIONS
    story.append(PageBreak())
    story.append(Paragraph('Revenue Projections (First Cohort)', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'Conservative, realistic, and stretch scenarios for the first cohort. '
        'Based on zero paid advertising and organic-only promotion from existing audience.',
        styles['Body2']))
    story.append(Spacer(1, 8))

    proj_rows = [
        ['Scenario', 'Starter ($15)', 'Builder ($30)', 'Full Access ($50)', 'Total Revenue', 'Total Students'],
        ['Conservative', '10 students', '15 students', '10 students', '$900', '35'],
        ['Realistic', '20 students', '30 students', '20 students', '$1,900', '70'],
        ['Stretch', '40 students', '50 students', '30 students', '$3,700', '120'],
    ]
    story.append(make_table3(proj_rows[0], proj_rows[1:], [W*0.16, W*0.16, W*0.16, W*0.20, W*0.18, W*0.14]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'Note: Revenue projections are estimates based on conversion rates of 1–3% from social audience. '
        'These figures do not include Gumroad transaction fees (10%). Realistic scenario assumes '
        'consistent daily posting across all platforms for 7 days before launch.',
        styles['Note2']))

    # PLATFORM DECISION
    story.append(Paragraph('Platform Decision — Where to Sell', styles['SectionHead']))
    story.append(hr())
    plat_rows = [
        ['Platform', 'Pros', 'Cons', 'Recommended Tier'],
        ['Gumroad', 'Zero setup cost, instant payment, simple link, good for one-time products', '10% fee, no community features', 'Starter ($15)'],
        ['Selar.co', 'Made for African creators, supports Naira and USD, lower fees', 'Smaller discovery audience', 'All tiers (primary for NGN buyers)'],
        ['Skool', 'Built-in community + course + live events. Subscription or one-time.', '$99/mo platform fee — only viable if 5+ students/month', 'Builder + Full Access (future)'],
        ['Direct (Telegram/DM)', 'Zero fees, full control, builds relationship', 'Manual, does not scale, payment via transfer', 'First 10 students only — build proof then move to platform'],
        ['Gumroad + Notion portal', 'Gumroad handles payment, Notion hosts pre-recorded content links', 'Manual access management', 'Best starter stack for this launch'],
    ]
    story.append(make_table3(plat_rows[0], plat_rows[1:], [W*0.17, W*0.30, W*0.28, W*0.25]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'Recommendation: Launch on Gumroad + Selar.co simultaneously. Gumroad for international buyers. '
        'Selar for Nigerian/African buyers paying in Naira. Course content delivered via Notion portal '
        'link (password-protected page). Community on Telegram. Live sessions on Google Meet.',
        styles['Body2']))

    # FOOTER
    story.append(Spacer(1, 24))
    footer = Table([[Paragraph('Quivira AI Course — Phase 3 Pricing Architecture Complete', styles['CoverTitle'])],
                    [Paragraph('Built April 3, 2026  ·  @big_quiv / ContentBrain', styles['CoverSub'])]],
                   colWidths=[W])
    footer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(footer)

    doc.build(story)
    print(f'PDF saved: {OUT_PATH}')

if __name__ == '__main__':
    build()
