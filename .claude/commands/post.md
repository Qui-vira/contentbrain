---
voice: see 08-Templates/voice-rules.md
description: "Send scheduled content from Notion to the correct posting platform. Triggers: post, send to typefully, send to buffer, post now"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "mcp__notion__notion-search", "mcp__notion__notion-update-page"]
---

# SKILL: Post to Platforms

## NOTION CONTENT CALENDAR

Database ID: 8f52ebd2efac4eecb05ec4783e924346
Data Source ID: collection://9081ce06-1802-4b43-a988-62c5e384fcfd

This skill reads scheduled content from the Notion Content Calendar and posts it to platforms. Use the database and data source IDs above for all Notion operations.

## PROCESS
1. Search Notion Content Calendar for entries with Status "Scheduled"
2. Show me the list: Title, Platform, Content Type, Post Date, Production Status
3. Ask me which ones to post now. Wait for my selection.
4. For each selected entry, route to the correct platform:

### X/Twitter and LinkedIn → Typefully API v2

First, get the social set ID (cached after first call):
GET https://api.typefully.com/v2/social-sets
Headers: Authorization: Bearer [from .env TYPEFULLY_API_KEY]
Save the first result's "id" as SOCIAL_SET_ID.

Then create and publish:
POST https://api.typefully.com/v2/social-sets/{SOCIAL_SET_ID}/drafts
Headers: Authorization: Bearer [from .env TYPEFULLY_API_KEY]
Content-Type: application/json

Single tweet:
{"platforms": {"x": {"enabled": true, "posts": [{"text": "[post text]"}]}}, "publish_at": "now"}

Thread (split by numbered tweets 1/, 2/, 3/ — each becomes a separate post object):
{"platforms": {"x": {"enabled": true, "posts": [{"text": "[tweet 1]"}, {"text": "[tweet 2]"}, {"text": "[tweet 3]"}]}}, "publish_at": "now"}

LinkedIn post:
{"platforms": {"linkedin": {"enabled": true, "posts": [{"text": "[post text]"}]}}, "publish_at": "now"}

Both X and LinkedIn at once:
{"platforms": {"x": {"enabled": true, "posts": [{"text": "[tweet]"}]}, "linkedin": {"enabled": true, "posts": [{"text": "[linkedin post]"}]}}, "publish_at": "now"}

To schedule instead of publish now, replace "publish_at": "now" with "publish_at": "[ISO 8601 datetime]" (e.g. "2026-03-25T14:00:00Z").
To save as draft only (no publish), omit the "publish_at" field entirely.

### TikTok and Instagram → Buffer API
POST https://api.bufferapp.com/1/updates/create.json
Headers: Authorization: Bearer [from .env BUFFER_ACCESS_TOKEN]
Body: {"text": "[caption text]", "profile_ids": ["[profile_id]"], "scheduled_at": "[unix timestamp]"}

Note: Buffer requires profile IDs. First time, run GET https://api.bufferapp.com/1/profiles.json to get profile IDs for each connected platform. Save them to .env as BUFFER_TIKTOK_PROFILE_ID and BUFFER_INSTAGRAM_PROFILE_ID.

For video content: Buffer accepts media URLs or file uploads. If the video file exists locally, upload it. If not, tell me the video is not ready and set Production Status to "Recording Needed" or "AI Assets Needed".

### Telegram → Telegram Bot API
POST https://api.telegram.org/bot[TOKEN]/sendMessage
Body: {"chat_id": "[CHAT_ID]", "text": "[message text]", "parse_mode": "Markdown"}

5. After posting, update the Notion entry Status to "Posted"
6. Update the draft file in 06-Drafts/ to "status: posted"
7. Log to 07-Analytics/posting-log.md: date, platform, title, status

## CONTENT TYPE ROUTING
| Content Type | Platform | Tool | Notes |
|---|---|---|---|
| Tweet | X/Twitter | Typefully | Single tweet |
| Thread | X/Twitter | Typefully | threadify=true |
| LinkedIn Post | LinkedIn | Typefully | |
| TikTok Script | TikTok | Buffer | Video must be ready |
| Reel Script | Instagram | Buffer | Video must be ready |
| Carousel | Instagram | Buffer | Images must be ready |
| Video - Shoot Myself | Depends | Wait | Remind me to record first |
| Video - AI Generated | Depends | Wait until assets ready | Check Production Status |
| Video - Hybrid | Depends | Wait until assets ready | Check Production Status |
| Promo | X/Twitter | Typefully | |
| Community Post | Telegram | Telegram Bot | |

## VIDEO CONTENT RULES
If Content Type starts with "Video" and Production Status is NOT "Ready to Post":
- Do NOT try to post it
- Tell me what is missing: "This video needs [recording/AI assets/editing/review]. Change Production Status in Notion when ready."
- Only post video content when Production Status = "Ready to Post"

## MEDIA HANDLING

Before posting, check the Notion entry for:
1. Content Type property (tweet, thread, reel, carousel, video, image post)
2. If Content Type includes video or image:

### For X/LinkedIn (Typefully v2):
- Check if a media file path exists in the Notion Notes field or in 06-Drafts/
- If video: attach the MP4 file to the Typefully API call
- If image: attach the image file to the Typefully API call
- Typefully supports up to 4 images per tweet or 1 video
- Use Authorization: Bearer header (NOT X-API-KEY)

