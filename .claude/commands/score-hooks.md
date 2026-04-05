---
voice: see 08-Templates/voice-rules.md
---

# /score-hooks — Weekly Hook Performance Feedback Loop

## ROLE

You are the Hook Performance Analyst. You scrape @big_quiv's recent posts across all 4 platforms, match them to hooks in the index, score by real engagement data, update hook-index.md, and generate a weekly performance report.

Run this command weekly (every Monday) or on-demand.

---

## PLATFORM CONFIG

| Platform | Username | Actor ID | Input Key |
|----------|----------|----------|-----------|
| X/Twitter | `_Quivira` | `apidojo~tweet-scraper` | `twitterHandles` |
| Instagram | `big_quiv` | `apify~instagram-scraper` | `directUrls` |
| TikTok | `big_quiv` | `clockworks~tiktok-scraper` | `profiles` |
| LinkedIn | `bigquiv` | `curious_coder~linkedin-post-search-scraper` | `profileUrls` |

If any username is wrong or a scrape returns 0 results, ask the user for the correct handle before continuing.

---

## Step 1: Scrape My Posts (Last 7 Days)

### Step 1A: Read posting-log first (PRIMARY SOURCE)

Before any Apify scrapes, read `07-Analytics/posting-log.md`. This log contains post URLs, platforms, dates, and titles for everything posted via /post.

1. Parse all entries from the last 7 days.
2. Extract: post URL, platform, date, title, content type.
3. Build a `known_posts` list — these do NOT need to be scraped from Apify.
4. For each known post, fetch engagement data directly:
   - X/Twitter: use the tweet URL with Apify `apidojo~tweet-scraper` (single URL mode, not full profile scrape)
   - Instagram: use the post URL with Apify `apify~instagram-scraper` (single post mode)
   - TikTok: use the post URL with Apify `clockworks~tiktok-scraper` (single URL mode)
   - LinkedIn: use the post URL with Apify `curious_coder~linkedin-post-search-scraper`
5. This is faster and cheaper than full profile scrapes — targeted URLs only.

### Step 1B: Scrape for posts NOT in the log

Only run full profile scrapes (Step 1 original code below) for platforms where:
- The posting-log has fewer posts than expected for that platform (TikTok: 4/day, X: 2/day, Instagram: 2/day, LinkedIn: 2/week)
- The user posted manually outside the /post pipeline
- The posting-log doesn't exist or is empty

Compare scraped results against `known_posts` to avoid duplicate scoring.

### Step 1C: Full profile scrapes (fallback)

Use the Apify API (same pattern as /scrape-instagram) to pull posts from all 4 platforms. Run all 4 scrapes in parallel using subagents. Only run for platforms not fully covered by Step 1A.

### X/Twitter

```bash
python -c "
import requests, os, json, time, sys
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')
actor_id = 'apidojo~tweet-scraper'
payload = {'twitterHandles': ['_Quivira'], 'maxTweets': 30, 'sort': 'Latest'}
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(120):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
if state != 'SUCCEEDED':
    print(f'ERROR: {state}')
    sys.exit(1)
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
# Filter to last 7 days
from datetime import datetime, timedelta
cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
recent = [r for r in results if r.get('createdAt', '') >= cutoff]
with open(r'C:\Users\Bigquiv\onedrive\desktop\contentbrain\02-Hooks\performance-data\x-last7.json', 'w') as f:
    json.dump(recent, f, indent=2)
print(f'X: {len(recent)} posts from last 7 days')
"
```

### Instagram

```bash
python -c "
import requests, os, json, time, sys
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')
actor_id = 'apify~instagram-scraper'
payload = {'directUrls': ['https://www.instagram.com/big_quiv/'], 'resultsLimit': 20, 'resultsType': 'posts'}
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(120):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
if state != 'SUCCEEDED':
    print(f'ERROR: {state}')
    sys.exit(1)
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
from datetime import datetime, timedelta
cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
recent = [r for r in results if r.get('timestamp', '') >= cutoff]
with open(r'C:\Users\Bigquiv\onedrive\desktop\contentbrain\02-Hooks\performance-data\ig-last7.json', 'w') as f:
    json.dump(recent, f, indent=2)
print(f'IG: {len(recent)} posts from last 7 days')
"
```

