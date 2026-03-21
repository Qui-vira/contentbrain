---
description: "Update post status and log engagement. Triggers: I posted this, update status, log engagement"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "mcp__notion__notion-search", "mcp__notion__notion-update-page"]
---

# SKILL: Publish Update

## PROCESS
1. When I say "/publish-update [title or keyword]", search Notion for the matching entry
2. Ask: new status? (Posted, Missed)
3. Ask: engagement rate? (optional number)
4. Update Notion page with new status and engagement rate
5. Update draft in 06-Drafts/ with "status: posted" and engagement data
6. Log to 07-Analytics/[date]-engagement.md

## INTERACTION PATTERN

After updating the status and logging engagement, always say:

**"Status updated. Anything else to log?"**

Then:
- If the user says "no", "done", or similar: finish
- If the user gives another post to update: apply immediately without asking again
- If the user gives additional engagement data: add it to the log and confirm
