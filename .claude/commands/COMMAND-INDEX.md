# ContentBrain Command Index

62 commands. 6 groups. One reference.

---

## DAILY — Content Production Pipeline

Run in this order: concept → ghostwriter/video-editor/graphic-designer → approve → publish → post
Or run `/produce` to execute the entire pipeline autonomously.

| Command | What It Does | Trigger |
|---|---|---|
| `/concept` | Turn a topic into 3 creative concepts with visual worlds, hook maps, and CONCEPT_LOCK handoff | `concept for [topic]`, called before ghostwriter/video-editor |
| `/ghostwriter` | Write tweets, threads, LinkedIn posts, TikTok scripts, video scripts in @big_quiv's voice | `write me a tweet`, `script for [topic]`, receives CONCEPT_LOCK |
| `/video-editor` | Full video pipeline: script → art direction → storyboard → AI visuals → voiceover → Remotion assembly | `produce a video about [topic]`, `full video pipeline`, receives CONCEPT_LOCK |
| `/graphic-designer` | Design carousels, thumbnails, social graphics with AI backgrounds and Pillow compositing | `design a carousel`, `make the slides`, receives CONCEPT_LOCK |
| `/approve` | Scan 06-Drafts/ for drafts, present for review, mark approved, auto-run /publish | `approve drafts`, `review drafts` |
| `/publish` | Push approved drafts to Notion Content Calendar with properties and media uploads | `publish`, `push to notion`, called by /approve |
| `/post` | Route content from Notion to platforms (Typefully for X/LinkedIn, Buffer for TikTok/IG, Telegram Bot) | `post`, `send to typefully`, `post now` |
| `/publish-update` | Update post status in Notion and log engagement metrics after posting | `I posted this`, `log engagement` |
| `/publish-status` | Check what's scheduled, posted, or missed in Notion Content Calendar | `publish status`, `what's scheduled` |
| `/manychat-dm` | Set up ManyChat DM automation for Instagram posts with keyword triggers | `set up manychat`, `create dm automation` |
| `/market-report` | Pull Binance/CoinGecko/DefiLlama data, generate daily market overview for content pipeline | `market report`, `morning report`, `daily report` |
| `/produce` | **Autonomous pipeline:** calendar → learn → concept → produce → approve → publish → post → log | `/produce`, `/produce today`, `/produce [date]`, `run the pipeline` |

---

## WEEKLY — Maintenance & Planning

Run Monday morning: score-hooks → learn → data-analyst → content-strategist
Or run `/monday` to execute the entire weekly review autonomously.

| Command | What It Does | Trigger |
|---|---|---|
| `/content-strategist` | Plan weekly content calendar, generate briefs, scout trends, align with monetization goals | `plan my content this week`, `what should I post about`, `trend scout` |
| `/score-hooks` | Scrape recent posts, match to hooks in index, score by engagement, update hook-index tiers | `score hooks`, run weekly Monday |
| `/learn` | Scan all modified vault files, extract hooks/structures/styles, score and file into all 4 indexes | `/learn`, `update indexes`, replaces /index-new-data |
| `/data-analyst` | Analyze content performance, generate weekly/monthly reports, track funnel conversion | `analyze my content performance`, `weekly analytics`, `monthly report` |
| `/operations-lead` | Turn ideas into tasks, track execution, manage priorities, generate daily/weekly reports | `what should I focus on today`, `plan my week`, `weekly report` |
| `/scrape-instagram` | Scrape posts from any platform (IG, X, TikTok, YouTube, LinkedIn, Reddit, etc.) via Apify | `scrape @username`, `research [topic] videos`, `study 50 videos about [topic]` |
| `/analyze-videos` | Download videos, extract frames, frame-by-frame visual analysis, extract techniques, update all indexes | `/analyze-videos` then paste URLs, `analyze these videos`, `study these reels` |
| `/research` | Deep topic research from links + web search → markdown doc + PDF guide + PPTX presentation | `/research [topic]`, paste links, `deep dive on [topic]` |
| `/index-new-data` | (DEPRECATED — use /learn) Ingest vault data into indexes | `index new data` |
| `/monday` | **Autonomous weekly review:** score-hooks → learn → data-analyst → content-strategist | `/monday`, `weekly review`, `start the week` |

---

## TRADING — Signal Production Pipeline

Run in this order: scan-all → technical-analyst → send-signals → signal-tracker
Or run `/produce-signals` to execute the entire signal pipeline autonomously.

| Command | What It Does | Trigger |
|---|---|---|
| `/scan-all` | Run full crypto TA scan on all watchlist pairs across 1h/4h/1d, generate binance_ta_summary.json | `/scan-all`, `run full scan` |
| `/scan-pair` | Scan a single crypto pair across all timeframes | `/scan-pair BTCUSDT`, `scan BTC` |
| `/scan-custom` | Scan a crypto pair on specific timeframes only | `/scan-custom ETHUSDT 1h,4h` |
| `/forex-scan` | Run full forex TA scan on all 8 pairs across all timeframes, generate forex_ta_summary.json | `/forex-scan`, `scan forex` |
| `/forex-pair` | Scan a single forex pair across all timeframes | `/forex-pair EUR/USD`, `scan GBP/JPY` |
| `/forex-custom` | Scan a forex pair on specific timeframes only | `/forex-custom EUR/USD 1h,4h` |
| `/technical-analyst` | Read pre-computed TA JSON, identify high-confluence setups, generate signals | `scan for setups`, `find me a trade`, `analyze BTC/USDT` |
| `/send-signals` | Send qualifying signals (3+ confluences) to Telegram approval channel | `/send-signals`, `send signals for approval` |
| `/send-signals-direct` | Send signals directly to Hustler's Krib + X draft, skip approval | `/send-signals-direct`, `distribute signals now` |
| `/signal-tracker` | Log signals, monitor SL/TP hits via Binance, calculate win rate, generate performance reports | `show performance`, `what's my win rate`, `monthly report` |
| `/produce-signals` | **Autonomous pipeline:** drawdown check → scan → analyze → send to approval → log | `/produce-signals`, `run signal pipeline`, `trading pipeline` |