### TikTok

```bash
python -c "
import requests, os, json, time, sys
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')
actor_id = 'clockworks~tiktok-scraper'
payload = {'profiles': ['big_quiv'], 'resultsPerPage': 20}
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(120):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
if state != 'SUCCEEDED':
    print(f'ERROR: {state}')
    sys.exit(1)
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
from datetime import datetime, timedelta
cutoff = int((datetime.utcnow() - timedelta(days=7)).timestamp())
recent = [r for r in results if r.get('createTime', 0) >= cutoff]
with open(r'C:\Users\Bigquiv\onedrive\desktop\contentbrain\02-Hooks\performance-data\tt-last7.json', 'w') as f:
    json.dump(recent, f, indent=2)
print(f'TT: {len(recent)} posts from last 7 days')
"
```

### LinkedIn

```bash
python -c "
import requests, os, json, time, sys
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')
actor_id = 'curious_coder~linkedin-post-search-scraper'
payload = {'profileUrls': ['https://www.linkedin.com/in/bigquiv/'], 'maxResults': 20}
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(120):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
if state != 'SUCCEEDED':
    print(f'ERROR: {state}')
    sys.exit(1)
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
from datetime import datetime, timedelta
cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
recent = [r for r in results if r.get('postedDate', r.get('publishedAt', '')) >= cutoff]
with open(r'C:\Users\Bigquiv\onedrive\desktop\contentbrain\02-Hooks\performance-data\li-last7.json', 'w') as f:
    json.dump(recent, f, indent=2)
print(f'LI: {len(recent)} posts from last 7 days')
"
```

**Run all 4 scrapes in parallel** using subagents or background tasks. Wait for all to complete before Step 2.

If any scrape returns 0 posts, note it in the report but continue with available data.

---

## Step 2: Extract Hooks & Match to Index

After all scrapes complete, read the 4 JSON files and process each post:

### 2A: Extract Hook From Each Post

| Platform | Hook = First Line Of | Text Field |
|----------|---------------------|------------|
| X/Twitter | `text` | Split on `\n`, take line 1 |
| Instagram | `caption` | Split on `\n`, take line 1 |
| TikTok | `caption` or `desc` | Split on `\n`, take line 1 |
| LinkedIn | `text` | Split on `\n`, take line 1 (before "see more") |

### 2B: Match Against hook-index.md

Read `02-Hooks/hook-index.md`. For each extracted hook:

1. **Exact match**: If the hook text matches an indexed hook (after stripping quotes, normalizing whitespace), link to that hook ID. Confidence: 100%.

2. **Fuzzy match**: If no exact match, compare using these rules:
   - Strip all [brackets] from the indexed hook template
   - Check if the extracted hook follows the same structure/pattern
   - Look for key phrases (e.g., if index has "I almost quit crypto" and post starts with "I almost quit trading")
   - Match confidence: estimate 0-100% based on structural similarity
   - Only accept matches at 75%+ confidence

3. **No match**: If confidence < 75%, this is a new hook not in the index. Queue it for addition.

### 2C: Output hook-matches.json

Save to `02-Hooks/performance-data/hook-matches.json`:

```json
[
  {
    "hook_id": "H-034",
    "hook_text_indexed": "You're spending 4-6 hours a day charting...",
    "hook_text_actual": "You're spending 4-6 hours a day charting. Your bot could do it in 4 minutes.",
    "match_confidence": 100,
    "platform": "X",
    "post_url": "https://twitter.com/_Quivira/status/...",
    "post_date": "2026-03-25",
    "metrics": {
      "impressions": 12400,
      "likes": 342,
      "saves": 0,
      "shares": 47,
      "comments": 23,
      "bookmarks": 112,
      "views": 12400
    }
  },
  {
    "hook_id": "NEW",
    "hook_text_actual": "Some hook I wrote that's not in the index",
    "match_confidence": 0,
    "platform": "TikTok",
    "post_url": "...",
    "post_date": "2026-03-26",
    "metrics": { "views": 8500, "likes": 210, "saves": 45, "shares": 12, "comments": 8 }
  }
]
```

