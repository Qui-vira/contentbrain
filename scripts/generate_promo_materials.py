"""Generate Promo Materials PDF for Quivira AI Course Launch — Phase 8."""
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
OUT_PATH = os.path.join(OUT_DIR, 'promo-materials.pdf')

DARK = HexColor('#1a1a2e')
RED = HexColor('#e94560')
GRAY = HexColor('#444444')
LIGHT = HexColor('#f5f5f5')
WHITE = HexColor('#ffffff')
MID = HexColor('#cccccc')
GREEN = HexColor('#2d6a4f')

styles = getSampleStyleSheet()
def S(name, **kw):
    try: styles.add(ParagraphStyle(name, **kw))
    except KeyError: pass

S('CT', parent=styles['Title'], fontSize=28, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=10)
S('CS', parent=styles['Normal'], fontSize=11, textColor=MID,
  alignment=TA_CENTER, spaceAfter=5)
S('SH', parent=styles['Heading1'], fontSize=15, textColor=DARK,
  fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6)
S('PlatHead', parent=styles['Heading1'], fontSize=13, textColor=WHITE,
  fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=0, alignment=TA_CENTER)
S('SubH', parent=styles['Heading2'], fontSize=11, textColor=RED,
  fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4)
S('B', parent=styles['Normal'], fontSize=9, textColor=GRAY, leading=13, spaceAfter=5)
S('AdCopy', parent=styles['Normal'], fontSize=10, textColor=DARK,
  leading=15, leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=8,
  fontName='Helvetica')
S('AdLabel', parent=styles['Normal'], fontSize=8, textColor=MID,
  fontName='Helvetica-Oblique', spaceAfter=2)
S('TH', parent=styles['Normal'], fontSize=8, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER)
S('TC', parent=styles['Normal'], fontSize=8, textColor=GRAY, leading=11)

def hr():
    return HRFlowable(width='100%', thickness=1, color=RED, spaceAfter=6, spaceBefore=2)

W = A4[0] - 3.6*cm

def cover_block(title, sub='', sub2=''):
    rows = [[Paragraph(title, styles['CT'])]]
    if sub: rows.append([Paragraph(sub, styles['CS'])])
    if sub2: rows.append([Paragraph(sub2, styles['CS'])])
    t = Table(rows, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), DARK),
        ('TOPPADDING',(0,0),(-1,-1), 12),
        ('BOTTOMPADDING',(0,0),(-1,-1), 12),
        ('LEFTPADDING',(0,0),(-1,-1), 18),
    ]))
    return t

def plat_banner(name, color):
    t = Table([[Paragraph(name, styles['PlatHead'])]], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), color),
        ('TOPPADDING',(0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING',(0,0),(-1,-1), 14),
    ]))
    return t

def ad_table(headers, rows, widths):
    data = [[Paragraph(h, styles['TH']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['TC']) for c in row])
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), DARK),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, LIGHT]),
        ('GRID',(0,0),(-1,-1),0.3,MID),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),5),
    ]))
    return t


