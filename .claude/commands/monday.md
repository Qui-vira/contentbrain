---
voice: see 08-Templates/voice-rules.md
description: "Weekly Review Pipeline. Scores last week's hooks, learns new vault data, generates performance report, plans next week's content. Triggers: '/monday', 'monday review', 'weekly review', 'start the week'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "WebSearch", "mcp__claude_ai_Notion__notion-search", "mcp__claude_ai_Notion__notion-update-page", "mcp__claude_ai_Notion__notion-create-pages", "mcp__claude_ai_Notion__notion-fetch"]
---

# SKILL: /monday — Weekly Review Pipeline

## ROLE
You are the Weekly Review Orchestrator. When Big Quiv runs /monday, you execute the full Monday morning review: score last week's hooks, ingest new vault data, analyze performance, and plan next week's content. One command. Every Monday.

## TRIGGER
- `/monday` — run full weekly review
- `monday review` / `weekly review` / `start the week`

## CONTEXT FILES TO READ FIRST
- CLAUDE.md (identity, rules)
- 07-Analytics/posting-log.md (last week's posts)
- 02-Hooks/hook-index.md (current hook scores)
- 02-Hooks/performance-data/last-learn.txt (learn timestamp)

## NOTION CONTENT CALENDAR
Database ID: 8f52ebd2efac4eecb05ec4783e924346

---

## THE PIPELINE (execute in order)

### STEP 1: SCORE HOOKS

1. Run `/score-hooks` logic:
   - Scrape engagement data for all posts from the past 7 days (from posting-log.md).
   - Match each post to its hook ID (H-XXX), visual hook ID (V-XXX), structure ID (PS-XXX), and delivery style ID (TH-XXX).
   - Calculate engagement score per hook: weighted average of views, likes, comments, shares, saves.
   - Update scores in all 4 indexes.
   - Promote hooks that outperformed (move up a tier if score crosses threshold).
   - Demote hooks that underperformed 3 weeks in a row (move down one tier, never delete).
2. If no posting-log data exists for last week: skip scoring, log "No posts logged last week. Scoring skipped."

**Output:** Hook score changes summary.

### STEP 2: LEARN

1. Run `/learn` logic:
   - Read `02-Hooks/performance-data/last-learn.txt`.
   - Find all files modified since last learn.
   - Extract hooks, visual hooks, structures, delivery styles from modified files.
   - Score, deduplicate, and file into all 4 indexes.
   - Scan `.claude/commands/` for unindexed knowledge.
   - Update timestamp.
2. If no files modified since last learn: log "Indexes fresh. No new data."

**Output:** Learn summary (new entries, updates, skips).

### STEP 3: DATA ANALYST

1. Run `/data-analyst` logic for weekly report:
   - Pull all posts from last 7 days (posting-log.md + Notion Content Calendar).
   - Calculate: total posts, posts per platform, engagement rate per platform, top 3 posts, worst 3 posts.
   - Calculate: hook success rate (which hook tiers performed best), content type breakdown, goal distribution (sales/reach/leads/authority/community).
   - Compare to previous week: up/down trends per metric.
   - Identify: what worked, what didn't, what to do more of, what to stop.
2. If Notion is unreachable: use posting-log.md data only, note "Notion data unavailable — report based on local logs."

**Output:** Weekly performance report.

### STEP 4: CONTENT STRATEGIST

1. Run `/content-strategist` logic:
   - Use performance data from Step 3 to inform this week's plan.
   - Double down on content types and hooks that performed well.
   - Reduce or retire approaches that underperformed.
   - Scout trends (web search for trending topics in Web3, crypto, AI, trading).
   - Generate this week's content calendar entries in Notion:
     - 7 days × platforms per day (per posting schedule in CLAUDE.md).
     - Each entry: Title, Platform, Content Type, Goal, Hook suggestion, Post Date, Status = "Draft".
   - Ensure goal distribution follows CLAUDE.md: ~35% Personality/Story, ~26% Value/Education, ~20% Authority/Transformation/Sales, ~8% Promo, ~6% Community, ~3% Engagement/Memes, ~2% Hot Takes.
   - Ensure no hook or visual hook repeats within 7 days.
2. If Notion is unreachable: save calendar to `06-Drafts/week-[start-date]-plan.md` with status "MANUAL_REQUIRED".

**Output:** Next week's content plan.

---

## OUTPUT FORMAT

```
WEEKLY REVIEW — [DATE]
---

### 1. Hook Scoring
Hooks scored: [N]
Promotions: [N] (list IDs)
Demotions: [N] (list IDs)
Top hook this week: [ID] — [name] — Score: [N]
Worst hook this week: [ID] — [name] — Score: [N]

### 2. Learn
Files scanned: [N]
New entries: [N] | Updated: [N] | Skipped: [N]

### 3. Weekly Performance
Total posts: [N]
| Platform | Posts | Avg Engagement | Best Post |
|----------|-------|----------------|-----------|
| X        | [N]   | [N]            | [title]   |
| LinkedIn | [N]   | [N]            | [title]   |
| TikTok   | [N]   | [N]            | [title]   |
| Instagram| [N]   | [N]            | [title]   |
| Telegram | [N]   | [N]            | [title]   |

Week-over-week: [up/down] [N]%
Top content type: [type]
Top goal category: [goal]

What worked: [1-2 sentences]
What didn't: [1-2 sentences]
Do more of: [1-2 sentences]

### 4. Next Week's Plan
Entries created: [N] across [N] platforms
Goal distribution: Sales [N]% | Reach [N]% | Leads [N]% | Authority [N]% | Community [N]%

| Day | Platform | Type | Title | Goal | Hook |
|-----|----------|------|-------|------|------|

### Next Steps
- [ ] Review content plan in Notion
- [ ] Run /produce daily to execute
- [ ] Friday: run /data-analyst for mid-week check
---
```

## RULES
1. Run steps in order. Step 4 depends on data from Steps 1-3.
2. Never skip Step 1 (scoring) — it's the feedback loop that makes everything smarter.
3. If a step fails, log the failure and continue to the next step. Never stop the whole pipeline.
4. Content strategist must use performance data, not just gut feel. Data-driven planning.
5. Never plan content without checking what hooks are available and fresh (not used in last 7 days).
6. The weekly plan must respect the posting schedule from CLAUDE.md: TikTok 4x/day, X 2x/day, Instagram 2x/day, LinkedIn 2x/week.
7. Run silently through Steps 1-3. Only present the full summary at the end.
