"""Generate Weekly Series Episodes PDF — 'Things You Didn't Know You Could Do With AI'."""
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
OUT_PATH = os.path.join(OUT_DIR, 'weekly-series-episodes.pdf')

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

S('CT', parent=styles['Title'], fontSize=30, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=10)
S('CS', parent=styles['Normal'], fontSize=12, textColor=MID,
  alignment=TA_CENTER, spaceAfter=5)
S('EpHead', parent=styles['Heading1'], fontSize=18, textColor=WHITE,
  fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=0, alignment=TA_CENTER)
S('EpSub', parent=styles['Normal'], fontSize=10, textColor=MID,
  alignment=TA_CENTER, spaceAfter=0)
S('SH', parent=styles['Heading2'], fontSize=12, textColor=RED,
  fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
S('B', parent=styles['Normal'], fontSize=10, textColor=GRAY, leading=14, spaceAfter=5)
S('BL', parent=styles['Normal'], fontSize=10, textColor=GRAY,
  leading=14, leftIndent=14, spaceAfter=3)
S('Q', parent=styles['Normal'], fontSize=11, textColor=DARK,
  fontName='Helvetica-Bold', leading=16, leftIndent=10, rightIndent=10,
  spaceBefore=6, spaceAfter=6)
S('Hook', parent=styles['Normal'], fontSize=13, textColor=RED,
  fontName='Helvetica-Bold', leading=18, alignment=TA_CENTER,
  spaceBefore=8, spaceAfter=8)
S('Platform', parent=styles['Normal'], fontSize=9, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER)
S('PlatformCell', parent=styles['Normal'], fontSize=9, textColor=GRAY, leading=13)

def hr():
    return HRFlowable(width='100%', thickness=1, color=RED, spaceAfter=6, spaceBefore=2)

W = A4[0] - 3.6*cm

def ep_banner(ep_num, tool, use_case, color=DARK):
    t = Table([
        [Paragraph(f'EPISODE {ep_num}', styles['EpHead'])],
        [Paragraph(f'Tool: {tool}  ·  Use Case: {use_case}', styles['EpSub'])],
        [Paragraph('"Things You Didn\'t Know You Could Do With AI"', styles['EpSub'])],
    ], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
    ]))
    return t

def platform_table(rows):
    headers = ['Platform', 'Format', 'Length', 'Adapted Content']
    data = [[Paragraph(h, styles['Platform']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['PlatformCell']) for c in row])
    t = Table(data, colWidths=[W*0.14, W*0.12, W*0.10, W*0.64])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

