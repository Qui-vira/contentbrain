# Hook Index — Scored, Ranked & Rotation-Tracked

> **Source of truth for hook selection.** All skills read this file FIRST when picking hooks.
> Last rebuilt: 2026-04-04 | Total hooks indexed: 125 | Scoring method: 4-criteria rubric

---

## Selection Algorithm

When a skill needs a hook, follow this exact process:

1. **Filter** by Goal (Sales/Reach/Leads/Authority/Community) AND Platform (All, or specific)
2. **Exclude** any hook where `Last Used` is within the last 7 days
3. **Sort** remaining hooks by Score (highest first)
4. **Pick top 3** candidates from the filtered, rotation-safe list
5. **Select the one** that best matches the specific topic/angle of the content
6. **Adapt, don't copy** — modify the hook to fit the specific topic. The indexed hook is a template, not a final draft.
7. **Update `Last Used`** — after selecting a hook, update its `Last Used` column to today's date (YYYY-MM-DD)

### Rotation Rule

A hook with `Last Used` within 7 days is **blocked** from selection. This forces variety. If ALL hooks in a Goal+Platform filter are blocked (unlikely with 80+ hooks), expand the filter to include adjacent goals or fall back to TEMPLATE tier hooks adapted to the topic.

---

## Who "Proves" a Hook?

Hooks earn their tier based on **where their engagement data comes from:**

| Tier | Who Proved It | What It Means |
|------|--------------|---------------|
| **COMPETITOR-PROVEN** (80-100) | Other creators' audiences | Scraped via Apify. These hooks got real likes/views/comments on someone else's account. They work — but for their audience, not necessarily yours. Adapt the formula, not the exact words. |
| **SELF-PROVEN** (80-100) | @big_quiv's audience | Posted by you, tracked in 07-Analytics, performed above your baseline. These are YOUR best hooks. Highest priority. |
| **STRONG** (60-79) | Criteria-scored, no audience data | Quivira originals or competitor-adapted hooks scored by the 4-criteria rubric below. Good on paper, unproven in practice. |
| **UNTESTED** (40-59) | Criteria-scored, lower confidence | Ideas that score lower on specificity or pattern interrupt. Worth trying but don't lead with these. |
| **TEMPLATE** (20-39) | Framework only | Hook formulas with [brackets]. Need topic inserted. Score reflects formula quality, not content quality. |

### Promotion Path

- Post a STRONG or UNTESTED hook → track in 07-Analytics
- If it outperforms your 30-day avg engagement by 20%+ → promote to SELF-PROVEN (score 85+)
- If it underperforms twice → demote by 10 points
- /publish-update and /data-analyst skills should flag promotion candidates

---

## Scoring Rubric (4 Criteria × 5 Points = /20)

Every non-PROVEN hook is scored on these 4 criteria. No gut feel.

| Criterion | 1 (Weak) | 3 (Average) | 5 (Strong) |
|-----------|----------|-------------|------------|
| **GAP** — Curiosity Gap | States the answer upfront | Creates mild "what?" | Impossible to scroll past without knowing |
| **SPEC** — Specificity | Zero concrete details | Some numbers or names | Vivid: dollar amounts, timeframes, contrasts |
| **CHARGE** — Emotional Charge | Neutral/informational | Mild aspiration or fear | Triggers anger, FOMO, desire, or vulnerability |
| **BREAK** — Pattern Interrupt | Follows expected format | Slight twist on common pattern | Completely breaks assumptions |

**Score normalization:**
- STRONG tier: `60 + round((total - 4) / 16 × 19)` → range 60-79
- UNTESTED tier: `40 + round((total - 4) / 16 × 19)` → range 40-59
- TEMPLATE tier: `20 + round((total - 4) / 16 × 19)` → range 20-39

---

## Hook Types

| Code | Type | Best For |
|------|------|----------|
| BC | Bold Claim | TikTok, Reels, Tweets |
| CG | Curiosity Gap | All platforms |
| QN | Question | Engagement, Community |
| CT | Contrarian | Reach, Authority |
| BA | Before-After | Story, Reach |
| SP | Simplicity Promise | Leads, TikTok |
| FM | FOMO/Urgency | Sales, Leads |
| DT | Demo Tease | Authority, Sales |
| AU | Authority | LinkedIn, Threads |
| ST | Story | Reach, Community |
| PS | Problem-Solver | Sales, Community |
| CTA-DM | DM Call-to-Action | Leads (Instagram) |
| RF | Result-First | Sales, Authority |
| PL | Polarizing | Reach, Authority |

---

## SELF-PROVEN HOOKS (Score 85-100)

