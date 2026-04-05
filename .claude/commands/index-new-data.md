---
voice: see 08-Templates/voice-rules.md
name: index-new-data
description: "Ingest new vault data into all 4 indexes (hooks, visual hooks, psychological structures, delivery styles). Run after dropping new research, competitor breakdowns, scraped data, or framework notes into the vault. Triggers: 'index new data', 'update indexes', 'ingest new vault data', 'I added new stuff to the vault', 'refresh indexes', 'rebuild indexes'"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---

# /index-new-data — Ingest New Vault Data Into All Indexes

## ROLE

You are the Index Librarian. When Big Quiv drops new files into the vault (research, competitor breakdowns, scraped data, framework notes, video references), you read them, extract every usable element, score it, and file it into the correct index. Nothing useful stays buried in a raw file.

## WHEN TO RUN

- After dropping new research files into the vault
- After adding competitor analysis or video breakdowns
- After importing scraped data manually (Apify JSON dumps, etc.)
- After writing new frameworks or updating existing ones
- Anytime Big Quiv says "I added new stuff to the vault"

---

## STEP 1: DETECT NEW OR MODIFIED FILES

Scan the entire ContentBrain vault for files modified in the last 7 days:

```bash
find . -name "*.md" -o -name "*.json" -o -name "*.txt" | xargs ls -lt --time=ctime 2>/dev/null | head -50
```

Also check these high-traffic folders specifically:
- `02-Hooks/`
- `04-Patterns/`
- `05-Frameworks/`
- `06-Delivery/`
- `10-Niche-Knowledge/`
- Root folder (for raw JSON dumps like `*_raw.json`)

List all files modified in the last 7 days. Read each one fully.

Exclude these from scanning (they are indexes, not sources):
- `02-Hooks/hook-index.md`
- `02-Hooks/visual-hook-index.md`
- `05-Frameworks/psychological-structure-index.md`
- `06-Delivery/talking-head-style-index.md`
- Any file in `02-Hooks/performance-data/`
- Any file in `node_modules/`, `.next/`, `google-cloud-sdk/`

---

## STEP 2: EXTRACT ELEMENTS BY CATEGORY

For each new/modified file, extract elements into 4 buckets:

### Bucket A: Text Hooks

Any phrase, sentence, or opener that could be used as a post hook or video hook line.

- Match against existing entries in `02-Hooks/hook-index.md`
- If it already exists, skip
- If new, score using the 4-criteria rubric (GAP, SPEC, CHARGE, BREAK)
- Assign tier based on score
- Add to hook-index.md with next available H-XXX ID

### Bucket B: Visual Hook Techniques

Any camera technique, scene setup, visual opener, transition, or first-3-seconds description.

Look for keywords: zoom, close-up, wide shot, pan, reveal, object, hand, walk, screen record, text overlay, b-roll, split screen, green screen, POV, overhead, time-lapse, slow motion, whip pan, jump cut, macro, Dutch angle, dolly, handheld, tripod, crane, orbit, freeze frame, match cut, flash, glitch.

- Match against existing entries in `02-Hooks/visual-hook-index.md`
- If it already exists, skip
- If new, score using the 4-criteria rubric (STOP POWER, CURIOSITY VISUAL, UNIQUENESS, EXECUTION EASE)
- If the source file has engagement data, use it to set the tier (COMPETITOR-PROVEN if high engagement)
- Add to visual-hook-index.md with next available V-XXX ID

### Bucket C: Psychological Structures

Any content structure, retention pattern, persuasion framework, narrative arc, or audience psychology principle.

Look for keywords: open loop, curiosity gap, pattern interrupt, tension, payoff, false ending, identity, fear, desire, social proof, authority, scarcity, urgency, contrast, anchoring, loss aversion, commitment, reciprocity, storytelling arc, hero's journey, problem-agitate-solve, before-after-bridge, peak-end, Zeigarnik, retention, emotional arc, script structure, content framework.

- Match against existing entries in `05-Frameworks/psychological-structure-index.md`
- If it already exists, check if the new source adds detail or context. If yes, update the existing entry.
- If new, score using the 4-criteria rubric (RETENTION PULL, EMOTIONAL ARC, ADAPTABILITY, PROVEN BASIS)
- Add to psychological-structure-index.md with next available PS-XXX ID

### Bucket D: Delivery Styles

Any camera setup, energy level, talking head framing, body language cue, or on-camera delivery technique.

Look for keywords: energy, calm, intense, whisper, shout, lean in, look away, pause, hand gesture, pointing, sitting, standing, walking, close to camera, far from camera, side angle, direct to camera, over shoulder, lighting, neon, spotlight, silhouette, Rembrandt, rim light, ring light, candle, golden hour.

