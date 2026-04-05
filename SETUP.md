# ContentBrain Setup

---

## 1. Required API Keys (.env Template)

```env
# === Content Distribution ===
TYPEFULLY_API_KEY=typ_xxxxxxxxxxxx          # X/Twitter + LinkedIn posting via /post
BUFFER_ACCESS_TOKEN=1/xxxxxxxxxxxxxxxx      # TikTok + Instagram posting via /post
BUFFER_TIKTOK_PROFILE_ID=xxxxxxxxxxxxxxxx   # Buffer profile ID for TikTok
BUFFER_INSTAGRAM_PROFILE_ID=xxxxxxxxxxxxxxxx # Buffer profile ID for Instagram

# === Telegram Bot ===
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjklmnoPQRstuvWXYZ  # Bot API token
TELEGRAM_CHAT_ID=-100xxxxxxxxxx             # Hustler's Krib group chat ID
TELEGRAM_POLY_CHANNEL_ID=-100xxxxxxxxxx     # Polymarket signals channel
TELEGRAM_APPROVAL_CHANNEL_ID=-100xxxxxxxxxx # Private signal approval channel
TELEGRAM_ADMIN_CHAT_ID=xxxxxxxxxx           # Personal admin DM chat ID
TELEGRAM_TEST_CHANNEL_ID=-100xxxxxxxxxx     # Signal testing/paper trading group

# === Image & Video Generation ===
FAL_KEY=fal_xxxxxxxxxxxx                    # fal.ai / Nano Banana image generation
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxx         # Google Gemini Flash image generation
PEXELS_API_KEY=xxxxxxxxxxxxxxxx             # Pexels stock photo references

# === Voice Generation ===
MINIMAX_API_KEY=xxxxxxxxxxxxxxxx            # MiniMax speech synthesis (primary voice)
MINIMAX_GROUP_ID=xxxxxxxxxxxxxxxx           # MiniMax group ID

# === Trading & Market Data ===
BINANCE_API_KEY=xxxxxxxxxxxxxxxx            # Binance spot + futures data
BINANCE_SECRET_KEY=xxxxxxxxxxxxxxxx         # Binance API secret
COINGECKO_API_KEY=CG-xxxxxxxxxxxx           # CoinGecko market data
TWELVEDATA_API_KEY=xxxxxxxxxxxxxxxx         # Twelve Data forex/crypto data

# === Web Scraping ===
APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxx    # Apify scraping (Instagram, X, TikTok, etc.)

# === Instagram Direct ===
IG_USER_ID=xxxxxxxxxxxxxxxx                 # Instagram business account user ID
IG_ACCESS_TOKEN=xxxxxxxxxxxxxxxx            # Instagram Graph API access token

# === ManyChat Automation ===
MANYCHAT_EMAIL=you@example.com              # ManyChat login
MANYCHAT_PASSWORD=xxxxxxxxxxxxxxxx          # ManyChat password

# === Database ===
SUPABASE_URL=https://xxxxxxxx.supabase.co   # Supabase project URL
SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxx       # Supabase anon/public key
SUPABASE_KEY=eyJxxxxxxxxxxxxxxxx            # Supabase service role key (scanner)

# === AI ===
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx   # Claude API (vision/analysis)

# === Bot Configuration ===
BOT_MODE=full                               # full | approvals | learning
ENABLE_CRON=true                            # Enable scheduled scanning
AUTO_SIGNAL_CAP=3                           # Max auto signals per day
TA_SCAN_INTERVAL_HOURS=2                    # Hours between TA scans
LEARNING_ENABLED=true                       # Adaptive learning toggle
LEARNING_CHAT_IDS=                          # Comma-separated chat IDs for learning

# === On-Chain Analytics ===
ETHERSCAN_API_KEY=xxxxxxxxxxxxxxxx          # Etherscan on-chain queries (/data-analyst)
```

---

## 2. Required Python Packages (requirements.txt)

```txt
anthropic
fal-client
google-genai
numpy
pandas
Pillow
playwright
python-binance
python-docx
python-dotenv
reportlab
requests
schedule
supabase
ta
urllib3
```

Post-install:
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 3. Notion Database Schemas

### Content Calendar