EPISODES = [
    {
        'ep': 1,
        'tool': 'Claude',
        'use_case': 'Trading Journal Analysis',
        'publish': 'April 9, 2026 (Day 9 of launch calendar)',
        'segments': ['Beginners', 'Developers', 'Traders', 'All'],
        'hook_x': '"You can ask Claude to scan your last 30 trades and tell you your worst habit. Most traders don\'t know this is possible. Here\'s how."',
        'hook_ig': '"I uploaded my trade journal to Claude. It found a pattern I had been missing for 6 months."',
        'hook_tiktok': '"Watch me upload 30 trades to Claude. What it found changed my trading." — First frame: spreadsheet drop into Claude.',
        'the_use_case': (
            'Most traders keep a trade journal but never actually analyse it. '
            'Claude can read a CSV or pasted table of your trades and identify: '
            'your worst time of day to trade, your most consistent losing setup, '
            'your best R:R ratio pairs, and patterns in your emotional decisions '
            '(e.g., "you revenge-trade after 2 consecutive losses"). '
            'This is behavioural analytics that used to require a trading coach or data analyst.'
        ),
        'step_demo': [
            '1. Export your trades from your broker (CSV or copy-paste into a table).',
            '2. Open Claude. Paste your trades. Prompt: "Analyse these trades. Tell me: (a) my worst trading habit, (b) my best-performing setup, (c) what time of day I perform worst, (d) any emotional patterns you can infer."',
            '3. Claude returns a structured analysis with specific observations and actionable changes.',
            '4. Optional: Ask Claude to write you a set of rules based on what it found.',
        ],
        'lead_in': (
            'In Module 1 of the AI Automation course — Developers Track — '
            'we build this as a full web app: upload your broker CSV, '
            'Claude analyses it automatically, and you get a weekly report in your inbox. '
            'No manual pasting required.'
        ),
        'platforms': [
            ('X/Twitter', 'Thread', '4 tweets', 'Hook tweet → step 1-2 → step 3-4 → lead-in to course. End with: "What does your journal say about your worst habit?"'),
            ('Instagram', 'Reel', '45s', 'Screen recording: paste trades into Claude → read the analysis. Add dramatic pause before the insight reveal. Text overlay: "It found this pattern in 8 seconds."'),
            ('TikTok', 'TikTok', '45s', 'Same screen recording. First frame: spreadsheet. Hook in first 2s. Show the analysis appearing in real time. No need to explain — the output speaks for itself.'),
        ],
        'tools_needed': 'Claude (web or API — free tier sufficient), trade journal CSV or copy-paste table, browser',
    },
    {
        'ep': 2,
        'tool': 'Kling AI',
        'use_case': 'AI Video Creation for Social Media',
        'publish': 'April 19, 2026 (Day 19 of launch calendar)',
        'segments': ['Creators', 'Business Owners', 'All'],
        'hook_x': '"You can generate a cinematic 5-second video from a single text prompt using Kling. No footage. No camera. No editor. Here\'s how."',
        'hook_ig': '"I made this video from a text prompt. It took 4 minutes. No camera. No editor." — First frame: the finished video clip.',
        'hook_tiktok': '"Text prompt → cinematic video → published in 10 minutes. Watch." — First frame: typing the prompt. Last frame: published post.',
        'the_use_case': (
            'Kling AI 3.0 generates videos up to 3 minutes long from a text prompt or image. '
            'It now supports native audio generation — synchronized dialogue, sound effects, '
            'and ambient noise — without any external audio tools. '
            'For content creators, this means: no camera, no filming, no editing software. '
            'Just a prompt, a style reference image, and 4–8 minutes of generation time. '
            'The output is social-media ready at 1080p with professional camera movements.'
        ),
        'step_demo': [
            '1. Go to klingai.com. Create a free account.',
            '2. Click "Text to Video". Write your prompt: describe the scene, the mood, the camera movement.',
            '   Example prompt: "A young man sits in a dark café late at night, neon lights reflecting off rain-slicked windows. Camera slowly zooms in. Cinematic, moody, 4K."',
            '3. Select duration (5s for free tier, up to 3min for paid). Click Generate.',
            '4. Download your clip. Add captions in CapCut. Upload directly to TikTok or Reels.',
            'PRO TIP: Use an image as your starting frame (Image to Video mode) for more consistent character and scene control.',
        ],
        'lead_in': (
            'In Module 3 of the AI Video Creation course — Creators Track — '
            'we go deeper: how to maintain character consistency across multiple clips, '
            'how to chain 6 Kling clips into a complete 60-second video, '
            'and how to add a professional voiceover with MiniMax in under 10 minutes.'
        ),
        'platforms': [
            ('X/Twitter', 'Thread', '4 tweets', 'Hook → what Kling does (one sentence) → 4-step demo → lead-in. End with: "What scene would you generate first?"'),
            ('Instagram', 'Reel', '45s', 'Split screen: text prompt on left, generated video on right. Show the generation timer. End with the final clip playing full screen. Caption: "No camera. No editor. Just a prompt."'),
            ('TikTok', 'TikTok', '45s', 'Same format. First frame: text on black background — "I made this with a text prompt." Second half: the generated video playing. Comment CTA: "Comment KLING and I\'ll show you the full workflow."'),
        ],
        'tools_needed': 'Kling AI account (free tier available), CapCut (free), optional: reference image for character consistency',
    },
    {
        'ep': 3,
        'tool': 'Supabase + Claude',
        'use_case': 'Natural Language Database Queries (No SQL)',
        'publish': 'April 24, 2026 (Day 24 of launch calendar — paired with freebie drop)',
        'segments': ['Developers', 'Business Owners', 'Beginners'],
        'hook_x': '"You can query a database in plain English using Claude + Supabase. No SQL. No developer. Just ask your question and get an answer. Here\'s how."',
        'hook_ig': '"I asked my database: \'who are my best customers this month?\' In plain English. Claude wrote the SQL. Supabase ran it. I got my answer in 8 seconds."',
        'hook_tiktok': '"Non-technical founder asks their own database a question in plain English. This is what happens." — First frame: typing a normal English question.',
        'the_use_case': (
            'Supabase is a free, open-source database platform. '
            'Claude can read your Supabase database schema and translate any plain English question '
            'into the correct SQL query — then run it and return the answer. '
            'For non-technical business owners: this means asking questions like '
            '"Show me all customers who haven\'t ordered in 60 days" or '
            '"What\'s my average order value by product category?" '
            'and getting the answer in seconds without knowing a single line of SQL.'
        ),
        'step_demo': [
            '1. Set up a free Supabase account. Create a simple table with your data (or use their demo dataset).',
            '2. Copy your table schema (column names and types).',
            '3. Open Claude. Paste your schema. Prompt: "I have a Supabase database with this schema: [paste schema]. Write me a SQL query that answers: [your question in plain English]."',
            '4. Claude returns the SQL query.',
            '5. Run the query in Supabase\'s SQL editor. Get your answer.',
            'PRO TIP: Set up Claude as an MCP tool connected directly to Supabase — then you never have to copy-paste schema again. We cover this in the Developers Track.',
        ],
        'lead_in': (
            'In Module 3 of the Coding with AI course — Developers Track — '
            'we connect Claude directly to Supabase via MCP. '
            'You type your business question in English. Claude writes the SQL, runs it, '
            'and returns the result. No copy-pasting. No SQL editor. Just answers.'
        ),
        'platforms': [
            ('X/Twitter', 'Thread', '4 tweets', 'Hook → what this solves (no SQL needed) → 5-step demo → MCP lead-in. Paired with freebie: "Module 1 is free for 24 hours. Link below."'),
            ('Instagram', 'Reel', '45s', 'Screen recording: type English question → Claude generates SQL → Supabase returns answer. Caption: "You don\'t need to know SQL to run your own business database."'),
            ('TikTok', 'TikTok', '45s', 'Same screen recording. First frame: "Non-technical founder. Their own database. No SQL." High contrast, simple setup.'),
        ],
        'tools_needed': 'Supabase account (free tier), Claude (web — free tier sufficient), basic understanding of what a database table is (no coding required)',
    },
    {
        'ep': 4,
        'tool': 'Remotion',
        'use_case': 'Batch Video Generation from a CSV File',
        'publish': 'April 30, 2026 (Day 30 of launch calendar — final day)',
        'segments': ['Developers', 'Creators', 'All'],
        'hook_x': '"You can use Remotion to generate 30 videos from a CSV file. One command. No manual editing. Here\'s the exact script."',
        'hook_ig': '"I generated 30 videos from a spreadsheet. Automatically. No editing. One command." — First frame: the CSV. Last frame: 30 rendered video files in a folder.',
        'hook_tiktok': '"Watch me generate 30 videos in one terminal command." — First frame: terminal. Show the render progress bar. Last frame: folder full of videos.',
        'the_use_case': (
            'Remotion is a React-based video framework that renders videos programmatically. '
            'Combined with a CSV file of topics, titles, and data — and Claude to write the content '
            'for each video — you can generate dozens of unique, branded videos in one automated run. '
            'Use cases: 30 product videos, 30 daily tip videos, 30 testimonial animations, '
            'or 30 platform-adapted versions of the same content. '
            'This is how serious content creators build scale without burning out.'
        ),
        'step_demo': [
            '1. Create a CSV with your video data: columns = title, hook, body_text, cta, bg_color.',
            '2. Build a Remotion composition (or use the template we provide in the course).',
            '3. Claude writes the Remotion component code that maps your CSV columns to video elements.',
            '4. Run: npx remotion render --props=\'{"csv":"your-data.csv"}\' MyComposition out/',
            '5. Remotion generates one MP4 file per row in your CSV. 30 rows = 30 videos.',
            '6. Upload to your platform of choice or pipe them to a scheduling tool automatically.',
        ],
        'lead_in': (
            'In Module 4 of the Coding with AI course — Developers Track — '
            'we build this pipeline from scratch: '
            'CSV → Claude writes scripts → fal.ai generates images → Kling animates → '
            'MiniMax voices → Remotion assembles → 5 complete videos in one command. '
            'This is Week 3 content. By then you\'ll have built everything that leads to it.'
        ),
        'platforms': [
            ('X/Twitter', 'Thread', '4 tweets', 'Hook → what Remotion is (one sentence) → 6-step demo → lead-in to Coding with AI course. Final tweet: "Which of the 4 Series episodes was most useful? A/B/C/D — reply now."'),
            ('Instagram', 'Reel', '45s', 'Terminal timelapse showing render progress. Cut to folder of 30 MP4 files. Caption: "30 videos. One command. This is the system." Full series retrospective in caption.'),
            ('TikTok', 'TikTok', '45s', 'Same terminal timelapse. First frame: "I generated 30 videos in 3 minutes." Last frame: folder of video files. CTA: "The course that teaches this is open now. Link in bio."'),
        ],
        'tools_needed': 'Node.js 18+, Remotion CLI (npm install), Claude API (to write the component code), CSV with video data',
    },
]


