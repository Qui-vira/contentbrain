"""Generate Outlier AI PDF Guide using reportlab."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', '06-Drafts')
OUT_PATH = os.path.join(OUT_DIR, 'outlier-ai-guide.pdf')

# Colors
BRAND_DARK = HexColor('#1a1a2e')
BRAND_RED = HexColor('#e94560')
BRAND_GRAY = HexColor('#333333')
BRAND_LIGHT = HexColor('#f5f5f5')
TABLE_HEADER = HexColor('#1a1a2e')
TABLE_ALT = HexColor('#f0f0f0')

styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontSize=28, textColor=BRAND_DARK, spaceAfter=10,
    fontName='Helvetica-Bold', alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'CoverSub', parent=styles['Normal'],
    fontSize=14, textColor=BRAND_GRAY, alignment=TA_CENTER, spaceAfter=30
))
styles.add(ParagraphStyle(
    'SectionHead', parent=styles['Heading1'],
    fontSize=18, textColor=BRAND_DARK, spaceBefore=20, spaceAfter=10,
    fontName='Helvetica-Bold', borderWidth=0, borderPadding=0,
    borderColor=BRAND_RED
))
styles.add(ParagraphStyle(
    'SubHead', parent=styles['Heading2'],
    fontSize=13, textColor=BRAND_GRAY, spaceBefore=12, spaceAfter=6,
    fontName='Helvetica-Bold'
))
styles.add(ParagraphStyle(
    'BodyText2', parent=styles['Normal'],
    fontSize=10, leading=14, textColor=BRAND_GRAY, spaceAfter=6,
    alignment=TA_JUSTIFY
))
styles.add(ParagraphStyle(
    'Tip', parent=styles['Normal'],
    fontSize=10, leading=13, textColor=HexColor('#0a5e2a'),
    spaceAfter=6, leftIndent=20, fontName='Helvetica-Oblique'
))
styles.add(ParagraphStyle(
    'Warning', parent=styles['Normal'],
    fontSize=10, leading=13, textColor=HexColor('#b30000'),
    spaceAfter=6, leftIndent=20, fontName='Helvetica-BoldOblique'
))
styles.add(ParagraphStyle(
    'BulletText', parent=styles['Normal'],
    fontSize=10, leading=13, textColor=BRAND_GRAY,
    spaceAfter=3, leftIndent=20, bulletIndent=10
))

def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    if col_widths is None:
        col_widths = [None] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t

def bullet(text):
    return Paragraph(f"• {text}", styles['BulletText'])

def build_pdf():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )
    story = []

    # COVER
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("Outlier AI", styles['CoverTitle']))
    story.append(Paragraph("Complete Registration & Earning Guide (2026)", styles['CoverSub']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Everything you need to know: registration, pay rates, tasks,<br/>payment methods, tips, and mistakes to avoid.", styles['CoverSub']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Compiled from 13 X/Twitter sources + 8 web sources<br/>April 2026", styles['CoverSub']))
    story.append(PageBreak())

    # TABLE OF CONTENTS
    story.append(Paragraph("Table of Contents", styles['SectionHead']))
    toc_items = [
        "1. What is Outlier?",
        "2. What Do You Actually Do?",
        "3. Requirements",
        "4. Step-by-Step Registration",
        "5. Pay Rates",
        "6. Payment Methods",
        "7. Tips to Get Accepted Faster",
        "8. Common Mistakes to Avoid",
        "9. Realistic Earning Expectations",
        "10. Frequently Asked Questions",
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles['BodyText2']))
    story.append(PageBreak())

    # SECTION 1
    story.append(Paragraph("1. What is Outlier?", styles['SectionHead']))
    story.append(Paragraph(
        "Outlier AI is a platform operated by <b>Scale AI</b> (valued at $14 billion) that pays freelancers "
        "to train artificial intelligence models. You evaluate, correct, and improve AI-generated responses "
        "— essentially teaching AI to be smarter.",
        styles['BodyText2']
    ))
    story.append(make_table(
        ['Detail', 'Info'],
        [
            ['Parent Company', 'Scale AI (Alexandr Wang, San Francisco)'],
            ['Total Paid Out', '$100M+ to 40,000+ contributors'],
            ['Domains', '40+ (writing, coding, STEM, languages, law, medicine)'],
            ['Relationship to Remotasks', 'Both Scale AI subsidiaries. Outlier = LLM/text. Remotasks = vision/images.'],
        ],
        col_widths=[2.5*inch, 4*inch]
    ))
    story.append(Spacer(1, 12))

    # SECTION 2
    story.append(Paragraph("2. What Do You Actually Do?", styles['SectionHead']))
    story.append(Paragraph(
        "You get paid to make AI smarter. Tasks include evaluating responses, rewriting content, "
        "reviewing code, fact-checking, prompt engineering, and data annotation.",
        styles['BodyText2']
    ))
    story.append(make_table(
        ['Task Type', 'What You Do'],
        [
            ['Response Evaluation', 'Compare AI answers, pick the better one, explain why'],
            ['Content Rewriting', 'Fix AI text for accuracy, clarity, structure'],
            ['Coding Tasks', 'Review AI code, debug errors, suggest improvements'],
            ['Fact-Checking', 'Verify AI claims against real data'],
            ['Prompt Engineering', 'Write questions to test AI limits'],
            ['Data Annotation', 'Label and categorize content for training'],
            ['Specialized Review', 'Domain expert review (law, medicine, math)'],
        ],
        col_widths=[2*inch, 4.5*inch]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "If you can read, think critically, and write clearly — you can do this work.",
        styles['Tip']
    ))

    # SECTION 3
    story.append(Paragraph("3. Requirements", styles['SectionHead']))
    story.append(Paragraph("Must-Have", styles['SubHead']))
    for item in [
        "Age: 18+",
        "Education: Associate degree minimum (bachelor's or higher preferred)",
        "Valid government ID: Passport or driver's license (not expired)",
        "Resume: Up to date, reflecting real skills",
        "LinkedIn profile: Connected and current",
        "Equipment: Laptop/desktop with stable internet",
        "English: Strong proficiency",
    ]:
        story.append(bullet(item))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Nice-to-Have (Higher Pay)", styles['SubHead']))
    for item in [
        "Graduate degree (Master's, PhD)",
        "STEM background (math, physics, chemistry, CS)",
        "Coding skills (Python, JavaScript, Java, C++)",
        "Legal or medical expertise",
        "Published academic work or GitHub portfolio",
    ]:
        story.append(bullet(item))
    story.append(PageBreak())

    # SECTION 4
    story.append(Paragraph("4. Step-by-Step Registration", styles['SectionHead']))
    steps = [
        ("Step 1: Go to outlier.ai",
         "Visit https://app.outlier.ai/en/expert/signup and click 'Create an Account.'"),
        ("Step 2: Create Your Account",
         "Sign up with email or Google. Enter full name, phone number, DOB, country, address."),
        ("Step 3: Complete Your Profile",
         "Upload your current resume. Connect your LinkedIn profile. Technical skills validated via GitHub/Google Scholar."),
        ("Step 4: Identity Verification",
         "Outlier uses Persona. Take clear photos of government ID (front/back) and a live selfie. Processing: 1-2 business days."),
        ("Step 5: Select Your Skills",
         "Choose max 10 skills. Only pick ones you can genuinely demonstrate — you WILL be tested."),
        ("Step 6: Take the Qualification Test",
         "General Reasoning Screening — must score 80% or higher. Often ONE attempt only. Prepare carefully."),
        ("Step 7: Start Earning",
         "Once approved, browse projects on your dashboard. Each shows task description, time, and pay rate."),
    ]
    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}</b>", styles['SubHead']))
        story.append(Paragraph(desc, styles['BodyText2']))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "NIGERIA USERS: Platform rejects +234 numbers. Use a paid VPN + US virtual number, "
        "or an RDP (preferred — gives real US machine fingerprint). Recommended proxies: NSocks, CleanLTE.",
        styles['Warning']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "April 2026 Update: Some users report the Aether assessment exam is temporarily suspended "
        "for new registrations. Check back regularly.",
        styles['Warning']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Timeline: Active onboarding = 30-90 minutes. Getting first project = 1 day to several weeks.",
        styles['Tip']
    ))
    story.append(PageBreak())

    # SECTION 5
    story.append(Paragraph("5. Pay Rates", styles['SectionHead']))
    story.append(make_table(
        ['Category', 'Hourly Rate', 'Who Qualifies'],
        [
            ['Entry-level tasks', '$12-$20/hr', 'Anyone with degree + 80% score'],
            ['Writing/content evaluation', '$15-$35/hr', 'Strong writers'],
            ['Creative writing', '$20-$40/hr', 'Published writers'],
            ['AI art training', 'Up to $30/hr', 'Artists, designers'],
            ['Math/STEM review', '$20-$50/hr', 'STEM degree holders'],
            ['Coding/technical', '$25-$50/hr', 'Developers (Python, JS)'],
            ['Voice acting', 'Up to $40/hr', 'Voice actors'],
            ['Software engineering', '~$43/hr', 'Senior developers'],
            ['Legal review', '$50-$100/hr', 'Lawyers, paralegals'],
            ['Medical review', '$50-$100/hr', 'Medical professionals'],
        ],
        col_widths=[2*inch, 1.5*inch, 3*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "US average across all contributors: ~$31/hr (Glassdoor, 1,461 salary reports)",
        styles['Tip']
    ))

    # SECTION 6
    story.append(Paragraph("6. Payment Methods", styles['SectionHead']))
    story.append(make_table(
        ['Method', 'Availability', 'Notes'],
        [
            ['PayPal', 'Global (most common)', 'Works in Nigeria via domiciliary account'],
            ['Airtm', 'Global', 'Good for African users, converts to local currency'],
            ['ACH Bank Transfer', 'US only', 'Direct deposit to US bank account'],
        ],
        col_widths=[1.5*inch, 2*inch, 3*inch]
    ))
    story.append(Spacer(1, 8))
    for item in [
        "Payments processed every Tuesday",
        "For work done previous Tuesday-Monday (midnight UTC)",
        "Minimum payout: $10",
        "Funds arrive within 1-3 business days",
    ]:
        story.append(bullet(item))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Nigeria tip: Use a domiciliary (USD) account at your Nigerian bank for PayPal withdrawals to avoid conversion losses.",
        styles['Tip']
    ))
    story.append(PageBreak())

    # SECTION 7
    story.append(Paragraph("7. Tips to Get Accepted Faster", styles['SectionHead']))
    tips = [
        '"RDP over VPN" — @ObaDeleke. RDP gives a real US machine fingerprint.',
        '"Accuracy matters more than speed" — @iamveektoria_. Quality score determines everything.',
        '"You need a solid proxy from Nigeria" — @sleektru. NSocks, CleanLTE recommended.',
        'Keep resume current — the system auto-extracts skills from your work history.',
        'Connect a strong LinkedIn — cross-referenced for credibility.',
        'Choose only 5-10 genuine skills — inflated claims get caught during screening.',
        'Highlight specialized knowledge — STEM, law, medicine, coding get priority AND higher pay.',
        'Connect GitHub/Google Scholar if applicable — technical validation.',
        'Score 80%+ on reasoning test — non-negotiable, often no retakes.',
        'Read ALL project guidelines before attempting any assessment.',
        'Be patient — getting tasks can take days to weeks after approval.',
        'Apply for Yoruba/Hausa projects if you are Nigerian — these are specifically available.',
    ]
    for i, tip in enumerate(tips, 1):
        story.append(Paragraph(f"<b>{i}.</b> {tip}", styles['BodyText2']))

    # SECTION 8
    story.append(Paragraph("8. Common Mistakes to Avoid", styles['SectionHead']))
    story.append(Paragraph("During Registration", styles['SubHead']))
    story.append(make_table(
        ['Mistake', 'What Happens', 'How to Avoid'],
        [
            ['Claiming false skills', 'Fail assessment, locked out', 'Only select genuine skills'],
            ['Expired/blurry ID', 'Verification fails', 'Check expiry, good lighting'],
            ['Profile doesn\'t match ID', 'Rejected', 'Name, DOB, address must match'],
            ['Rushing reasoning test', 'Score below 80%', 'Take your time, no speed bonus'],
        ],
        col_widths=[1.8*inch, 2.2*inch, 2.5*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("While Working", styles['SubHead']))
    story.append(make_table(
        ['Mistake', 'What Happens', 'How to Avoid'],
        [
            ['Speed over accuracy', 'Quality drops, account banned', 'Accuracy always comes first'],
            ['Using AI tools', 'Detected and banned', 'Do all work yourself'],
            ['Ignoring guidelines', 'Flagged, restricted', 'Read every instruction'],
            ['Not checking daily', 'Miss high-paying projects', 'Check dashboard daily'],
            ['Large balance buildup', 'Risk losing if deactivated', 'Withdraw regularly'],
        ],
        col_widths=[1.8*inch, 2.2*inch, 2.5*inch]
    ))
    story.append(PageBreak())

    # SECTION 9
    story.append(Paragraph("9. Realistic Earning Expectations", styles['SectionHead']))
    story.append(make_table(
        ['Scenario', 'Hours/Week', 'Rate', 'Weekly', 'Monthly'],
        [
            ['Casual', '5-10', '$15/hr', '$75-$150', '$300-$600'],
            ['Consistent', '15-20', '$20/hr', '$300-$400', '$1,200-$1,600'],
            ['Active', '30-40', '$25/hr', '$750-$1,000', '$3,000-$4,000'],
            ['Specialist', '20-30', '$40-60/hr', '$800-$1,800', '$3,200-$7,200'],
        ],
        col_widths=[1.3*inch, 1.2*inch, 1.2*inch, 1.4*inch, 1.4*inch]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Reality check: Task availability is inconsistent. Not everyone gets approved. "
        "Income is NOT guaranteed. Some training is unpaid. Best as supplemental income — "
        "combine with other platforms for stability.",
        styles['Warning']
    ))

    # SECTION 10
    story.append(Paragraph("10. Frequently Asked Questions", styles['SectionHead']))
    faqs = [
        ("Is Outlier AI legit?",
         "Yes. Operated by Scale AI ($14B valuation). $100M+ paid to contributors. Multiple Nigerian users confirm payments."),
        ("Can I use Outlier from Nigeria?",
         "Yes, with workarounds. Nigerian numbers rejected. Need VPN/RDP + US virtual number. Yoruba/Hausa projects available."),
        ("How long to start earning?",
         "Onboarding: 30-90 min. ID verification: 1-2 days. First project: days to weeks."),
        ("What's the minimum payout?",
         "$10. Payments processed every Tuesday."),
        ("Can my account be banned?",
         "Yes. Low accuracy, AI tools usage, or guideline violations = immediate ban with no warning."),
        ("Is it worth it for Nigerians?",
         "Worth trying if you have the right skills. Don't rely on it as sole income. Combine with other platforms."),
        ("Outlier vs Remotasks?",
         "Both Scale AI. Outlier pays more ($15-100/hr vs $1-5/task) but harder to get in. Remotasks better for beginners."),
    ]
    for q, a in faqs:
        story.append(Paragraph(f"<b>Q: {q}</b>", styles['SubHead']))
        story.append(Paragraph(f"A: {a}", styles['BodyText2']))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Sources: 13 X/Twitter posts + 8 web sources (Outlier official blog, RemoWork, TechFixAI, "
        "Dollarbreak, AdsPower, Glassdoor, Techpoint Africa, AI Training Jobs). "
        "Compiled April 2026.",
        styles['BodyText2']
    ))

    doc.build(story)
    print(f"PDF saved to: {OUT_PATH}")

if __name__ == '__main__':
    build_pdf()
