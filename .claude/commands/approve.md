---
voice: see 08-Templates/voice-rules.md
name: approve
description: "Review and approve draft content in 06-Drafts/. Scan for all drafts with status: draft, list them, let user approve all or pick specific ones, set status to approved and production_status to Ready to Post, then auto-run /publish. Triggers: 'approve drafts', 'approve content', 'review drafts', 'what drafts are ready', 'approve all', 'approve and publish'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# SKILL: Approve Drafts

## ROLE
You are the Draft Approval Gate. You scan 06-Drafts/ for content waiting for approval, present it for review, and mark approved items so /publish can push them to Notion.

## WHEN TO USE THIS SKILL
- "Approve drafts"
- "Approve content"
- "Review drafts"
- "What drafts are ready?"
- "Approve all"
- "Approve and publish"

---

## Step 1: Scan for Pending Drafts

Glob for all `.md` files in `06-Drafts/` (not subdirectories like `visuals/`):

```
06-Drafts/*.md
```

For each file, read the frontmatter. Collect files where `status: draft` (not `approved`, `synced-to-notion`, or `posted`).

If no drafts with `status: draft` are found, say: **"No pending drafts in 06-Drafts/. Nothing to approve."** and stop.

---

## Step 2: Present Draft List

Show a numbered table:

```
## Pending Drafts

| # | File | Platform | Content Type | Date | Title/Topic | Source Skill |
|---|------|----------|-------------|------|-------------|-------------|
| 1 | 2026-04-01-x-crypto-clarity.md | X/Twitter | Tweet | Apr 1 | Crypto Clarity | Ghostwriter |
| 2 | 2026-04-01-tiktok-ai-trading.md | TikTok | TikTok Script | Apr 1 | AI Trading Setup | Video Editor |
| 3 | 2026-04-01-carousel-token-picks.md | Instagram | Carousel | Apr 1 | Top Token Picks | Graphic Designer |
...
```

For each draft, show a 1-line preview of the content (first 80 characters of the body below frontmatter).

---

## Step 3: Ask for Approval

**"Approve all, pick specific numbers (e.g., 1, 3, 5), or review any draft in full?"**

Then:
- **"approve all"** or **"all"**: approve every listed draft
- **Specific numbers** (e.g., "1, 3"): approve only those drafts
- **"review [number]"**: show the full content of that draft, then ask again
- **"skip [number]"**: exclude that draft from approval
- **"reject [number]"**: set that draft's status to `rejected` (it will not appear in future scans)

---

## Step 4: Mark Approved

For each approved draft, edit the frontmatter:

1. Change `status: draft` → `status: approved`
2. If `production_status` exists in frontmatter, change it to `production_status: Ready to Post`
3. If `production_status` does not exist, add `production_status: Ready to Post`
4. Add `approved_date: [today's date YYYY-MM-DD]`

Do NOT modify any content below the frontmatter. Only touch the YAML block.

---

## Step 5: Summary + Auto-Publish

After marking all approved drafts, show:

```
## Approved

- [filename] — [platform] — [content type]
- [filename] — [platform] — [content type]
...

Total: [N] drafts approved.
```

Then immediately say:

**"Running /publish to push approved drafts to Notion..."**

And execute the /publish skill on the approved files. Do not wait for the user to ask.

---

## RULES

1. **Never auto-approve.** Always show the list and wait for the user's selection.
2. **Never modify content.** This skill only changes frontmatter fields (status, production_status, approved_date).
3. **Never skip the list.** Even if there's only 1 draft, show it and ask.
4. **Rejected drafts** get `status: rejected` and are excluded from future scans. They are NOT deleted.
5. **Media drafts** (from /graphic-designer or /video-editor) will have `media_dir` in frontmatter. Verify the media directory exists before approving. If media files are missing, warn: "Draft [name] references media at [path] but directory is empty/missing. Approve anyway?"
6. **Cross-post sets**: If multiple drafts share the same topic slug but different platforms, list them as a group and offer "approve group" as an option.

## INTERACTION PATTERN

After completing approval and /publish, ask:

**"All approved drafts pushed to Notion. Post now, schedule for later, or done?"**

Then:
- **"post now"**: run /post on the newly published entries
- **"schedule"**: confirm the dates are set in Notion, done
- **"done"**: finish
