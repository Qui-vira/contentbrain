---
name: scrape-instagram
description: "Scrape competitor posts from ANY social media platform via Apify (Instagram, X/Twitter, TikTok, YouTube, LinkedIn, Facebook, Reddit, Pinterest, Threads). Analyzes for patterns/frameworks/knowledge, distributes insights to vault folders. Triggers: 'scrape instagram', 'scrape @username', 'scrape tiktok', 'scrape twitter', 'scrape youtube', 'scrape linkedin', 'scrape facebook', 'scrape reddit', 'scrape pinterest', 'scrape threads', 'update competitors', 'pull posts from [platform]', 'learn about [topic]', 'research [topic] videos', 'study 50 videos about [topic]', 'scrape videos about [topic]', 'what are the best [topic] videos', 'educate yourself on [topic]', 'research how to [topic]'"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebFetch", "WebSearch"]
---

# Multi-Platform Scraper & Intelligence Extractor

## ROLE
You scrape posts from competitor accounts on ANY social media platform using Apify. After collection, you analyze all content for patterns, frameworks, and knowledge — then distribute insights to the correct vault folders so all other skills can learn from them.

## SUPPORTED PLATFORMS

| Platform | Apify Actor | Input Key | Post Text Field |
|----------|-------------|-----------|-----------------|
| Instagram | `apify/instagram-scraper` | `directUrls` | `caption` |
| Instagram Reels (transcript) | `apify/instagram-reel-scraper` | `directUrls` | `caption`, `transcript` |
| Twitter/X | `apidojo/tweet-scraper` | `twitterHandles` | `text` |
| TikTok | `clockworks/tiktok-scraper` | `profiles` | `caption` |
| YouTube | `streamers/youtube-scraper` | `startUrls` | `description` |
| LinkedIn | `curious_coder/linkedin-post-search-scraper` | `profileUrls` | `text` |
| Facebook | `apify/facebook-posts-scraper` | `startUrls` | `text` |
| Reddit | `trudax/reddit-scraper` | `startUrls` | `selfText` |
| Pinterest | `epctex/pinterest-scraper` | `startUrls` | `description` |
| Threads | `curious_coder/threads-scraper` | `usernames` | `text` |

## MODE SELECTION

**Mode 1: Profile Scrape** (existing behavior)
Triggered by: "scrape @username", "scrape [platform] @username", "update competitors"
Scrapes a specific account's posts. Analyzes for patterns, hooks, frameworks. Saves to competitor folders.

**Mode 2: Topic Research** (new)
Triggered by: "learn about [topic]", "research [topic]", "study videos about [topic]", "scrape videos about [topic]", "educate yourself on [topic]", "research how to [topic]"
Searches across platforms by KEYWORD or HASHTAG (no username needed). Pulls up to 50 results per platform. Extracts learnings and distributes them to vault skill files (prompt-library, hooks, frameworks, patterns, niche knowledge). This mode makes your skills smarter.

If the user provides a @username → Mode 1.
If the user provides a topic/keyword without a username → Mode 2.
If unclear, ask: "Do you want to (1) scrape a specific account, or (2) research a topic across platforms?"

## WHEN TO USE
- "Scrape @username" — Instagram by default (backward compatible)
- "Scrape @username on tiktok" — specific platform
- "Scrape tiktok @username" — specific platform
- "Scrape twitter @username" — X/Twitter
- "Scrape youtube [channel]" — YouTube
- "Update my competitor posts" — scrape watchlist + analysis
- "Pull latest posts from [platform]" — full pipeline
- "Learn about [topic]" — Mode 2 topic research
- "Research [topic] videos" — Mode 2 across YouTube, TikTok, Instagram
- "Study 50 videos about [topic]" — Mode 2 with high volume
- "Educate yourself on [topic]" — Mode 2 skill education
- "Research how to [topic]" — Mode 2 skill education
- "What are the best [topic] videos" — Mode 2 topic search

## PLATFORM DETECTION