- **Database ID:** `f405e62cf2804e6a8c217ebd2f8f4210`
- **Data Source ID:** `collection://9081ce06-1802-4b43-a988-62c5e384fcfd`

| Property | Type | Values |
|---|---|---|
| Title | title | Content topic/heading |
| Status | select | Draft, Approved, Scheduled, Posted, Missed |
| Platform | select | X/Twitter, LinkedIn, TikTok, Instagram, YouTube, Telegram |
| Content Type | select | Tweet, Thread, LinkedIn Post, TikTok Script, Reel Script, Carousel, Video - Shoot Myself, Video - AI Generated, Video - Hybrid, Promo, DM Script, Community Post |
| Priority | select | Urgent, High, Normal, Low |
| Goal | select | Sales, Reach, Leads, Authority, Community |
| Post Date | date | ISO-8601 (with time, is_datetime=1) |
| Deadline | date | ISO-8601 |
| Content | text | Full post/script text |
| Hook Used | text | Hook formula reference (H-XXX) |
| Monetization | checkbox | true/false |
| Production Status | select | Script Ready, Recording Needed, Recorded, Editing, AI Assets Needed, Review, Ready to Post |
| Recurring | select | Daily, Weekly, Bi-Weekly, Monthly, One-Time |
| Source Skill | select | Ghostwriter, Content Strategist, Video Editor, Funnel Builder, Community Manager, Sales Closer, Market Report, Signal Tracker |
| Engagement Rate | number | Numeric score |
| Notes | text | Cross-posting instructions, CTA notes, media paths |

**Read by:** concept, content-strategist, ghostwriter, graphic-designer, market-report, operations-lead, post, publish, publish-status, publish-update, sales-closer, signal-tracker, video-editor

**Written by:** publish (only skill that writes to Notion)

### Tasks Database

- **Database ID:** `244f20560a254f278bf2842b96b5c979`
- **Data Source ID:** `collection://4451f489-f22e-4bc8-b497-695c195563de`

| Property | Type | Values |
|---|---|---|
| Task name | title | Action-oriented task title |
| Status | status | Not Started, In Progress, Done, Archived |
| Priority | select | Low, Medium, High |
| Due | date | ISO-8601 |
| Summary | text | Deliverable, time estimate, category |
| Tags | multi_select | Mobile, Website, Improvement, etc. |
| Project | relation | Links to Projects database |
| Sub-tasks | relation | Links to other tasks |
| Parent-task | relation | Links to parent task |
| Assignee | person | Team member |

**Read/Written by:** operations-lead

---

## 4. Bot Configurations

### Telegram Bot (polymarket_bot.py)

| Config | .env Variable | Purpose |
|---|---|---|
| Bot Token | `TELEGRAM_BOT_TOKEN` | Bot API authentication |
| Hustler's Krib | `TELEGRAM_CHAT_ID` | Public signal distribution |
| Poly Channel | `TELEGRAM_POLY_CHANNEL_ID` | Polymarket signals |
| Approval Channel | `TELEGRAM_APPROVAL_CHANNEL_ID` | Private signal review |
| Admin DM | `TELEGRAM_ADMIN_CHAT_ID` | Personal admin interface |
| Test Channel | `TELEGRAM_TEST_CHANNEL_ID` | Paper trading group |

**Referenced by:** post.md, send-signals.md, send-signals-direct.md, community-manager.md, technical-analyst.md

### Typefully Social Sets

| Social Set ID | Platform | Account |
|---|---|---|
| 61071 | X/Twitter | @_Quivira |
| 292564 | LinkedIn | bigquiv |

Discovered via: `GET https://api.typefully.com/v2/social-sets` with Bearer token.

### Buffer Profile IDs

Run once to discover:
```bash
curl -H "Authorization: Bearer $BUFFER_ACCESS_TOKEN" https://api.bufferapp.com/1/profiles.json
```
Save to `.env` as `BUFFER_TIKTOK_PROFILE_ID` and `BUFFER_INSTAGRAM_PROFILE_ID`.

---

## 5. Required Local Tools