PLATFORMS = [
    {
        'name': 'X / TWITTER',
        'color': HexColor('#1a1a2e'),
        'organic': [
            {
                'label': 'Organic Post 1 — Pre-Announcement (Days 8–16)',
                'copy': (
                    'I\'ve been building something for the past month.\n\n'
                    'Three AI courses. Four audience tracks. Live classes twice a week.\n\n'
                    'AI Automation. AI Video Creation. Coding with AI.\n\n'
                    'For beginners who\'ve never touched AI.\n'
                    'For developers who want to build faster.\n'
                    'For creators who want a content system that runs itself.\n'
                    'For business owners who want time back.\n\n'
                    'Price: $15 to $50. First cohort only.\n\n'
                    'Dropping details this week. Follow so you don\'t miss it.'
                ),
                'target': 'All segments — curiosity/anticipation builder',
            },
            {
                'label': 'Organic Post 2 — Hard Announcement (Day 17)',
                'copy': (
                    'The Quivira AI Course is live.\n\n'
                    '3 topics:\n'
                    '→ AI Automation\n'
                    '→ AI Video Creation\n'
                    '→ Coding with AI\n\n'
                    '4 tracks: Beginners. Developers. Creators. Business Owners.\n\n'
                    'Live classes twice a week via Google Meet.\n'
                    'Community on Telegram.\n'
                    'Start date: May 3, 2026.\n\n'
                    '$15 — self-paced (pre-recorded)\n'
                    '$30 — live classes + recordings\n'
                    '$50 — full access + direct DM to me + 2 bonuses\n\n'
                    'DM me COURSE for the link.'
                ),
                'target': 'All segments — launch announcement',
            },
            {
                'label': 'Organic Post 3 — Final Push (Day 29)',
                'copy': (
                    'Last 24 hours.\n\n'
                    'Quivira AI Course Cohort 1 closes tonight.\n\n'
                    'After today:\n'
                    '→ Prices go up for Cohort 2\n'
                    '→ Full Access (all 3 topics) cap is 20 students — almost full\n'
                    '→ ContentBrain + Trigon bonuses no longer included\n\n'
                    '$15 / $30 / $50. Pick yours.\n\n'
                    'DM COURSE. Link in bio.'
                ),
                'target': 'All segments — FOMO/urgency',
            },
        ],
        'ads': [
            {
                'variant': 'Ad Variant A — Beginners (Pre-Class)',
                'copy': 'You don\'t need to code to use AI. You don\'t need to be technical. You just need someone to show you the workflow. Live AI classes, twice a week, starting May 3. $30. DM COURSE.',
                'targeting': 'Interests: "AI tools", "online learning", "side hustle", "ChatGPT". Age: 18–35. Location: Nigeria, Ghana, UK, US.',
                'timing': 'Run Days 14–30 (2 weeks before and during enrolment window)',
                'format': 'Promoted tweet — single post, no image required',
                'est_cost': '$50–$100 test budget. CPM $8–$15. Est. 3,300–6,200 impressions. Target: 10–20 DM responses.',
            },
            {
                'variant': 'Ad Variant B — Developers (Pre-Class)',
                'copy': 'Claude Code is changing how developers ship. Learn it from someone who uses it every day to build trading systems, content pipelines, and client apps. Live cohort. 30 days. $50 full access.',
                'targeting': 'Interests: "software development", "Claude", "LLMs", "API integration". Followers of: @AnthropicAI, @levelsio. Age: 22–40.',
                'timing': 'Run Days 17–29',
                'format': 'Promoted tweet — include code screenshot image',
                'est_cost': '$50–$100 test. CPM $10–$18. Target: developer segment — lower volume, higher intent.',
            },
            {
                'variant': 'Ad Variant C — Business Owners (Mid-Campaign)',
                'copy': 'What if you could save 10 hours a week without hiring anyone? AI automation. No code. No developer. Just systems that work. I\'ll show you live. $30 for the full month of classes.',
                'targeting': 'Interests: "business automation", "entrepreneurship", "productivity". Job title: "Founder", "CEO", "Director". Age: 28–45.',
                'timing': 'Run Days 20–30',
                'format': 'Promoted tweet — include before/after time-saving visual',
                'est_cost': '$50–$100 test. CPM $12–$20. Target: business owner intent keywords.',
            },
        ],
    },
    {
        'name': 'TELEGRAM',
        'color': HexColor('#0088cc'),
        'organic': [
            {
                'label': 'Organic Post 1 — Community Teaser (Day 13)',
                'copy': (
                    'To everyone in the Krib.\n\n'
                    'I\'ve been building something for 30 days. You\'re the first to hear about it.\n\n'
                    'A live AI course. Three topics. Four tracks.\n'
                    'Built for beginners, developers, creators, and business owners.\n\n'
                    'Priced at $15–$50 because the first cohort deserves founding prices.\n\n'
                    'Full announcement on April 17. Watch this space.\n\n'
                    'If you\'re already interested, reply NOW so I can send you early access.'
                ),
                'target': 'Existing community — exclusivity play',
            },
            {
                'label': 'Organic Post 2 — Course Announcement (Day 17)',
                'copy': (
                    '🔒 QUIVIRA AI COURSE — Cohort 1\n\n'
                    'What\'s inside:\n'
                    '→ 3 course topics\n'
                    '→ 4 audience tracks (you pick yours)\n'
                    '→ Live sessions 2× per week on Google Meet\n'
                    '→ Telegram community access\n'
                    '→ Pre-recorded modules for async learners\n'
                    '→ Demo Day on May 3\n\n'
                    'Tiers:\n'
                    '$15 — Self-paced (pre-recorded only)\n'
                    '$30 — Live classes + recordings\n'
                    '$50 — Everything + direct DM access to me + 2 exclusive bonuses\n\n'
                    'Link: [GUMROAD/SELAR LINK]\n\n'
                    'Pinning this. Reply with your tier when you\'re in.'
                ),
                'target': 'Community — conversion push. PIN THIS MESSAGE.',
            },
            {
                'label': 'Organic Post 3 — Urgency (Day 27)',
                'copy': (
                    '3 days left.\n\n'
                    'Cohort 1 of the Quivira AI Course closes May 2.\n\n'
                    'Full Access (all 3 topics + direct DM to me) is almost full.\n'
                    'After we close, Cohort 2 prices will be higher.\n\n'
                    'Any questions? Drop them here. I\'ll answer every one personally.\n\n'
                    'Link still live: [LINK]'
                ),
                'target': 'Community fence-sitters — objection handling',
            },
        ],
        'ads': [
            {
                'variant': 'Telegram Channel Ads — not currently available for organic creators',
                'copy': 'N/A — Telegram does not have a self-serve ad platform for course promotions. Use cross-posting from X/Instagram to Telegram instead.',
                'targeting': 'N/A',
                'timing': 'N/A',
                'format': 'Organic community posts only',
                'est_cost': '$0 (organic) — future option: pay to be posted in relevant Telegram channels (DM channel admins).',
            },
        ],
    },
    {
        'name': 'INSTAGRAM',
        'color': HexColor('#C13584'),
        'organic': [
            {
                'label': 'Organic Post 1 — Course Reveal Reel (Day 17)',
                'copy': (
                    'I built this in 30 days.\n\n'
                    '3 AI courses. 4 tracks. Live classes. Real builds.\n\n'
                    'No theory. No fluff. Just the tools and the system.\n\n'
                    'AI Automation / AI Video Creation / Coding with AI\n\n'
                    'Starting May 3. Founding prices: $15–$50.\n\n'
                    'DM me COURSE for the link. First come, first seated.'
                ),
                'target': 'All segments — visual hook first (show the course preview)',
            },
            {
                'label': 'Organic Post 2 — Carousel Breakdown (Day 21)',
                'copy': (
                    'Slide 1: "What you get inside the Quivira AI Course"\n'
                    'Slide 2: Topic 1 — AI Automation (what you\'ll build)\n'
                    'Slide 3: Topic 2 — AI Video Creation (what you\'ll produce)\n'
                    'Slide 4: Topic 3 — Coding with AI (what you\'ll ship)\n'
                    'Slide 5: Your audience track (Beginner / Developer / Creator / Business Owner)\n'
                    'Slide 6: Live sessions schedule\n'
                    'Slide 7: Pricing tiers ($15 / $30 / $50)\n'
                    'Slide 8: "DM COURSE — link also in bio"\n\n'
                    'Caption: "Save this if you\'ve been thinking about getting serious with AI."'
                ),
                'target': 'All segments — full offer reveal',
            },
            {
                'label': 'Organic Post 3 — Social Proof Reel (Day 25)',
                'copy': (
                    'Week 1 inside the Quivira AI Course.\n\n'
                    'What students built:\n'
                    '→ A voice-note-to-social-post automation\n'
                    '→ An AI video in 90 minutes (first time)\n'
                    '→ A working web app, zero prior coding\n\n'
                    'This is just Week 1.\n\n'
                    'Last week to join Cohort 1. Link in bio.'
                ),
                'target': 'All segments — social proof + FOMO',
            },
        ],
        'ads': [
            {
                'variant': 'Meta Ad Variant A — Beginners (Video Ad)',
                'copy': 'Headline: "Your First AI Automation — Live Class"\nBody: Zero coding. Zero tech background. Just you and a system that saves 10 hours a week. Live AI classes starting May 3. $30 for the full month. Limited seats.\nCTA: "DM to Enrol"',
                'targeting': 'Age 18–35. Interests: "AI tools", "online courses", "digital skills", "work from home". Lookalike from email list.',
                'timing': 'Days 17–30. 2-week flight.',
                'format': '30s video ad (screen recording of AI automation running) or single image (dark bg, red text)',
                'est_cost': '$50–$100 test. CPM $8–$12 (NG/GH). Expected reach: 4,000–8,000. Target: 5–10 DMs.',
            },
            {
                'variant': 'Meta Ad Variant B — Creators (Story Ad)',
                'copy': 'Headline: "Make AI Videos Without Filming"\nBody: No camera. No studio. Just prompts and the right workflow. Learn it live in 4 weeks. AI Video Creation course — $30 or $50 full access.\nCTA: "Learn More"',
                'targeting': 'Age 18–34. Interests: "content creation", "TikTok", "Instagram Reels", "video editing". Behaviours: "video content creators".',
                'timing': 'Days 14–28.',
                'format': 'Story ad (9:16). First 3 frames = the before (filming setup). Last 3 frames = the after (AI-generated video).',
                'est_cost': '$50–$100 test. CPM $6–$10 (Stories format cheaper). Target: creator segment.',
            },
            {
                'variant': 'Meta Ad Variant C — Business Owners (Feed Ad)',
                'copy': 'Headline: "Save 10 Hours/Week with AI"\nBody: Most business owners are doing manually what a system could handle in seconds. Learn to build it. Live classes. No developer required. Starting May 3.\nCTA: "DM AUTOMATE"',
                'targeting': 'Age 28–50. Job title: Founder, Director, Manager, Entrepreneur. Interests: "business automation", "productivity tools", "AI".',
                'timing': 'Days 20–30.',
                'format': 'Single image or short video (30s). Business aesthetic — clean, professional.',
                'est_cost': '$100 minimum test. CPM $15–$25 (business targeting more expensive). ROI target: 2 sign-ups at $50 covers the ad spend.',
            },
        ],
    },
]