def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='Quivira — Weekly Series Episodes', author='@big_quiv'
    )
    story = []

    # COVER
    cover = Table([
        [Paragraph('WEEKLY CONTENT SERIES', styles['CT'])],
        [Paragraph('"Things You Didn\'t Know You Could Do With AI"', styles['CS'])],
        [Paragraph('4 Episodes  ·  April 9 – April 30, 2026  ·  @big_quiv', styles['CS'])],
        [Spacer(1, 4)],
        [Paragraph('Platforms: X/Twitter  ·  Instagram  ·  TikTok', styles['CS'])],
        [Paragraph('Each episode: standalone post + course lead-in', styles['CS'])],
    ], colWidths=[W])
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
    ]))
    story += [cover, Spacer(1, 16)]

    # SERIES OVERVIEW
    story.append(Paragraph('Series Overview', styles['SH']))
    story.append(hr())
    story.append(Paragraph(
        'One episode per week for 4 weeks. Each episode covers one specific, surprising, or underrated '
        'use case from the ContentBrain tool stack. Format is identical across all episodes — '
        'allowing the audience to build a habit of expecting the series. '
        'Each episode works as a standalone post on X, Instagram, and TikTok. '
        'Each episode contains a natural lead-in to the relevant course module.',
        styles['B']))

    ov_data = [
        [Paragraph(h, styles['Platform']) for h in ['Ep', 'Publish Date', 'Tool', 'Use Case', 'Primary Segment', 'Course Lead-in']],
    ]
    for ep in EPISODES:
        ov_data.append([
            Paragraph(f'EP{ep["ep"]}', styles['PlatformCell']),
            Paragraph(ep['publish'].split(' (')[0], styles['PlatformCell']),
            Paragraph(ep['tool'], styles['PlatformCell']),
            Paragraph(ep['use_case'], styles['PlatformCell']),
            Paragraph(', '.join(ep['segments'][:2]), styles['PlatformCell']),
            Paragraph(ep['lead_in'][:80]+'...', styles['PlatformCell']),
        ])
    ov_t = Table(ov_data, colWidths=[W*0.06, W*0.13, W*0.15, W*0.22, W*0.14, W*0.30])
    ov_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
    ]))
    story += [ov_t, Spacer(1, 8)]

    # EPISODES
    for ep in EPISODES:
        story.append(PageBreak())
        story.append(ep_banner(ep['ep'], ep['tool'], ep['use_case']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Publish: {ep['publish']}", styles['B']))
        story.append(Paragraph(f"Primary audience: {', '.join(ep['segments'])}", styles['B']))
        story.append(Spacer(1, 6))

        # HOOKS
        story.append(Paragraph('Hooks (by Platform)', styles['SH']))
        for label, hook in [('X/Twitter:', ep['hook_x']),
                            ('Instagram:', ep['hook_ig']),
                            ('TikTok:', ep['hook_tiktok'])]:
            story.append(Paragraph(f'<b>{label}</b>', styles['B']))
            story.append(Paragraph(f'"{hook}"', styles['Q']))

        # USE CASE
        story.append(Paragraph('The Use Case — Explained Simply', styles['SH']))
        story.append(Paragraph(ep['the_use_case'], styles['B']))

        # STEP DEMO
        story.append(Paragraph('Step-by-Step Demo (Try This Now)', styles['SH']))
        for step in ep['step_demo']:
            story.append(Paragraph(step, styles['BL']))

        story.append(Paragraph(f"<b>Tools you need:</b> {ep['tools_needed']}", styles['B']))

        # LEAD-IN
        story.append(Paragraph('Course Lead-In', styles['SH']))
        story.append(Paragraph(ep['lead_in'], styles['B']))

        # PLATFORM TABLE
        story.append(Paragraph('Platform-Adapted Content', styles['SH']))
        story.append(platform_table(ep['platforms']))
        story.append(Spacer(1, 10))

    # FOOTER
    story.append(PageBreak())
    footer = Table([
        [Paragraph('Weekly Series — All 4 Episodes — Phase 7 Complete', styles['CT'])],
        [Paragraph('Built April 3, 2026  ·  @big_quiv / ContentBrain', styles['CS'])],
    ], colWidths=[W])
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