Determine the platform from the user's message:

1. If user explicitly names a platform ("scrape tiktok", "scrape twitter", "scrape youtube", etc.) → use that platform
2. If no platform specified → default to **Instagram** (backward compatible)

---

## Step 1: Determine Targets

Detect the platform (see PLATFORM DETECTION above).

**For Instagram:** Read the competitor watchlist at `10-Niche-Knowledge/personal-brand/instagram-competitors.md`.
**For other platforms:** Check if `10-Niche-Knowledge/personal-brand/[platform]-competitors.md` exists. If not, require the user to provide a username/handle.

- If the user gives a specific username/handle, scrape that account only.
- If no username given and a watchlist exists, scrape all accounts in the watchlist.
- If no watchlist and no username, ask the user for a username.

## Step 2: Scrape via Apify API

Use the platform-specific actor and input format. The core API pattern is the same for ALL platforms — only the actor ID and payload change.

**Universal scrape script (replace ACTOR_ID, PAYLOAD per platform):**

```bash
python -c "
import requests, os, json, time, sys

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('APIFY_API_KEY')
if not API_KEY:
    print('ERROR: APIFY_API_KEY not set in .env')
    sys.exit(1)

actor_id = sys.argv[1]   # e.g., 'apify~instagram-scraper'
payload_json = sys.argv[2]  # JSON string with platform-specific input

payload = json.loads(payload_json)

# Start the scraper run
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}

print(f'Starting scrape with actor {actor_id}...')
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']

# Poll until run finishes (max 10 minutes)
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(120):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
    if i % 6 == 0:
        print(f'  Waiting... ({state})')

if state != 'SUCCEEDED':
    print(f'ERROR: Run ended with status {state}')
    sys.exit(1)

# Fetch results
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
print(json.dumps(results, indent=2))
" "$ACTOR_ID" '$PAYLOAD_JSON'
```

**Platform-specific ACTOR_ID and PAYLOAD:**

#### Instagram
```
ACTOR_ID: apify~instagram-scraper
PAYLOAD: {"directUrls": ["https://www.instagram.com/USERNAME/"], "resultsLimit": LIMIT, "resultsType": "posts"}
```

#### Twitter/X
```
ACTOR_ID: apidojo~tweet-scraper
PAYLOAD: {"twitterHandles": ["USERNAME"], "maxTweets": LIMIT, "sort": "Latest"}
```

#### TikTok
```
ACTOR_ID: clockworks~tiktok-scraper
PAYLOAD: {"profiles": ["USERNAME"], "resultsPerPage": LIMIT}
```

#### YouTube
```
ACTOR_ID: streamers~youtube-scraper
PAYLOAD: {"startUrls": [{"url": "https://www.youtube.com/@USERNAME"}], "maxResults": LIMIT}
```

#### LinkedIn
```
ACTOR_ID: curious_coder~linkedin-post-search-scraper
PAYLOAD: {"profileUrls": ["https://www.linkedin.com/in/USERNAME/"], "maxResults": LIMIT}
```

#### Facebook
```
ACTOR_ID: apify~facebook-posts-scraper
PAYLOAD: {"startUrls": [{"url": "https://www.facebook.com/USERNAME"}], "maxPosts": LIMIT}
```

#### Reddit
```
ACTOR_ID: trudax~reddit-scraper
PAYLOAD: {"startUrls": [{"url": "https://www.reddit.com/user/USERNAME"}], "maxItems": LIMIT, "searchType": "posts"}
```

#### Pinterest
```
ACTOR_ID: epctex~pinterest-scraper
PAYLOAD: {"startUrls": [{"url": "https://www.pinterest.com/USERNAME/"}], "maxItems": LIMIT}
```

#### Threads
```
ACTOR_ID: curious_coder~threads-scraper
PAYLOAD: {"usernames": ["USERNAME"], "maxPosts": LIMIT}
```

Replace `USERNAME` with the target (no @ symbol) and `LIMIT` with number of posts (default 10).

