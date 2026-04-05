---
voice: see 08-Templates/voice-rules.md
description: "Scan the entire vault for new data, extract content elements, score and file them into all 4 indexes. Replaces /index-new-data. Triggers: '/learn', 'learn from vault', 'update indexes', 'ingest new data', 'I added new stuff', 'refresh indexes'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# SKILL: Learn

## ROLE
You are the vault's learning engine. You scan every modified file since the last run, extract usable content elements (hooks, visual hooks, psychological structures, delivery styles, frameworks, strategies, patterns, voice patterns, camera angles), score them, and file them into the correct index. You also scan all skills for unindexed knowledge. One command. Drop data. Run /learn. Done.

## WHEN TO USE THIS SKILL
- "/learn"
- "Learn from vault" / "Update indexes"
- "I added new stuff to the vault"
- "Refresh indexes" / "Rebuild indexes"
- After running /scrape-instagram, dropping competitor research, adding new frameworks, or editing any vault file
- Weekly as part of the maintenance routine

## TIMESTAMP FILE
`02-Hooks/performance-data/last-learn.txt`

Format: single line, ISO-8601 datetime.
```
2026-04-01T09:00:00Z
```

## PROCESS

### Step 1: Read Timestamp
Read `02-Hooks/performance-data/last-learn.txt`.
- If it exists, store the timestamp as `LAST_RUN`.
- If it does not exist, set `LAST_RUN` to epoch (process everything).

### Step 2: Find Modified Files
Use Bash to find all files modified since `LAST_RUN`:
```bash
find . -name "*.md" -newer 02-Hooks/performance-data/last-learn.txt -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./website/*"
```
If `last-learn.txt` does not exist (first run), scan ALL .md files:
```bash
find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./website/*"
```

Store the file list. If empty, report "No files modified since last /learn run." and update timestamp.

### Step 3: Read Modified Files
Read every file in the list. For large files (>500 lines), read in chunks.

### Step 4: Extract Content Elements

For each file, extract ANY of the following if present:

**Text Hooks** (→ `02-Hooks/hook-index.md`)
- Opening lines that stop the scroll
- Callout patterns, flex patterns, reveal patterns
- Question hooks, stat hooks, contrarian hooks
- Any first line of a post, script, thread, or caption that functions as a hook

**Visual Hooks** (→ `02-Hooks/visual-hook-index.md`)
- Opening scene descriptions for video/reel content
- First-frame descriptions, visual openers
- Camera setups described for the first 1-3 seconds
- Thumbnail concepts, carousel cover slide descriptions

**Psychological Structures** (→ `05-Frameworks/psychological-structure-index.md`)
- Content structures with tension arcs (buildup → payoff)
- Script frameworks (e.g., Problem-Agitate-Solution, Callout-Flex-Reveal)
- Any multi-section format with a defined emotional progression
- Timeline-based structures (0-3s → 3-7s → 7-15s → etc.)

**Delivery Styles** (→ `06-Delivery/talking-head-style-index.md`)
- Camera setup descriptions (close-up, medium, wide, overhead, POV)
- Energy level descriptions (calm, intense, hype, raw, reflective)
- Performance notes (lean in, whisper, speed up, pause)
- Combined camera + energy + performance packages

**Other Extractable Elements** (noted but not indexed — saved to vault notes):
- Frameworks and strategies → note for `05-Frameworks/`
- Brand voice patterns → note for CLAUDE.md review
- Content calendar patterns → note for `/content-strategist`

### Step 5: Score Each Element

For each extracted element, assign:

**Score (0-100):**
- 80-100: SELF-PROVEN (from our own content with engagement data)
- 60-79: COMPETITOR-PROVEN (from scraped competitor content that performed well)
- 40-59: STRONG (from frameworks, research, or patterns without direct engagement data)
- 20-39: UNTESTED (new, unproven, but structurally sound)
- 0-19: Do not index. Too weak or vague.

