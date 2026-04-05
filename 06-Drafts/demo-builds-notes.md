---
title: Demo Builds Notes (PDF Companion)
date: 2026-04-04
source: companion to demo-builds.pdf (5 pages, Phase 7b)
topic: 3 proof-of-concept live class demo builds for Quivira AI Course
content_type_audit: Completed 2026-04-04
---

# Demo Builds — PDF Companion Notes

> **Content Type Audit:** Demo builds are **OPERATIONAL REFERENCE** — internal live class build plans. Repurposed as content:
> - "Watch me build this" posts = VALUE (Demo) — body teaches the build process
> - "I built [X] live with students" post-class = PERSONALITY hook → VALUE body
> - "Build this in the course" CTA = PROMO tail
>
> **Rule:** Never post a demo build description without showing the actual steps. If the body is "join the course to see this" only → that is PROMO. If the body walks through the steps → VALUE.

---

## The 3 Demo Builds

### Demo 1 — AI Trading Journal Analyser
**Income stream:** AI-Assisted Freelancing + Consulting
**Course topic:** AI Automation — Developer Track (M1–M3)
**Live class date:** Week 2, April 15

**What gets built:**
Web app → CSV upload → Claude API behavioural analysis → structured report (worst habit, best setup, emotional patterns, personalised rules). Deployable in under 90 minutes.

**Tools required:**
- Claude API
- Python (FastAPI or Flask)
- Simple HTML frontend
- Supabase (optional — for storing analysis history)
- Railway (deployment)

**Build steps (post-ready — VALUE format):**
1. HTML form with CSV file upload button
2. Python backend receives CSV, parses with pandas, converts to readable table string
3. Sends to Claude API: "You are a trading coach. Analyse these trades. Return: (1) Worst habit, (2) Best performing setup, (3) Time-of-day patterns, (4) 5 personalised rules."
4. Claude returns structured response
5. Frontend renders clean report
6. Deploy to Railway — runs permanently at public URL

**Market proof (cite in content):** Freelancers charge $300–$500 for custom trading analytics dashboards. This replicates that in an open afternoon.

**Content type labels:**
| Post angle | Content Type |
|-----------|-------------|
| "Here's how to build an AI trading journal analyser in 90 minutes" | VALUE (tutorial) |
| "I built a trading coach app live with students last Tuesday" | PERSONALITY hook → VALUE body |
| "Students are building this in the course. You can too." | PROMO |

---

### Demo 2 — Voice Note → Social Post Pipeline (No-Code)
**Income stream:** AI-Assisted Freelancing + Automation Services
**Course topic:** AI Automation — Creator Track (M2) + Beginner Track (M4)
**Live class date:** Week 1, April 8

**What gets built:**
Make.com automation → records voice note → Whisper API transcribes → Claude generates platform-specific posts → pushes drafts to Typefully. No code. No developer.

**Tools required:**
- Make.com (free tier)
- OpenAI Whisper API (or AssemblyAI free tier)
- Claude API
- Typefully API

**Build steps (post-ready — VALUE format):**
1. Make.com: new scenario
2. Trigger: "Watch for new files in Google Drive folder" (drop voice note here)
3. HTTP request to Whisper API → returns transcript
4. HTTP request to Claude: "Transform this transcript into: (a) one tweet, (b) one LinkedIn post, (c) one TikTok script. Match this tone: [paste 3 examples]."
5. Typefully API → create draft with each output
6. Build time: 45–90 minutes for non-technical students

**Market proof:** Content automation agencies charge $500–$2,000 to set up this workflow for clients. Students learn to build and sell it.

**Content type labels:**
| Post angle | Content Type |
|-----------|-------------|
| "Turn any voice note into 3 social posts automatically — here's the Make.com workflow" | VALUE (tutorial) |
| "No code. No developer. A voice note becomes a tweet, LinkedIn post, and TikTok script in 4 minutes." | HOT TAKE opener → VALUE body |

---

### Demo 3 — AI Crypto Signal Scanner (Claude + Binance API)
**Income stream:** AI Automation Services + Consulting
**Course topic:** AI Automation — Developer Track (M4)
**Live class date:** Week 2, April 15/17

**What gets built:**
Python agent → Binance API OHLCV data → Claude TA interpretation → filters high-confluence setups → sends qualifying signals to Telegram. Simplified Trigon Labs system. Demo-able live in class.

**Tools required:**
- Python
- Binance API (read-only — no trading keys required)
- Claude API
- Telegram Bot API
- Railway (deployment + cron)

**Build steps (post-ready — VALUE format):**
1. Fetch OHLCV data for 5 pairs from Binance API (free, no auth)
2. Calculate RSI, MACD, EMA using ta-lib or pandas_ta
3. Send to Claude: "Given these indicators for [PAIR], identify if there is a high-confluence setup. If yes: direction, confluence factors, entry zone, risk level."
4. Parse Claude response — if "yes" → format signal message
5. Send to Telegram channel via Bot API
6. Schedule via Railway cron: runs every 4 hours

**Content type labels:**
| Post angle | Content Type |
|-----------|-------------|
| "How to build an AI crypto signal scanner using Claude + Binance API" | VALUE (tutorial) |
| "This is a simplified version of the system I run live — Trigon Labs. Here's how to build your own." | PERSONALITY hook → VALUE body |
| "Students are building a live crypto signal bot in the course. Join." | PROMO |

---

## Notes on PDF Regeneration

If this PDF is regenerated, update:
- [ ] Add content type labels to each demo section header
- [ ] Confirm live class dates align with the final delivery schedule
- [ ] Demo 2: verify AssemblyAI free tier is still available as Whisper alternative
- [ ] Demo 3: update if Binance API access requirements changed (currently read-only, no auth)
- [ ] Add "No hashtags on X/Twitter" to any platform-specific copy guidelines
- [ ] Confirm Railway free tier availability for student deployments (pricing changed Feb 2026)