---

## BUSINESS — Standalone Marketing & Sales Tools

| Command | What It Does | Trigger |
|---|---|---|
| `/ad-creative` | Generate ad creative variations (headlines, descriptions, primary text) for any paid platform | `generate ad creative`, `ad variations for [platform]` |
| `/ai-seo` | Optimize content for AI search engines (ChatGPT, Perplexity, Google AI Overviews) | `AI SEO`, `get cited by ChatGPT`, `answer engine optimization` |
| `/cold-email` | Write B2B cold emails and follow-up sequences that get replies | `write cold email`, `cold outreach`, `prospecting email` |
| `/community-manager` | Write Telegram/Discord announcements, welcome messages, engagement prompts, FAQ banks | `write a Telegram announcement`, `create community rules` |
| `/competitor-alternatives` | Create competitor comparison and alternative pages for SEO and sales | `[Product] vs [Product]`, `alternative page`, `comparison page` |
| `/copy-editing` | Edit, review, and improve existing marketing copy via Seven Sweeps Framework | `edit this copy`, `review my copy`, `proofread`, `make this better` |
| `/funnel-builder` | Design conversion funnels, landing pages, email sequences, lead magnets, Telegram funnels | `build a funnel`, `write a landing page`, `create email sequence` |
| `/launch-strategy` | Plan product launch, feature release, or go-to-market strategy | `plan a launch`, `Product Hunt`, `go-to-market`, `beta launch` |
| `/marketing-ideas` | Access 139 proven marketing ideas, get 3-5 most relevant for your product/stage | `marketing ideas`, `growth ideas`, `ways to promote` |
| `/marketing-psychology` | Apply cognitive biases and behavioral science to marketing decisions | `psychology in marketing`, `mental models`, `why people buy` |
| `/paid-ads` | Create and optimize paid ad campaigns on Google, Meta, LinkedIn, X | `PPC`, `paid media`, `ROAS`, `ad campaign`, `retargeting` |
| `/pricing-strategy` | Design SaaS pricing, packaging, and monetization strategy | `pricing tiers`, `freemium`, `price increase`, `value metric` |
| `/product-marketing-context` | Create or update foundational positioning and messaging document | `product context`, `positioning`, `ICP`, `target audience` |
| `/referral-program` | Create referral, affiliate, or ambassador programs | `referral program`, `affiliate`, `viral loop`, `refer a friend` |
| `/revops` | Design revenue operations connecting marketing, sales, and CS | `RevOps`, `lead scoring`, `pipeline stages`, `MQL`, `SQL` |
| `/sales-closer` | Write DM scripts, objection handling, brand deal pitches, follow-up sequences | `write a DM script`, `handle the objection`, `pitch to [brand]` |
| `/free-tool-strategy` | Plan and build free tools for lead generation and SEO | `free tool strategy`, `engineering as marketing`, `calculator` |