> Hooks posted by @big_quiv that outperformed his 30-day average. **Highest selection priority.**

| ID | Hook | Score | Goal | Type | Platform | Engagement | Date Posted | Last Used | RD |
|----|------|-------|------|------|----------|-----------|-------------|-----------|-----|
| H-114 | Q1 is done. Some of you are exactly where you were in January. | 100 | Reach | PL | X | 9L 3RT 112V | 2026-04-01 | 2026-04-01 | yes | <!-- RETEST: strong first result, needs confirmation -->
| H-115 | Next week: CLARITY Act vote, Q1 close, and a potential BTC breakout above $73K. | 100 | Authority | AU | X | 54L 19RT 482V | 2026-03-29 | 2026-03-29 | yes | <!-- RETEST: strong first result, needs confirmation -->
| H-116 | My AI scans 50 crypto pairs every 4 hours. RSI. MACD. Volume. Support. Resistance. | 100 | Authority | DT | X | 40L 12RT 6BM 827V | 2026-03-25 | 2026-03-25 | yes | <!-- RETEST: strong first result, needs confirmation -->
| H-117 | 27. God's timing is everything. | 100 | Reach | ST | IG+TT | 9L(IG) 37L(TT) 6cmt | 2026-03-28 | 2026-03-28 | yes | <!-- RETEST: strong first result, needs confirmation -->
| H-118 | I built my entire system during a bear market. Now I don't work harder in a bull. I just approve signals. | 98 | Story | RF | X | 31L 7RT 501V | 2026-03-27 | 2026-03-27 | yes | <!-- RETEST: strong first result, needs confirmation -->
| H-123 | New age. New level. | 96 | Reach | BC | X | 109L 9RT 44cmt 1724V | 2026-03-27 | 2026-03-27 | yes | <!-- RETEST: strong first result, needs confirmation -->

*Pending confirmation: all hooks above have 1 data point. Need 2+ uses at 80+ to confirm as SELF-PROVEN. Run `/score-hooks` weekly.*

**Real Data tag:** Hooks with `RD:yes` have scores from actual engagement data (via /score-hooks). Hooks without it are still AI-estimated by the 4-criteria rubric. Real data always overrides AI estimates.

---

## COMPETITOR-PROVEN HOOKS (Score 80-100)

> Real engagement data from competitor scrapes. Adapt the formula for @big_quiv's voice.

### Instagram — Scraped via Apify

| ID | Hook | Score | Goal | Type | GAP | SPEC | CHARGE | BREAK | Likes | Source | Last Used |
|----|------|-------|------|------|-----|------|--------|-------|-------|--------|-----------|
| H-001 | Comment with "[keyword]" | 100 | Leads | CTA-DM | — | — | — | — | 230K | @nordic_scott | — |
| H-002 | This is the low → high quality effect. | 97 | Reach | CG | — | — | — | — | 106K | @tapewarp.ai | — |
| H-003 | If you create a digital product and focus on these pain points... you have a million dollar business in 365 days. | 95 | Sales | BC | — | — | — | — | 100K | @viralclubhouse_ | — |
| H-004 | [Relatable POV hook] + comment for part 2 | 93 | Reach | CG | — | — | — | — | 91K | @andrewandsilvia | — |
| H-005 | Steal these viral small business hooks | 91 | Leads | SP | — | — | — | — | 80K | @iammattjupp | — |
| H-006 | Life is unfair. Use your unfair advantages. | 90 | Reach | CT | — | — | — | — | 70K | @im_roy_lee | — |
| H-007 | Comment "[keyword]" for [specific resource] | 89 | Leads | CTA-DM | — | — | — | — | 54K | @albert.olgaard | — |
| H-008 | Claude Code just became free. | 88 | Reach | BC | — | — | — | — | 55K | @thevibefounder | — |
| H-009 | first course buyer [emotional emoji] | 86 | Sales | ST | — | — | — | — | 46K | @brownietrds | — |
| H-010 | Here's some tips to help keep prospects on the phone... | 85 | Authority | SP | — | — | — | — | 45K | @jeremyleeminer | — |
| H-011 | The advice you never knew you needed about the knowledge in your own brain | 84 | Authority | CG | — | — | — | — | 4K+10K cmt | @steveofallstreets | — |
| H-012 | A 22-year-old dropout is making $700,000/year from videos people fall asleep to. | 83 | Reach | BC | — | — | — | — | 7K+17K cmt | @nivedan.ai | — |
| H-013 | Comment "[keyword]" and I'll send you [specific guide] | 82 | Leads | CTA-DM | — | — | — | — | 5K+16K cmt | @timkoda_ | — |
| H-014 | The best AI tools for these tasks | 81 | Authority | SP | — | — | — | — | 20K | @danmartell | — |
| H-015 | I study the fastest-growing creators, and they all rely on these 6 content types to blow up. | 80 | Authority | AU | — | — | — | — | 473+102 cmt | @peter.visuals | — |

