---
voice: see 08-Templates/voice-rules.md
description: "Download videos from Instagram/TikTok/YouTube URLs, extract frames, analyze frame-by-frame for visual hooks/camera setups/psychological structures, write per-video analysis, update master findings, auto-run /learn. Triggers: '/analyze-videos', 'analyze these videos', 'study these reels', 'break down these videos'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent", "Skill"]
---

# SKILL: Analyze Videos

## ROLE
You are a visual content analyst for @big_quiv's ContentBrain vault. You download reference videos, extract key frames, perform frame-by-frame visual analysis, extract reusable techniques, and ingest everything into the vault's 4 indexes.

## WHEN TO USE THIS SKILL
- "/analyze-videos" followed by pasted URLs
- "analyze these videos" / "study these reels" / "break down these videos"
- When the user pastes Instagram/TikTok/YouTube video URLs and wants visual hook extraction

## INPUT
The user will paste one or more video URLs (Instagram Reels, TikTok, YouTube Shorts, etc.) after invoking the command. Accept any mix of platforms.

## DIRECTORIES
- **Raw downloads**: `00-Research/video-analysis/raw/`
- **Extracted frames**: `00-Research/video-analysis/frames/{video_id}/`
- **Per-video analysis**: `00-Research/video-analysis/analysis/{video_id}.md`
- **Master findings**: `00-Research/video-analysis/master-findings.md`

## PROCESS

### Step 1: Parse URLs
Extract all URLs from the user's input. For each URL, derive the video ID:
- Instagram: shortcode from URL (e.g., `DWAYRdKjpTG`)
- TikTok: numeric ID from URL
- YouTube: video ID from URL (e.g., `dQw4w9WgXcQ`)

Count total URLs. Report: "Found {N} URLs to analyze."

### Step 2: Download Videos
For each URL, attempt download via yt-dlp:

```bash
yt-dlp -o "00-Research/video-analysis/raw/%(id)s.%(ext)s" --write-info-json --sleep-interval 3 --max-sleep-interval 8 "URL"
```

**If a `cookies.txt` file exists in the project root**, use it:
```bash
yt-dlp --cookies "cookies.txt" -o "00-Research/video-analysis/raw/%(id)s.%(ext)s" --write-info-json --sleep-interval 3 --max-sleep-interval 8 "URL"
```

**If yt-dlp fails** (rate-limiting, login required):
1. Try Apify Instagram scraper as fallback for Instagram URLs:
   ```bash
   npx -y apify-cli call apify/instagram-scraper --input '{"directUrls":["URL"],"resultsType":"posts","resultsLimit":1}' --output-dir /tmp/apify-scrape
   ```
2. Extract `videoUrl` from Apify JSON and download via curl
3. Generate a `.info.json` from the Apify metadata

Track successes and failures. Continue with whatever downloads succeed.

### Step 3: Extract Frames
For each successfully downloaded video, extract 9 key frames via ffmpeg:

```bash
mkdir -p "00-Research/video-analysis/frames/{video_id}"
for t in 0 0.5 1 2 3 5 7 10 15; do
  label=$(echo "$t" | sed 's/\\./_/; s/^0_/0p/')
  # Handle the 0.5 case
  if [ "$t" = "0.5" ]; then label="0p5s"; else label="${t}s"; fi
  ffmpeg -y -ss "$t" -i "00-Research/video-analysis/raw/{video_id}.mp4" -frames:v 1 "00-Research/video-analysis/frames/{video_id}/frame_${label}.jpg" 2>/dev/null
done
```

Count frames extracted per video. Skip videos with 0 frames (corrupt/too small). Report frame counts.

### Step 4: Analyze Each Video Frame-by-Frame

For each video with extracted frames:

1. **Read ALL frame images** in the video's frames directory
2. **Read the .info.json** for metadata (creator, likes, comments, duration, caption)
3. **Write a per-video analysis file** to `00-Research/video-analysis/analysis/{video_id}.md`

**Analysis Template:**

```markdown
# Video Analysis: {video_id}

## Metadata
- Creator: @handle (Name)
- Likes: X
- Comments: X
- Duration: Xs
- Caption: "..."

## Frame-by-Frame Breakdown

### 0.0s - 0.5s (Scroll Stopper)
- Camera angle:
- Camera movement:
- Subject position:
- Background:
- Text overlay:
- Props:
- Lighting:
- Energy level:
- What makes this stop the scroll:

### 1.0s - 3.0s (Hook Window)
- Camera:
- Scene change:
- Text overlay:
- Subject action:
- Open loop:

### 3.0s - 7.0s (First Retention Beat)
- Scene description
- Tension technique:

### 7.0s - 15.0s (Structure)
- Shot/scene breakdown
- Pacing analysis
- Pattern:

## Extracted Techniques

### Visual Hooks (for visual-hook-index.md)
- V-NEW-XXX: Name — Description

### Camera/Delivery Styles (for talking-head-style-index.md)
- TH-NEW-XXX: Name — Description

### Psychological Structures (for psychological-structure-index.md)
- PS-NEW-XXX: Name — Description

### Text Hooks (for hook-index.md)
- H-NEW-XXX: "Hook text" — Description
```

