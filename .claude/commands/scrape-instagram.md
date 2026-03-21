---
name: scrape-instagram
description: "Scrape Instagram competitor posts using Apify and save to vault. Triggers: 'scrape instagram', 'scrape @username', 'update competitors', 'pull instagram posts'"
allowed-tools: ["Read", "Write", "Bash", "WebFetch"]
---

# Instagram Scraper

## ROLE
You scrape Instagram posts from competitor accounts using Apify and save them to the vault so all other skills can read them during Intelligence Gathering.

## WHEN TO USE
- "Scrape @username"
- "Update my competitor posts"
- "Pull latest Instagram posts from competitors"
- "Scrape instagram"

## HOW IT WORKS

### Step 1: Determine Targets

Read the competitor watchlist at `10-Niche-Knowledge/personal-brand/instagram-competitors.md`.

- If the user gives a specific `@username`, scrape that account only.
- If no username given, scrape all accounts in the watchlist.
- If the watchlist is empty and no username given, ask the user for a username.

### Step 2: Scrape via Apify API

Run this Python script for each target username. The script handles the full Apify actor lifecycle (start run, poll for completion, fetch results):

```bash
python -c "
import requests, os, json, time, sys

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('APIFY_API_KEY')
if not API_KEY:
    print('ERROR: APIFY_API_KEY not set in .env')
    sys.exit(1)

username = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

# Start the scraper run
url = 'https://api.apify.com/v2/acts/apify~instagram-scraper/runs'
headers = {'Authorization': f'Bearer {API_KEY}'}
payload = {
    'directUrls': [f'https://www.instagram.com/{username}/'],
    'resultsLimit': limit,
    'resultsType': 'posts'
}

print(f'Starting scrape for @{username} (limit: {limit})...')
resp = requests.post(url, json=payload, headers=headers, timeout=30)
resp.raise_for_status()
run = resp.json()
run_id = run['data']['id']
dataset_id = run['data']['defaultDatasetId']

# Poll until run finishes (max 5 minutes)
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}'
for i in range(60):
    time.sleep(5)
    status = requests.get(status_url, headers=headers, timeout=15).json()
    state = status['data']['status']
    if state in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
    print(f'  Waiting... ({state})')

if state != 'SUCCEEDED':
    print(f'ERROR: Run ended with status {state}')
    sys.exit(1)

# Fetch results
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
results = requests.get(dataset_url, headers=headers, timeout=30).json()
print(json.dumps(results, indent=2))
" "$USERNAME" "$LIMIT"
```

Replace `$USERNAME` with the target (no @ symbol) and `$LIMIT` with number of posts (default 10).

### Step 3: Extract Post Data

For each post in the results, extract:

| Field | JSON Key |
|-------|----------|
| Caption | `caption` |
| Likes | `likesCount` |
| Comments | `commentsCount` |
| Post date | `timestamp` |
| Post type | `type` (Sidecar = carousel, Video = reel, Image = image) |
| URL | `url` |
| Display URL | `displayUrl` |
| Hashtags | `hashtags` |
| Mentions | `mentions` |

### Step 4: Save to Vault

Save results to `01-Competitors/instagram/[username]-[YYYY-MM-DD].md` using this format:

```
# Instagram Scrape: @[username]

> Scraped on [date] via Apify | [X] posts collected

---

## Account Summary

- **Posts scraped**: [count]
- **Avg likes**: [calculated]
- **Avg comments**: [calculated]
- **Top post**: [highest engagement post URL]
- **Most used hashtags**: [top 5]

---

## Posts

### Post 1
- **Date**: [date]
- **Type**: [Reel/Carousel/Image]
- **Likes**: [count] | **Comments**: [count]
- **URL**: [link]
- **Caption**:
> [full caption text]

- **Hashtags**: [list]

---

### Post 2
[repeat format]

---

## Patterns Noticed

> Auto-generated observations:
> - Posting frequency: [X posts per week]
> - Best performing content type: [Reels/Carousels/Images]
> - Common themes: [list]
> - Hook patterns: [first lines of top posts]
```

### Step 5: Extract Hooks

For each scraped post, extract the **first line of the caption** (everything before the first newline). This is the hook.

Append all hooks to `02-Hooks/instagram-hooks.md` in this format:

```
## @[username] — [date]

| Hook | Likes | Comments | Type |
|------|-------|----------|------|
| [first line of caption] | [count] | [count] | [Reel/Carousel/Image] |
| [next post first line] | [count] | [count] | [type] |
```

Create the file if it does not exist. If it exists, append to the bottom (do not overwrite previous hooks).

### Step 6: Report

After saving, tell the user:

"Scraped [X] posts from @[username]. Saved to 01-Competitors/instagram/. Extracted [Y] hooks to 02-Hooks/."

Also show:
- Top 3 posts by engagement (likes + comments)
- Any patterns worth noting

## RULES

- Maximum 10 posts per account per scrape (Apify rate limits)
- Maximum 5 accounts per session
- Always extract the first line of each caption as a hook
- Do not scrape the same account more than once per day — check if `01-Competitors/instagram/[username]-[today's date].md` already exists before scraping
- Save raw data so skills can read it during Intelligence Gathering
- Never modify any existing command files
- If APIFY_API_KEY is missing from .env, tell the user to add it and provide signup link: https://apify.com
- If a scrape file already exists for that username + date, append a number (e.g., `username-2026-03-21-2.md`)