def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='Quivira AI Course — Promo Materials', author='@big_quiv'
    )
    story = []

    story.append(cover_block(
        'PROMOTION MATERIALS',
        'Phase 8 — Organic Content + Paid Ad Copy (All Platforms)',
        'Quivira AI Course Launch  ·  April 2026  ·  @big_quiv'
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph('Usage Rules', styles['SH']))
    story.append(hr())
    for rule in [
        'Tone: direct, no fluff, zero salesy language. Write like you\'re texting a friend who asked for the real answer.',
        'No hashtags on X/Twitter posts (per @big_quiv brand rules).',
        'Organic posts run before AND during the 30-day class period. Ads run only when budget is available.',
        'Paid ad copy is provided for future use. Do NOT activate until budget is confirmed.',
        'Adapt all copy for your voice before posting — these are frameworks, not final copy.',
        'Never post the same copy across platforms — always adapt tone and format.',
    ]:
        story.append(Paragraph(f'• {rule}', styles['B']))
    story.append(Spacer(1, 8))

    for plat in PLATFORMS:
        story.append(PageBreak())
        story.append(plat_banner(f"PLATFORM: {plat['name']}", plat['color']))
        story.append(Spacer(1, 10))

        # ORGANIC
        story.append(Paragraph('Organic Promotion Content', styles['SH']))
        story.append(hr())
        for post in plat['organic']:
            story.append(KeepTogether([
                Paragraph(post['label'], styles['SubH']),
                Paragraph(f"<b>Target:</b> {post['target']}", styles['B']),
                Paragraph(post['copy'], styles['AdCopy']),
            ]))
            story.append(Spacer(1, 8))

        # ADS
        story.append(Paragraph('Paid Ad Copy (Future Use — Budget Required)', styles['SH']))
        story.append(hr())
        for ad in plat['ads']:
            story.append(KeepTogether([
                Paragraph(ad['variant'], styles['SubH']),
                Paragraph('<b>Ad copy:</b>', styles['B']),
                Paragraph(ad['copy'], styles['AdCopy']),
                Paragraph(f"<b>Targeting:</b> {ad['targeting']}", styles['B']),
                Paragraph(f"<b>Run timing:</b> {ad['timing']}", styles['B']),
                Paragraph(f"<b>Format:</b> {ad['format']}", styles['B']),
                Paragraph(f"<b>Estimated cost:</b> {ad['est_cost']}", styles['B']),
            ]))
            story.append(Spacer(1, 10))

    # AD BUDGET SUMMARY TABLE
    story.append(PageBreak())
    story.append(Paragraph('Paid Ad Budget Summary (When Ready)', styles['SH']))
    story.append(hr())
    story.append(Paragraph(
        'All paid options are for future use when budget is available. '
        'Zero budget required to launch Cohort 1. Organic-only is the primary strategy.',
        styles['B']))
    story.append(Spacer(1, 6))

    ad_rows = [
        ['Platform', 'Ad Variant', 'Segment', 'Min Budget', 'Est. Reach', 'Est. Conversions', 'Timing'],
        ['Meta (IG/FB)', 'Video — Beginners', 'Beginners', '$50–$100', '4,000–8,000', '5–10 DMs', 'Days 17–30'],
        ['Meta (IG/FB)', 'Story — Creators', 'Creators', '$50–$100', '5,000–10,000', '5–10 DMs', 'Days 14–28'],
        ['Meta (IG/FB)', 'Feed — Business', 'Biz Owners', '$100', '2,000–4,000', '2–4 sign-ups', 'Days 20–30'],
        ['X/Twitter', 'Tweet — Beginners', 'Beginners', '$50–$100', '3,300–6,200', '10–20 DMs', 'Days 14–30'],
        ['X/Twitter', 'Tweet — Developers', 'Developers', '$50–$100', '2,000–4,000', '5–10 DMs', 'Days 17–29'],
        ['X/Twitter', 'Tweet — Business', 'Biz Owners', '$50–$100', '2,500–5,000', '5–10 DMs', 'Days 20–30'],
        ['Telegram', 'Channel cross-post', 'All', '$0 (organic)', 'Community size', 'Varies', 'Days 13, 17, 27'],
        ['TOTAL', '—', 'All', '$350–$600', '20,000–37,000', '32–64 contacts', 'Days 14–30'],
    ]
    story.append(ad_table(
        ad_rows[0], ad_rows[1:],
        [W*0.13, W*0.17, W*0.12, W*0.12, W*0.12, W*0.15, W*0.19]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Note: All cost and conversion estimates are benchmarks. Actual performance depends on creative quality, '
        'audience match, and offer resonance. Start with $50 test budgets before scaling.',
        styles['B']))

    story.append(Spacer(1, 20))
    story.append(cover_block('Promo Materials — Phase 8 Complete', 'Built April 3, 2026  ·  @big_quiv'))
    doc.build(story)
    print(f'Promo materials PDF saved: {OUT_PATH}')

if __name__ == '__main__':
    build()