### Topic/Keyword Search Actors (Mode 2 only)

When searching by TOPIC instead of USERNAME, use these actors and payloads:

#### YouTube Keyword Search
```
ACTOR_ID: streamers~youtube-scraper
PAYLOAD: {"searchKeywords": ["KEYWORD1", "KEYWORD2"], "maxResults": LIMIT, "searchType": "video"}
```

#### Instagram Hashtag Search
```
ACTOR_ID: apify~instagram-hashtag-scraper
PAYLOAD: {"hashtags": ["HASHTAG1", "HASHTAG2"], "resultsLimit": LIMIT}
```

#### TikTok Hashtag Search
```
ACTOR_ID: clockworks~free-tiktok-scraper
PAYLOAD: {"hashtags": ["HASHTAG1", "HASHTAG2"], "maxItems": LIMIT}
```

#### Twitter/X Keyword Search
```
ACTOR_ID: apidojo~tweet-scraper
PAYLOAD: {"searchTerms": ["KEYWORD"], "maxTweets": LIMIT, "sort": "Top"}
```

#### Reddit Search
```
ACTOR_ID: trudax~reddit-scraper
PAYLOAD: {"startUrls": [{"url": "https://www.reddit.com/search/?q=KEYWORD&sort=top&t=month"}], "maxItems": LIMIT}
```

Replace `KEYWORD` / `HASHTAG` with the topic (remove spaces for hashtags, e.g., "graphic design" → "graphicdesign"). Replace `LIMIT` with the number of results (default 50 for Mode 2).

**Platform selection for Mode 2:**
- If user specifies a platform ("research [topic] on youtube") → search that platform only
- If user says "research [topic] videos" → search YouTube + TikTok + Instagram
- If user says "learn about [topic]" → search ALL platforms (YouTube, TikTok, Instagram, Twitter, Reddit)
- Default: YouTube + TikTok + Instagram (video-focused platforms)

### Step 2B: Extract Instagram Reel Transcripts

**Only for Instagram scrapes.** After the main scrape completes, run a second pass using the `apify/instagram-reel-scraper` actor to extract transcripts from Reels.

```
ACTOR_ID: apify~instagram-reel-scraper
PAYLOAD: {"directUrls": ["https://www.instagram.com/USERNAME/reels/"], "resultsLimit": LIMIT}
```

Use the same universal scrape script from Step 2 with this actor and payload. The reel scraper returns a `transcript` field (string) for each Reel when audio transcription is available.

After both scrapes complete, merge transcript data into the main post results by matching on `url` or `shortCode`. For each post in the main scrape results:
- If the post is a Reel (type = `Video`) and a matching reel scraper result has a non-empty `transcript` field, attach that transcript to the post.
- If the post is not a Reel or no transcript is available, set `transcript` to `""` (empty string).

Skip this step entirely for non-Instagram platforms.

### Step 2C: Extract YouTube Transcripts (Mode 2 only)

For YouTube results from Mode 2 topic research, extract video transcripts using yt-dlp:

```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download --sub-format vtt -o "%(id)s" "VIDEO_URL" 2>/dev/null && cat "%(id)s.en.vtt" 2>/dev/null | grep -v "^$" | grep -v "^[0-9]" | grep -v "\-\->" | sort -u
```

For each YouTube video in the results:
1. Attempt to extract the auto-generated English transcript
2. If successful, attach the transcript to the video result
3. If yt-dlp fails (private video, no captions), set transcript to "" and continue
4. Limit transcript extraction to the top 10 videos by view count (to avoid excessive yt-dlp calls)

## Step 3: Extract Post Data

Normalize data from any platform into a common structure. Map platform-specific fields:

**Instagram:**
| Field | JSON Key |
|-------|----------|
| Caption | `caption` |
| Transcript | `transcript` (from reel scraper, empty if not a Reel or unavailable) |
| Likes | `likesCount` |
| Comments | `commentsCount` |
| Post date | `timestamp` |
| Post type | `type` (Sidecar = carousel, Video = reel, Image = image) |
| URL | `url` |
| Hashtags | `hashtags` |
| Mentions | `mentions` |

**Twitter/X:**
| Field | JSON Key |
|-------|----------|
| Caption | `text` |
| Likes | `likeCount` |
| Comments | `replyCount` |
| Post date | `createdAt` |
| Post type | `media.type` or "tweet" |
| URL | `url` |
| Retweets | `retweetCount` |
| Views | `viewCount` |
| Bookmarks | `bookmarkCount` |

**TikTok:**
| Field | JSON Key |
|-------|----------|
| Caption | `caption` |
| Likes | `diggCount` |
| Comments | `commentCount` |
| Post date | `createTime` |
| Post type | "video" |
| URL | `url` |
| Views | `playCount` |
| Shares | `shareCount` |
| Saves | `collectCount` |

**YouTube:**
| Field | JSON Key |
|-------|----------|
| Title | `title` |
| Description | `description` |
| Likes | `likeCount` |
| Comments | `commentCount` |
| Post date | `publishedAt` |
| Post type | "video" or "short" |
| URL | `url` |
| Views | `viewCount` |

**LinkedIn:**
| Field | JSON Key |
|-------|----------|
| Caption | `text` |
| Likes | `likesCount` or `numLikes` |
| Comments | `commentsCount` or `numComments` |
| Post date | `postedDate` or `publishedAt` |
| Post type | `type` or "post" |
| URL | `url` |

**Facebook:**
| Field | JSON Key |
|-------|----------|
| Caption | `text` |
| Likes | `likesCount` |
| Comments | `commentsCount` |
| Post date | `timestamp` |
| Post type | `type` |
| URL | `url` |
| Shares | `sharesCount` |

**Reddit:**
| Field | JSON Key |
|-------|----------|
| Title | `title` |
| Caption | `selfText` |
| Likes | `score` |
| Comments | `numComments` |
| Post date | `createdUtc` |
| Post type | `isVideo` ? "video" : "text" |
| URL | `url` |
| Upvote Ratio | `upvoteRatio` |

**Pinterest:**
| Field | JSON Key |
|-------|----------|
| Caption | `description` |
| Saves/Repins | `repinCount` |
| Comments | `commentCount` |
| Post date | `createdAt` |
| Post type | "pin" |
| URL | `url` |
| Outbound Link | `link` |

**Threads:**
| Field | JSON Key |
|-------|----------|
| Caption | `text` |
| Likes | `likesCount` |
| Comments | `repliesCount` |
| Post date | `timestamp` |
| Post type | "thread" |
| URL | `url` |
| Reposts | `repostsCount` |

## Step 4: Save Raw Data to Vault

Save results to `01-Competitors/[platform]/[username]-[YYYY-MM-DD].md` using this format:

```
# [Platform] Scrape: @[username]

> Scraped on [date] via Apify ([actor_id]) | [X] posts collected

---

## Account Summary

- **Posts scraped**: [count]
- **Avg likes**: [calculated]
- **Avg comments**: [calculated]
- **Top post**: [highest engagement post URL]
- **Most used hashtags**: [top 5, if available]

---

## Posts

### Post 1
- **Date**: [date]
- **Type**: [Reel/Carousel/Image/Video/Tweet/Thread/Pin/etc.]
- **Likes**: [count] | **Comments**: [count] | [Other metrics: Views, Shares, Saves, etc.]
- **URL**: [link]
- **Caption**:
> [full caption/text]

- **Transcript** (Reels only, if available):
> [full transcript of what's being said in the video, or empty if not a Reel / no transcript]

- **Hashtags**: [list, if available]

---

[repeat for each post]
```