---

## Step 3: Calculate Real Performance Score

### Platform-Specific Engagement Rate Formulas

**X/Twitter:**
```
engagement = likes + retweets + replies + bookmarks
rate = engagement / impressions
score = min(100, round(rate * 1000))
```

**Instagram:**
```
engagement = likes + (saves * 2) + (shares * 3) + comments
rate = engagement / max(views, 1)
score = min(100, round(rate * 1000))
```
Saves weighted 2x (signal value), shares weighted 3x (signal virality).

**TikTok:**
```
engagement = likes + (saves * 2) + (shares * 3) + comments
rate = engagement / max(views, 1)
score = min(100, round(rate * 1000))
```

**LinkedIn:**
```
engagement = likes + (comments * 2) + (reposts * 3)
rate = engagement / max(impressions, 1)
score = min(100, round(rate * 1000))
```

### Cross-Platform Composite

If a hook was used on multiple platforms in the same week:
```
composite_score = round(mean(platform_scores))
```

### 30-Day Baseline

Read previous weekly reports from `02-Hooks/performance-data/` to calculate the running 30-day average score. If no prior reports exist (first run), use the median score from this week as the baseline.

```
baseline = mean(all_hook_scores_from_last_4_weekly_reports)
```

If no prior data: `baseline = median(this_week_scores)`

---

## Step 4: Update hook-index.md

For each hook with new performance data, update the index:

### 4A: Score Update

- **Replace the AI-estimated score** with the real engagement score
- The 4-criteria columns (GAP, SPEC, CHARGE, BREAK) remain as-is — they're the AI estimate for comparison
- Add the real score as the primary `Score` column value

### 4B: Tier Reassignment

| New Score | New Tier | Action |
|-----------|----------|--------|
| 80-100 | SELF-PROVEN | Move hook to SELF-PROVEN section. This is now a proven winner for YOUR audience. |
| 60-79 | STRONG | Keep or move to STRONG. Good but not exceptional. |
| 40-59 | UNTESTED | Demote if it was STRONG. Single bad performance = keep tier, add `<!-- RETEST -->` |
| Below 40 | TEMPLATE | Demote. Stop using as a primary hook. Only use as structural inspiration. |

**Rules:**
- A single data point is not enough to promote to SELF-PROVEN. Require 2+ uses with score 80+ before promoting.
- A single bad performance does NOT demote. Require 2+ underperformances (score < 40) before demoting.
- First-time use scoring 80+: add `<!-- RETEST: strong first result, needs confirmation -->`
- 3+ uses averaging below 30: add `<!-- RETIRE: consistently underperforms -->`

### 4C: Last Used Update

Set `Last Used` = most recent post date for each matched hook. **After selecting a hook, write today's date to the Last Used field of that hook in hook-index.md or visual-hook-index.md. Format: YYYY-MM-DD. This is mandatory. Hook rotation cannot function without it.**

### 4D: Real Data Tag

After the Source column, hooks with real performance data get tagged:
- `RD:yes` = has real engagement data (overrides AI estimate)
- `RD:no` or blank = still AI-estimated only

### 4E: New Hook Registration

For hooks matched as "NEW" (not in index):
1. Assign next available H-XXX ID
2. Score using the real engagement data (Step 3 formula)
3. Place in appropriate tier based on score
4. Run the 4-criteria AI scoring on them too (so both scores exist)
5. Tag with `RD:yes`
6. Set Goal, Platform, Type based on content analysis

---

## Step 5: Generate Weekly Hook Report

Write to `02-Hooks/performance-data/weekly-report-[YYYY-MM-DD].md`:

```markdown
# Hook Performance Report — [DATE]

> Posts analyzed: [X] across [Y] platforms | Hooks matched: [Z] | New hooks found: [N]
> 30-day baseline score: [X]

---

## Top 5 Hooks This Week

| Rank | ID | Hook | Score | Platform | Key Metric |
|------|----|------|-------|----------|------------|
| 1 | H-XXX | "[hook text]" | XX | X | 342 likes, 12.4K impressions |
| 2 | ... | ... | ... | ... | ... |

## Bottom 5 Hooks This Week

| Rank | ID | Hook | Score | Platform | Key Metric |
|------|----|------|-------|----------|------------|
| 1 | H-XXX | "[hook text]" | XX | IG | 12 likes, 800 views |
| 2 | ... | ... | ... | ... | ... |

## New Hooks Discovered (Not Previously Indexed)

| New ID | Hook | Score | Platform | Suggested Tier |
|--------|------|-------|----------|---------------|
| H-XXX | "[new hook text]" | XX | TT | STRONG |

## Tier Changes

| ID | Hook | Old Tier | New Tier | Old Score | New Score | Reason |
|----|------|----------|----------|-----------|-----------|--------|
| H-XXX | "..." | UNTESTED | SELF-PROVEN | 54 | 87 | 2x uses, both 80+ |
| H-XXX | "..." | STRONG | TEMPLATE | 72 | 28 | 3 underperformances |

## Hooks Pending Retest

| ID | Hook | First Score | Needs |
|----|------|-------------|-------|
| H-XXX | "..." | 85 | 1 more use at 80+ to confirm promotion |

## Recommendations

### Reuse Next Week (highest-scoring, rotation-safe)
1. H-XXX — "[hook]" (Score: XX, last used [date])
2. H-XXX — "[hook]" (Score: XX, last used [date])
3. H-XXX — "[hook]" (Score: XX, last used [date])

### Retire (3+ underperformances)
- H-XXX — "[hook]" (Avg score: XX across [N] uses)

### Test Next (highest UNTESTED + PROMOTE-flagged hooks)
1. H-XXX — "[hook]" (AI score: XX, criteria: GAP:X SPEC:X CHARGE:X BREAK:X)
2. H-XXX — "[hook]" (AI score: XX)
3. H-XXX — "[hook]" (AI score: XX)

### Platform Insights
- **Best platform this week:** [platform] (avg score: XX)
- **Worst platform this week:** [platform] (avg score: XX)
- **Best hook type:** [type code] (avg score: XX across [N] uses)
- **Worst hook type:** [type code] (avg score: XX across [N] uses)
```

---

## Step 5B: Score Visual Hooks, Structures & Delivery Styles

After matching text hooks, also identify and score the visual hook, psychological structure, and delivery style used in each **video post** (TikTok, Instagram Reels, YouTube).

### 5B-A: Visual Hook Matching

For each video post, identify the opening visual technique:
1. Read the post caption, thumbnail URL, and video metadata for scene clues
2. Match against entries in `02-Hooks/visual-hook-index.md` using the technique name and scene description
3. If a match is found (75%+ confidence), record the V-XXX ID
4. If no match, describe the visual hook and queue as NEW for addition
5. Score using the same platform-specific engagement rate formula from Step 3

**Update visual-hook-index.md:**
- Update matched V-XXX entry's score with real engagement data (engagement score overrides AI estimate)
- Update `Last Used` to the post date
- Apply same tier rules as text hooks: 2+ uses at 80+ → promote, 2+ under 40 → demote
- New visual hooks → assign next V-XXX ID, set tier based on engagement score, tag `RD:yes`

### 5B-B: Psychological Structure Matching

For each post (text or video), identify the content structure used:
1. Analyze the full post/script arc: how does it open, build, and close?
2. Match against entries in `05-Frameworks/psychological-structure-index.md`
3. Record the PS-XXX ID if matched
4. Score: did the structure retain viewers? (Use completion rate if available, otherwise engagement rate)

**Update psychological-structure-index.md:**
- Update matched PS-XXX entry's score with real data
- Track which structures consistently produce high retention
- Note which structures underperform on specific platforms

### 5B-C: Delivery Style Matching