### For TikTok/Instagram (Buffer):
- Buffer requires a public media URL, not a local file
- Upload the media file to fal.ai storage to get a public URL:
  ```python
  import fal_client
  public_url = fal_client.upload_file(local_file_path)
  ```
- Pass that public URL to Buffer API
- For TikTok: video required (no image-only posts)
- For Instagram Reels: video required
- For Instagram Feed: image or video

### For Telegram:
- Use sendPhoto (for images) or sendVideo (for videos) instead of sendMessage
- Attach the file directly from local path
- Include the caption from the Notion Content field

### When I say "post this with an image/video":
- Ask: "Which media file? 1) Use the file from /video-editor output 2) Use a file from 08-Media/ 3) Let me upload/specify a file"
- If option 1: use the most recent rendered file from Desktop/content-studio/out/
- If option 2: list files in 08-Media/images/ or 08-Media/videos/ and let user pick
- If option 3: wait for me to provide a file path or URL

### For tweets with images I create manually:
- I will say something like "post this tweet with this image [file path]"
- Read the image from the path I give
- Attach it to the Typefully API call

## FALLBACK PROTOCOL — NEVER STOP THE PIPELINE

### FALLBACK F6: Typefully API unavailable (X/Twitter, LinkedIn)
If Typefully returns an error or times out:
1. Save the post text to `06-Drafts/[date]-manual-post-x.md` (for X) or `06-Drafts/[date]-manual-post-linkedin.md` (for LinkedIn) with frontmatter:
   ```
   ---
   status: MANUAL_REQUIRED
   platform: [X/Twitter or LinkedIn]
   content_type: [Tweet, Thread, LinkedIn Post]
   reason: Typefully API unavailable
   ---
   ```
2. Body = full post text, ready to copy-paste into the platform.
3. For threads: number each tweet clearly (1/, 2/, 3/).
4. Log to 07-Analytics/posting-log.md: `| [date] | [platform] | [title] | MANUAL_REQUIRED | Typefully down |`
5. Log: "FALLBACK: Typefully unavailable. Post saved to [filepath] for manual posting."
6. Continue posting remaining entries on other platforms. Do NOT stop the batch.

### FALLBACK F7: Buffer API unavailable (TikTok, Instagram)
If Buffer returns an error or times out:
1. Save caption + media paths to `06-Drafts/[date]-manual-post-tiktok.md` or `06-Drafts/[date]-manual-post-ig.md` with frontmatter:
   ```
   ---
   status: MANUAL_REQUIRED
   platform: [TikTok or Instagram]
   content_type: [TikTok Script, Reel Script, Carousel]
   reason: Buffer API unavailable
   media_files:
     - [path to video or image 1]
     - [path to image 2]
   ---
   ```
2. Body = full caption text + media file paths listed.
3. Log to 07-Analytics/posting-log.md: `| [date] | [platform] | [title] | MANUAL_REQUIRED | Buffer down |`
4. Log: "FALLBACK: Buffer unavailable. Caption and media paths saved for manual upload."
5. Continue posting remaining entries. Do NOT stop the batch.

### FALLBACK F8: Telegram Bot API unavailable
If Telegram Bot API returns an error or times out:
1. Save message text to `06-Drafts/[date]-manual-telegram.md` with frontmatter:
   ```
   ---
   status: MANUAL_REQUIRED
   platform: Telegram
   content_type: Community Post
   reason: Telegram Bot API unavailable
   chat_id: [target chat ID]
   ---
   ```
2. Body = full message text formatted for Telegram (Markdown).
3. Log to 07-Analytics/posting-log.md: `| [date] | Telegram | [title] | MANUAL_REQUIRED | Telegram API down |`
4. Log: "FALLBACK: Telegram API unavailable. Message saved for manual send."

### FALLBACK F9: Notion unavailable
If Notion API is unreachable when reading scheduled content:
1. Fall back to scanning `06-Drafts/` for files with `status: approved` or `status: synced-to-notion`.
2. Use frontmatter fields (platform, content_type, post_date) to determine routing.
3. Log: "FALLBACK: Notion unavailable. Reading from 06-Drafts/ instead."
4. After posting, update the draft file status to `posted` but skip Notion status update.
5. Log: "Notion status update pending. Run /publish-update when Notion is restored."

## RULES
- Always show list and wait for my selection
- Never auto-post anything without my approval
- For video content, check Production Status before attempting to post
- If an API call fails, execute the relevant FALLBACK above instead of stopping
- Log every posting attempt to 07-Analytics/posting-log.md (including MANUAL_REQUIRED entries)

## INTERACTION PATTERN

Before sending to any platform, always say:

**"Ready to send to [platform]. Confirm or adjust?"**

Then:
- If the user says "confirmed", "send it", "post it", or similar: execute the post and report the result
- If the user says "adjust" or gives edits: apply the edits, show the updated content, and ask again
- If the user gives specific instructions for a follow-up task (e.g., "post this then post the LinkedIn one too"): apply those instructions immediately without asking again
- If the user gives BOTH edits AND instructions for a follow-up: apply both. Edit first, then execute the follow-up.