**Folder mapping:**
- Instagram → `01-Competitors/instagram/`
- Twitter/X → `01-Competitors/twitter/`
- TikTok → `01-Competitors/tiktok/`
- YouTube → `01-Competitors/youtube/`
- LinkedIn → `01-Competitors/linkedin/`
- Facebook → `01-Competitors/facebook/`
- Reddit → `01-Competitors/reddit/`
- Pinterest → `01-Competitors/pinterest/`
- Threads → `01-Competitors/threads/`

Create the subfolder if it does not exist.

## Step 5: Intelligence Analysis

This is the core value step. Analyze ALL collected content and generate insights for 4 vault destinations.

**Important (Instagram):** When transcripts are available for Reels, treat them as a primary content source alongside captions. Many creators say more in their videos than they write in captions. Analyze transcripts for hooks (spoken opening lines), frameworks, teaching patterns, storytelling techniques, and niche knowledge. If a Reel has both a caption and a transcript, analyze both — they often contain different information.

Use the author's username as `[source]` in filenames.

### 5A: Extract Hooks → `02-Hooks/[platform]-hooks.md`

For each post, extract the **first line** (everything before the first newline). This is the hook.

**For Instagram Reels with transcripts:** Also extract the **spoken hook** — the first sentence of the transcript (what they say to open the video). Spoken hooks often differ from caption hooks and reveal what actually stops the scroll.

Append to `02-Hooks/[platform]-hooks.md` (create if missing, never overwrite existing):
- Instagram → `02-Hooks/instagram-hooks.md`
- Twitter/X → `02-Hooks/twitter-hooks.md`
- TikTok → `02-Hooks/tiktok-hooks.md`
- YouTube → `02-Hooks/youtube-hooks.md`
- All others → `02-Hooks/[platform]-hooks.md`

```
## @[source] — [date]

| Hook | Spoken Hook | Likes | Comments | Type |
|------|-------------|-------|----------|------|
| [first line of caption] | [first sentence of transcript, or — if none] | [count] | [count] | [Reel/Carousel/Image/Video/Tweet/etc.] |
| [next post first line] | [spoken hook or —] | [count] | [count] | [type] |
```

### 5B: Content Patterns → `04-Patterns/[source]-content-patterns.md`

Analyze all collected content and identify:

1. **Format patterns** — What content formats do they use? (carousels, reels, threads, static images, videos, tweets, pins)
2. **Structure patterns** — How do they structure their posts? (problem→solution, story→lesson, list, question→answer)
3. **Engagement patterns** — What correlates with high engagement? (length, format, topic, time)
4. **Hook patterns** — What hook formulas appear repeatedly? (number, question, bold claim, callout)
5. **CTA patterns** — How do they close? (follow, save, DM, link, comment)
6. **Spoken content patterns** (Instagram Reels with transcripts only) — How do they deliver value verbally? (pacing, teaching style, storytelling arc, energy level, script vs off-the-cuff)

Write to `04-Patterns/[source]-content-patterns.md` matching the table/quick-reference format:

```
# Content Patterns: @[source] ([platform])

> Analyzed [X] posts on [date] | Platform: [platform]

## Format Performance

| Format | Count | Avg Engagement | Best For |
|--------|-------|----------------|----------|
| [Reel/Video/Tweet/etc.] | [X] | [avg likes+comments] | [reach/authority/saves] |
| [Carousel/Thread/etc.] | [X] | [avg] | [saves/authority] |

## Post Structure Patterns

| Pattern | Example | Frequency | Performance |
|---------|---------|-----------|-------------|
| Problem → Solution | "[first line]..." | [X/total] | [High/Med/Low] |
| Story → Lesson | "[first line]..." | [X/total] | [High/Med/Low] |

## Hook Formulas Used

| Formula | Example | Performance |
|---------|---------|-------------|
| Bold Claim | "[hook]" | [High/Med/Low] |
| Number List | "[hook]" | [High/Med/Low] |

## CTA Patterns

| CTA Type | Example | Frequency |
|----------|---------|-----------|
| [Save] | "Save this for later" | [X/total] |
| [Follow] | "Follow for more" | [X/total] |

## Key Takeaways
- [3-5 bullet points: what works, what to steal, what to avoid]
```

