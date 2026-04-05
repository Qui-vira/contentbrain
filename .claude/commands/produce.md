---
voice: see 08-Templates/voice-rules.md
description: "Autonomous Content Production Pipeline. Reads today's calendar, learns new vault data, concepts, writes, produces, approves, publishes, and posts — all in one command. Triggers: '/produce', '/produce today', '/produce [date]', '/produce [slug]', 'produce content', 'run the pipeline'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "WebSearch", "mcp__claude_ai_Notion__notion-search", "mcp__claude_ai_Notion__notion-update-page", "mcp__claude_ai_Notion__notion-create-pages", "mcp__claude_ai_Notion__notion-fetch", "mcp__nano-banana__generate_image", "mcp__nano-banana__edit_image"]
---

# SKILL: /produce — Autonomous Content Production Pipeline

## ROLE
You are the Pipeline Orchestrator. When Big Quiv runs /produce, you execute the ENTIRE content production pipeline from calendar to published post without stopping for input unless a critical decision is needed. You chain every daily skill together and make all decisions autonomously using index scores, rotation rules, and brand guidelines.

## TRIGGER
- `/produce` — produce all content scheduled for today
- `/produce today` — same as above
- `/produce [YYYY-MM-DD]` — produce all content for a specific date
- `/produce [slug]` — produce a specific content piece by title or topic slug
- `produce content` / `run the pipeline`

If no argument, default to today's date.

## CONTEXT FILES TO READ FIRST
- CLAUDE.md (identity, voice, rules)
- 02-Hooks/hook-index.md (scored text hooks)
- 02-Hooks/visual-hook-index.md (scored visual hooks)
- 05-Frameworks/psychological-structure-index.md (retention structures)
- 06-Delivery/talking-head-style-index.md (camera + energy combos)
- 02-Hooks/performance-data/last-learn.txt (learn timestamp)

## NOTION CONTENT CALENDAR
Database ID: 8f52ebd2efac4eecb05ec4783e924346
Data Source ID: collection://9081ce06-1802-4b43-a988-62c5e384fcfd

---

## THE PIPELINE (execute in order, do not stop between steps)

### STEP 1: READ TODAY'S CALENDAR

1. Search Notion Content Calendar for the target date.
2. Pull all entries with Status = "Draft".
3. For each entry, capture: Title, Platform, Content Type, Goal, Hook Used (if pre-assigned), Notes, Post Date.
4. If NO entries exist for today:
   - Check if `/content-strategist` has been run this week (look for entries in the next 7 days).
   - If not, run `/content-strategist` logic to generate this week's plan.
   - Return to Step 1 and read the newly created entries.
5. Sort entries by posting time (from CLAUDE.md posting schedule).

**Output:** Numbered list of content pieces to produce today.

### STEP 2: LEARN (auto-ingest new vault data)

1. Read `02-Hooks/performance-data/last-learn.txt`.
2. If last run was more than 24 hours ago:
   - Execute `/learn` logic: scan vault for modified files, extract elements, update all 4 indexes, update timestamp.
3. If last run was within 24 hours: skip. Log: "Indexes fresh (last learn: [timestamp])."

### STEP 3: CONCEPT (for each content piece)

For each planned content piece:

1. Run `/concept` logic using the entry's Title, Platform, Content Type, and Goal.
2. Generate 3 concepts (A/B/C) with HOOK MAP for each.
3. **AUTO-SELECT:** Pick the concept with the highest combined index score:
   - Combined score = text hook score + visual hook score + structure score + delivery style score
   - If scores are tied (within 5 points), pick the one whose text hook has the oldest `Last Used` date.
   - If still tied, pick the one with the most visually distinct opening (different from previous content piece in today's batch).
4. Generate CONCEPT_LOCK block for the selected concept.
5. Update `Last Used` to today for all selected index entries. **After selecting a hook, write today's date to the Last Used field of that hook in hook-index.md or visual-hook-index.md. Format: YYYY-MM-DD. This is mandatory. Hook rotation cannot function without it.**

**Output:** CONCEPT_LOCK per content piece. Do not present concepts to user. Auto-select and move on.

### STEP 4: PRODUCE (route by content type)

For each content piece, route based on Content Type:

#### If Tweet or LinkedIn Post:
1. Run `/ghostwriter` logic with CONCEPT_LOCK.
2. Apply multi-hook structure for the text (opening hook from index, re-hooks generated fresh).
3. Run `/copy-editing` logic on the output (clarity sweep + voice sweep only, not full 7 sweeps).
4. Save to `06-Drafts/[date]-[platform]-[topic-slug].md` with frontmatter.
5. Auto-set `status: approved` in frontmatter.
6. Proceed to Step 6.

#### If Thread:
1. Run `/ghostwriter` logic with CONCEPT_LOCK in thread mode.
2. Hook tweet gets the opening hook from index. Each subsequent tweet gets a re-hook (fresh, topic-specific).
3. Run `/copy-editing` logic (clarity + voice sweeps).
4. Save to `06-Drafts/[date]-thread-[topic-slug].md` with frontmatter.
5. Auto-set `status: approved`.
6. Proceed to Step 6.

#### If Video (TikTok Script, Reel Script, Video - AI Generated):
1. Run `/ghostwriter` logic with CONCEPT_LOCK to generate the script.
   - Script MUST include: all 5 hook points (text + visual), delivery notes per scene, structure timeline.
2. Run `/video-editor` logic with CONCEPT_LOCK and the script:
   - Step 1 (Art Direction): Auto-generate from CLAUDE.md brand system + topic.
   - Step 2 (Storyboard): Map 5 hook points to shot deck with effects and SFX.
   - Step 3 (Generate Visuals): Generate images via Nano Banana MCP (free) first, fal.ai as backup. Generate video via Kling. Save all to `06-Drafts/visuals/[slug]/`.
   - Step 4 (Voiceover): Generate via MiniMax. Save to `06-Drafts/visuals/[slug]/voiceover.mp3`.
   - Step 5 (Assembly): Assemble via Remotion. Save manifest + render to `06-Drafts/visuals/[slug]/`.
3. Save draft .md with full frontmatter (including `media_dir`) to `06-Drafts/`.
4. If ALL generation succeeded: auto-set `status: approved`.
5. If ANY generation failed: set `status: partial`, add `missing: [list]` to frontmatter.
6. Proceed to Step 5 (review) for partial, Step 6 for complete.

#### If Carousel:
1. Run `/ghostwriter` logic with CONCEPT_LOCK for carousel copy (slide-by-slide text).
2. Run `/graphic-designer` logic with CONCEPT_LOCK for slide generation.
   - First slide: aesthetic image (never text-first).
   - Generate AI backgrounds via Nano Banana MCP / fal.ai.
   - Composite text overlays via Pillow.
   - Save slides to `06-Drafts/visuals/[slug]/slide-01.png` through `slide-XX.png`.
3. Save draft .md with frontmatter (including `media_dir`, `slide_count`) to `06-Drafts/`.
4. If ALL slides generated: auto-set `status: approved`.
5. If generation failed: set `status: partial`.
6. Proceed accordingly.

#### If Community Post (Telegram):
1. Run `/ghostwriter` logic for Telegram-style community post.
2. Auto-set `status: approved`.
3. Proceed to Step 6.

### STEP 5: REVIEW PARTIAL CONTENT (only runs if something failed)

This is the ONLY point where the pipeline pauses for user input.

1. List all content pieces with `status: partial`.
2. For each, show:
   - Title, Platform, Content Type
   - What's missing (images, video, voiceover, assembly)
   - File paths where manual prompts/scripts/assembly kits were saved
   - Which fallback was triggered (F2, F3, F4, F5)
3. Ask: **"Complete these manually and run /approve when ready, or skip and publish what's ready?"**
4. If user says "skip" or "publish what's ready": proceed to Step 6 with only `status: approved` pieces.
5. If user says "I'll fix them": end pipeline here. User runs `/approve` later.

### STEP 6: PUBLISH

1. Gather all content with `status: approved` from today's batch.
2. Run `/publish` logic:
   - Push each draft to Notion Content Calendar.
   - Set Notion Status = "Scheduled".
   - Attach media files (upload to fal.ai storage, pass URLs to Notion).
   - Update draft frontmatter to `status: synced-to-notion`.
3. If Notion is down: save locally, log "FALLBACK: Notion unavailable. Drafts saved locally. Run /publish when restored."

### STEP 7: POST

1. Run `/post` logic for all scheduled content:
   - **X/Twitter, LinkedIn** → Typefully API v2 (Bearer token auth).
   - **TikTok, Instagram** → Buffer API (upload media to fal.ai storage first for public URL).
   - **Telegram** → Telegram Bot API.
2. For each platform:
   - If API succeeds: update Notion Status = "Posted".
   - If API fails: save `06-Drafts/[date]-manual-post-[platform].md` with `status: MANUAL_REQUIRED`, continue with other platforms.
3. Always show confirmation before each post: **"Posting [title] to [platform]. Confirm?"** Wait for user approval.
   - Exception: If user ran `/produce --auto`, skip confirmations and post directly.

### STEP 8: LOG

1. Update all Notion entries to Status = "Posted" (for successful posts).
2. Log to `07-Analytics/posting-log.md` for EVERY post (successful and MANUAL_REQUIRED):
   ```
   | [date] | [platform] | [title] | [status] | H-[XXX] | V-[XXX] | PS-[XXX] | TH-[XXX] |
   ```
3. This data feeds `/score-hooks` on Monday.

---

## DECISION RULES (so the pipeline doesn't stop)

| Decision Point | Auto-Rule |
|---|---|
| Which concept (A/B/C)? | Highest combined index score wins |
| Which hook? | Top scored hook matching goal + platform, not used in 7 days |
| Which visual hook? | Top scored visual hook matching platform + content type, not used in 7 days |
| Which structure? | Best match for content goal, not used on same platform in last 3 posts |
| Which delivery style? | Match energy to topic emotion, different from last 2 videos |
| Approve draft? | Auto-approve if all assets generated successfully |
| Skip or wait for manual? | Only ask if assets are missing (partial status) |
| Copy editing? | Auto-run clarity + voice sweep on all text. Skip only if user says "raw" |
| Post confirmation? | Always confirm unless `--auto` flag is passed |

## FALLBACK CHAIN (inherited from all skills)

Every step inherits the fallback logic built into each skill:
- **fal.ai down (F2):** saves prompts to manual-prompts.md, tries Nano Banana MCP, continues
- **Kling down (F3):** saves video prompts, uses static images + KenBurns, continues
- **MiniMax down (F4):** saves voiceover script, tries ElevenLabs, uses text-on-screen, continues
- **Remotion down (F5):** saves assembly kit with instructions for CapCut/Premiere, continues
- **Typefully down (F6):** saves manual-post files with MANUAL_REQUIRED status, continues
- **Buffer down (F7):** saves manual-post files with media paths, continues
- **Telegram down (F8):** saves manual-telegram files, continues
- **Notion down (F9):** saves locally to 06-Drafts/, continues
- **Apify down (F1):** uses cached data or skips scraping, continues

The pipeline NEVER stops completely. It degrades gracefully and tells you what needs manual work.

## Content Type Definitions

**Content types and mix ratios are defined in CLAUDE.md (single source of truth).** Reference: 35% Personality/Story | 26% Value/Education | 20% Authority/Transformation/Sales | 8% Promo | 6% Community | 3% Engagement/Memes | 2% Hot Takes

**Daily TikTok Rotation:** Morning: Value/Education | Midday: Personality/Story | Afternoon: Authority/Transformation | Evening: Promo or Hot Take

**Formats by Platform:**
- TikTok/Video: Talking head, Screen record, B-roll + voiceover, Quick clip, Reel, YouTube Short
- Instagram: Reel, Carousel, Static post, Story, Sidecar
- X/Twitter: Single tweet, Thread, Quote tweet, Poll
- LinkedIn: Long-form post, Carousel post, Poll post, Article

**Content Structure Types:** Visual Explainer, Tactical, Problem Solver, Authority, Complete Thought/Story, Promo/CTA

**RULE: Before producing any content piece, verify it has:**
1. Content type (Personality/Story, Value/Education, Authority/Transformation/Sales, Promo, Community, Engagement/Memes, Hot Take)
2. Platform and format
3. Structure type
4. Which daily slot it fills

If any of the 4 are missing from the Notion entry, infer from the calendar context before proceeding.

## OUTPUT FORMAT

At the end of /produce, output a production summary:

```
PRODUCTION SUMMARY — [DATE]
---

### Completed (auto-published)
| # | Platform | Type | Title | Text Hook | Visual Hook | Structure | Status |
|---|----------|------|-------|-----------|-------------|-----------|--------|
| 1 | X/Twitter | Tweet | [title] | H-XXX | — | — | Posted |
| 2 | TikTok | Reel | [title] | H-XXX | V-XXX | PS-XXX | Posted |

### Partial (needs manual work)
| # | Platform | Type | Title | What's Missing | Manual Files Location |
|---|----------|------|-------|----------------|----------------------|
| 3 | Instagram | Carousel | [title] | Slides 3-5 | 06-Drafts/visuals/[slug]/manual-prompts.md |

### Failed (API down, skipped)
| # | Platform | Type | Title | Reason |
|---|----------|------|-------|--------|
| — | — | — | — | — |

### Index Usage Today
- Hooks used: H-XXX, H-XXX, H-XXX
- Visual hooks used: V-XXX, V-XXX
- Structures used: PS-XXX, PS-XXX
- Delivery styles used: TH-XXX

### Next Steps
- [ ] Complete partial items and run /approve
- [ ] Monday: run /score-hooks to track this week's performance
---
```

## RULES
1. Never produce content without checking the calendar first. If nothing is planned, run /content-strategist.
2. Never reuse the same text hook on the same platform within 7 days.
3. Never reuse the same visual hook within 7 days.
4. Auto-approve only when ALL assets are generated. Any missing asset = partial = human review.
5. Log every index ID used in posting-log.md so /score-hooks can track performance.
6. If the user passes `--auto`, skip posting confirmations. Otherwise, always confirm before sending to each platform.
7. Process content pieces in posting-schedule order (earliest time first).
8. If producing multiple pieces, ensure no two consecutive pieces use the same hook formula or visual hook.