### Instagram — Multi-Creator Hook Study (2026-04-01)

| ID | Hook | Score | Goal | Type | GAP | SPEC | CHARGE | BREAK | Likes | Source | Last Used |
|----|------|-------|------|------|-----|------|--------|-------|-------|--------|-----------|
| H-124 | A lesson about markets that no one teaches you — told in 60 seconds. | 99 | Authority | ST | 5 | 3 | 4 | 5 | 292K | @humphreytalks | — |
| H-125 | This "extremely easy" edit makes your content look like a $10K production. Comment LEVEL to get the settings. | 97 | Leads | CTA-DM | 4 | 5 | 4 | 4 | 124K | @karenxcheng | — |
| H-126 | How I find 3x setups before breakfast — using one AI tool. | 98 | Authority | DT | 5 | 5 | 4 | 4 | 170K | @johnbucog | — |
| H-127 | Hope this gives you some clarity on what's actually happening on-chain right now. | 96 | Community | ST | 3 | 3 | 3 | 5 | 106K | @npcfaizan | — |
| H-128 | Comment SIGNAL and I'll DM you the exact settings my bot uses to scan 50 pairs. | 94 | Leads | CTA-DM | 4 | 5 | 4 | 3 | 47K | @karenxcheng-adapted | — |
| H-129 | Three months ago I read an on-chain report that completely changed how I trade. Here's what happened. | 93 | Reach | ST | 5 | 4 | 4 | 4 | 37K | @jimruitang | — |
| H-130 | How I create AI-generated charts that actually explain the trade — step by step. | 92 | Authority | DT | 4 | 4 | 3 | 4 | 36K | @__diditee__ | — |
| H-131 | Comment ALPHA and I'll send you the 6 content types that blew up my crypto account. | 93 | Leads | CTA-DM | 4 | 5 | 3 | 3 | 45K | @karenxcheng-adapted | — |
| H-132 | I turned one sponsor deal into a full content series. Here's the formula. | 91 | Sales | RF | 4 | 4 | 3 | 4 | 39K | @karenxcheng | — |
| H-133 | This edit took me 3 minutes and it looks like I hired a production team. Comment EASY to get it. | 91 | Leads | CTA-DM | 4 | 5 | 3 | 4 | 33K | @karenxcheng | — |
| H-134 | The Prophet Muhammad used stories to teach complex truths. Here's what that means for your content. | 89 | Reach | ST | 5 | 3 | 5 | 5 | 24K | @its.normss | — |
| H-135 | I studied what makes hooks go viral. These 3 patterns show up in every post above 100K views. Comment HOOKS to get the full breakdown. | 87 | Leads | CTA-DM | 5 | 5 | 3 | 3 | 40K | @thepostprotocol | — |
| H-136 | The hooks that actually convert followers into buyers — backed by data from 500 posts. Comment PROVEN. | 86 | Sales | CTA-DM | 4 | 5 | 4 | 3 | 2.4K | @thepostprotocol | — |
| H-137 | Every creator is using AI wrong. Here's what the top 1% do differently with on-chain data. | 85 | Authority | CT | 5 | 3 | 4 | 4 | 820 | @thepostprotocol-adapted | — |
| H-138 | I built a Web3 content system that ships daily without me touching it. Comment BOT for the checklist. | 83 | Leads | CTA-DM | 4 | 4 | 3 | 4 | 9K | @tobi.the.og | — |
| H-139 | How I trained an AI model on my personal brand style — and now it creates visuals I actually use. | 82 | Authority | DT | 4 | 4 | 3 | 4 | 8K | @timkoda_ | — |
| H-140 | The storytelling framework that turns complex DeFi concepts into content people actually save. Part 1 of 10. DM BLUEPRINT for the full series. | 81 | Leads | CTA-DM | 4 | 4 | 3 | 3 | 7K | @jade.got.curious | — |
| H-141 | The art of the re-hook: your best-performing crypto post deserves a second life. Here's how. | 80 | Reach | RF | 4 | 3 | 3 | 4 | 5K | @bymoussari | — |
| H-142 | You already posted your best content. You just never re-used the hook that worked. | 80 | Reach | CG | 4 | 3 | 4 | 4 | 5K | @bymoussari-adapted | — |
| H-143 | Save this and steal a hook for your next crypto thread. 12 patterns that work every time. | 80 | Authority | SP | 3 | 5 | 3 | 3 | 278 | @soravjain | — |

