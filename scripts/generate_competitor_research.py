"""Generate Competitor Research PDF for AI Course Launch using reportlab."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', '06-Drafts')
OUT_PATH = os.path.join(OUT_DIR, 'competitor-research.pdf')

# Brand Colors
DARK = HexColor('#1a1a2e')
RED = HexColor('#e94560')
GRAY = HexColor('#444444')
LIGHT = HexColor('#f5f5f5')
WHITE = HexColor('#ffffff')
MID = HexColor('#cccccc')

styles = getSampleStyleSheet()

def add_style(name, **kwargs):
    styles.add(ParagraphStyle(name, **kwargs))

add_style('CoverTitle', parent=styles['Title'], fontSize=32, textColor=WHITE,
          fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=12)
add_style('CoverSub', parent=styles['Normal'], fontSize=13, textColor=MID,
          alignment=TA_CENTER, spaceAfter=6)
add_style('SectionHead', parent=styles['Heading1'], fontSize=17, textColor=DARK,
          fontName='Helvetica-Bold', spaceBefore=18, spaceAfter=8)
add_style('SubHead', parent=styles['Heading2'], fontSize=13, textColor=RED,
          fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
add_style('Body', parent=styles['Normal'], fontSize=10, textColor=GRAY,
          leading=15, spaceAfter=6)
add_style('BulletItem', parent=styles['Normal'], fontSize=10, textColor=GRAY,
          leading=14, leftIndent=14, bulletIndent=0, spaceAfter=3)
add_style('TableHead', parent=styles['Normal'], fontSize=9, textColor=WHITE,
          fontName='Helvetica-Bold', alignment=TA_CENTER)
add_style('TableCell', parent=styles['Normal'], fontSize=9, textColor=GRAY,
          leading=12)
add_style('Tag', parent=styles['Normal'], fontSize=9, textColor=RED,
          fontName='Helvetica-Bold', spaceAfter=4)
add_style('Quote', parent=styles['Normal'], fontSize=10, textColor=DARK,
          fontName='Helvetica-Oblique', leftIndent=20, rightIndent=20,
          leading=15, spaceAfter=8)

def make_table(headers, rows, col_widths):
    data = [[Paragraph(h, styles['TableHead']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['TableCell']) for c in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.4, MID),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t

def hr():
    return HRFlowable(width='100%', thickness=1, color=RED, spaceAfter=8, spaceBefore=4)

def build():
    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='AI Course Competitor Research — Quivira',
        author='@big_quiv'
    )
    story = []
    W = A4[0] - 3.6*cm  # usable width

    # ── COVER ────────────────────────────────────────────────────────────────
    cover_bg = Table(
        [[Paragraph('AI COURSE LAUNCH', styles['CoverTitle']),],
         [Paragraph('Competitor Research & Market Intelligence', styles['CoverSub'])],
         [Paragraph('Phase 1 — Quivira Course Launch 2026', styles['CoverSub'])],
         [Spacer(1, 10)],
         [Paragraph('Compiled: April 3, 2026  ·  Launch Window: 30 days  ·  @big_quiv', styles['CoverSub'])]],
        colWidths=[W]
    )
    cover_bg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 24),
        ('RIGHTPADDING', (0, 0), (-1, -1), 24),
    ]))
    story.append(cover_bg)
    story.append(Spacer(1, 24))

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────────────────
    story.append(Paragraph('Executive Summary', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'AI course consumption on Udemy alone grew 291% year-over-year in 2025–2026. '
        'The market is not saturated — it is bifurcating. Generic "intro to AI" courses '
        'are commoditised. Practical, niche-specific, workflow-driven AI education is in '
        'peak demand with almost no dominant player in the Web3/crypto/creator intersection. '
        'This report maps the competitive landscape across Udemy, Skool, Gumroad, X/Twitter, '
        'YouTube, and Telegram, then identifies the white-space opportunities Quivira can own.',
        styles['Body']))
    story.append(Spacer(1, 8))

    # ── SECTION 1: MARKET DEMAND SIGNALS ────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('1. Market Demand Signals', styles['SectionHead']))
    story.append(hr())

    demand_rows = [
        ['Metric', 'Data Point', 'Source'],
        ['AI course YoY growth (Udemy)', '+291%', 'Udemy Marketplace Report 2026'],
        ['AI Engineer Course (Ed Donner)', '110,000+ students, 4.6★', 'Udemy / travis.media'],
        ['LLM Engineering course', '204,000+ students, 4.7★', 'Udemy / travis.media'],
        ['Complete Generative AI (non-tech)', '333,000+ students', 'Udemy'],
        ['AI Automation with n8n', '55,000+ students — Bestseller', 'Udemy'],
        ['AI Video Bootcamp (Skool)', '14,000+ creators enrolled', 'aivideobootcamp.com'],
        ['Kling AI ARR (Dec 2025)', '$240M — video tool demand proxy', 'cybernews.com/kling-ai-review'],
        ['AI Agents topic (Udemy)', 'Bestseller badge, 4.7★', 'Udemy topic page'],
        ['Vibe coding courses (Udemy)', '20+ courses reviewed, trending March 2026', 'Medium/Javarevisited'],
        ['Claude Code courses (Udemy)', '20+ courses reviewed, trending 2026', 'dev.to/scrimba'],
    ]
    story.append(make_table(
        demand_rows[0], demand_rows[1:],
        [W*0.35, W*0.38, W*0.27]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph('Key Demand Insight', styles['SubHead']))
    story.append(Paragraph(
        'The top-performing courses are NOT the most comprehensive — they are the most '
        'practical. "Hands-on projects," "production-ready," and "no prior experience needed" '
        'are the phrases that drive enrollment. Courses with 50+ hours of content and '
        '10+ real projects consistently outperform shorter theory-only content.',
        styles['Body']))

    # ── SECTION 2: PLATFORM BREAKDOWN ────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('2. Platform-by-Platform Breakdown', styles['SectionHead']))
    story.append(hr())

    platforms = [
        {
            'name': 'Udemy',
            'model': 'One-time purchase, $10–$200 list price (frequent 80–90% sales → effective ~$10–$15). Personal Plan: $30/mo for 10,000+ courses.',
            'top': [
                'The AI Engineer Course 2026 — 110K students, 4.6★ (production LLM pipeline)',
                'LLM Engineering: Master AI, LLMs & Agents — 204K students, 4.7★',
                'Complete Generative AI Course — 333K students (non-technical entry point)',
                'Complete AI Automation with n8n — 55K students (no-code automation, Bestseller)',
                'AI Agents & Agentic AI — 4.7★, rapidly growing',
                'Vibe Coding courses — 20+ reviewed, trending March 2026',
                'Claude Code courses — 20+ reviewed, emerging category',
            ],
            'gap': 'Zero courses at the AI × Web3/crypto intersection. Zero courses on AI video workflows for social creators. No course teaches AI-powered personal brand building or content systems.',
            'hooks': '"Production-ready" · "No prior experience" · "14 hands-on projects" · "Watch me build X from scratch" · "Save $X/month on API costs"',
        },
        {
            'name': 'Skool',
            'model': 'Subscription community model. $5–$9/mo for members. $99/mo platform cost for creators (new $9/mo hobby plan available). Community + live Q&A hybrid.',
            'top': [
                'AI Video Bootcamp — $9/mo or $55/year, 14,000+ creators (largest AI video community on Skool)',
                'AI Filmmaking — $5/mo (entry-level, smaller community)',
                'Growing trend: Skool communities replacing standalone courses — community = retention moat',
            ],
            'gap': 'No Skool community combining AI tools + crypto/trading + content creation. The AI × Web3 niche is completely open on this platform.',
            'hooks': '"Learn with a community" · "Live sessions every week" · "Access to creators like you"',
        },
        {
            'name': 'Gumroad',
            'model': 'One-time purchase digital products. Gumroad takes 10% per transaction. No recurring revenue on base plan. Best for standalone PDFs, mini-courses, templates.',
            'top': [
                'AI Video Creation guides — individual creators selling workflow PDFs',
                'AI Cinematic Course (aivideoacademy) — targeted at cinematic content creators',
                'Video Production & Editing category actively trending',
            ],
            'gap': 'Almost no AI automation templates or prompt packs for Web3/crypto contexts. Massive gap for "AI trading workflow" templates and "content system" guides.',
            'hooks': '"Instant download" · "Pay once, use forever" · "Template included"',
        },
        {
            'name': 'X / Twitter',
            'model': 'Free content → paid DM funnels. Course drops announced via threads. Price range not standardised — varies from $15 info products to $500 cohorts.',
            'top': [
                'Claude Code build threads going viral (March 2026)',
                '"I built X with AI in Y minutes" format dominating impressions',
                'Vibe coding demos — screen recordings of AI-assisted development',
                'AI income breakdown threads performing strongly',
            ],
            'gap': 'No consistent voice connecting AI tools to crypto income in a practical, non-hype way. The "AI × trading signals" angle is completely unclaimed.',
            'hooks': '"I built this in 10 minutes with Claude" · "I replaced my [workflow] with AI" · "The AI tool nobody is talking about"',
        },
        {
            'name': 'YouTube',
            'model': 'Free content → course upsells. Typically 15–30% course conversion from loyal subscribers. Long-form tutorials (20–45 min) drive highest conversions.',
            'top': [
                'n8n automation walkthroughs — high demand, growing search volume',
                'Claude Code terminal demos — "watch me build X" format',
                'AI video generation comparisons (Kling vs Sora vs Runway)',
                'Workflow teardowns: "My full AI content system"',
            ],
            'gap': '"AI signals pipeline" — zero YouTube creators showing how to build AI-powered crypto signal systems. "AI content OS" — no one teaching the ContentBrain-style full system.',
            'hooks': '"Watch me build this in real time" · "The workflow I use every day" · "I automated my [pain point]"',
        },
        {
            'name': 'Telegram',
            'model': 'Paid channel access ($5–$50/mo range) or community bundles. Live class delivery via Telegram group + Google Meet links. Growing model for emerging market educators.',
            'top': [
                'DeepLearning AI Telegram channel: 53,035 subscribers (free)',
                'KDnuggets channel: 23,190 members (free)',
                'No dominant PAID AI course community identified on Telegram in the $15–$50 range',
                'Graphy platform: 200K+ creators using it to sell Telegram-based courses',
            ],
            'gap': 'The $15–$50 live AI course on Telegram is an almost entirely open market. Most Telegram AI education is free. Paid live classes are extremely rare in this price bracket.',
            'hooks': '"Live class every week" · "Ask me anything in real time" · "Join X other builders"',
        },
    ]

    for p in platforms:
        story.append(KeepTogether([
            Paragraph(p['name'], styles['SubHead']),
            Paragraph(f"<b>Pricing model:</b> {p['model']}", styles['Body']),
            Paragraph('<b>Top course titles / demand signals:</b>', styles['Body']),
        ]))
        for item in p['top']:
            story.append(Paragraph(f'• {item}', styles['BulletItem']))
        story.append(Paragraph(f"<b>Gap / opportunity:</b> {p['gap']}", styles['Body']))
        story.append(Paragraph(f"<b>Traffic hooks that work:</b> {p['hooks']}", styles['Body']))
        story.append(Spacer(1, 10))

    # ── SECTION 3: PAIN POINTS BY AUDIENCE SEGMENT ───────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('3. Pain Points by Audience Segment', styles['SectionHead']))
    story.append(hr())

    segments = [
        {
            'segment': 'Beginners (No Prior AI or Tech Experience)',
            'pains': [
                '"100 AI tools launched today — I don\'t know which one to start with."',
                '"I tried ChatGPT, got bad results, gave up. Now I feel behind."',
                '"Every tutorial assumes I already know something. Nothing is actually for zero."',
                '"I see people making money with AI but I don\'t know where they even started."',
                '"I\'m scared I\'ll pay for a course and still not be able to DO anything."',
            ],
            'desires': 'First win within 30 minutes. Clear tool selection. Hand-holding without condescension. Proof it works for people like them.',
            'hooks': '"You don\'t need to know how to code." · "Your first AI win in under an hour." · "Watch a total beginner build this."',
            'demand': 'Complete Generative AI Course: 333,000+ students. Massive validation — non-technical entry point is the largest audience segment on Udemy.',
        },
        {
            'segment': 'Developers (Technical — Wants to Build and Automate)',
            'pains': [
                '"I know Python/JS but I don\'t know how to wire AI APIs into real production systems."',
                '"My company is asking me to add AI to everything. I\'m guessing, not knowing."',
                '"I\'m spending $400/month on API costs. I know there\'s a smarter way."',
                '"I can build things but I don\'t know which architecture to choose for agents."',
                '"Vibe coding is everywhere. Am I using Claude Code wrong or just differently?"',
            ],
            'desires': 'Build real projects. Multi-agent systems. Cost-efficient architectures. Production-ready patterns. Competitive edge vs peers.',
            'hooks': '"Replace 50% of your manual workflow with one agent." · "The API architecture pattern that costs $0.02 per run." · "Claude Code: what the tutorials get wrong."',
            'demand': 'LLM Engineering course: 204K+ students, 4.7★. Claude Code courses: 20+ options emerging March 2026.',
        },
        {
            'segment': 'Creators (Content-Focused — Wants AI Video, Writing, Distribution)',
            'pains': [
                '"My AI videos look AI. The character looks different in every clip."',
                '"I spent 6 hours editing a 60-second video. There has to be a better way."',
                '"I know tools exist but I don\'t know how to chain them together into a workflow."',
                '"I tried Kling/Sora/Runway. They all do different things. I don\'t know which to use when."',
                '"My content system is broken. I batch, I miss days, I restart. The cycle never ends."',
            ],
            'desires': 'Consistent character rendering. Full video in under 2 hours. A repeatable system they can run alone. Native audio sync. Platform-specific adaptation.',
            'hooks': '"Never film yourself again." · "My full AI video workflow in 10 minutes." · "How I make 30 videos a month working 4 hours."',
            'demand': 'AI Video Bootcamp (Skool): 14,000+ creators. Kling AI: $240M ARR in Dec 2025. Kling 3.0 supports 3-minute videos with native audio — biggest pain point now solved.',
        },
        {
            'segment': 'Business Owners (Outcome-Focused — Wants Automation, Lead Gen, Time Savings)',
            'pains': [
                '"95% of AI pilots fail to produce measurable business impact." (McKinsey stat)',
                '"I don\'t know which task to automate first. I automate the wrong thing and waste $3K."',
                '"I tried Zapier/Make but it broke on week 2 and I don\'t know why."',
                '"I hired someone to set up AI workflows. They left. Now nothing works."',
                '"I want to save 10 hours a week but every tool requires 10 hours to learn."',
            ],
            'desires': 'Clear ROI. Save hours per week. Lead gen automation. Reports that update themselves. Not having to learn to code.',
            'hooks': '"I saved 12 hours/week with this one automation." · "No code. No complexity. Just results." · "The 3 automations every business should run first."',
            'demand': 'SCORE Academy, Vertical Institute, Google all targeting this segment — high commercial intent. Business automation is the highest-ticket segment.',
        },
    ]

    for s in segments:
        story.append(Paragraph(s['segment'], styles['SubHead']))
        story.append(Paragraph('<b>Top pain points:</b>', styles['Body']))
        for pain in s['pains']:
            story.append(Paragraph(f'• {pain}', styles['BulletItem']))
        story.append(Paragraph(f"<b>What they desire:</b> {s['desires']}", styles['Body']))
        story.append(Paragraph(f"<b>Content hooks that convert:</b> {s['hooks']}", styles['Body']))
        story.append(Paragraph(f"<b>Demand signal:</b> {s['demand']}", styles['Body']))
        story.append(Spacer(1, 10))

    # ── SECTION 4: PRICING BENCHMARKS ────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('4. Pricing Benchmarks', styles['SectionHead']))
    story.append(hr())

    pricing_rows = [
        ['Platform / Model', 'Low End', 'Mid Range', 'High End', 'Notes'],
        ['Udemy (sale price)', '$10', '$15–$20', '$30', 'List price $100–$200 but 90% off sales are constant'],
        ['Udemy (Personal Plan)', '$30/mo', '—', '—', 'Access to 10,000+ courses — competes with all platforms'],
        ['Skool (member)', '$5/mo', '$9/mo', '$55/year', 'AI Video Bootcamp: $9/mo — benchmark for live community model'],
        ['Gumroad (one-time)', '$15', '$30–$49', '$99', '10% fee on all transactions'],
        ['Telegram (paid channel)', '$10/mo', '$25/mo', '$50/mo', 'Emerging model — almost no competition in AI education space'],
        ['Live cohort (Google Meet)', '$50', '$97–$197', '$500+', 'Your range ($15–$50) is entry-level — underpriced vs. market'],
        ['Coursera / Wharton AI', '$49/mo', '$199–$399 cert', '—', 'Too formal/structured for Quivira audience'],
    ]
    story.append(make_table(
        pricing_rows[0], pricing_rows[1:],
        [W*0.25, W*0.11, W*0.13, W*0.11, W*0.40]
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '<b>Pricing conclusion:</b> Your $15–$50 range is correctly positioned for first-time buyers '
        'in emerging markets and younger audiences. It is significantly below market rate for live '
        'cohort delivery (typically $97–$500), giving you a "no-brainer" entry offer. Recommend '
        'anchoring $50 as the "full access" tier — everything else looks like a discount against it.',
        styles['Body']))

    # ── SECTION 5: HIGH-DEMAND UNSATURATED USE CASES ─────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('5. High-Demand, Unsaturated AI Use Cases', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'These are AI use cases with demonstrated demand signals but limited or zero dominant '
        'course competitors — the white-space Quivira can own in 30 days.',
        styles['Body']))
    story.append(Spacer(1, 8))

    gaps = [
        {
            'title': '1. AI × Crypto/Web3 Trading Automation',
            'demand': 'VERY HIGH. Crypto audience actively seeks automation. Signal bots, portfolio scanners, on-chain analysis agents are all in demand. Zero course competitors teaching this workflow.',
            'angle': 'Quivira already runs this system (Trigon Labs). This is build-in-public teaching — the most credible angle possible.',
            'saturation': 'ZERO dominant competitor on Udemy, Skool, Gumroad, or Telegram.',
            'topic_fit': 'AI Automation + Coding with AI',
        },
        {
            'title': '2. AI Video for Social Media Content Workflows (Platform-Specific)',
            'demand': 'HIGH. Kling hit $240M ARR. 14K creators on AI Video Bootcamp. But most courses teach the tool, not the workflow.',
            'angle': 'Nobody teaches the full pipeline: concept → Nano Banana → Kling → voiceover → Remotion assembly → posting. The ContentBrain stack IS the differentiation.',
            'saturation': 'Moderate on tools — but ZERO on end-to-end social workflow.',
            'topic_fit': 'AI Video Creation',
        },
        {
            'title': '3. Non-Technical AI Automation for Solopreneurs',
            'demand': 'HIGH. Most automation courses (n8n, Make, Zapier) require technical setup. The non-coder who just wants to save 10 hours/week is underserved.',
            'angle': '"No-code AI systems that actually work" — not another n8n tutorial but practical outcomes: email sorting, DM replies, report generation, lead capture.',
            'saturation': 'Low at the solopreneur + outcome level. Most courses target developers.',
            'topic_fit': 'AI Automation',
        },
        {
            'title': '4. AI-Powered Personal Brand Content System',
            'demand': 'EMERGING. Creators are asking "how do I use AI to post consistently without burning out?" But no course teaches a full content OS.',
            'angle': 'Teach the ContentBrain system as a product. Hooks → concepts → scripts → production → publishing → analytics — AI-assisted at every step.',
            'saturation': 'ZERO competitors teaching a full AI content OS for creators.',
            'topic_fit': 'AI Automation + AI Video Creation',
        },
        {
            'title': '5. Coding with AI for Complete Beginners (Vibe Coding)',
            'demand': 'EXPLODING. "Vibe coding" courses are the #1 emerging category on Udemy as of March 2026. 20+ courses reviewed, still no definitive beginner resource.',
            'angle': 'Teach beginners to build real things with Claude Code — no coding background required. First project: build your own trading dashboard or content scheduler.',
            'saturation': 'Low — 20+ courses exist but no dominant resource specifically for total beginners.',
            'topic_fit': 'Coding with AI',
        },
        {
            'title': '6. AI for Lead Generation and Client Acquisition',
            'demand': 'HIGH COMMERCIAL INTENT. Business owners will pay the most. Lead gen automation (outreach, DMs, email sequences) is the #1 outcome business owners want.',
            'angle': 'Show the exact system: AI writes the outreach → AI qualifies replies → AI books calls. Tie to real results from Quivira\'s own client work.',
            'saturation': 'Low at the "done with you" level. High as a topic in general marketing circles.',
            'topic_fit': 'AI Automation',
        },
    ]

    for g in gaps:
        story.append(KeepTogether([
            Paragraph(g['title'], styles['SubHead']),
            Paragraph(f"<b>Demand:</b> {g['demand']}", styles['Body']),
            Paragraph(f"<b>Quivira angle:</b> {g['angle']}", styles['Body']),
            Paragraph(f"<b>Saturation level:</b> {g['saturation']}", styles['Body']),
            Paragraph(f"<b>Maps to course topic:</b> {g['topic_fit']}", styles['Body']),
            Spacer(1, 8),
        ]))

    # ── SECTION 6: INCOME PROOF DATA (Phase 7b Seed) ─────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('6. Income Proof Data — Phase 7b Seed', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        '<b>Verification note:</b> Most "real example" articles in this space publish income ranges '
        'without named, verifiable case studies. The data below is sourced from industry reports, '
        'platform benchmarks, and credible publications. All figures are clearly labeled as '
        'industry ranges vs. verified individual examples. No invented numbers are included.',
        styles['Body']))
    story.append(Spacer(1, 8))

    income_rows = [
        ['Use Case / Method', 'Income Range', 'Tool(s)', 'Verification Level', 'Source'],
        ['AI-assisted freelancing (content, copy, research)', '$2,000–$8,000/mo', 'Claude, ChatGPT', 'Industry range', 'KDnuggets, Motley Fool 2026'],
        ['Claude Code client projects (dev)', '$500–$10,000/mo', 'Claude Code', 'Industry range', 'marksinsights.com, amazon.com listing'],
        ['Workflow automation services', '$800 setup + $200/mo retainer', 'n8n, Make, Claude', 'Semi-verified (unnamed consultant example)', 'humai.blog'],
        ['Prompt engineering (salaried)', '$98K–$162K/year', 'Various LLMs', 'Salary range (Glassdoor cited)', 'jobbers.io 2026'],
        ['AI digital products (entry)', '$100–$500/mo', 'Claude, Midjourney', 'Industry estimate', 'labla.org 2026'],
        ['AI consulting retainer (senior)', '$5,000–$50,000/mo', 'Various', 'Industry range', 'humai.blog 2026'],
        ['AI video production (per project)', '$200–$5,000/deal', 'Kling, fal.ai, ElevenLabs', 'Industry estimate', 'labla.org 2026'],
        ['ChatGPT automation services (beginner)', '$500/mo within 90 days', 'ChatGPT + automation tools', 'Industry estimate', 'easyguideshub.com 2026'],
    ]
    story.append(make_table(
        income_rows[0], income_rows[1:],
        [W*0.26, W*0.16, W*0.15, W*0.17, W*0.26]
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '<b>Phase 7b action item:</b> The strongest verified proof will come from Quivira\'s own '
        'results — the trading signal system, ContentBrain outputs, and any client wins. '
        'Supplement with above industry benchmarks clearly labeled as ranges, not guarantees.',
        styles['Body']))

    # ── SECTION 7: STRATEGIC RECOMMENDATIONS ────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('7. Strategic Recommendations for Quivira Course Launch', styles['SectionHead']))
    story.append(hr())

    recs = [
        ('Own the AI × Web3 intersection immediately.',
         'Zero competitors exist at this crossroads. Every competitor teaching AI automation is targeting generic business owners or developers. Quivira is the only person with live proof — a running crypto signal system, a content OS, real trading experience. This is the moat. Lead every course with this angle.'),
        ('Price is not the risk. Proof is.',
         '$15–$50 is below market rate for live cohort delivery. The barrier is not price — it is credibility. Lead with Quivira\'s own verified results (ContentBrain, Trigon Labs signals) before asking for payment.'),
        ('The content stack IS the curriculum.',
         'Claude, Claude Code, fal.ai, Kling, MiniMax, Remotion, Supabase — students can\'t get this stack anywhere else taught as an integrated system. This is not a "tools overview" course. It\'s a workflow system. Position it that way.'),
        ('Telegram is open terrain.',
         'The paid AI course on Telegram in the $15–$50 bracket is effectively unclaimed. This is Quivira\'s native platform. Use it as both the delivery mechanism AND the proof-of-community for future marketing.'),
        ('Start with one audience, add others.',
         'Beginners and Creators are the highest-volume segments. Developers and Business Owners convert at higher prices. Launch with Beginners + Creators to build social proof fast, then use testimonials to close Developers and Business Owners at higher tiers.'),
    ]

    for i, (title, body) in enumerate(recs, 1):
        story.append(Paragraph(f'{i}. {title}', styles['SubHead']))
        story.append(Paragraph(body, styles['Body']))
        story.append(Spacer(1, 6))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 40))
    story.append(Paragraph('Quivira Course Launch — Phase 1 Complete', styles['CoverTitle']))
    story.append(Spacer(1, 8))
    story.append(Paragraph('Compiled April 3, 2026  ·  @big_quiv / ContentBrain Vault', styles['CoverSub']))
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        'Sources: Udemy Marketplace, travis.media, aivideobootcamp.com, cybernews.com, '
        'medium.com/javarevisited, KDnuggets, marksinsights.com, humai.blog, labla.org, '
        'easyguideshub.com, jobbers.io, fal.ai, dev.to, graphy.com',
        styles['Body']))

    doc.build(story)
    print(f'PDF saved: {OUT_PATH}')

if __name__ == '__main__':
    build()