### 5C: Strategic Frameworks → `05-Frameworks/[source]-content-framework.md`

Analyze the overall content strategy and extract a reusable framework. Match the structured framework format:

```
# Content Framework: @[source] ([platform])

> Reverse-engineered from [X] posts on [date] | Platform: [platform]

---

## CONTENT PILLARS

What topics do they consistently post about?

1. **[Pillar 1]** — [description, frequency, example post]
2. **[Pillar 2]** — [description, frequency, example post]
3. **[Pillar 3]** — [description, frequency, example post]

## POSTING FORMULA

What is their repeatable content creation formula?

1. **Hook**: [Their hook style — bold claim, question, callout, etc.]
2. **Body**: [Their body structure — story, list, breakdown, etc.]
3. **Close**: [Their CTA style — save, follow, DM, etc.]

## ENGAGEMENT STRATEGY

How do they drive engagement beyond the post itself?

- **Comment strategy**: [Do they ask questions? Reply to all? Pin comments?]
- **Story integration**: [Do they tease posts in stories? Use polls?]
- **Community plays**: [DM groups, close friends, collab posts?]

## MONETIZATION PATH

How does their content connect to revenue?

- **Products/services mentioned**: [list]
- **Funnel structure**: [free content → lead magnet → paid offer]
- **Soft sell patterns**: [how they sell without being salesy]

## WHAT @big_quiv CAN STEAL

Actionable adaptations for Quivira's brand:

- [Specific tactic 1 — how to adapt it]
- [Specific tactic 2 — how to adapt it]
- [Specific tactic 3 — how to adapt it]

## GAPS THEY ARE MISSING

What are they NOT doing that @big_quiv can exploit?

- [Gap 1]
- [Gap 2]
```

### 5D: Niche Knowledge → `10-Niche-Knowledge/personal-brand/competitor-insights-[source].md`

Extract domain-specific knowledge and positioning insights. Match the rules/observations format:

```
# Competitor Insights: @[source] ([platform])

> Analyzed [X] posts on [date] | Platform: [platform]

## Positioning
- How they position themselves: [description]
- Their unique angle: [what makes them different]
- Their target audience: [who they speak to]
- Their brand voice: [tone, style, energy]

## Content Rules They Follow
1. [Rule observed from their content — e.g., "Never posts without a visual metaphor"]
2. [Rule — e.g., "Always includes data or proof in claims"]
3. [Rule — e.g., "Posts 2x daily, morning and evening"]
4. [Rule — e.g., "Every carousel ends with a save CTA"]
5. [Rule — e.g., "Uses controversy hooks on Mondays"]

## Topics That Perform
- [Topic 1]: [why it works for their audience]
- [Topic 2]: [why it works]
- [Topic 3]: [why it works]

## Narrative Techniques
- [Technique 1 — e.g., "Uses 'I used to be broke' origin story in every 5th post"]
- [Technique 2 — e.g., "Names the enemy (9-to-5, scammers) in hooks"]
- [Technique 3 — e.g., "Creates 'us vs them' framing with community members"]

## Spoken Content Insights (from Reel transcripts, if available)
- [Insight 1 — e.g., "Opens every Reel with a direct question to the viewer"]
- [Insight 2 — e.g., "Teaches in 3-step frameworks spoken casually, not scripted"]
- [Insight 3 — e.g., "Uses slang and cultural references not found in captions"]
- [Key knowledge shared verbally but not in captions — topics, tips, frameworks only revealed in video]

## Lessons for @big_quiv
- [Lesson 1 — specific, actionable]
- [Lesson 2]
- [Lesson 3]
```

---

## Step 6: Report

After all files are written, tell the user:

```
Scraped [X] posts from @[username] on [platform].

Saved to:
- 01-Competitors/[platform]/[filename] — raw posts
- 02-Hooks/[platform]-hooks.md — [Y] hooks extracted
- 04-Patterns/[source]-content-patterns.md — format, structure, engagement patterns
- 05-Frameworks/[source]-content-framework.md — reverse-engineered content strategy
- 10-Niche-Knowledge/personal-brand/competitor-insights-[source].md — positioning & knowledge

Top 3 posts by engagement:
1. [post]
2. [post]
3. [post]

Key insight: [most interesting finding from the analysis]
```

**Mode 2 Report (Topic Research):**

```
Researched [topic] across [X] platforms. Collected [Y] videos/posts.

Saved to:
- 02-Hooks/topic-research-[date].md — [X] hooks extracted ([Y] bold claim, [Z] question, etc.)
- 05-Frameworks/topic-research-[topic]-[date].md — [X] frameworks reverse-engineered
- 08-Templates/topic-research-production-[date].md — production techniques analyzed
- 10-Niche-Knowledge/[folder]/topic-research-[topic]-[date].md — [X] insights extracted

Top 3 videos by engagement:
1. [video title] — [platform] — [views/likes]
2. [video]
3. [video]

Key learning: [most actionable finding from the research]

Suggested vault updates:
- [X] new hook formulas ready to add to 02-Hooks/
- [X] new prompt blocks ready for prompt-library.md
- [X] new framework(s) ready for 05-Frameworks/

Want me to apply these updates to the vault?
```

---

## Step 5-ALT: Skill Education Analysis (Mode 2 only)

When running in Mode 2 (Topic Research), replace the standard Step 5 intelligence analysis with this skill education pipeline. The goal is to extract learnings that make your vault skills smarter.

### 5-ALT-A: Extract Hooks → `02-Hooks/topic-research-[date].md`

From all scraped content, extract the opening hooks (first line of caption, first sentence of transcript/spoken content). Group by hook type:

```
## Topic Research: [topic] — [date]

### Bold Claim Hooks
| Hook | Platform | Source | Engagement |
|------|----------|--------|-----------|
| "[hook text]" | YouTube | @[creator] | [views/likes] |

### Question Hooks
| Hook | Platform | Source | Engagement |
...

### Story Hooks
...

### Data/Number Hooks
...

### Contrarian Hooks
...

### Callout Hooks
...
```

### 5-ALT-B: Extract Content Frameworks → `05-Frameworks/topic-research-[topic]-[date].md`

Analyze the top-performing content (by engagement) and reverse-engineer the frameworks used:

```
# Frameworks Learned: [topic]

> Researched [X] videos/posts on [date] | Platforms: [list]

## Framework 1: [Name]
- **Structure**: [step-by-step breakdown]
- **Why it works**: [analysis]
- **Example**: [specific video/post that uses it]
- **How @big_quiv can use it**: [adaptation]

## Framework 2: [Name]
...
```

### 5-ALT-C: Extract Production Techniques → `08-Templates/topic-research-production-[date].md`

For video content, analyze HOW the content was produced:

```
# Production Techniques: [topic]

> Analyzed [X] videos on [date]

## Visual Patterns
- **Camera angles most used**: [list with frequency]
- **Lighting styles**: [what lighting setups appear in top videos]
- **Scene types**: [environments, backgrounds, settings]
- **Text overlay styles**: [font size, placement, animation]
- **Transition patterns**: [cuts, zooms, swipes, etc.]

## Pacing Patterns
- **Average video length**: [seconds]
- **Hook duration**: [how long before the main content starts]
- **Cut frequency**: [cuts per minute average]
- **Energy arc**: [how energy changes through the video]

## Audio Patterns
- **Music usage**: [background music style, volume relative to voice]
- **Voice delivery**: [pace, tone, energy level]
- **Sound effects**: [if any, what types]

## Thumbnail/Cover Patterns
- **Style**: [what thumbnails/covers look like]
- **Text on thumbnail**: [yes/no, what kind]
- **Colors**: [dominant colors]

## Prompt Library Updates
Based on these observations, add these new prompt blocks to 08-Templates/prompt-library.md:
- [any new camera angles, lighting styles, moods, or environments discovered]
```