For each video post, identify the camera/delivery style:
1. Analyze video metadata, thumbnail, and caption for camera/energy clues
2. Match against entries in `06-Delivery/talking-head-style-index.md`
3. Record the TH-XXX ID if matched
4. Score based on video engagement rate

**Update talking-head-style-index.md:**
- Update matched TH-XXX entry's `Last Used` to the post date
- Track which camera + energy combos produce highest engagement

### 5B-D: Cross-Index Performance Data

Save all matches to `02-Hooks/performance-data/all-posts-scored.json`:

```json
[
  {
    "post_url": "...",
    "platform": "TikTok",
    "post_date": "2026-04-01",
    "text_hook_id": "H-034",
    "visual_hook_id": "V-007",
    "structure_id": "PS-002",
    "delivery_id": "TH-005",
    "engagement_score": 85,
    "metrics": { "views": 12400, "likes": 342, "saves": 112, "shares": 47, "comments": 23 }
  }
]
```

This data enables pattern analysis: which combinations of text hook + visual hook + structure + delivery style produce the best results.

---

## Step 5C: Extended Weekly Report Sections

Add these sections to the weekly report (after the existing text hook sections):

```markdown
## Visual Hook Performance

| Rank | V-ID | Technique | Score | Platform | Key Metric |
|------|------|-----------|-------|----------|------------|
| 1 | V-XXX | [technique] | XX | TT | 12.4K views |

## Best Structure This Week

| PS-ID | Pattern | Score | Platform | Used With |
|-------|---------|-------|----------|-----------|
| PS-XXX | [pattern name] | XX | TT | V-XXX + TH-XXX |

## Delivery Style Performance

| TH-ID | Setup | Energy | Score | Platform |
|-------|-------|--------|-------|----------|
| TH-XXX | [setup] | High | XX | TT |

## Winning Combinations (Text + Visual + Structure + Delivery)

| Post | Text Hook | Visual Hook | Structure | Delivery | Score |
|------|-----------|-------------|-----------|----------|-------|
| [url] | H-XXX | V-XXX | PS-XXX | TH-XXX | XX |

## Recommendations: Index Updates

- **Promote:** V-XXX to SELF-PROVEN (2+ uses at 80+)
- **Demote:** PS-XXX (2+ underperformances)
- **Retest:** TH-XXX (strong first result, needs confirmation)
- **Best combo to reuse:** H-XXX + V-XXX + PS-XXX + TH-XXX (score: XX)
```

---

## Step 6: Append to Education Log

Append a summary to `07-Analytics/skill-education-log.md`:

```markdown
## [date] — /score-hooks Weekly Run

**Posts analyzed:** [X] across [Y] platforms
**Hooks matched:** [Z] of [total posts]
**New hooks added:** [N]
**Tier changes:** [list]
**Top hook:** H-XXX "[hook]" (Score: XX on [platform])
**30-day baseline:** [X] → [new X]
```

---

## RULES

1. **Real data always overrides AI estimates.** Once a hook has `RD:yes`, its score comes from engagement data, not the 4-criteria rubric.
2. **Never delete hooks.** Demote, retire-flag, but keep them. A hook that fails on X might work on TikTok.
3. **Require 2+ data points** before promoting to SELF-PROVEN or demoting to TEMPLATE. One bad day isn't a pattern.
4. **Run all 4 platform scrapes in parallel** to minimize Apify credit usage and time.
5. **If APIFY_API_KEY is missing**, tell the user and stop.
6. **If a platform returns 0 posts**, note it in the report and continue with other platforms.
7. **If this is the first run** (no prior weekly reports), set baseline to median of current scores and note "First run — baseline established."
8. **Saves and shares are weighted higher** than likes because they indicate real value (saves = "I'll come back to this", shares = "others need to see this").
9. **Do not modify the 4-criteria columns** (GAP, SPEC, CHARGE, BREAK) when updating with real data. Keep both the AI estimate and real score visible for comparison.
10. **The `Last Used` field** in hook-index.md is updated by THIS command (from post dates) AND by content skills (when they select a hook for drafting). Both sources are valid.
