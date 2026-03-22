---
description: "Push approved drafts to Notion Content Calendar. Triggers: publish, push to notion, sync drafts"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "mcp__notion__notion-create-pages", "mcp__notion__notion-update-page", "mcp__notion__notion-search"]
---

# SKILL: Publish to Notion

## NOTION CONTENT CALENDAR

Database ID: f405e62cf2804e6a8c217ebd2f8f4210
Data Source ID: collection://9081ce06-1802-4b43-a988-62c5e384fcfd

This skill pushes approved drafts to the Notion Content Calendar. Use the database and data source IDs above for all Notion operations.

## PROCESS
1. Scan 06-Drafts/ for files with frontmatter "status: approved" that are NOT "synced-to-notion" or "posted"
2. List every approved draft: filename, platform, content type, date, first 50 characters of content
3. Ask me which ones to push. Wait for my selection.
4. For each selected draft, create a page in Notion Content Calendar (data source: 9081ce06-1802-4b43-a988-62c5e384fcfd) with all properties: Title, Platform, Status "Scheduled", Content Type, Post Date (with time, is_datetime 1), Content (full text), Goal, Production Status (for video), Hook Used, Monetization, Source Skill, Notes
5. Update each draft frontmatter to "status: synced-to-notion" and add "notion_page_id: [page ID]"
6. Show summary of what was pushed

## RULES
- Never push without "status: approved"
- Always show list and wait for selection
- If no date, ask me
- If no platform, ask me

## MEDIA ATTACHMENT

When publishing content that has an associated media file (image or video):

1. Check if the draft in 06-Drafts/ references a media file path in its frontmatter or body (e.g., "media: 08-Media/images/chart.png" or "Media: Desktop/content-studio/out/topic-final.mp4")
2. If a media file exists:
   - Upload it to fal.ai storage using fal.storage.upload() to get a public URL
   - Attach the URL to the Notion entry's Files property
   - Include the media type in the Notes field: "Media: [image/video], URL: [public URL]"
3. If no media file exists, skip this step silently.

When I manually provide an image or video:
- I will say "/publish this with [file path]" or paste a file path
- Upload it to fal.ai storage
- Attach the URL to the Notion entry

The /post command then reads the Files property or Notes field from Notion to find the media URL when routing to platforms.

## INTERACTION PATTERN

After pushing drafts to Notion, always say:

**"Drafts pushed to Notion. Confirm, adjust, or give me specific instructions?"**

Then:
- If the user says "confirmed", "good", "done", or similar: finish
- If the user says "adjust" or gives edits: apply the edits and ask again
- If the user gives specific instructions for a follow-up task (e.g., "now post the Monday tweet"): apply those instructions immediately without asking again
- If the user gives BOTH edits AND instructions for a follow-up: apply both. Edit first, then execute the follow-up.
