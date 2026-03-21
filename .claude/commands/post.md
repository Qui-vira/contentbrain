---
description: "Send scheduled content from Notion to the correct posting platform. Triggers: post, send to typefully, send to buffer, post now"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "mcp__notion__notion-search", "mcp__notion__notion-update-page"]
---

# SKILL: Post to Platforms

## PROCESS
1. Search Notion Content Calendar for entries with Status "Scheduled"
2. Show me the list: Title, Platform, Content Type, Post Date, Production Status
3. Ask me which ones to post now. Wait for my selection.
4. For each selected entry, route to the correct platform:

### X/Twitter and LinkedIn → Typefully API
POST https://api.typefully.com/v1/drafts/
Headers: X-API-KEY: [from .env TYPEFULLY_API_KEY]
Body: {"content": "[post text]", "schedule-date": "[ISO date if scheduling]"}

For threads on X: split content by numbered tweets (1/, 2/, 3/), send as threadify=true

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

### For X/LinkedIn (Typefully):
- Check if a media file path exists in the Notion Notes field or in 06-Drafts/
- If video: attach the MP4 file to the Typefully API call
- If image: attach the image file to the Typefully API call
- Typefully supports up to 4 images per tweet or 1 video

### For TikTok/Instagram (Buffer):
- Buffer requires a public media URL, not a local file
- Upload the media file to fal.ai storage (fal.storage.upload) and get a public URL
- Pass that URL to Buffer API
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

## RULES
- Always show list and wait for my selection
- Never auto-post anything without my approval
- For video content, check Production Status before attempting to post
- If an API call fails, show the error and do not update status
- Log every posting attempt to 07-Analytics/posting-log.md

## INTERACTION PATTERN

Before sending to any platform, always say:

**"Ready to send to [platform]. Confirm or adjust?"**

Then:
- If the user says "confirmed", "send it", "post it", or similar: execute the post and report the result
- If the user says "adjust" or gives edits: apply the edits, show the updated content, and ask again
- If the user gives specific instructions for a follow-up task (e.g., "post this then post the LinkedIn one too"): apply those instructions immediately without asking again
- If the user gives BOTH edits AND instructions for a follow-up: apply both. Edit first, then execute the follow-up.