### X/Twitter — Scraped via Apify

| ID | Hook | Score | Goal | Type | GAP | SPEC | CHARGE | BREAK | Likes | Views | Source | Last Used |
|----|------|-------|------|------|-----|------|--------|-------|-------|-------|--------|-----------|
| H-016 | 10 people made [X] each from [specific opportunity] | 95 | Sales | FM | — | — | — | — | 1.4K | 155K | @Farmercist | — |
| H-017 | the realest thing a person can ever do for you is put you on money making opportunities. | 92 | Community | ST | — | — | — | — | 1.3K | 37K | @Farmercist | — |
| H-018 | It's [year] and you reading this will [aspirational outcome] this Year. | 90 | Reach | BA | — | — | — | — | 1K | 17K | @Farmercist | — |
| H-019 | I got the notification of receiving $[X] yesterday but I never really checked. | 88 | Sales | RF | — | — | — | — | 818 | 113K | @Farmercist | — |
| H-020 | [Number] followers But you chasing a free $100 mint | 86 | Reach | CT | — | — | — | — | 728 | 26K | @Farmercist | — |
| H-021 | IT SHOULD BE A CRIME TO BE THIS EARLY!!! | 85 | Reach | FM | — | — | — | — | 614 | 42K | @Farmercist | — |
| H-022 | Stop reading 100 books. Focus on taking action. | 84 | Authority | CT | — | — | — | — | 632 | — | @matt_gray_ | — |
| H-023 | consistency always wins | 83 | Authority | BC | — | — | — | — | 354 | — | @matt_gray_ | — |
| H-024 | The highest leverage activity: Sitting alone. Thinking clearly. Making decisions. | 82 | Authority | AU | — | — | — | — | 328 | — | @matt_gray_ | — |
| H-025 | Overthinking is the silent killer of progress. | 81 | Reach | CT | — | — | — | — | 244 | — | @matt_gray_ | — |
| H-026 | A rule that will give you true freedom: If you don't have a system, you are the system. | 80 | Authority | AU | — | — | — | — | 201 | — | @matt_gray_ | — |

---

## STRONG HOOKS (Score 60-79) — Criteria-Scored

> Quivira originals and competitor-adapted hooks. Scored by rubric, not gut feel.

### Sales Goal

| ID | Hook | Score | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-034 | You're spending 4-6 hours a day charting. Your bot could do it in 4 minutes. | 74 | All | PS | 3 | 5 | 4 | 4 | quivira-os-sales | 2026-04-02 | <!-- PROMOTE: 16/20 — test next -->
| H-036 | My bot found 3 setups while I was asleep. I woke up, tapped approve, and they were live. | 74 | All | RF | 3 | 5 | 4 | 4 | quivira-os-sales | — | <!-- PROMOTE: 16/20 — test next -->
| H-037 | I stopped guessing what hooks work. Now I scrape 9 platforms and let the data tell me. | 74 | All | RF | 4 | 5 | 3 | 4 | quivira-os-sales | — | <!-- PROMOTE: 16/20 — test next -->
| H-039 | If you're still charting every pair manually, you don't have a business. You have a job. | 73 | All | PL | 2 | 3 | 5 | 5 | quivira-os-sales | — |
| H-032 | Stop paying for signals that lose money. Here is what a real signal group looks like. | 72 | All | CT | 3 | 4 | 4 | 3 | hooks-by-goal | — |
| H-033 | I charged $[X] for this advice last week. Here it is for free. | 72 | All | FM | 4 | 3 | 4 | 3 | hooks-by-goal | — |
| H-031 | 3 people messaged me this week saying [result]. Here is what they all had in common. | 72 | All | RF | 4 | 4 | 3 | 3 | hooks-by-goal | — |
| H-038 | This system saves me 20+ hours a week. And it makes me money while it runs. | 71 | All | RF | 3 | 4 | 4 | 2 | quivira-os-sales | — |
| H-030 | I made $[X] this month from [product]. Here is what I did differently. | 70 | All | RF | 3 | 4 | 3 | 2 | hooks-by-goal | — |
| H-040 | Signal providers who don't automate will be replaced by those who do. | 68 | All | PL | 2 | 2 | 4 | 3 | quivira-os-sales | — |
| H-035 | Every signal provider burns out eventually. Unless they automate. | 67 | All | CT | 2 | 2 | 3 | 3 | quivira-os-sales | — |

### Reach Goal