---

## WEBSITE/CRO — SaaS Optimization Tools

| Command | What It Does | Trigger |
|---|---|---|
| `/ab-test-setup` | Design statistically valid A/B tests with proper hypothesis and measurement | `plan A/B test`, `design experiment`, `multivariate test` |
| `/analytics-tracking` | Set up or audit GA4, GTM, conversion tracking, event tracking, UTM parameters | `set up tracking`, `GA4 implementation`, `event tracking` |
| `/form-cro` | Optimize any form (lead capture, contact, demo, checkout) for maximum completion | `form optimization`, `checkout form`, `lead capture form` |
| `/onboarding-cro` | Optimize post-signup onboarding, activation, and time-to-value | `onboarding flow`, `activation rate`, `first-run experience` |
| `/page-cro` | Analyze marketing pages and provide conversion rate optimization recommendations | `CRO`, `improve this page`, `landing page optimization` |
| `/paywall-upgrade-cro` | Optimize in-app paywalls, upgrade screens, and feature gates | `paywall optimization`, `upsell modal`, `convert free to paid` |
| `/popup-cro` | Optimize popups, modals, slide-ins, and banners for conversion | `popup optimization`, `exit intent popup`, `email popup` |
| `/programmatic-seo` | Build SEO-optimized pages at scale using templates and data | `programmatic SEO`, `template pages`, `[keyword] + [city] pages` |
| `/schema-markup` | Implement schema.org structured data and JSON-LD for rich search results | `schema markup`, `structured data`, `JSON-LD`, `FAQ schema` |
| `/seo-audit` | Audit and diagnose SEO issues, provide actionable fix recommendations | `SEO audit`, `why am I not ranking`, `my traffic dropped` |
| `/signup-flow-cro` | Optimize signup, registration, and trial activation flows | `signup conversions`, `registration friction`, `reduce signup dropoff` |
| `/site-architecture` | Plan website page hierarchy, navigation, URL patterns, internal linking | `sitemap`, `site structure`, `information architecture` |

---

## UTILITY — Support Commands

| Command | What It Does | Trigger |
|---|---|---|
| `/learn` | Scan vault, extract content elements, update all 4 indexes (replaces /index-new-data) | `/learn`, `update indexes`, `refresh indexes` |
| `/approve` | Gate between drafting and publishing, reviews all pending drafts | `approve drafts`, called after ghostwriter/video-editor |
| `/publish` | Bridge between local drafts and Notion Content Calendar | `publish`, called by /approve |
| `/publish-status` | Read-only status check on Notion Content Calendar | `what's scheduled`, `what did I miss` |
| `/publish-update` | Post-publishing status and engagement logging | `I posted this`, `log engagement` |
| `/index-new-data` | (DEPRECATED) Replaced by /learn | `index new data` |

---

## Quick Reference: Pipeline Sequences

**Daily Content:** `/produce` (autonomous) or `/concept` → `/ghostwriter` or `/video-editor` or `/graphic-designer` → `/approve` → `/publish` → `/post`

**Daily Trading:** `/produce-signals` (autonomous) or `/scan-all` → `/technical-analyst` → `/send-signals` → `/signal-tracker`

**Weekly Monday:** `/monday` (autonomous) or `/score-hooks` → `/learn` → `/data-analyst` → `/content-strategist`

**Weekly Friday:** `/data-analyst` (weekly report)

**Monthly 1st:** `/data-analyst` (monthly report) → `/signal-tracker` (monthly report)

---

*62 commands. Last updated: 2026-04-01.*
