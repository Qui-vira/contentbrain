---
description: "Check status of all content in Notion. Triggers: publish status, what's scheduled, what did I miss"
allowed-tools: ["Read", "Glob", "mcp__notion__notion-search", "mcp__notion__notion-update-page"]
---

# SKILL: Publish Status

## NOTION CONTENT CALENDAR

Database ID: f405e62cf2804e6a8c217ebd2f8f4210
Data Source ID: collection://9081ce06-1802-4b43-a988-62c5e384fcfd

This skill reads from the Notion Content Calendar to show content status. Use the database and data source IDs above for all Notion operations.

## PROCESS
1. Search Notion Content Calendar for all entries
2. Group by status: Scheduled, Posted, Missed, Draft
3. Show table: Title, Platform, Status, Post Date, Content Type, Production Status
4. Flag entries with Status "Scheduled" and Post Date in the past as potentially "Missed"
5. Ask if I want to update any statuses
6. For video content, show Production Status pipeline: Script Ready → Recording Needed → Recorded → Editing → AI Assets Needed → Review → Ready to Post

## INTERACTION PATTERN

This is a read-only skill. After showing the status report, do not ask for approval. Just show the report.

If the user asks to update a status after seeing the report, hand off to /publish-update.