| ID | Hook | Score | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-050 | I almost quit crypto. Here is the thought that changed everything. | 75 | All | ST | 5 | 3 | 5 | 4 | hooks-by-goal | — | <!-- PROMOTE: 17/20 — test next -->
| H-055 | This is the most controversial thing I have ever said about [niche topic]. | 73 | All | PL | 5 | 2 | 4 | 4 | hooks-by-goal | — |
| H-057 | Delete this tweet if it offends you. But [bold statement]. | 73 | X | PL | 4 | 1 | 5 | 5 | hooks-by-goal | — |
| H-054 | 3 years ago I was [bad situation]. Today I [current result]. Here is what happened. | 73 | All | BA | 4 | 4 | 5 | 2 | hooks-by-goal | — |
| H-052 | I lost [money/time/trust] because of [mistake]. Here is the lesson. | 72 | All | BA | 4 | 3 | 4 | 3 | hooks-by-goal | — |
| H-051 | Nobody is talking about this, and it is going to be a problem. | 71 | All | CG | 5 | 1 | 4 | 3 | hooks-by-goal | — |
| H-056 | I was wrong about [thing]. Here is what I know now. | 71 | All | ST | 4 | 1 | 4 | 4 | hooks-by-goal | — |
| H-053 | Everyone is doing [common thing]. Here is why it is wrong. | 70 | All | CT | 4 | 1 | 3 | 4 | hooks-by-goal | — |
| H-120 | Yesterday started with messages from strangers who became family. | 71 | X | ST | 4 | 3 | 5 | 3 | score-hooks-2026-04-01 | 2026-03-28 | no |

### Leads Goal

| ID | Hook | Score | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-063 | Free for the next 48 hours: [resource]. After that, it goes behind the paywall. | 73 | All | FM | 3 | 4 | 5 | 3 | hooks-by-goal | — |
| H-062 | I made a checklist for [specific process]. 0 fluff. [number] steps. Comment "[keyword]" and I'll DM it. | 72 | IG/TikTok | CTA-DM | 3 | 5 | 3 | 3 | hooks-by-goal | — |
| H-060 | I spent [time] building this [resource]. You can have it for free. | 71 | All | FM | 3 | 3 | 4 | 3 | hooks-by-goal | — |
| H-061 | Drop "[keyword]" in my DMs and I will send you [lead magnet]. | 68 | IG/TikTok | CTA-DM | 3 | 3 | 3 | 2 | hooks-by-goal | — |
| H-064 | Everyone asks me how I [skill]. I wrote it down. Free. Link in bio. | 67 | All | SP | 3 | 2 | 3 | 2 | hooks-by-goal | — |

### Authority Goal

| ID | Hook | Score | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-077 | A pattern I've noticed: Most founders chase $10K months but very few design for $10K days. | 77 | LinkedIn | AU | 4 | 5 | 4 | 5 | @matt_gray_ adapted | — | <!-- PROMOTE: 18/20 — test next -->
| H-078 | If you repeated today exactly as it was for 12 months, where would you end up? | 77 | All | QN | 4 | 4 | 5 | 5 | @matt_gray_ adapted | — | <!-- PROMOTE: 18/20 — test next -->
| H-074 | The data says something different from what CT is telling you. Let me show you. | 75 | All | CT | 5 | 3 | 4 | 5 | hooks-by-goal | — | <!-- PROMOTE: 17/20 — test next -->
| H-073 | I predicted [event]. Here is the signal nobody else was watching. | 74 | All | AU | 5 | 3 | 4 | 4 | hooks-by-goal | — | <!-- PROMOTE: 16/20 — test next -->
| H-075 | [Number] years in [niche] taught me [insight]. Most people will not accept this. | 74 | All | AU | 5 | 3 | 4 | 4 | hooks-by-goal | — | <!-- PROMOTE: 16/20 — test next -->
| H-071 | I analyzed [number] [things]. They all had [pattern] in common. | 73 | All | AU | 5 | 4 | 3 | 3 | hooks-by-goal | — |
| H-079 | What breaks when you take a week off? That's where systems haven't caught up to growth. | 73 | LinkedIn | QN | 3 | 4 | 4 | 4 | @matt_gray_ adapted | — |
| H-076 | A pattern I've noticed: the founders who scale fastest are committed to boring business. | 72 | LinkedIn | AU | 3 | 4 | 3 | 4 | @matt_gray_ adapted | — |
| H-070 | Everyone is looking at this wrong. Here is what actually matters. | 71 | All | CT | 5 | 1 | 3 | 4 | hooks-by-goal | — |
| H-072 | Here is my framework for [specific skill]. Use it. | 67 | All | AU | 3 | 2 | 2 | 3 | hooks-by-goal | — |
| H-119 | 1/ BlackRock made staking institutional on March 12. | 77 | X | AU | 5 | 5 | 4 | 3 | score-hooks-2026-04-01 | 2026-03-28 | no |
| H-121 | Tomorrow, $14 billion in BTC options expire on Deribit. | 69 | X | FM | 5 | 5 | 4 | 3 | score-hooks-2026-04-01 | 2026-03-26 | no |
| H-122 | Some of you sound like experts in Spaces, but your DMs are begging for relevance. | 66 | X | PL | 3 | 2 | 5 | 5 | score-hooks-2026-04-01 | 2026-03-26 | no |

