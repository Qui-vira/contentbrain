"""Generate Course Outline PDF for Quivira AI Course Launch."""
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
OUT_PATH = os.path.join(OUT_DIR, 'course-outline.pdf')

DARK = HexColor('#1a1a2e')
RED = HexColor('#e94560')
GRAY = HexColor('#444444')
LIGHT = HexColor('#f5f5f5')
WHITE = HexColor('#ffffff')
MID = HexColor('#cccccc')
ACCENT = HexColor('#2d6a4f')  # green for "live"
BLUE = HexColor('#1d4e89')    # blue for "pre-recorded"

styles = getSampleStyleSheet()

def S(name, **kw):
    styles.add(ParagraphStyle(name, **kw))

S('CoverTitle', parent=styles['Title'], fontSize=30, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=10)
S('CoverSub', parent=styles['Normal'], fontSize=12, textColor=MID,
  alignment=TA_CENTER, spaceAfter=5)
S('SectionHead', parent=styles['Heading1'], fontSize=16, textColor=DARK,
  fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=6)
S('TopicHead', parent=styles['Heading1'], fontSize=14, textColor=WHITE,
  fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=0, alignment=TA_CENTER)
S('TrackHead', parent=styles['Heading2'], fontSize=12, textColor=RED,
  fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
S('ModuleHead', parent=styles['Normal'], fontSize=10, textColor=DARK,
  fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=2)
S('Body', parent=styles['Normal'], fontSize=9, textColor=GRAY, leading=13, spaceAfter=4)
S('BulletCO', parent=styles['Normal'], fontSize=9, textColor=GRAY,
  leading=13, leftIndent=12, spaceAfter=2)
S('Tag', parent=styles['Normal'], fontSize=8, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER)
S('TableHead2', parent=styles['Normal'], fontSize=8, textColor=WHITE,
  fontName='Helvetica-Bold', alignment=TA_CENTER)
S('TableCell2', parent=styles['Normal'], fontSize=8, textColor=GRAY, leading=11)
S('Note', parent=styles['Normal'], fontSize=8, textColor=GRAY,
  fontName='Helvetica-Oblique', leftIndent=10, spaceAfter=4)

def hr():
    return HRFlowable(width='100%', thickness=1, color=RED, spaceAfter=6, spaceBefore=2)

W = A4[0] - 3.6*cm

def tag(text, color):
    t = Table([[Paragraph(text, styles['Tag'])]], colWidths=[2.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    return t

def topic_banner(title, color=DARK):
    t = Table([[Paragraph(title, styles['TopicHead'])]], colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
    ]))
    return t

def module_table(modules):
    """modules: list of (module_name, objective, format, duration, materials, platform)"""
    headers = ['Module', 'Learning Objective', 'Format', 'Duration', 'Materials Needed', 'Platform']
    data = [[Paragraph(h, styles['TableHead2']) for h in headers]]
    for m in modules:
        data.append([Paragraph(str(c), styles['TableCell2']) for c in m])
    t = Table(data, colWidths=[W*0.14, W*0.28, W*0.10, W*0.08, W*0.22, W*0.18])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

# ── COURSE DATA ──────────────────────────────────────────────────────────────

COURSES = [
    {
        'topic': 'TOPIC 1: AI Automation',
        'description': (
            'Students learn to identify automatable tasks, select the right tools, '
            'build real working automations, and connect AI agents to their existing workflows. '
            'No hype — only systems that save measurable hours per week.'
        ),
        'tracks': [
            {
                'name': 'Track A — Beginners (Zero Experience)',
                'goal': 'Build and run their first AI automation without writing a single line of code. '
                        'Walk away with one live automation saving them 2+ hours/week.',
                'modules': [
                    ('M1: What AI Automation Actually Is',
                     'Define automation, debunk AI myths, identify 5 tasks in your life you can automate today',
                     'Live', '45 min',
                     'Laptop, browser, free Make.com account',
                     'Telegram (screen share)'),
                    ('M2: Tool Selection — The Only 3 You Need',
                     'Understand when to use Claude vs. Make vs. Zapier. Never get confused by tool overload again.',
                     'Pre-recorded', '30 min',
                     'Reference PDF (provided)',
                     'Gumroad / hosted link'),
                    ('M3: Build Your First Automation',
                     'Build a real automation live: auto-sort your emails by category using Claude + Make',
                     'Live', '60 min',
                     'Gmail account, Make.com free tier, Claude API key (free tier OK)',
                     'Google Meet'),
                    ('M4: Your First Win — Social Post Scheduler',
                     'Build a system that drafts and schedules 5 social posts from a single voice note',
                     'Live', '60 min',
                     'Make.com, Claude API, Typefully or Buffer free tier',
                     'Google Meet'),
                    ('M5: Review + Next Steps',
                     'Demo your running automation. Get feedback. Map your next 3 automations.',
                     'Live', '45 min',
                     'Working automation from M3 or M4',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track B — Developers (Technical Builders)',
                'goal': 'Build multi-step AI agents using Claude API, n8n, and production deployment patterns. '
                        'Walk away with a deployable automation pipeline.',
                'modules': [
                    ('M1: Agent Architecture 101',
                     'Understand the anatomy of an AI agent: tools, memory, reasoning loop. When to use agents vs. simple automation.',
                     'Live', '60 min',
                     'Claude API key, Python 3.10+, VS Code',
                     'Google Meet'),
                    ('M2: n8n + Claude Integration',
                     'Wire Claude into n8n as a reasoning node. Build a multi-step research + summarise + email agent.',
                     'Live', '75 min',
                     'n8n (self-hosted or cloud), Claude API',
                     'Google Meet'),
                    ('M3: Memory and Context in Agents',
                     'Implement short-term (conversation) and long-term (Supabase) memory for Claude agents.',
                     'Live', '60 min',
                     'Supabase free tier, Claude API, Python',
                     'Google Meet'),
                    ('M4: Building a Crypto Signal Scanner',
                     'Build a live AI agent that scans Binance pairs, runs TA logic via Claude, and sends alerts to Telegram.',
                     'Live', '90 min',
                     'Binance API (read-only), Claude API, Python, Telegram Bot token',
                     'Google Meet'),
                    ('M5: Production Deployment',
                     'Deploy your agent to Railway or Render. Set up cron jobs, error handling, and uptime monitoring.',
                     'Pre-recorded', '45 min',
                     'Railway or Render account (free tier)',
                     'Gumroad / hosted link'),
                    ('M6: Agent Review + Portfolio Demo',
                     'Present your agent live. Get architecture feedback. Package it as a portfolio piece.',
                     'Live', '60 min',
                     'Running deployed agent',
                     'Google Meet'),
                ],
            },
            {
                'name': 'Track C — Creators (Content-Focused)',
                'goal': 'Build an AI-powered content automation system that drafts, schedules, and repurposes '
                        'content across platforms — running in the background without daily manual input.',
                'modules': [
                    ('M1: Map Your Content System',
                     'Audit your current workflow. Identify the 3 highest-friction points. Map an AI solution for each.',
                     'Live', '45 min',
                     'Current content calendar or workflow doc',
                     'Telegram (screen share)'),
                    ('M2: Auto-Draft System with Claude',
                     'Build a system: voice note → Claude transcript → platform-adapted draft → Typefully queue',
                     'Live', '60 min',
                     'Claude API, Make.com or Zapier, Typefully',
                     'Google Meet'),
                    ('M3: Repurposing Pipeline',
                     'Build a pipeline that takes one piece of content (a tweet thread) and repurposes it for LinkedIn, TikTok script, and Instagram carousel automatically.',
                     'Pre-recorded', '45 min',
                     'Claude API, Make.com',
                     'Gumroad / hosted link'),
                    ('M4: Analytics + Content Scoring',
                     'Build an automation that pulls your post performance weekly and identifies your top hooks using Claude.',
                     'Live', '60 min',
                     'Typefully API or Buffer analytics, Claude API, Google Sheets',
                     'Google Meet'),
                    ('M5: The Full System Demo',
                     'Run through the complete content OS live. From idea capture to published post — fully automated.',
                     'Live', '45 min',
                     'All systems built in M2–M4',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track D — Business Owners (Outcome-Focused)',
                'goal': 'Identify the 3 highest-ROI automations for their business, build them, and measure '
                        'time and cost savings within the 30-day window.',
                'modules': [
                    ('M1: The Automation Audit',
                     'Score your top 10 business tasks by time cost and repetitiveness. Select the 3 to automate first.',
                     'Live', '45 min',
                     'List of your current weekly tasks (prepared before class)',
                     'Telegram (screen share)'),
                    ('M2: Lead Gen Automation',
                     'Build an AI outreach system: scrape LinkedIn leads → Claude writes personalised first-line → sends via email or DM.',
                     'Live', '75 min',
                     'Apollo.io or similar (free tier), Claude API, Make.com',
                     'Google Meet'),
                    ('M3: Customer Support Automation',
                     'Build a Claude-powered FAQ bot for your Telegram group or website that handles 80% of common questions.',
                     'Pre-recorded', '45 min',
                     'Claude API, ManyChat or Telegram Bot API',
                     'Gumroad / hosted link'),
                    ('M4: Reporting That Runs Itself',
                     'Build a weekly business report that pulls data from your tools, summarises with Claude, and emails you every Monday.',
                     'Live', '60 min',
                     'Google Sheets or Airtable, Claude API, Make.com, Gmail',
                     'Google Meet'),
                    ('M5: ROI Review',
                     'Calculate hours saved. Calculate cost saved. Present to the group. Map next quarter\'s automation priorities.',
                     'Live', '45 min',
                     'Working automations from M2–M4',
                     'Telegram group call'),
                ],
            },
        ],
    },
    {
        'topic': 'TOPIC 2: AI Video Creation',
        'description': (
            'Students learn to produce professional AI-generated video content from concept to final cut '
            'using tools in the ContentBrain stack. Focus is on repeatable workflows, not one-off experiments.'
        ),
        'tracks': [
            {
                'name': 'Track A — Beginners (First Video Ever)',
                'goal': 'Produce and publish a complete AI-generated short video (30–60 sec) from scratch by end of course.',
                'modules': [
                    ('M1: The AI Video Landscape',
                     'Understand what each tool does: Kling (video gen), fal.ai / Nano Banana (image gen), MiniMax (voice), Remotion (assembly). Pick your starting toolkit.',
                     'Live', '45 min',
                     'Kling free account, fal.ai account',
                     'Telegram (screen share)'),
                    ('M2: Your First AI Image',
                     'Generate your first scene-ready image with Nano Banana. Learn prompt structure, aspect ratios, and consistency tricks.',
                     'Live', '60 min',
                     'Nano Banana (Gemini API key), browser',
                     'Google Meet'),
                    ('M3: Animating Your Image',
                     'Turn a static image into a 5-second cinematic clip using Kling. Apply camera movements (zoom, pan, dolly).',
                     'Live', '60 min',
                     'Kling account (standard tier), image from M2',
                     'Google Meet'),
                    ('M4: Adding Voice',
                     'Generate a voiceover using MiniMax. Sync it to your video clip. Export the combined result.',
                     'Pre-recorded', '30 min',
                     'MiniMax API access, CapCut or DaVinci Resolve free',
                     'Gumroad / hosted link'),
                    ('M5: Publish Your First Video',
                     'Format for TikTok / Instagram Reels. Add captions. Post and share in the group.',
                     'Live', '45 min',
                     'CapCut (free), finished video from M4',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track B — Developers (Programmatic Video)',
                'goal': 'Build a programmatic video generation pipeline using Remotion, fal.ai API, and Claude — '
                        'producing batches of videos from data or scripts without manual tool-clicking.',
                'modules': [
                    ('M1: Remotion Fundamentals',
                     'Understand Remotion\'s React-based video composition model. Build a basic text + image video programmatically.',
                     'Live', '60 min',
                     'Node.js 18+, Remotion CLI, VS Code',
                     'Google Meet'),
                    ('M2: fal.ai API Integration',
                     'Call Nano Banana and Kling APIs programmatically. Build an image-to-video pipeline in Python or JS.',
                     'Live', '75 min',
                     'fal.ai API key, Python or Node.js',
                     'Google Meet'),
                    ('M3: Claude as Art Director',
                     'Use Claude to generate scene descriptions from a script. Feed descriptions to fal.ai. Automate the creative brief.',
                     'Live', '60 min',
                     'Claude API, fal.ai API',
                     'Google Meet'),
                    ('M4: Batch Video Generation',
                     'Build a pipeline: CSV of topics → Claude writes scripts → fal.ai generates images → Kling animates → MiniMax voices → Remotion assembles. Run 5 videos in one command.',
                     'Live', '90 min',
                     'All APIs from M1–M3, Python, Remotion',
                     'Google Meet'),
                    ('M5: Deploy + Schedule',
                     'Deploy your pipeline to Railway. Schedule weekly batch runs. Output videos to a Google Drive folder automatically.',
                     'Pre-recorded', '45 min',
                     'Railway account, Google Drive API',
                     'Gumroad / hosted link'),
                ],
            },
            {
                'name': 'Track C — Creators (Full Production Workflow)',
                'goal': 'Build and run a repeatable AI video production workflow producing 4+ videos per week, '
                        'platform-optimised, without manual scene-by-scene editing.',
                'modules': [
                    ('M1: Art Direction Before Scripting',
                     'Define your visual world first. Pick colour palette, character style, scene types. Create your visual bible.',
                     'Live', '45 min',
                     'Moodboard tool (Canva or Figma free), reference images',
                     'Telegram (screen share)'),
                    ('M2: Script → Storyboard with Claude',
                     'Write a video script then use Claude to break it into shot-by-shot storyboard with visual prompts for each scene.',
                     'Live', '60 min',
                     'Claude (web or API), script topic prepared',
                     'Google Meet'),
                    ('M3: Scene Generation Pipeline',
                     'Generate all scenes from your storyboard prompts using Nano Banana. Apply consistency techniques: seed locking, style reference, character anchor.',
                     'Live', '75 min',
                     'Nano Banana / fal.ai, Kling',
                     'Google Meet'),
                    ('M4: Voiceover + Assembly',
                     'Generate voiceover with MiniMax (your voice clone or alternative). Assemble scenes in CapCut or via Remotion. Add captions via auto-subtitle.',
                     'Live', '60 min',
                     'MiniMax API, CapCut, finished scenes',
                     'Google Meet'),
                    ('M5: Platform Optimisation',
                     'Adapt the same video for TikTok (9:16, 30–60s, native audio), Instagram Reel, LinkedIn (square, 60s), and YouTube Short. One video → 4 posts.',
                     'Pre-recorded', '30 min',
                     'CapCut, finished video',
                     'Gumroad / hosted link'),
                    ('M6: Live Production Review',
                     'Each student shares one finished video. Group gives hooks/visual feedback. Build your production SOP.',
                     'Live', '60 min',
                     'One finished video ready to screen',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track D — Business Owners (Marketing Video Automation)',
                'goal': 'Produce professional marketing videos (product demos, testimonials, explainers) '
                        'using AI — without hiring a video editor or agency.',
                'modules': [
                    ('M1: What Video Does For Your Business',
                     'Map the 3 video types your business needs most: explainer, demo, social proof. Set production targets.',
                     'Live', '45 min',
                     'List of your current marketing assets',
                     'Telegram (screen share)'),
                    ('M2: Product Demo in 90 Minutes',
                     'Produce a 60-second product or service explainer video from brief → script → visuals → voice → final cut.',
                     'Live', '90 min',
                     'Product description, Nano Banana, Kling, MiniMax, CapCut',
                     'Google Meet'),
                    ('M3: Testimonial Automation',
                     'Turn written testimonials into talking-head style AI videos using Hedra or similar. No customer filming required.',
                     'Pre-recorded', '30 min',
                     'Hedra free account or similar tool',
                     'Gumroad / hosted link'),
                    ('M4: Ad Creative Workflow',
                     'Build 3 ad creative variants for the same offer using AI video — different hooks, same message. A/B test ready.',
                     'Live', '60 min',
                     'Script, Nano Banana, Kling, CapCut',
                     'Google Meet'),
                    ('M5: Video Review + Distribution Plan',
                     'Review all produced videos. Set up a simple distribution system: Google Drive + Typefully or Buffer.',
                     'Live', '45 min',
                     'Finished videos, Typefully or Buffer',
                     'Telegram group call'),
                ],
            },
        ],
    },
    {
        'topic': 'TOPIC 3: Coding with AI',
        'description': (
            'Students learn to use AI as a coding co-pilot to build real tools — dashboards, bots, '
            'scripts, and web apps — regardless of their starting experience level. '
            '"Vibe coding" for beginners. Production engineering for developers.'
        ),
        'tracks': [
            {
                'name': 'Track A — Beginners (Never Coded Before)',
                'goal': 'Build and deploy a real working web app or tool using Claude Code, '
                        'without memorising syntax or taking a traditional programming course.',
                'modules': [
                    ('M1: What Coding With AI Actually Means',
                     'Understand vibe coding. Set up Claude Code in terminal. Write your first prompt that produces working code.',
                     'Live', '45 min',
                     'Laptop, Claude Code (free tier), terminal access',
                     'Telegram (screen share)'),
                    ('M2: Your First App — Price Tracker',
                     'Build a crypto price tracker web app with Claude Code. No prior coding. Just prompts and iteration.',
                     'Live', '75 min',
                     'Claude Code, browser',
                     'Google Meet'),
                    ('M3: Debugging Without Stress',
                     'Learn to read error messages with Claude\'s help. Fix 3 common bugs live. Build error-handling confidence.',
                     'Live', '60 min',
                     'Broken code (provided as starter), Claude Code',
                     'Google Meet'),
                    ('M4: Make It Yours — Custom Tool Build',
                     'Each student picks ONE tool they want. Claude Code builds it step by step with instructor guidance.',
                     'Live', '90 min',
                     'Claude Code, idea for your personal tool',
                     'Google Meet'),
                    ('M5: Deploy to the Web',
                     'Deploy your built app to Vercel or Netlify in under 10 minutes with AI guidance. Share your live URL.',
                     'Pre-recorded', '30 min',
                     'Vercel free account, GitHub account',
                     'Gumroad / hosted link'),
                    ('M6: Demo Day',
                     'Each student presents their live app. Gets feedback. Celebrates their first build.',
                     'Live', '60 min',
                     'Live deployed app URL',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track B — Developers (Advanced AI-Assisted Engineering)',
                'goal': 'Master Claude Code workflows, MCP server integration, and AI-assisted production '
                        'deployment — becoming 3–5× faster at shipping client projects.',
                'modules': [
                    ('M1: Claude Code Workflow Mastery',
                     'Advanced prompting for code: CLAUDE.md context files, plan mode, subagent delegation. How to set up a project for max output quality.',
                     'Live', '60 min',
                     'Claude Code, existing project codebase',
                     'Google Meet'),
                    ('M2: MCP Server Integration',
                     'Connect Claude Code to external tools via MCP: Supabase, Notion, GitHub. Build a Claude-powered dev workflow.',
                     'Live', '75 min',
                     'Claude Code, Supabase account, GitHub',
                     'Google Meet'),
                    ('M3: Building AI Agents with Claude SDK',
                     'Build a multi-tool agent using Claude\'s tool_use API. Implement retry logic, error handling, and streaming.',
                     'Live', '90 min',
                     'Claude API, Python or Node.js',
                     'Google Meet'),
                    ('M4: Full-Stack AI App in 4 Hours',
                     'Build a complete Next.js + Supabase + Claude API app live. Real database, real auth, real AI features.',
                     'Live', '90 min',
                     'Node.js, Next.js, Supabase, Claude API',
                     'Google Meet'),
                    ('M5: Testing and CI/CD for AI Apps',
                     'Write tests for AI-dependent code. Set up GitHub Actions CI. Deploy to Railway with zero-downtime strategy.',
                     'Pre-recorded', '45 min',
                     'GitHub, Railway, Jest or Pytest',
                     'Gumroad / hosted link'),
                    ('M6: Code Review + Portfolio Polish',
                     'Peer review session. Each dev presents architecture. Group improves code quality and documents for portfolio.',
                     'Live', '60 min',
                     'Completed project from M4',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track C — Creators (Build Your Own Content Tools)',
                'goal': 'Build personal AI-powered tools that automate the boring parts of content creation — '
                        'hook generators, caption writers, analytics dashboards — without hiring a developer.',
                'modules': [
                    ('M1: Prompts as Programs',
                     'Understand that a prompt is code. Build your first "tool" — a Claude prompt that consistently outputs great hooks.',
                     'Live', '45 min',
                     'Claude (web), notepad for prompt iteration',
                     'Telegram (screen share)'),
                    ('M2: Build a Hook Generator App',
                     'Turn your best hook prompt into a simple web app using Claude Code. Input: topic → output: 10 hooks.',
                     'Live', '75 min',
                     'Claude Code, browser',
                     'Google Meet'),
                    ('M3: Build Your Content Dashboard',
                     'Build a personal dashboard that shows your scheduled posts, hook performance, and next post suggestions.',
                     'Live', '75 min',
                     'Claude Code, Notion API or Airtable',
                     'Google Meet'),
                    ('M4: Script-to-Storyboard Automator',
                     'Build a tool: input a video topic → Claude writes script → Claude writes shot-by-shot storyboard → PDF export.',
                     'Pre-recorded', '45 min',
                     'Claude API, Python (simple), reportlab',
                     'Gumroad / hosted link'),
                    ('M5: Creator Tool Demo + SOP',
                     'Present your tools live. Document each tool as a SOP. Share with the class as a resource pack.',
                     'Live', '60 min',
                     'All built tools from M2–M4',
                     'Telegram group call'),
                ],
            },
            {
                'name': 'Track D — Business Owners (Build Without a Developer)',
                'goal': 'Use Claude Code to build internal tools, client-facing mini-apps, and simple automations '
                        'without hiring a developer or learning to code from scratch.',
                'modules': [
                    ('M1: What "Coding with AI" Means for Non-Coders',
                     'Reframe coding as problem description, not syntax memorisation. Identify 3 internal tools your business needs.',
                     'Live', '45 min',
                     'Claude Code (web), list of business pain points',
                     'Telegram (screen share)'),
                    ('M2: Build an Internal Tool in 60 Minutes',
                     'Build a client intake form + auto-responder using Claude Code. No agency, no developer, no waiting.',
                     'Live', '75 min',
                     'Claude Code, Supabase free tier or Google Forms',
                     'Google Meet'),
                    ('M3: Proposal and Report Generator',
                     'Build a tool: input client brief → Claude generates proposal draft → PDF export. Save 3 hours per client.',
                     'Live', '60 min',
                     'Claude Code, Python basic (instructor guides every step)',
                     'Google Meet'),
                    ('M4: Simple Lead Scoring Tool',
                     'Build a spreadsheet automation that scores new leads based on criteria and flags top priorities.',
                     'Pre-recorded', '30 min',
                     'Claude API, Google Sheets + Apps Script (Claude writes the script)',
                     'Gumroad / hosted link'),
                    ('M5: Business Tool Review + Handoff',
                     'Present your built tools. Instructor helps document and hand off to any future team member.',
                     'Live', '45 min',
                     'All tools built in M2–M4',
                     'Telegram group call'),
                ],
            },
        ],
    },
]

# ── DELIVERY SCHEDULE ─────────────────────────────────────────────────────────

SCHEDULE_NOTE = (
    'The 30-day launch window (April 3 – May 2, 2026) is marketing and enrolment only. '
    'No teaching happens before May 3. Classes start May 3, 2026 and run through May 31 (Demo Day). '
    'Students self-select ONE topic and ONE audience track on sign-up. '
    'Live sessions are held Tuesday and Thursday evenings (7–9 PM WAT) via Google Meet, '
    'with Telegram group discussions and Q&A between sessions. '
    'Pre-recorded modules are released 48 hours before the next live session so students arrive prepared.'
)

WEEK_PLAN = [
    ['Week', 'Live Sessions', 'Pre-Recorded Drops', 'Milestone'],
    ['Week 1\n(May 3–9)', 'M1 (Tue May 6) — All topics, all tracks', 'M2 released May 4', 'Students complete M1 and M2 before Week 2'],
    ['Week 2\n(May 10–16)', 'M3 (Tue May 13)\nM4 preview (Thu May 15)', 'M3 released May 11', 'Students have built first working output'],
    ['Week 3\n(May 17–23)', 'M4 (Tue May 20)\nQ&A session (Thu May 22)', 'M4/M5 released May 18', 'Core system/tool/video complete'],
    ['Week 4\n(May 24–30)', 'M5 Final (Tue May 27)', 'Final pre-recorded released May 25', 'All modules done, demo-ready'],
    ['Demo Day\n(May 31)', 'Demo Day (Google Meet) — All tracks', '—', 'Students publish live work, testimonials captured'],
]


def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='Quivira AI Course Outline', author='@big_quiv'
    )
    story = []

    # COVER
    cover = Table(
        [[Paragraph('QUIVIRA AI COURSE', styles['CoverTitle'])],
         [Paragraph('Complete Course Architecture — All Topics × All Audience Tracks', styles['CoverSub'])],
         [Paragraph('Launch Window: Apr 3 – May 2  ·  Classes: May 3 – 31, 2026', styles['CoverSub'])],
         [Spacer(1, 6)],
         [Paragraph('Topics: AI Automation  ·  AI Video Creation  ·  Coding with AI', styles['CoverSub'])],
         [Paragraph('Tracks: Beginners  ·  Developers  ·  Creators  ·  Business Owners', styles['CoverSub'])],
         ],
        colWidths=[W]
    )
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story += [cover, Spacer(1, 20)]

    # OVERVIEW
    story.append(Paragraph('Course Architecture Overview', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'Three course topics. Four audience tracks each. Twelve distinct learning paths. '
        'Students self-select on sign-up — they never sit through content that is not for them. '
        'All live sessions are delivered on Telegram (screen share for short sessions) or Google Meet '
        '(for hands-on builds). Pre-recorded modules are hosted on Gumroad and released on a schedule.',
        styles['Body']))
    story.append(Spacer(1, 8))

    # Overview table
    ov_data = [
        [Paragraph(h, styles['TableHead2']) for h in ['Topic', 'Beginner Track', 'Developer Track', 'Creator Track', 'Business Track', 'Total Modules']],
        [Paragraph('AI Automation', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('6 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('21', styles['TableCell2'])],
        [Paragraph('AI Video Creation', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('6 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('21', styles['TableCell2'])],
        [Paragraph('Coding with AI', styles['TableCell2']),
         Paragraph('6 modules', styles['TableCell2']),
         Paragraph('6 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('5 modules', styles['TableCell2']),
         Paragraph('22', styles['TableCell2'])],
        [Paragraph('<b>TOTAL</b>', styles['TableCell2']),
         Paragraph('<b>16</b>', styles['TableCell2']),
         Paragraph('<b>17</b>', styles['TableCell2']),
         Paragraph('<b>16</b>', styles['TableCell2']),
         Paragraph('<b>15</b>', styles['TableCell2']),
         Paragraph('<b>64 modules</b>', styles['TableCell2'])],
    ]
    ov_t = Table(ov_data, colWidths=[W*0.22, W*0.14, W*0.15, W*0.15, W*0.15, W*0.19])
    ov_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [WHITE, LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story += [ov_t, Spacer(1, 12)]

    # DELIVERY SCHEDULE
    story.append(Paragraph('Delivery Schedule', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(SCHEDULE_NOTE, styles['Body']))
    story.append(Spacer(1, 8))

    sched_data = [[Paragraph(h, styles['TableHead2']) for h in WEEK_PLAN[0]]]
    for row in WEEK_PLAN[1:]:
        sched_data.append([Paragraph(c, styles['TableCell2']) for c in row])
    sched_t = Table(sched_data, colWidths=[W*0.13, W*0.30, W*0.25, W*0.32])
    sched_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, MID),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story += [sched_t, Spacer(1, 12)]

    # COURSES
    for course in COURSES:
        story.append(PageBreak())
        story.append(topic_banner(course['topic']))
        story.append(Spacer(1, 8))
        story.append(Paragraph(course['description'], styles['Body']))
        story.append(Spacer(1, 8))

        for track in course['tracks']:
            story.append(KeepTogether([
                Paragraph(track['name'], styles['TrackHead']),
                Paragraph(f"<b>Track goal:</b> {track['goal']}", styles['Body']),
            ]))
            story.append(Spacer(1, 4))
            rows = [
                (m[0], m[1], m[2], m[3], m[4], m[5])
                for m in track['modules']
            ]
            story.append(module_table(rows))
            story.append(Spacer(1, 14))

    # COMPLETION CRITERIA
    story.append(PageBreak())
    story.append(Paragraph('Completion Criteria', styles['SectionHead']))
    story.append(hr())
    story.append(Paragraph(
        'A student is considered to have completed the course when:', styles['Body']))
    criteria = [
        'They have attended or watched all modules in their selected track.',
        'They have built and demonstrated one working output (automation, video, tool, or app).',
        'They have shared their output in the Telegram group for peer feedback.',
        'They have completed the final live session (Demo Day, May 31, 2026).',
    ]
    for c in criteria:
        story.append(Paragraph(f'• {c}', styles['BulletCO']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'Completion certificate (PDF, branded Quivira) issued via Gumroad upon submission of Demo Day output.', styles['Note']))

    # FOOTER
    story.append(Spacer(1, 30))
    story.append(Paragraph('Quivira Course Architecture — Phase 2 Complete', styles['CoverTitle']))
    story.append(Paragraph('Built April 3, 2026  ·  @big_quiv / ContentBrain', styles['CoverSub']))

    doc.build(story)
    print(f'PDF saved: {OUT_PATH}')

if __name__ == '__main__':
    build()