| Tool | Install | Used By |
|---|---|---|
| Python 3.10+ | `winget install Python.Python.3.12` | All scripts |
| Node.js 18+ | `winget install OpenJS.NodeJS.LTS` | Remotion video assembly |
| Remotion | `npm install -g @remotion/cli` | /video-editor (assembly) |
| yt-dlp | `pip install yt-dlp` | /ghostwriter, /concept, /content-strategist (YouTube transcripts) |
| ffmpeg | `winget install Gyan.FFmpeg` | Video/audio processing |
| Playwright browsers | `playwright install chromium` | ManyChat automation scripts |
| Pillow | included in requirements.txt | /graphic-designer (image compositing) |

---

## 6. First-Run Checklist

```
1. Clone repo, cd into contentbrain/
2. Copy .env.template to .env, fill all API keys
3. pip install -r requirements.txt
4. playwright install chromium
5. npm install -g @remotion/cli
6. Verify Notion databases exist with correct schemas (Section 3)
7. Run: curl -H "Authorization: Bearer $TYPEFULLY_API_KEY" https://api.typefully.com/v2/social-sets
   → Save social set IDs
8. Run: curl -H "Authorization: Bearer $BUFFER_ACCESS_TOKEN" https://api.bufferapp.com/1/profiles.json
   → Save profile IDs to .env
9. Verify Telegram bot responds: curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
10. Create vault folders if missing: 01-Competitors/ 02-Hooks/ 03-Trends/ 04-Patterns/ 05-Frameworks/ 06-Drafts/ 07-Analytics/ 08-Templates/ 08-Media/ 09-Skills/ 10-Niche-Knowledge/ 11-Presentations/
11. Verify indexes exist:
    - 02-Hooks/hook-index.md
    - 02-Hooks/visual-hook-index.md
    - 05-Frameworks/psychological-structure-index.md
    - 08-Templates/talking-head-style-index.md
    If missing, run: /index-new-data
12. Run /content-strategist to generate first weekly plan
13. Run /scan-all to verify Binance TA pipeline works
14. Run /market-report to verify market data pipeline works
```

---

## 7. Weekly Routine

| Day | Time (WAT) | Command | Purpose |
|---|---|---|---|
| Monday | 7:00 AM | `/content-strategist` | Plan the week's content |
| Monday | 9:00 AM | `/score-hooks` | Score last week's hooks, update tiers |
| Monday | 11:00 AM | `/operations-lead` (weekly report) | Task completion rates, priorities |
| Friday | 2:00 PM | `/data-analyst` (weekly) | Content performance analysis |
| 1st of month | 8:00 AM | `/data-analyst` (monthly) | 30-day deep dive |

---

## 8. Daily Routine

```
Morning (6-8 AM WAT):
  1. /market-report              → Daily market overview + setups
  2. /scan-all                   → Full crypto TA scan
  3. /send-signals               → Send qualifying signals to approval channel

Content Production (9 AM - 12 PM WAT):
  4. /concept [topic]            → 3 creative concepts → pick one → CONCEPT_LOCK
  5. /ghostwriter [brief]        → Draft text content → saves to 06-Drafts/
  6. /video-editor [brief]       → Full video pipeline → saves to 06-Drafts/
  7. /graphic-designer [brief]   → Carousel/graphics → saves to 06-Drafts/

Review & Publish (12-1 PM WAT):
  8. /approve                    → Review all drafts → mark approved
  9. /publish                    → Push approved drafts to Notion (auto after /approve)
 10. /post                       → Send from Notion to platforms

Post-Publishing:
 11. /publish-update             → Log engagement after posting
 12. /publish-status             → Check what's scheduled, what was missed
```

### Posting Schedule (12 posts/day)

| Time (WAT) | Platform | Content Type |
|---|---|---|
| 7:00 AM | TikTok | Morning hook/value |
| 8:00 AM | X/Twitter | Tweet |
| 9:00 AM | LinkedIn | Professional post |
| 10:00 AM | Instagram | Reel or carousel |
| 12:00 PM | TikTok | Midday content |
| 1:00 PM | Telegram | Community update |
| 3:00 PM | X/Twitter | Thread or tweet |
| 4:00 PM | TikTok | Afternoon content |
| 5:00 PM | LinkedIn | Engagement post |
| 6:00 PM | Instagram | Story or post |
| 8:00 PM | TikTok | Evening content |
| 9:00 PM | Telegram | Alpha/signal update |