### Community Goal

| ID | Hook | Score | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-092 | The [common enemy] wants you to stay confused. Here is how you fight back. | 73 | All | PL | 4 | 2 | 5 | 4 | hooks-by-goal | — |
| H-091 | We do not [common bad practice] in this community. Here is what we do instead. | 72 | All | PL | 4 | 2 | 4 | 4 | hooks-by-goal | — |
| H-081 | I keep getting DMs about [topic]. Let me address it publicly. | 71 | All | ST | 4 | 3 | 3 | 3 | hooks-by-goal | — |
| H-093 | I built [product/community] because I was tired of [enemy/problem]. | 70 | All | ST | 3 | 2 | 4 | 3 | hooks-by-goal | — |
| H-090 | If you believe [shared value], you belong here. | 68 | All | ST | 2 | 1 | 5 | 3 | hooks-by-goal | — |
| H-080 | Someone asked me [question]. Here is my honest answer. | 68 | All | QN | 4 | 2 | 3 | 2 | hooks-by-goal | — |
| H-083 | Raise your hand if you have ever [relatable struggle]. Let me help. | 67 | All | QN | 2 | 2 | 4 | 2 | hooks-by-goal | — |
| H-082 | Quick question for my traders: [specific question]. | 66 | All | QN | 2 | 3 | 2 | 2 | hooks-by-goal | — |
| H-084 | What should I cover next? Your comments decide. | 64 | All | QN | 1 | 1 | 3 | 2 | hooks-by-goal | — |

---

### AI Course Launch + Weekly Series (2026-04-04)

> Quivira-original hooks written for the 30-day course launch calendar, validation posts, and weekly series episodes. Scored by rubric. All are course-adjacent and should pair with AI course CTAs.

