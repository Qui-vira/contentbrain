import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import { hash } from "bcryptjs";
import * as schema from "./schema";

async function seed() {
  const client = createClient({
    url: process.env.TURSO_DATABASE_URL!,
    authToken: process.env.TURSO_AUTH_TOKEN,
  });
  const db = drizzle(client, { schema });

  console.log("Seeding database...");

  // ─── Admin user ───
  const passwordHash = await hash("admin123", 12);
  await db.insert(schema.adminUsers).values({
    username: "admin",
    passwordHash,
  });
  console.log("✓ Admin user created (username: admin, password: admin123)");

  // ─── Settings ───
  await db.insert(schema.settings).values([
    { key: "calendly_url", value: "https://calendly.com/_quivira/one-on-one-meeting" },
    { key: "calendly_free_url", value: "https://calendly.com/_quivira/one-on-one-meeting" },
    { key: "email", value: "contact@bigquivdigitals.com" },
    { key: "telegram_handle", value: "@Quivira_Ophir" },
    { key: "telegram_url", value: "https://t.me/Quivira_Ophir" },
    { key: "formsubmit_email", value: "contact@bigquivdigitals.com" },
    { key: "hero_tagline", value: "The Future of Web3 Content and Trading" },
    { key: "hero_subtitle", value: "Automated trading signals. AI content intelligence. Real education that produces builders. One brand. Zero noise." },
  ]);
  console.log("✓ Settings seeded");

  // ─── Social links ───
  await db.insert(schema.socialLinks).values([
    { name: "X (Twitter)", href: "https://x.com/_Quivira", sortOrder: 0 },
    { name: "LinkedIn", href: "https://linkedin.com/in/bigquiv", sortOrder: 1 },
    { name: "TikTok", href: "https://tiktok.com/@big_quiv", sortOrder: 2 },
    { name: "Instagram", href: "https://instagram.com/big_quiv", sortOrder: 3 },
    { name: "YouTube", href: "https://youtube.com/@big_quiv", sortOrder: 4 },
    { name: "Telegram", href: "https://t.me/Quivira_Ophir", sortOrder: 5 },
  ]);
  console.log("✓ Social links seeded");

  // ─── Stats ───
  await db.insert(schema.stats).values([
    // Home trust bar
    { page: "home_trust", label: "Community Members", value: 500, suffix: "+", sortOrder: 0 },
    { page: "home_trust", label: "Pairs Scanned Daily", value: 20, suffix: "+", sortOrder: 1 },
    { page: "home_trust", label: "Platforms", value: 6, suffix: "", sortOrder: 2 },
    { page: "home_trust", label: "Signal Win Rate", value: 85, suffix: "%+", sortOrder: 3 },
    // Home results section
    { page: "home_results", label: "Community Members", value: 500, suffix: "+", sortOrder: 0 },
    { page: "home_results", label: "Signal Win Rate", value: 85, suffix: "%+", sortOrder: 1 },
    { page: "home_results", label: "Pairs Tracked", value: 20, suffix: "+", sortOrder: 2 },
    { page: "home_results", label: "AI Products Live", value: 3, suffix: "", sortOrder: 3 },
  ]);
  console.log("✓ Stats seeded");

  // ─── Services ───
  await db.insert(schema.services).values([
    // Consulting
    { category: "consulting", title: "Brand Visibility & Content Strategy", description: "Full content strategy tailored to your niche. Platform audits, hook frameworks, content calendars, and growth playbooks that turn attention into authority.", icon: "Eye", sortOrder: 0 },
    { category: "consulting", title: "Community Management", description: "Discord and Telegram setup, moderation systems, engagement frameworks, and retention strategies. Build a community that actually stays.", icon: "Users", sortOrder: 1 },
    { category: "consulting", title: "Strategic Partnerships & KOL Networking", description: "Introductions, deal structuring, and negotiation support. Connect with the right KOLs, projects, and partners to amplify your reach.", icon: "Handshake", sortOrder: 2 },
    { category: "consulting", title: "Launch & Campaign Management", description: "Token launches, product releases, NFT drops, and marketing campaigns. End-to-end execution from pre-launch hype to post-launch retention.", icon: "Rocket", sortOrder: 3 },
    { category: "consulting", title: "1-on-1 Strategy Calls", description: "60-minute deep dive into your brand, content, trading, or business strategy. Walk away with a clear action plan.", icon: "Phone", price: "$250/session", ctaText: "Book a Strategy Call", ctaHref: "calendly", sortOrder: 4 },
    // Education
    { category: "education", title: "Crypto Builders Circle", description: "Private community with weekly calls, market breakdowns, airdrop alerts, and direct access to Quivira. Built for serious builders.", icon: "BookOpen", price: "$97/mo", priceDetail: "$497 lifetime", sortOrder: 0 },
    { category: "education", title: "Ophir Dev Accelerator", description: "8-week cohort-based program. Go from zero to deploying smart contracts, building dApps, and understanding Web3 architecture.", icon: "Code", price: "$1,200", priceDetail: "per cohort", sortOrder: 1 },
    { category: "education", title: "Airdrop Mastery Playbook", description: "Step-by-step system for finding, qualifying, and farming airdrops. Includes wallet management, on-chain activity templates, and tracking sheets.", icon: "Crosshair", price: "$149", sortOrder: 2 },
    { category: "education", title: "KOL Accelerator", description: "Build your personal brand as a crypto KOL. Content strategy, deal negotiation, audience growth, and monetization frameworks.", icon: "Crown", price: "$149", sortOrder: 3 },
    { category: "education", title: "The Trader's Manual", description: "Complete trading education. Technical analysis, risk management, position sizing, and psychology. Spot and perpetual futures covered.", icon: "BarChart3", price: "$147", sortOrder: 4 },
    // AI Products
    { category: "ai_products", title: "SignalOS", description: "Automated crypto and forex trading signals. Technical analysis across 20+ pairs, risk management levels, confluence scoring, and real-time Telegram delivery.", icon: "Zap", price: "$97/mo", ctaText: "Get SignalOS", ctaHref: "calendly", sortOrder: 0 },
    { category: "ai_products", title: "ContentBrain", description: "AI content intelligence engine. Competitor analysis, trend scouting, hook generation, content calendars, and full production pipelines, all automated.", icon: "Cpu", price: "$47/mo", ctaText: "Get ContentBrain", ctaHref: "calendly", sortOrder: 1 },
    { category: "ai_products", title: "Quivira OS Bundle", description: "SignalOS + ContentBrain + priority support + early access to new tools. The full operating system for builders who want everything in one layer.", icon: "Layers", price: "$297/mo", ctaText: "Get the Bundle", ctaHref: "calendly", sortOrder: 2 },
  ]);
  console.log("✓ Services seeded");

  // ─── Personal services (pricing page table) ───
  await db.insert(schema.personalServices).values([
    { name: "1-on-1 Strategy Call", price: "$250", detail: "60-minute session", sortOrder: 0 },
    { name: "Crypto Builders Circle", price: "$97/mo or $497 lifetime", detail: "Private community", sortOrder: 1 },
    { name: "Ophir Dev Accelerator", price: "$1,200", detail: "6-week cohort", sortOrder: 2 },
    { name: "Airdrop Mastery Playbook", price: "$149", detail: "Self-paced course", sortOrder: 3 },
    { name: "KOL Accelerator", price: "$149", detail: "Self-paced course", sortOrder: 4 },
    { name: "The Trader's Manual", price: "$147", detail: "Self-paced course", sortOrder: 5 },
    { name: "Custom Consulting", price: "Contact", detail: "Scoped per project", sortOrder: 6 },
  ]);
  console.log("✓ Personal services seeded");

  // ─── Pricing tiers ───
  await db.insert(schema.pricingTiers).values([
    // SignalOS
    { product: "signalos", productTitle: "SignalOS", productSubtitle: "Automated Trading Signals", tierKey: "starter", tierLabel: "Starter", tierPrice: "$97/mo", sortOrder: 0 },
    { product: "signalos", productTitle: "SignalOS", productSubtitle: "Automated Trading Signals", tierKey: "pro", tierLabel: "Pro", tierPrice: "$197/mo", sortOrder: 1 },
    { product: "signalos", productTitle: "SignalOS", productSubtitle: "Automated Trading Signals", tierKey: "premium", tierLabel: "Premium", tierPrice: "$297/mo", sortOrder: 2 },
    // ContentBrain
    { product: "contentbrain", productTitle: "ContentBrain", productSubtitle: "AI Content Intelligence", tierKey: "starter", tierLabel: "Starter", tierPrice: "$47/mo", sortOrder: 0 },
    { product: "contentbrain", productTitle: "ContentBrain", productSubtitle: "AI Content Intelligence", tierKey: "pro", tierLabel: "Pro", tierPrice: "$97/mo", sortOrder: 1 },
    { product: "contentbrain", productTitle: "ContentBrain", productSubtitle: "AI Content Intelligence", tierKey: "premium", tierLabel: "Premium", tierPrice: "$197/mo", sortOrder: 2 },
    // Quivira OS
    { product: "quivira_os", productTitle: "Quivira OS", productSubtitle: "Full Stack Bundle", tierKey: "starter", tierLabel: "Standard", tierPrice: "$297/mo", sortOrder: 0 },
    { product: "quivira_os", productTitle: "Quivira OS", productSubtitle: "Full Stack Bundle", tierKey: "pro", tierLabel: "Pro", tierPrice: "$397/mo", sortOrder: 1 },
    { product: "quivira_os", productTitle: "Quivira OS", productSubtitle: "Full Stack Bundle", tierKey: "premium", tierLabel: "Agency", tierPrice: "$497/mo", sortOrder: 2 },
  ]);
  console.log("✓ Pricing tiers seeded");

  // ─── Pricing features ───
  await db.insert(schema.pricingFeatures).values([
    // SignalOS features
    { product: "signalos", featureName: "Crypto signals", starter: "true", pro: "true", premium: "true", sortOrder: 0 },
    { product: "signalos", featureName: "Pairs scanned", starter: "10", pro: "20+", premium: "Unlimited", sortOrder: 1 },
    { product: "signalos", featureName: "Scan frequency", starter: "4h", pro: "2h", premium: "1h", sortOrder: 2 },
    { product: "signalos", featureName: "Confluence filtering", starter: "true", pro: "true", premium: "true", sortOrder: 3 },
    { product: "signalos", featureName: "Telegram approval", starter: "false", pro: "true", premium: "true", sortOrder: 4 },
    { product: "signalos", featureName: "Auto-publish", starter: "false", pro: "false", premium: "true", sortOrder: 5 },
    { product: "signalos", featureName: "Priority support", starter: "false", pro: "true", premium: "true", sortOrder: 6 },
    // ContentBrain features
    { product: "contentbrain", featureName: "Platform scraping", starter: "3 platforms", pro: "6 platforms", premium: "9+ platforms", sortOrder: 0 },
    { product: "contentbrain", featureName: "Hook & pattern extraction", starter: "true", pro: "true", premium: "true", sortOrder: 1 },
    { product: "contentbrain", featureName: "AI analysis", starter: "false", pro: "true", premium: "true", sortOrder: 2 },
    { product: "contentbrain", featureName: "Transcript extraction", starter: "false", pro: "true", premium: "true", sortOrder: 3 },
    { product: "contentbrain", featureName: "AI video analysis", starter: "false", pro: "false", premium: "true", sortOrder: 4 },
    { product: "contentbrain", featureName: "Vault distribution", starter: "false", pro: "true", premium: "true", sortOrder: 5 },
    // Quivira OS features
    { product: "quivira_os", featureName: "SignalOS (full)", starter: "true", pro: "true", premium: "true", sortOrder: 0 },
    { product: "quivira_os", featureName: "ContentBrain (full)", starter: "true", pro: "true", premium: "true", sortOrder: 1 },
    { product: "quivira_os", featureName: "Custom pairs & platforms", starter: "false", pro: "true", premium: "true", sortOrder: 2 },
    { product: "quivira_os", featureName: "Priority support", starter: "false", pro: "true", premium: "true", sortOrder: 3 },
    { product: "quivira_os", featureName: "White-label / multi-client", starter: "false", pro: "false", premium: "true", sortOrder: 4 },
  ]);
  console.log("✓ Pricing features seeded");

  // ─── FAQ items ───
  await db.insert(schema.faqItems).values([
    { question: "Can I switch plans later?", answer: "Yes. You can upgrade or downgrade at any time. Changes take effect on your next billing cycle.", sortOrder: 0 },
    { question: "Is there a free trial?", answer: "We offer a 15-minute discovery call so you can see if the product fits before committing. No credit card required to book.", sortOrder: 1 },
    { question: "What payment methods do you accept?", answer: "We accept all major credit cards, crypto payments (USDT, USDC), and bank transfers for annual plans.", sortOrder: 2 },
    { question: "Are there contracts or lock-in periods?", answer: "No. All monthly plans are month-to-month. Cancel anytime with no penalties.", sortOrder: 3 },
    { question: "Do you offer refunds?", answer: "Courses and digital products are non-refundable once accessed. SaaS subscriptions can be cancelled before the next billing cycle.", sortOrder: 4 },
    { question: "What is Quivira OS exactly?", answer: "Quivira OS is a full-stack automation suite that bundles SignalOS (automated trading signals) and ContentBrain (AI content intelligence) into one platform.", sortOrder: 5 },
    { question: "Can I use SignalOS for forex?", answer: "Yes. SignalOS scans both crypto and forex pairs depending on your plan tier.", sortOrder: 6 },
    { question: "How do I get support?", answer: "All paid plans include Telegram-based support. Pro and Premium tiers get priority response times and direct access.", sortOrder: 7 },
  ]);
  console.log("✓ FAQ items seeded");

  // ─── Testimonials ───
  await db.insert(schema.testimonials).values([
    // Home page
    { page: "home", quote: "The signals are insane. I made back my subscription in the first week.", attribution: "Krib Member, Crypto Trader", sortOrder: 0 },
    { page: "home", quote: "Quivira\u2019s content strategy transformed my LinkedIn. 10x engagement in 60 days.", attribution: "Web3 Founder", sortOrder: 1 },
    { page: "home", quote: "The courses are no-fluff. I went from zero to building smart contracts in 8 weeks.", attribution: "Ophir Dev Accelerator Graduate", sortOrder: 2 },
    // Portfolio page
    { page: "portfolio", quote: "The signals alone paid for 3 months of my subscription in the first week. This is the real deal.", attribution: "Krib Member, Crypto Trader", sortOrder: 0 },
    { page: "portfolio", quote: "I went from posting randomly to having a full content system. My engagement tripled in 30 days.", attribution: "Creator, Personal Brand", sortOrder: 1 },
    { page: "portfolio", quote: "Quivira's consulting changed how I think about my entire business model. Clear, sharp, no fluff.", attribution: "Founder, Web3 Startup", sortOrder: 2 },
    { page: "portfolio", quote: "The community alone is worth the price. Builders helping builders \u2014 that energy is rare in crypto.", attribution: "Krib Member, Developer", sortOrder: 3 },
  ]);
  console.log("✓ Testimonials seeded");

  // ─── Case studies ───
  const csData = [
    { title: "Signal Performance", stats: ["85%+ win rate across crypto & forex signals", "20+ pairs scanned every cycle", "Multi-timeframe confluence filtering", "Automated Telegram delivery with approval flow"] },
    { title: "Community Growth", stats: ["500+ active members across Telegram & Discord", "15+ countries represented", "Daily engagement without paid promotion", "Organic referral-driven growth"] },
    { title: "Content Results", stats: ["6 platforms posting consistently", "9 platform intelligence scrapers running", "AI-generated hooks with 2x engagement lift", "Fully automated content pipeline from research to draft"] },
    { title: "Client Outcomes", stats: ["48-hour launch from brief to live product", "Autopilot signal systems running 24/7", "Custom dashboards and Telegram bots deployed", "End-to-end systems, not one-off deliverables"] },
  ];
  for (let i = 0; i < csData.length; i++) {
    const cs = csData[i];
    const [inserted] = await db.insert(schema.caseStudies).values({ title: cs.title, sortOrder: i }).returning();
    for (let j = 0; j < cs.stats.length; j++) {
      await db.insert(schema.caseStudyStats).values({ caseStudyId: inserted.id, stat: cs.stats[j], sortOrder: j });
    }
  }
  console.log("✓ Case studies seeded");

  // ─── About values ───
  await db.insert(schema.aboutValues).values([
    { icon: "Crosshair", title: "Clarity Over Noise", description: "Every signal, every post, every product is built to cut through the noise and give you what actually matters.", sortOrder: 0 },
    { icon: "Hammer", title: "Builder, Not Talker", description: "We ship systems, not promises. Everything is tested, automated, and designed to produce real results.", sortOrder: 1 },
    { icon: "Users", title: "Community Is the Moat", description: "The strongest edge in crypto is the people around you. We build tribes, not audiences.", sortOrder: 2 },
  ]);
  console.log("✓ About values seeded");

  // ─── About ecosystem ───
  await db.insert(schema.aboutEcosystem).values([
    { name: "Quivira", role: "Personal Brand", description: "Authority content across X, LinkedIn, TikTok, Instagram, YouTube, and Facebook.", sortOrder: 0 },
    { name: "Ophir Institute", role: "Education", description: "Structured courses and cohorts for builders, traders, and creators.", sortOrder: 1 },
    { name: "Trigon Labs", role: "AI Signals", description: "Automated trading signal engine scanning crypto and forex markets around the clock.", sortOrder: 2 },
    { name: "Hustler's Krib", role: "Community", description: "Private community of builders, traders, and creators helping each other grow.", sortOrder: 3 },
  ]);
  console.log("✓ About ecosystem seeded");

  // ─── About content ───
  await db.insert(schema.aboutContent).values([
    { key: "hero_title", value: "The person behind the brand." },
    { key: "hero_subtitle", value: "Builder. Trader. Strategist. Helping people earn, grow, and transform with practical execution \u2014 not noise." },
    { key: "story_title", value: "From the Trenches" },
    { key: "story", value: `I didn't start in crypto with a blueprint. No mentor, no connections, no safety net. Just a laptop, an internet connection, and the kind of hunger that only comes from knowing you have no Plan B.

I learned trading by losing money first. I learned content by posting into the void for months. I learned marketing by studying what actually converts \u2014 not what looks good in a course thumbnail.

Over the years, I built systems that replaced the guesswork. Automated signals that scan markets around the clock. AI pipelines that turn raw research into ready-to-post content. Communities that grow themselves because the value is real.

Every product I sell, I use myself. Every strategy I teach, I've tested. The brand isn't built on hype \u2014 it's built on execution.` },
    { key: "mission_title", value: "The Mission" },
    { key: "mission", value: "Make crypto simple, profitable, and relevant for the everyday builder and trader \u2014 while delivering high-value services that actually move the needle. Clarity over noise. Execution over talk. Community over clout." },
  ]);
  console.log("✓ About content seeded");

  // ─── CTA banners ───
  await db.insert(schema.ctaBanners).values([
    { page: "home", headline: "Ready to build?", subtext: "Stop guessing. Start executing. Let\u2019s talk about what you need.", buttonText: "Book a Call", buttonHref: "calendly" },
    { page: "pricing", headline: "Start with what fits. Upgrade when ready.", subtext: "Book a call and we\u2019ll figure out the right plan for you.", buttonText: "Book a Call to Get Started", buttonHref: "/contact" },
    { page: "services", headline: "Not sure which service fits?", subtext: "Book a free 15-minute call and I\u2019ll help you find the right path \u2014 no pressure, no pitch.", buttonText: "Book a Free Call", buttonHref: "calendly_free" },
    { page: "portfolio", headline: "Want results like these?", subtext: "Let\u2019s talk about what you\u2019re building and how I can help.", buttonText: "Book a Call", buttonHref: "/contact" },
  ]);
  console.log("✓ CTA banners seeded");

  // ─── Contact options ───
  await db.insert(schema.contactOptions).values([
    { icon: "MessageCircle", title: "Telegram", description: "DM @Quivira_Ophir", href: "https://t.me/Quivira_Ophir", sortOrder: 0 },
    { icon: "Mail", title: "Email", description: "contact@bigquivdigitals.com", href: "mailto:contact@bigquivdigitals.com", sortOrder: 1 },
    { icon: "Calendar", title: "Book a Call", description: "Schedule a free 15-minute call", href: "https://calendly.com/bigquiv/15min", sortOrder: 2 },
  ]);
  console.log("✓ Contact options seeded");

  // ─── Service options (contact form dropdown) ───
  await db.insert(schema.serviceOptions).values([
    { name: "1-on-1 Strategy Call", sortOrder: 0 },
    { name: "Crypto Builders Circle", sortOrder: 1 },
    { name: "Ophir Dev Accelerator", sortOrder: 2 },
    { name: "SignalOS", sortOrder: 3 },
    { name: "ContentBrain", sortOrder: 4 },
    { name: "Quivira OS Bundle", sortOrder: 5 },
    { name: "Custom Consulting", sortOrder: 6 },
    { name: "Other", sortOrder: 7 },
  ]);
  console.log("✓ Service options seeded");

  // ─── Marquee items ───
  await db.insert(schema.marqueeItems).values([
    // Home
    { page: "home", text: "TRADING SIGNALS", sortOrder: 0 },
    { page: "home", text: "AI CONTENT", sortOrder: 1 },
    { page: "home", text: "WEB3 CONSULTING", sortOrder: 2 },
    { page: "home", text: "COMMUNITY", sortOrder: 3 },
    { page: "home", text: "EDUCATION", sortOrder: 4 },
    { page: "home", text: "AUTOMATION", sortOrder: 5 },
    // Pricing
    { page: "pricing", text: "NO HIDDEN FEES", sortOrder: 0 },
    { page: "pricing", text: "CANCEL ANYTIME", sortOrder: 1 },
    { page: "pricing", text: "CRYPTO PAYMENTS", sortOrder: 2 },
    { page: "pricing", text: "INSTANT ACCESS", sortOrder: 3 },
    { page: "pricing", text: "PRIORITY SUPPORT", sortOrder: 4 },
    // Services
    { page: "services", text: "BRAND STRATEGY", sortOrder: 0 },
    { page: "services", text: "COMMUNITY", sortOrder: 1 },
    { page: "services", text: "PARTNERSHIPS", sortOrder: 2 },
    { page: "services", text: "LAUNCHES", sortOrder: 3 },
    { page: "services", text: "STRATEGY CALLS", sortOrder: 4 },
    // About
    { page: "about", text: "CLARITY OVER NOISE", sortOrder: 0 },
    { page: "about", text: "BUILDER NOT TALKER", sortOrder: 1 },
    { page: "about", text: "COMMUNITY IS THE MOAT", sortOrder: 2 },
    { page: "about", text: "EXECUTION OVER TALK", sortOrder: 3 },
  ]);
  console.log("✓ Marquee items seeded");

  console.log("\n✅ Database seeded successfully!");
  process.exit(0);
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