### 5-ALT-D: Extract Niche Knowledge → `10-Niche-Knowledge/[relevant-folder]/topic-research-[topic]-[date].md`

Extract domain-specific knowledge shared in the content:

```
# Topic Research: [topic]

> Extracted from [X] videos/posts on [date]

## Key Insights
1. [Insight from content — fact, technique, strategy, or tip]
2. [Insight]
3. [Insight]
...

## Expert Opinions Cited
- [Creator name]: "[what they said]"
- [Creator name]: "[what they said]"

## Tools/Resources Mentioned
- [Tool 1]: [what it does, who mentioned it]
- [Tool 2]: [what it does]

## Common Mistakes Identified
- [Mistake that multiple creators warn about]
- [Mistake]

## Step-by-Step Processes Found
### [Process Name]
1. [Step]
2. [Step]
...
```

### 5-ALT-E: Update Existing Vault Files (conditional)

After generating the research files above, check if any findings should be appended to existing vault files:

1. **New hook formulas discovered** → Append to `02-Hooks/[platform]-hooks.md` (never overwrite)
2. **New prompt blocks** (camera angles, lighting, moods not in prompt-library) → Suggest additions to `08-Templates/prompt-library.md` but ASK before modifying
3. **New frameworks** → Check if similar framework exists in `05-Frameworks/`. If not, save as new. If similar, suggest merging.
4. **Niche knowledge** → Save to the correct subfolder based on topic:
   - Trading/crypto → `10-Niche-Knowledge/crypto-trading/`
   - AI/tools → `10-Niche-Knowledge/artificial-intelligence/`
   - Personal brand/content → `10-Niche-Knowledge/personal-brand/`
   - Web3 → `10-Niche-Knowledge/web3-development/`

Always ASK before modifying existing template files (prompt-library.md, character-library.md, etc.). Only auto-save to research-specific files.

---

## RULES

- Maximum 10 posts per account per scrape (Apify rate limits)
- Maximum 5 accounts per session
- Always extract the first line of each caption as a hook
- Do not scrape the same account more than once per day — check if `01-Competitors/[platform]/[username]-[today's date].md` already exists before scraping
- Save raw data so skills can read it during Intelligence Gathering
- **Never modify any existing command/skill files** — only write to vault data folders
- If APIFY_API_KEY is missing from .env, tell the user to add it and provide signup link: https://apify.com
- If a scrape file already exists for that username + date, append a number (e.g., `username-2026-03-21-2.md`)
- When analyzing fewer than 3 posts, note that patterns may be unreliable due to small sample size
- Always match the existing format of each vault folder — read an example file first if unsure
- Intelligence analysis (Step 5) always runs — never skip it
- Default to Instagram when no platform is specified (backward compatible)
- Create platform subfolders under `01-Competitors/` as needed
- LinkedIn scraping has stricter limits — warn user about max ~500 profiles/day
- Some platforms (TikTok, YouTube) return view counts — include these in engagement analysis when available
- **Mode 2 limits:** Maximum 50 results per platform per topic search. Maximum 3 platforms per session.
- **Mode 2 transcript extraction:** Limit YouTube transcript extraction to top 10 videos by view count
- **Mode 2 vault updates:** Always ASK before modifying existing template files (prompt-library.md, character-library.md, etc.). Auto-save is only for new research files.
- **Mode 2 file naming:** Use `topic-research-[topic-slug]-[date].md` format for all Mode 2 output files
- **Mode 2 keyword conversion:** Convert topic phrases to hashtags by removing spaces (e.g., "graphic design" → "graphicdesign", "video editing tips" → "videoeditingtips")
- **Mode 2 dedup:** Before saving, check if a topic research file for the same topic already exists from the same day. If yes, append new findings instead of creating a duplicate file.