| ID | Hook | Score | Goal | Platform | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used | RD |
|----|------|-------|------|----------|------|-----|------|--------|-------|--------|-----------|-----|
| H-144 | If someone ran live AI classes twice a week — no coding required — would you join? Not selling yet. Actually asking. | 73 | Leads | X/TikTok | QN | 4 | 3 | 4 | 4 | validation-posts.md | — | no |
| H-145 | I'm thinking about running a live AI engineering course. Which would you pay to attend: A) Claude Code B) Multi-agent systems C) Full-stack AI apps in 4hrs? | 73 | Leads | LinkedIn/X | QN | 3 | 5 | 4 | 3 | validation-posts.md | — | no |
| H-146 | If I ran live AI video creation classes — no camera, no editing skills needed — would you join? What would make you say yes immediately? | 71 | Leads | Instagram/X | QN | 3 | 3 | 4 | 3 | validation-posts.md | — | no |
| H-147 | If you could save 10+ hours a week automating your 3 most repetitive tasks — live, in real time — would you pay $30 for a month of those sessions? Be honest. | 73 | Leads | LinkedIn/Telegram | QN | 3 | 5 | 4 | 3 | validation-posts.md | — | no |
| H-148 | You can ask Claude to scan your last 30 trades and tell you your worst habit. Most traders don't know this is possible. Here's how. | 78 | Authority | X/TikTok | DT | 5 | 5 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-149 | I uploaded my trade journal to Claude. It found a pattern I had been missing for 6 months. | 77 | Authority | Instagram | CG | 5 | 4 | 5 | 4 | weekly-series-briefs.md | — | no |
| H-150 | You can generate a cinematic 5-second video from a single text prompt using Kling. No footage. No camera. No editor. Here's how. | 78 | Reach | X/TikTok | SP | 5 | 5 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-151 | I made this video from a text prompt. It took 4 minutes. No camera. No editor. | 75 | Reach | Instagram | RF | 4 | 5 | 4 | 4 | weekly-series-briefs.md | — | no |
| H-152 | Text prompt → cinematic video → published in 10 minutes. Watch. | 73 | Reach | TikTok | DT | 3 | 3 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-153 | You can query a database in plain English using Claude + Supabase. No SQL. No developer. Just ask your question and get an answer. | 78 | Authority | X/TikTok | SP | 5 | 5 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-154 | I asked my database who my best customers were. In plain English. Claude wrote the SQL. Supabase ran it. Answer in 8 seconds. | 77 | Authority | Instagram | RF | 5 | 5 | 4 | 4 | weekly-series-briefs.md | — | no |
| H-155 | You can use Remotion to generate 30 videos from a CSV file. One command. No manual editing. Here's the exact script. | 78 | Authority | X/TikTok | DT | 5 | 5 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-156 | I generated 30 videos from a spreadsheet. Automatically. No editing. One command. | 77 | Reach | Instagram | RF | 4 | 5 | 4 | 5 | weekly-series-briefs.md | — | no |
| H-157 | The first time I used AI to do something I couldn't do myself, I froze. I didn't know if it was cheating. Here's what I figured out. | 74 | Reach | X | ST | 4 | 3 | 5 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-158 | I replaced 3 hours of manual work with one Claude Code script this week. Here's exactly what I built. | 74 | Authority | X | RF | 4 | 5 | 3 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-159 | I made a 60-second video this week. Zero filming. Here's the 4-tool workflow: Nano Banana → Kling → MiniMax → CapCut. | 75 | Authority | X | DT | 4 | 5 | 4 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-160 | I stopped doing 14 hours of business tasks manually last month. Here's what I automated — and what I did with the time back. | 74 | Authority | X | RF | 4 | 5 | 4 | 3 | 30-day-x-recovery-calendar.md | — | no |
| H-161 | You don't need to understand how AI works to use it. You just need 3 prompts. Here they are. | 73 | Reach | All | SP | 4 | 3 | 4 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-162 | The automation that gave me 12 hours back last week. Built in an afternoon. Cost: $0 beyond what I already pay. | 75 | Authority | X | RF | 4 | 5 | 4 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-163 | Free: My AI Starter Pack. The 5 prompts I give to anyone who has never used AI before. Repost so it reaches someone who needs it. | 73 | Leads | X | FM | 3 | 4 | 5 | 3 | 30-day-x-recovery-calendar.md | — | no |
| H-164 | What changed when I stopped writing code from scratch: I ship 3× more, my clients get faster results, and I focus on architecture instead of syntax. | 74 | Authority | X | BA | 4 | 4 | 4 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-165 | 5 ways people are making real money with AI tools in 2026. With numbers and sources. | 72 | Authority | X/LinkedIn | AU | 3 | 4 | 4 | 3 | 30-day-x-recovery-calendar.md | — | no |
| H-166 | Something I've been building for 30 days. A live AI course. 3 topics. 4 audience tracks. $15–$50. Starting May 3. Here's everything inside. | 74 | Leads | X | RF | 4 | 5 | 4 | 3 | 30-day-x-recovery-calendar.md | — | no |
| H-167 | A freelance writer with zero coding experience raised her rates and works half the hours using Claude. Here's the exact method. | 75 | Authority | X/Instagram | RF | 4 | 4 | 5 | 4 | 30-day-x-recovery-calendar.md | — | no |
| H-168 | The 5 AI skills that will define what you can charge in 2027. And which one to start with if you're non-technical. | 77 | Authority | X/LinkedIn | AU | 5 | 4 | 5 | 4 | 30-day-x-recovery-calendar.md | — | no |

---

## UNTESTED HOOKS (Score 40-59) — Criteria-Scored

> Original ideas with lower specificity or weaker pattern interrupt. Test these to find hidden gems.