**Tier:**
- S-TIER: Score 80+, proven with data
- A-TIER: Score 60-79, competitor-proven or strong pattern
- B-TIER: Score 40-59, structurally sound, needs testing
- C-TIER: Score 20-39, speculative, monitor

**Source:** File path where the element was found.

**Platform applicability:** Which platforms this element works for.

**Goal match:** Which content goals (Sales, Reach, Leads, Authority, Community) this element serves.

### Step 6: Deduplicate

Before adding any element to an index:
1. Read the target index file.
2. Check if the element already exists (same hook text, same visual description, same structure name).
3. If it exists AND the new version has a higher score or more data, UPDATE the existing entry.
4. If it exists AND the new version has a lower or equal score, SKIP it.
5. If it does not exist, ADD it with the next available ID (H-XXX, V-XXX, PS-XXX, TH-XXX).

### Step 7: Scan Skills for Unindexed Knowledge

Read every file in `.claude/commands/`:
```bash
ls .claude/commands/*.md
```

For each skill file, check if it contains:
- Hook formulas or examples not in hook-index.md
- Visual descriptions not in visual-hook-index.md
- Content structures not in psychological-structure-index.md
- Delivery/camera notes not in talking-head-style-index.md
- Framework knowledge that should be captured

Extract and index any unindexed elements found. Score them as STRONG (40-59) since they are embedded knowledge, not engagement-proven.

### Step 8: Update Indexes

Write all new/updated entries to the correct index files:
- `02-Hooks/hook-index.md` — text hooks
- `02-Hooks/visual-hook-index.md` — visual hooks
- `05-Frameworks/psychological-structure-index.md` — psychological structures
- `06-Delivery/talking-head-style-index.md` — delivery styles

Maintain the existing format of each index. Do not reformat existing entries. Only append new entries or update existing ones in place.

**MANDATORY: After selecting a hook, write today's date to the Last Used field of that hook in hook-index.md or visual-hook-index.md. Format: YYYY-MM-DD. This is mandatory. Hook rotation cannot function without it.**

### Step 9: Update Timestamp

Write the current ISO-8601 datetime to `02-Hooks/performance-data/last-learn.txt`.

## OUTPUT FORMAT

```
LEARN COMPLETE — [DATE]
---
Files scanned: [N] modified since [LAST_RUN date]
Skills scanned: [N] command files

New text hooks indexed: [N] (IDs: H-XXX to H-XXX)
Updated text hooks: [N]
New visual hooks indexed: [N] (IDs: V-XXX to V-XXX)
Updated visual hooks: [N]
New psychological structures indexed: [N] (IDs: PS-XXX to PS-XXX)
Updated structures: [N]
New delivery styles indexed: [N] (IDs: TH-XXX to TH-XXX)
Updated delivery styles: [N]

Skipped (duplicates): [N]
Skipped (too weak): [N]

Top additions:
1. [Type] [ID]: [name] — Score: [N] — Source: [file]
2. [Type] [ID]: [name] — Score: [N] — Source: [file]
3. [Type] [ID]: [name] — Score: [N] — Source: [file]

Timestamp updated: [ISO-8601]
---
```

## RULES
1. Never delete existing index entries. Only add or update.
2. Never lower an existing entry's score. Scores only go up.
3. If an element contradicts an existing entry (e.g., a hook formula that a newer pattern disproves), add a note to the existing entry: `[CONTESTED — see [source file] for counter-evidence]`.
4. Always preserve the `Last Used` column of existing entries. Never reset it.
5. Run silently. Do not ask questions. Scan, extract, score, file, done.
6. If an index file does not exist yet, create it with the standard header format and start IDs from 001.
7. Process everything in one pass. No partial runs.

## CONNECTIONS
- Replaces `/index-new-data` (deprecated)
- Feeds: `/ghostwriter` (hook selection), `/video-editor` (visual hooks, structures, delivery), `/concept` (all indexes), `/graphic-designer` (visual hooks), `/score-hooks` (hook IDs for scoring)
- Fed by: `/scrape-instagram` (competitor data), `/score-hooks` (engagement scores), any manual vault additions