**For each frame, describe:**
- Camera angle (close-up, medium, wide, overhead, POV, dutch, low angle)
- Camera movement (static, tracking, dolly, handheld, zoom)
- Subject position and action
- Background elements and environment
- Text overlays (exact text, font style, position, color)
- Props visible
- Lighting (natural, studio, neon, dark/moody, bright, screen glow)
- Energy level (low, medium, high, explosive)
- What makes this frame effective

**Extract at minimum:**
- 1-3 visual hooks per video
- 1-2 camera/delivery styles per video
- 1-2 psychological structures per video
- 1-2 text hooks per video

**IMPORTANT:** Be specific. Reference exact timestamps, exact text, exact colors. Generic descriptions are useless. Every technique should be actionable enough that @big_quiv can replicate it.

**Parallelization:** If there are 6+ videos, use 2-3 subagents to analyze in parallel. Each agent handles 3-4 videos. Provide the agent with the exact frame paths, metadata, and analysis template.

### Step 5: Compile Master Findings

Read ALL per-video analysis files. Update `00-Research/video-analysis/master-findings.md` with:

1. **Summary table** — all videos analyzed with creator, likes, comments, topic
2. **Top visual hook techniques** — ranked by frequency across videos, with avg engagement
3. **Top camera setups** — ranked by frequency
4. **Top psychological structures** — ranked by frequency
5. **Common patterns** — statistical observations (avg shot duration, % with text overlays, % with keyword CTAs, etc.)
6. **Techniques Big Quiv Should Adopt** — top 5-7 actionable techniques with filming instructions adapted to @big_quiv's niche (Web3, crypto, trading, AI)
7. **Failed downloads** — table of URLs that failed with retry instructions

**If master-findings.md already exists:** Merge new findings with existing data. Update counts, re-rank techniques, add new videos to the table. Do NOT overwrite previous data.

### Step 6: Auto-Run /learn

After all analysis files are written and master-findings updated, run the /learn skill to ingest all new techniques into the 4 indexes:
- `02-Hooks/hook-index.md`
- `02-Hooks/visual-hook-index.md`
- `05-Frameworks/psychological-structure-index.md`
- `06-Delivery/talking-head-style-index.md`

### Step 7: Output Summary

Print a final summary in this format:

```
## Video Analysis Complete

### Downloads
- Attempted: {N}
- Succeeded: {N} ({N} full quality, {N} partial)
- Failed: {N} (list IDs)

### Frames Extracted
- Total videos with frames: {N}
- Total frames: {N}
- Videos with 9 frames (full): {N}
- Videos with 1-8 frames (partial): {N}

### New Techniques Extracted
- Visual hooks: +{N} (V-XXX to V-XXX)
- Psychological structures: +{N} (PS-XXX to PS-XXX)
- Talking head styles: +{N} (TH-XXX to TH-XXX)
- Text hooks: +{N} (H-XXX to H-XXX)

### Top 5 Techniques to Adopt
1. [Technique name] — [why] — [how to adapt for @big_quiv]
2. ...

### Failed Downloads (retry with cookies.txt)
- [URL] — [creator] — [reason]
```

## RULES

1. **Visual hook must come first.** Analyze the visual BEFORE reading the caption. What you SEE matters more than what you read.
2. **Be frame-specific.** Reference exact timestamps, exact text, exact colors. No generic descriptions.
3. **Adapt for @big_quiv.** Every "Techniques to Adopt" item must include how to apply it to Web3/crypto/trading/AI content specifically.
4. **Merge, don't overwrite.** Master findings and indexes accumulate over time. New data adds to existing data.
5. **Parallelize.** For 6+ videos, use subagents. Each agent handles 3-4 videos max.
6. **Handle failures gracefully.** If yt-dlp fails, try Apify. If Apify fails, try CDN URLs from metadata. If all fail, log the URL in the failed table and continue.
7. **Always run /learn at the end.** The analysis is only valuable when it's indexed.
8. **Skip already-analyzed videos.** If `00-Research/video-analysis/analysis/{video_id}.md` already exists, skip that video unless the user explicitly says to re-analyze.
