"""Generate outreach DM/email openers PDF - VERIFIED OPEN opportunities only.
Framework: Pain-Bridge-Solution (from @andrescontrerasofficial cold call technique)
1. Paint the pain scenario they live through
2. Bridge to your solution naturally
3. Quantify the win
4. Ask a qualifying question to extract MORE pain
Voice: cold-email + sales-closer + ghostwriter rules. No em dashes. Conversational."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "06-Drafts", "outreach", "pipeline-outreach-openers-final.pdf"
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "Title2", parent=styles["Title"],
    fontSize=22, textColor=HexColor("#1a1a1a"), spaceAfter=6
)
subtitle_style = ParagraphStyle(
    "Sub", parent=styles["Normal"],
    fontSize=10, textColor=HexColor("#666666"), spaceAfter=20, alignment=TA_CENTER
)
section_style = ParagraphStyle(
    "Section", parent=styles["Heading2"],
    fontSize=14, textColor=HexColor("#c0392b"), spaceBefore=22, spaceAfter=6
)
company_style = ParagraphStyle(
    "Company", parent=styles["Heading3"],
    fontSize=12, textColor=HexColor("#1a1a1a"), spaceBefore=14, spaceAfter=2
)
label_style = ParagraphStyle(
    "Label", parent=styles["Normal"],
    fontSize=9, textColor=HexColor("#888888"), spaceBefore=2, spaceAfter=1
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=HexColor("#222222"), spaceAfter=4
)
contact_style = ParagraphStyle(
    "Contact", parent=styles["Normal"],
    fontSize=9, textColor=HexColor("#2980b9"), spaceBefore=2, spaceAfter=10,
    leftIndent=12
)
framework_style = ParagraphStyle(
    "Framework", parent=styles["Normal"],
    fontSize=9, leading=13, textColor=HexColor("#444444"), spaceAfter=4,
    leftIndent=12, borderColor=HexColor("#e0e0e0"), borderWidth=0.5,
    borderPadding=6, backColor=HexColor("#fafafa")
)

# ════════════════════════════════════════════════════════════════════════
# FRAMEWORK REFERENCE (printed on page 2)
# ════════════════════════════════════════════════════════════════════════

framework_text = """<b>PAIN-BRIDGE-SOLUTION FRAMEWORK</b> (from @andrescontrerasofficial)<br/><br/>
<b>1. Paint the pain:</b> "You know how [their type of company] often [specific problem]? But because [reason], they end up [consequence/lost money]..."<br/>
<b>2. Bridge to solution:</b> "So what we do is [your solution], that way [specific outcome they want]."<br/>
<b>3. Quantify the win:</b> "That way they're typically [saving/gaining X per month]."<br/>
<b>4. Qualify with a question:</b> "Just to see if it would even be helpful for you, [question about their current setup]?"<br/><br/>
<b>WHY IT WORKS:</b> The prospect shows up thinking "I'm here to solve MY problem", not "I'm here to get pitched."<br/>
<b>RULE:</b> Never lead with "I built X." Lead with the pain they feel, THEN reveal the fix."""

# ════════════════════════════════════════════════════════════════════════
# TIER 1: VERIFIED OPEN ROLES
# ════════════════════════════════════════════════════════════════════════

tier1 = [
    ("PrimeIntellect", "AI Infrastructure",
     "DM @PrimeIntellect on X. Apply at jobs.ashbyhq.com/PrimeIntellect",
     "Head of Growth (open role, 6 GTM roles total)",
     "VERIFIED OPEN",
     "You know how most AI infra companies hire growth people who understand marketing but have never actually built with AI? They write campaigns about products they've never touched. And then the content feels generic because the growth lead is translating from engineers instead of thinking like one. I actually build AI systems. My ContentBrain engine automates content production, competitive intelligence, and distribution. It's live, deployed, running 24/7. Just to see if there's a fit, what does your current content pipeline look like?"),

    ("Kalshi", "Prediction Markets, $22B valuation",
     "Apply at kalshi.com/careers (Greenhouse). LinkedIn: linkedin.com/company/kalshi",
     "5 open roles: Growth Marketing Mgr, Performance Marketer, Partnerships Mgr, Video Editor, Marketing Ops",
     "VERIFIED OPEN",
     "You know how prediction markets still feel like a crypto niche to most people? Even with a $22B valuation, the average person doesn't wake up thinking 'I should bet on the next Fed rate decision.' And then when they do hear about it, they go to Polymarket because that's the name they've seen everywhere. So what I do is build AI content systems that produce 60+ pieces a month, track what competitors are posting in real time, and adapt messaging based on what's actually working. Just to see if this is relevant, how are you handling content volume right now across platforms?"),

    ("Airwallex", "Global Payments, Fintech",
     "Apply at careers.airwallex.com. LinkedIn: linkedin.com/company/airwallex",
     "6 open roles: Growth Content Marketing Mgr (SF), Sr Product Marketing Mgr (SF + London), Content Marketing Mgr Enterprise (EMEA), Sr Field Marketing (SEA), Director Global Performance Marketing (SF)",
     "VERIFIED OPEN",
     "You know how fintech companies scale into new markets but the content still sounds like it was written for one audience? The messaging that works in San Francisco doesn't land in Singapore or London. And then the team is stretched thin trying to localize everything manually while keeping compliance happy. I build AI content systems that produce localized, high-volume content at speed without sacrificing quality or brand voice. Just to see if this is useful, how many markets is your content team covering right now, and what's the turnaround on new market content?"),

    ("Lido Finance", "DeFi, Liquid Staking",
     "Apply at jobs.ashbyhq.com/Lido.fi. LinkedIn: linkedin.com/company/lidofinance",
     "Institutional Growth Lead, USA (open role)",
     "VERIFIED OPEN (EMEA closed, USA only)",
     "You know how DeFi protocols spend months building incredible tech but then struggle to get institutions to take them seriously? The product is ready for enterprise, but the content still reads like it was written for crypto Twitter. And then the institutional leads go to competitors who just tell a cleaner story. I build AI growth systems that translate DeFi tech into institutional-grade thought leadership at scale. 60+ posts a month, automated competitor tracking, consistent positioning. Just to see if this is relevant, who's handling Lido's institutional-facing content right now?"),

    ("TransFi", "Cross-border Stablecoin Payments",
     "Check transfi.com/careers in browser. DM CEO Raj Kamal on LinkedIn (linkedin.com/company/trans-fi)",
     "~1 marketing role (confirm title on Wellfound/careers page)",
     "LIKELY OPEN",
     "Raj. You know how cross-border payment companies raise a big round and then realize they need to scale marketing across 5+ emerging markets at the same time? But hiring a local team in every market takes months, and agencies don't understand stablecoins. So what I do is run an AI content engine that produces localized, multi-platform content at scale. 60+ pieces a month. The angle for TransFi: make stablecoins feel as natural as mobile money in every market you enter, without hiring 10 content people. How are you handling multi-market content post-raise?"),
]

# ════════════════════════════════════════════════════════════════════════
# TIER 2: VERIFIED ACTIVE EXCHANGE PROGRAMS
# ════════════════════════════════════════════════════════════════════════

tier2 = [
    ("KuCoin", "Content Creator Program + KuCoin Live 2026",
     "Telegram: @Kucoinlive8. Also apply at kucoin.com/content-creator-program",
     "Creator Program team (2.7M USDT reward pool for Live 2026)",
     "VERIFIED ACTIVE",
     "Hey. I'm @big_quiv. You know how most creator programs get flooded with low-effort content that doesn't actually drive signups? People just slap the exchange logo on a generic trading video and call it a day. I run an AI production system that lets me create high-quality educational content at scale. 60+ posts/month across X, TikTok, LinkedIn, Instagram. Every piece is built to teach something specific, not just fill space. What kind of content is performing best in the creator program right now?"),

    ("CoinEx", "KOL Program",
     "Apply at coinex.com/en/kol",
     "KOL Program team (5K+ followers required, up to 60% commission)",
     "VERIFIED ACTIVE",
     "Hey CoinEx team. You know how most KOLs just repost announcements and call it promotion? No original education, no exchange-specific content that actually helps users navigate the platform. I produce AI-assisted educational content about trading, DeFi, and exchange features at volume. Tutorials, strategy breakdowns, feature highlights. Multiple pieces per week, not month. My audience is active crypto traders. What formats are driving the most signups through the KOL program right now?"),

    ("MEXC", "UGC Learn Creator Program",
     "Apply at mexc.com/learn or blog.mexc.com/mexc-learn-ugc-creator-recruitment",
     "UGC Creator Program team ($200 USDT/article, 71 creators recruited so far)",
     "VERIFIED ACTIVE",
     "Hey MEXC Learn team. You know how a lot of exchange educational content reads like it was written by someone who doesn't actually trade? The articles are technically correct but nobody learns anything because there's no real perspective behind them. I'm @big_quiv. I produce AI-assisted educational content backed by actual trading experience. Market analysis, strategy breakdowns, DeFi deep dives. I can deliver multiple pieces per week with depth that readers actually bookmark. What topics are getting the most traction on MEXC Learn right now?"),

    ("Crypto.com", "Exchange Affiliate Programme",
     "Apply at crypto.com/us/affiliate (Impact.com dashboard)",
     "Affiliate Program (up to 50% fee commission + 1,050 USDC per active referral)",
     "VERIFIED ACTIVE",
     "You know how most affiliates just drop a referral link in their bio and hope for the best? No educational content, no trust building, no reason for someone to pick Crypto.com over the 10 other exchanges they've heard of. I run a content brand (@big_quiv) with an AI engine that produces 60+ pieces monthly. Trading education, DeFi explainers, market analysis. Each piece naturally positions the exchange as the tool, not just a link. What's the average conversion rate you're seeing from content-driven affiliates vs link-droppers?"),

    ("Bitpanda", "Affiliate + Internal KOL",
     "Affiliate: app.impact.com (Bitpanda). For KOL deals: pitch marketing team via LinkedIn (linkedin.com/company/bitpanda)",
     "Affiliate Programme (20% rev share). Larger KOL deals managed internally.",
     "VERIFIED ACTIVE",
     "You know how the European crypto market has a trust problem? People want to invest but they don't know which platform to trust, especially after everything that happened the last few years. I produce AI-assisted educational content focused on trading fundamentals and crypto adoption. My audience skews toward people who want clarity before they commit. That's exactly who Bitpanda needs. Signing up for the affiliate programme and also interested in a larger KOL conversation. Who handles those partnerships on your side?"),
]

# ════════════════════════════════════════════════════════════════════════
# TIER 3: SERVICE PITCHES (No specific role, pitch the service)
# ════════════════════════════════════════════════════════════════════════

tier3 = [
    ("TRM Labs", "Blockchain Analytics, $1B valuation",
     "LinkedIn: linkedin.com/company/trmlabs. Research marketing team.",
     "Esteban Castano, CEO",
     "SERVICE PITCH",
     "You know how blockchain analytics companies do incredible work behind the scenes but most people outside the industry have no idea what you actually do? The product fights crypto crime, but the content reads like a compliance doc. And then when enterprise buyers evaluate vendors, they go with whoever told the clearest story, not whoever has the best tech. I build AI content systems that turn complex technical products into thought leadership at scale. 60+ posts/month, automated competitive tracking. Just to see if this is relevant, who's handling TRM's content production right now?"),

    ("Ostium", "On-chain Perps for RWA",
     "DM co-founder Kaledora Kiernan-Linn on X or LinkedIn",
     "Kaledora Kiernan-Linn, Co-founder",
     "SERVICE PITCH",
     "Kaledora. You know how traditional derivatives traders look at on-chain perps and think 'that's a crypto thing, not for me'? The $10T CFD market is right there, but the messaging from most DeFi protocols still speaks crypto-native language that TradFi people tune out. And then those traders stay on centralized platforms paying higher fees. I build AI content systems that bridge that gap. Institutional-quality content, 60+ posts/month, automated trend detection. Who's handling Ostium's content strategy right now?"),

    ("Simile", "AI Marketing Testing, $100M Series A",
     "Research contact via simile.ai. Co-founder: Joon Park",
     "Joon Park, Co-founder",
     "SERVICE PITCH",
     "Joon. You know how AI companies come out of stealth with incredible tech but zero market awareness? The product works, the funding is there, but nobody knows you exist yet. And then some competitor with worse tech but better marketing captures the category first. That's the stealth-to-awareness gap. I build AI growth systems that close it fast. 60+ posts/month, competitive analysis, video production, all automated. Just to see if this is relevant, what does Simile's go-to-market content look like right now?"),

    ("Fundamental", "Enterprise AI, $1.4B valuation",
     "Research CEO via fundamental.ai. CEO: Jeremy Fraenkel",
     "Jeremy Fraenkel, CEO",
     "SERVICE PITCH",
     "Jeremy. You know how enterprise AI companies hit unicorn valuation but the brand still doesn't match the scale? The product serves Fortune 500 but the content reads like a Series A startup. And then when enterprise buyers compare you to competitors, they pick the one that feels more established, even if your tech is better. I build AI content systems that produce thought leadership at unicorn scale. Multi-platform, data-driven, consistent. Who's owning Fundamental's content right now?"),

    ("Myriad", "Prediction Markets, Seed Stage",
     "DM @MyriadMarkets on X. CEO: Loxley Fernandes",
     "Loxley Fernandes, CEO",
     "SERVICE PITCH",
     "Loxley. You know how new prediction markets launch and immediately get compared to Polymarket and Kalshi? Even if your product is different, you're fighting for attention in a space where two names already dominate the conversation. And then every day without a strong brand voice is a day someone else captures your potential users. I build AI content engines that can have your full content stack live across all platforms in 2 weeks. What does Myriad's content presence look like right now?"),

    ("Project Eleven", "Post-Quantum Crypto, $20M Series A",
     "LinkedIn: linkedin.com/company/p-11. CEO: Alex Pruden",
     "Alex Pruden, CEO",
     "SERVICE PITCH",
     "Alex. You know how post-quantum cryptography is one of the most important problems in crypto, but most people's eyes glaze over the second you try to explain it? The tech is critical, but the content doesn't connect because it's written for researchers, not builders or buyers. I build AI content systems that translate deep technical concepts into social content people actually engage with. Threads, short-form video, visual explainers. How is Project Eleven handling content right now?"),

    ("Pixelmon", "Web3 Gaming, Animoca Brands",
     "DM @Pixelmon on X. CEO: Giulio Xiloyannis",
     "Giulio Xiloyannis, CEO",
     "SERVICE PITCH",
     "Giulio. You know how Web3 games have this problem where the crypto community cares about tokenomics but the gaming community cares about gameplay, and most content only speaks to one side? You end up with traders who don't play and gamers who don't trust crypto. I build AI production systems that create gaming-native content at scale. Short-form video, community content, social across every platform. 60+ posts/month. Who's running Pixelmon's content right now?"),

    ("Illuvium", "AAA Blockchain RPG",
     "DM @illaboratory on X. Research marketing contact.",
     "Marketing Lead",
     "SERVICE PITCH",
     "You know how AAA blockchain games spend years building incredible visuals and gameplay, but then the marketing looks like every other crypto project? Generic announcement tweets, no cinematic content, no visual storytelling that matches the quality of the game itself. And then people scroll right past it. I build AI content systems that produce cinematic short-form content, community automation, and competitive intelligence at scale. What does Illuvium's content production pipeline look like right now?"),

    ("Impossible Finance", "DeFi + NFT (acquired Rarible)",
     "DM @ImpossibleFi on X",
     "Marketing team",
     "SERVICE PITCH",
     "You know how post-acquisition rebrands are a nightmare for content? Two different communities, two different brand voices, and a narrow window before people lose interest in the story. Every day without a unified narrative is a day users drift to competitors. I build AI content engines that handle exactly this kind of transition. High-volume production, brand voice alignment, community management. Who's leading the rebrand content right now?"),

    ("World Markets", "Everything DEX on MegaETH",
     "Find Co-founder Kevin Coons on X or LinkedIn",
     "Kevin Coons, Co-founder",
     "SERVICE PITCH",
     "Kevin. You know how new DEXs launch and have about a 30-day window to capture attention before the next one drops? If you don't have a content presence from day one, you're invisible. And then users default to whatever protocol already has the loudest voice in the ecosystem. I build AI content engines that can have your brand live across every platform in 2 weeks. Full production. What does World Markets' content stack look like right now?"),

    ("Lendasat", "Bitcoin-backed Lending, Pre-seed",
     "Research founder via lendasat.com",
     "Founder (find on LinkedIn or X)",
     "SERVICE PITCH",
     "You know how Bitcoin lending has a massive trust problem? People have been burned by centralized lenders, and now even good products get side-eyed. The only way to build trust at this stage is consistent education before you ever ask for a signup. I build AI content engines that produce educational threads, explainer videos, and community content at scale. Pre-seed is the perfect time to own the 'trusted Bitcoin lending' narrative. Who's handling content for Lendasat right now?"),
]

# ════════════════════════════════════════════════════════════════════════
# TIER 4: PARTNERSHIP PITCHES
# ════════════════════════════════════════════════════════════════════════

tier4 = [
    ("Coinbound", "Web3 Agency, 800+ clients",
     "DM @coinaboratory on X. coinbound.io",
     "Partnerships team",
     "PARTNERSHIP PITCH",
     "You know how agencies hit a ceiling where taking on more clients means hiring more people, and hiring more people means lower margins? Especially with content, every new client needs a writer, a strategist, a designer. And then either quality drops or profits do. I built an AI content engine that automates production, competitor analysis, and performance tracking. Here's the pitch: white-label partnership. I plug into your workflow, you deliver 3x the content to clients at the same cost. Would that model work for Coinbound?"),

    ("theKOLLAB", "Web3 KOL Agency",
     "Research contact via thekollab.io",
     "Partnerships team",
     "PARTNERSHIP PITCH",
     "You know how KOL campaign management is mostly manual? Briefs, content reviews, performance tracking, reporting. Every campaign eats hours that could go toward landing the next client. I build AI systems that automate the repetitive parts. Faster briefs, more content variations, real-time performance optimization. Exploring partnership models where my AI stack handles the production side of your campaigns. Would that be useful for your workflow?"),

    ("Formo.so", "DeFi Growth Platform",
     "Research contact via formo.so",
     "Partnerships team",
     "PARTNERSHIP PITCH",
     "You know how DeFi protocols use your growth platform to track and optimize, but then struggle to produce the content that actually drives that growth? The analytics are there, but the content pipeline is the bottleneck. My AI content engine is the other half of that equation. Thinking integration: protocols using Formo get AI-powered content recommendations and production built into the workflow. Moat for both of us. Worth a conversation?"),
]

# ════════════════════════════════════════════════════════════════════════
# TIER 5: BOUNTIES (Active but changed)
# ════════════════════════════════════════════════════════════════════════

tier5 = [
    ("MindoAI", "AI Attention Economy",
     "DM @MindoAI on X. Enter at mindoshare.ai",
     "Partnerships / Community team",
     "VERIFIED ACTIVE (changed: $50K PERC token leaderboard, not $70K video)",
     "Your Perceptron Network leaderboard is interesting. I run an AI video production pipeline. Scripting, visual generation, voiceover, assembly. I can produce competitive entries at volume. What are the current Epoch 3 categories and how are submissions ranked?"),

    ("Alchemist AI", "AI Creation Platform",
     "DM @alchemistAIapp on X. Check Discord for current bounties.",
     "Community / Bounty team",
     "UNCONFIRMED for 2026 (was $100-$2K/post)",
     "Saw your content bounty program from last year. Is it still running for 2026? I'm @big_quiv. I run an AI production pipeline and can deliver high-quality educational content, tutorials, and promo videos about Alchemist AI at volume. What are the current briefs?"),
]


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
    )
    story = []

    # ── Title ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.0 * inch))
    story.append(Paragraph("Pipeline Outreach Openers", title_style))
    story.append(Paragraph(
        "Pain-Bridge-Solution Framework (from @andrescontrerasofficial)<br/>"
        "Verified Open Opportunities Only<br/>"
        "@big_quiv | March 28, 2026",
        subtitle_style
    ))
    story.append(Spacer(1, 0.2 * inch))

    # ── Framework reference ─────────────────────────────────────────────
    story.append(Paragraph(framework_text, framework_style))
    story.append(PageBreak())

    # ── Summary table ───────────────────────────────────────────────────
    all_entries = (
        [("VERIFIED ROLE", *e) for e in tier1]
        + [("EXCHANGE PROGRAM", *e) for e in tier2]
        + [("SERVICE PITCH", *e) for e in tier3]
        + [("PARTNERSHIP", *e) for e in tier4]
        + [("BOUNTY", *e) for e in tier5]
    )

    summary_data = [["#", "Company", "Type", "Where to Reach Out"]]
    for i, (tier_label, company, _, where, _, _, _) in enumerate(all_entries, 1):
        short_where = where.split(".")[0].strip()
        if len(short_where) > 45:
            short_where = short_where[:42] + "..."
        summary_data.append([str(i), company, tier_label, short_where])

    t = Table(summary_data, colWidths=[0.35 * inch, 1.2 * inch, 1.3 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#c0392b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f9f9f9"), HexColor("#ffffff")]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ── Render tiers ────────────────────────────────────────────────────
    def render_tier(title, entries, start_num):
        story.append(Paragraph(title, section_style))
        n = start_num
        for company, category, where, contact, status, message in entries:
            story.append(Paragraph(
                f"{n}. {company} <font size=8 color='#888888'>({category})</font>",
                company_style
            ))
            story.append(Paragraph(f"STATUS: <font color='#27ae60'>{status}</font>", label_style))
            story.append(Paragraph("CONTACT:", label_style))
            story.append(Paragraph(contact, contact_style))
            story.append(Paragraph("WHERE TO DM / APPLY:", label_style))
            story.append(Paragraph(where, contact_style))
            story.append(Paragraph("OPENER MESSAGE:", label_style))
            story.append(Paragraph(message, body_style))
            story.append(Spacer(1, 8))
            n += 1
        return n

    n = 1
    n = render_tier("TIER 1: VERIFIED OPEN ROLES", tier1, n)
    n = render_tier("TIER 2: VERIFIED EXCHANGE PROGRAMS", tier2, n)
    n = render_tier("TIER 3: SERVICE PITCHES (no specific role)", tier3, n)
    n = render_tier("TIER 4: PARTNERSHIP PITCHES", tier4, n)
    n = render_tier("TIER 5: BOUNTIES / LEADERBOARDS", tier5, n)

    # ── Closed roles ────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("CLOSED / REMOVED (for reference)", section_style))
    closed = [
        "Paradex - Growth Marketing Lead (expired Nov 2024)",
        "Variational - no public openings found",
        "Bluesky - Community Marketing Manager (filled)",
        "Turnkey - zero marketing roles (Sales + RevOps only)",
        "Mangrove - zero active openings",
        "Dynatrace - careers page shows 0 positions",
        "Sogni AI - no careers page exists",
        "The Rundown AI - no internal roles (job board is external only)",
        "BVNK - Mastercard $1.8B acquisition pending (likely hiring freeze)",
    ]
    for item in closed:
        story.append(Paragraph(
            f"<font color='#c0392b'>X</font>  {item}", body_style
        ))

    # ── Footer ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "<i>Generated by ContentBrain | @big_quiv | Verified March 28, 2026<br/>"
        "DM framework: Pain-Bridge-Solution (@andrescontrerasofficial)</i>",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       fontSize=8, textColor=HexColor("#aaaaaa"),
                       alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"PDF saved -> {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
