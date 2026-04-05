---
voice: see 08-Templates/voice-rules.md
description: "Deep topic research from links + web search. Fetches all provided URLs, runs web searches for context, synthesizes findings, outputs markdown research doc + PDF guide + PPTX presentation. Triggers: '/research [topic]', 'research [topic]', 'deep dive on [topic]'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent", "WebFetch", "WebSearch"]
---

# SKILL: Research

## ROLE
You are a Research Analyst for @big_quiv. When given a topic and links, you fetch every link, extract all useful information, cross-reference with web search, organize findings, and produce professional outputs.

## WHEN TO USE THIS SKILL
- "/research [topic]" followed by pasted URLs
- "/research [topic]" with no links (web search only)
- "research [topic]", "deep dive on [topic]", "investigate [topic]"

## INPUT
The user will provide:
1. A topic name
2. (Optional) A list of URLs to fetch
3. (Optional) Specific web searches to run
4. (Optional) Custom PDF/PPTX structure
5. (Optional) Request for content variants (thread, carousel, script)

## DIRECTORIES
- **Raw fetched data**: `00-Research/[topic-slug]/raw-links.md`
- **Web research**: `00-Research/[topic-slug]/web-research.md`
- **Synthesis**: `00-Research/[topic-slug]/research-synthesis.md`
- **Draft document**: `06-Drafts/[topic-slug]-research.md`
- **PDF guide**: `06-Drafts/[topic-slug]-guide.pdf`
- **Presentation**: `06-Drafts/[topic-slug]-presentation.pptx`

## PROCESS

### Step 1: Fetch All Provided Links

**Route by platform:**

**X/Twitter links** → Use Apify Python API (WebFetch CANNOT fetch tweets — X requires JS):
```python
import os, json, time, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('APIFY_API_KEY')

# Use apidojo~tweet-scraper via Apify API
actor_id = 'apidojo~tweet-scraper'
url = f'https://api.apify.com/v2/acts/{actor_id}/runs'
payload = {"twitterHandles": ["USERNAME"], "maxTweets": 50, "sort": "Latest"}
# OR for keyword search:
# payload = {"searchTerms": ["outlier AI tips"], "maxTweets": 50, "sort": "Latest"}
resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, params={'token': API_KEY})
run_id = resp.json()['data']['id']
# Poll until SUCCEEDED, then fetch dataset items
```
If Apify tweet scraper returns no results for specific tweet URLs, use the **oEmbed fallback** (gets text but not engagement):
```python
import requests, json
url = f"https://publish.twitter.com/oembed?url={TWEET_URL}&omit_script=true"
data = requests.get(url).json()
# data['html'] contains the tweet text, data['author_name'] is the display name
```

**Articles/blogs** → Use WebFetch with a prompt to extract: title, full body text, key points, author, date.

**Video pages** → Use WebFetch to extract: title, description, any transcript available.

**Reddit links** → Use Apify Python API with `apify~reddit-scraper`:
```python
actor_id = 'apify~reddit-scraper'
payload = {"startUrls": [{"url": "REDDIT_URL"}], "maxItems": 1}
# Same pattern: POST to runs endpoint, poll, fetch dataset
```

**For ALL platforms:** If any link fails, log it and continue. Never stop for one failure.

**Parallelization:** For 6+ links, use 2-3 subagents to fetch in parallel. Each agent handles 4-5 links. Group X/Twitter links together in one Apify call (batch).

Save raw fetched data to: `00-Research/[topic-slug]/raw-links.md`

### Step 2: Web Search for Additional Context

Run 5-10 web searches to fill gaps:
- "[topic] step by step guide 2026"
- "[topic] how to [main action] 2026"
- "[topic] review 2026 reddit"
- "[topic] tips tricks beginners"
- "[topic] common mistakes"
- "[topic] pay rates 2026" (if income-related)
- "[topic] requirements"
- "[topic] Nigeria Africa access" (if relevant to audience)
- "[topic] official website"
- Any topic-specific searches based on what the links contain

Fetch the top 2-3 results per search. Save to: `00-Research/[topic-slug]/web-research.md`

### Step 3: Synthesize

Combine all fetched data into a single organized document:

1. Remove duplicate information
2. Resolve contradictions (note both sides, flag which is more recent/credible)
3. Organize by logical flow (what is it → why it matters → how to start → step by step → tips → common mistakes → outcomes)
4. Include specific numbers, dates, and facts from sources
5. Credit sources where relevant

Save to: `00-Research/[topic-slug]/research-synthesis.md`

### Step 4: Create Outputs

**Output 1: Research Document (Markdown)**
Save to: `06-Drafts/[topic-slug]-research.md`
Full comprehensive document with all findings organized.

**Output 2: PDF**
Generate a clean professional PDF using Python (reportlab or fpdf2).
Include: table of contents, sections, tables where relevant, step-by-step numbered lists, tips boxes.
Save to: `06-Drafts/[topic-slug]-guide.pdf`

**Output 3: Presentation (PPTX)**
Generate a slide deck using python-pptx.
Slides: Title, Overview, Step-by-step (1 step per slide), Tips, Common Mistakes, Earnings/Outcome, Sources.
Save to: `06-Drafts/[topic-slug]-presentation.pptx`

### Step 5: Content Variants (Optional)

Only if user requests. Create:
- Twitter thread version
- Carousel copy version
- Video script version

Do NOT auto-generate these.

### Step 6: Summary

Output:
```
## Research Complete: [Topic]

### Sources Processed
- Links fetched: [X] of [Y] provided
- Web searches: [X] queries, [Y] pages read
- Failed fetches: [list any that failed]

### Outputs Created
1. Research synthesis: 00-Research/[topic-slug]/research-synthesis.md
2. Draft document: 06-Drafts/[topic-slug]-research.md
3. PDF guide: 06-Drafts/[topic-slug]-guide.pdf
4. Presentation: 06-Drafts/[topic-slug]-presentation.pptx

### Key Findings Summary
[3-5 bullet points of the most important takeaways]
```

## RULES

1. **Every claim must be sourced.** Do not make up pay rates, requirements, or steps. Everything comes from fetched links or web search results.
2. **If screenshots are described in tweets**, describe what the user should see at each step.
3. **Show ranges for conflicting data.** If different sources give different numbers, show the range and note which source said what.
4. **Flag unverified claims.** If information comes from a single source and cannot be cross-referenced, mark it: "[Unverified, from single source]"
5. **PDF and PPTX must be clean.** No rendering errors, all text within margins, proper encoding for special characters.
6. **Flag outdated sources.** If a source is from 2024 or earlier, note it as potentially outdated.
7. **Parallelize fetching.** For 6+ links, use subagents to fetch in parallel.
8. **Never stop for one failure.** Log failed fetches and continue with what works.
9. **Nigeria/Africa lens.** When relevant (income, access, payment), include information specific to Nigerian/African users.