| ID | Hook | Score | Goal | Type | GAP | SPEC | CHARGE | BREAK | Source | Last Used |
|----|------|-------|------|------|-----|------|--------|-------|--------|-----------|
| H-103 | My first content got zero likes. Now it pays my bills. | 54 | Reach | BA | 3 | 4 | 5 | 4 | master-strategy | — | <!-- PROMOTE: 16/20 — test next -->
| H-106 | I post every day but I do not grow | 53 | Community | PS | 4 | 3 | 5 | 3 | master-strategy | 2026-03-27 | <!-- RETEST: first use scored 14 -->
| H-107 | I know crypto but I cannot make money from it | 53 | Community | PS | 4 | 3 | 5 | 3 | master-strategy | 2026-03-28 | <!-- RETEST: first use scored 5 -->
| H-112 | The exact funnel you use to get clients from X | 53 | Sales | DT | 4 | 5 | 3 | 3 | master-strategy | — |
| H-101 | I lost money from trusting the wrong person. Lesson. | 52 | Reach | ST | 4 | 2 | 5 | 3 | master-strategy | — |
| H-109 | Every airdrop I farm ends up being useless | 52 | Community | PS | 3 | 4 | 4 | 3 | master-strategy | — |
| H-111 | How Quivira grew as a KOL with no team | 52 | Authority | ST | 4 | 4 | 3 | 3 | master-strategy | — |
| H-100 | Someone told me I would fail. Here is what I learned. | 50 | Reach | ST | 4 | 2 | 4 | 2 | master-strategy | — |
| H-102 | I built my brand alone for years. Here is why it was worth it. | 50 | Authority | ST | 3 | 2 | 4 | 3 | master-strategy | — |
| H-104 | You do not need motivation. You need structure. | 50 | Authority | CT | 2 | 2 | 3 | 5 | master-strategy | — |
| H-108 | I trade but my results are inconsistent | 50 | Community | PS | 3 | 3 | 4 | 2 | master-strategy | — |
| H-110 | I am scared of losing money trading | 50 | Community | PS | 2 | 2 | 5 | 3 | master-strategy | — |
| H-105 | If you focus for 90 days everything will change. | 47 | Reach | BC | 2 | 3 | 3 | 2 | master-strategy | — |
| H-113 | What real community building means | 44 | Community | AU | 2 | 1 | 2 | 2 | master-strategy | — |

---

## TEMPLATE HOOKS (Score 20-39) — Fill in [brackets] before use

| ID | Template | Score | Goal | Type | GAP | SPEC | CHARGE | BREAK | Format | Last Used |
|----|----------|-------|------|------|-----|------|--------|-------|--------|-----------|
| T-03 | "There is one thing 99% of [audience] do not know about [topic]." | 33 | Reach | CG | 5 | 3 | 4 | 3 | All | — |
| T-10 | "After [X] years of [niche], here are the [N] things nobody tells you." | 33 | Authority | AU | 5 | 3 | 4 | 3 | Thread, LinkedIn | — |
| T-04 | "I turned $[X] into $[Y] using this exact system." | 32 | Sales | BC | 4 | 4 | 4 | 2 | TikTok, Tweet | — |
| T-07 | "200 people already grabbed this [resource]. You are falling behind." | 32 | Leads | FM | 3 | 3 | 5 | 3 | IG, TikTok | — |
| T-08 | "[Time] ago I had [before]. Today I have [after]. One thing changed." | 32 | Reach | BA | 5 | 3 | 4 | 2 | All | — |
| T-06 | "Stop [common practice]. Here is what smart money does instead." | 31 | Authority | CT | 4 | 2 | 3 | 4 | All | — |
| T-01 | "[Trend] is happening. Here is what they are missing." | 30 | Reach | CG | 5 | 1 | 3 | 3 | Tweet, TikTok | — |
| T-09 | "Watch me [do thing] in [short time]." | 30 | Authority | DT | 3 | 3 | 3 | 3 | TikTok, Reel | — |
| T-02 | "Set up [thing] in under 10 minutes. No experience needed." | 28 | Leads | SP | 3 | 3 | 3 | 2 | TikTok, Reel | — |
| T-05 | "Struggling to [pain point] with zero [result]? Read this." | 28 | Community | QN | 3 | 2 | 4 | 2 | Tweet, LinkedIn | — |

---

## How to Add New Hooks

### From Scrapes (auto — handled by /scrape-instagram Step 5A-2)

1. Any scraped hook with 1K+ likes or 10K+ views → COMPETITOR-PROVEN section
2. Score = `80 + round((engagement_rank / total_scraped) × 20)`
3. Tag with Goal, Type, Platform, Source
4. Set `Last Used` = `—`

### From @big_quiv's Posts (manual — triggered by /publish-update or /data-analyst)

1. When a posted hook outperforms 30-day avg by 20%+ → promote to SELF-PROVEN
2. Score = 85 (baseline) + up to 15 bonus based on how much it exceeded baseline
3. Move the hook from its current tier into SELF-PROVEN section
4. Record the engagement data and date posted

### From New Ideas (manual — when creating hooks during content planning)

1. Score using the 4-criteria rubric (GAP, SPEC, CHARGE, BREAK — each 1-5)
2. If total ≥ 14/20 → STRONG tier
3. If total < 14/20 → UNTESTED tier
4. Show the criteria scores so future reviewers can verify/challenge the ranking

### Demotion

- If a hook underperforms twice (below 30-day avg) → subtract 10 points
- If score drops below current tier floor → move to next tier down
- Never delete hooks — demoted hooks may work in different contexts