- Match against existing entries in `06-Delivery/talking-head-style-index.md`
- If it already exists, skip
- If new, add to talking-head-style-index.md with next available TH-XXX ID
- Assign energy level (Low/Medium/High/Explosive)
- Specify when to use (hook/middle/payoff/transition)

---

## STEP 3: DEDUPLICATION CHECK

Before adding ANY new entry to ANY index, do a fuzzy match against all existing entries in that index.

**Threshold: 80%+ similarity = duplicate.**

When a duplicate is detected:
- If the new entry has **better engagement data**, update the existing entry's score and tier
- If the new entry **adds new context** (new platform data, new source creator, additional use cases), append to the existing entry's metadata
- If the new entry is **genuinely the same thing worded differently**, skip it entirely

**How to fuzzy match:**
1. Normalize both entries: lowercase, strip punctuation, remove filler words
2. Compare technique/pattern names first (cheapest check)
3. If names differ, compare descriptions — look for same core mechanism
4. When in doubt, keep both entries with a note: `<!-- REVIEW: possible duplicate of [other ID] -->`

---

## STEP 4: UPDATE INDEX METADATA

After all additions, update the header of each modified index:

1. Update `Last rebuilt` date to today
2. Update `Total [entries]` count
3. Re-sort entries within each tier by score (highest first)
4. Verify all IDs are sequential (no gaps, no duplicates)

---

## STEP 5: GENERATE INGEST REPORT

Output a summary:

```markdown
## Index Ingest Report — [DATE]

### Files Scanned
- [file path] (modified [date])
- [file path] (modified [date])

### New Entries Added

**hook-index.md**
- [count] new hooks added
- [list each: ID, hook text preview, score, tier]

**visual-hook-index.md**
- [count] new visual techniques added
- [list each: ID, technique name, score, tier]

**psychological-structure-index.md**
- [count] new structures added
- [list each: ID, pattern name, score, tier]

**talking-head-style-index.md**
- [count] new styles added
- [list each: ID, setup description, energy level]

### Existing Entries Updated
- [ID] in [index] — updated score from [old] to [new] (new engagement data from [source])
- [ID] in [index] — added [platform] source data

### Duplicates Skipped
- [count] duplicates detected and skipped
- [list: "new entry X" matched existing [ID] at [similarity]% — skipped]

### No Data Found
- [list any scanned files that contained nothing extractable for any index]
```

---

## STEP 6: AUTO-INGEST WIRING

This command should be triggered automatically by other skills. The following skills have auto-ingest steps built in:

### /scrape-instagram (and all platform scrapers)

After scraping competitor posts, the scraper auto-extracts:
- **Visual hooks** from top-performing video posts (1K+ likes/views) → adds to `visual-hook-index.md` as COMPETITOR-PROVEN
- **Text hooks** from high-engagement posts → adds to `hook-index.md` as COMPETITOR-PROVEN
- Runs deduplication before adding

### /score-hooks

After scoring @big_quiv's own posts, also identifies and scores:
- **Visual hook used** in each video post (matched to `visual-hook-index.md`)
- **Psychological structure used** (matched to `psychological-structure-index.md`)
- **Delivery style used** (matched to `talking-head-style-index.md`)
- Updates all 4 indexes with real performance data

### Manual trigger

Run `/index-new-data` manually after:
- Dropping raw JSON files into the vault root
- Adding new framework files to `05-Frameworks/`
- Writing video breakdowns or production notes
- Any bulk vault update

---

## RULES

1. **Never delete entries.** Only add, update scores, or add `<!-- RETIRE -->` flags.
2. **Never modify the scoring rubric** in any index. The rubric is fixed.
3. **Engagement data overrides AI scoring.** If a visual hook has real performance data (from /score-hooks), that score takes priority.
4. **Require 2+ data points** before setting SELF-PROVEN tier. One good result is not proof.
5. **Always read existing index entries first** before adding. Dedup is mandatory.
6. **Preserve ID sequences.** New entries get the next available number in the series. Never reuse retired IDs.
7. **Log everything.** The ingest report is the audit trail for how indexes grow over time.
8. **Speed over perfection.** When in doubt about whether something is a new technique vs. a variation of an existing one, add it with a `<!-- REVIEW -->` comment rather than skipping it.
9. **Cross-reference between indexes.** When adding a new visual hook (V-XXX), check if it pairs naturally with existing delivery styles (TH-XXX) and update the `Pairs With Visual Hook` fields.
10. **Source attribution is required.** Every new entry must have a Source field citing where it came from (file path, creator name, or scrape URL).
