#!/usr/bin/env python3
"""
migrate_calendar.py — Generate migration instructions (JSON) to transfer
content from OLD Notion batch files (notion_batch_0..9) into NEW calendar
slot batch files (calendar_batch_0..10).

Output:
  migration_day_001.json .. migration_day_091.json  (Apr 1 – Jun 30, 2026)
  migration_summary.json
"""

import json, os, re, sys
from collections import defaultdict
from datetime import date, timedelta

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 1.  Load batch files
# ---------------------------------------------------------------------------

def load_batches(prefix, count):
    """Load all entries from <prefix>_0.json .. <prefix>_{count-1}.json"""
    entries = []
    for i in range(count):
        path = os.path.join(SCRIPTS_DIR, f"{prefix}_{i}.json")
        with open(path, "r", encoding="utf-8") as f:
            batch = json.load(f)
        for item in batch:
            entries.append(item["properties"])
    return entries

new_entries = load_batches("calendar_batch", 11)
old_entries = load_batches("notion_batch", 10)

print(f"Loaded {len(new_entries)} NEW entries, {len(old_entries)} OLD entries")

# ---------------------------------------------------------------------------
# 2.  Parse helpers
# ---------------------------------------------------------------------------

SLOT_PREFIX_RE = re.compile(r"^\[([A-Z]{1,2}-\d|X-AM|X-PM)\]\s*")

# Map old prefixes → new slot IDs
PREFIX_MAP = {
    "TK-1": "TK-1", "TK-2": "TK-2", "TK-3": "TK-3", "TK-4": "TK-4",
    "X-AM": "X-1",  "X-PM": "X-2",
    "IG-1": "IG-1", "IG-2": "IG-2",
    "LI-1": "LI-1", "LI-2": "LI-2",
}

# Platform → ordered list of slot IDs to try
PLATFORM_SLOT_ORDER = {
    "TikTok":    ["TK-1", "TK-2", "TK-3", "TK-4"],
    "Instagram": ["IG-1", "IG-2"],
    "X/Twitter": ["X-1", "X-2"],
    "LinkedIn":  ["LI-1", "LI-2"],
    "Telegram":  ["TG-1", "TG-2"],
}


def extract_date(props):
    """Return date string YYYY-MM-DD from Post Date."""
    raw = props.get("date:Post Date:start", "")
    return raw[:10] if raw else ""


def extract_slot_id(title):
    """Return (slot_id_or_None, content_part_of_title)."""
    m = SLOT_PREFIX_RE.match(title)
    if m:
        raw_prefix = m.group(1)
        slot_id = PREFIX_MAP.get(raw_prefix)
        content_part = title[m.end():].strip()
        return slot_id, content_part
    return None, title.strip()


def new_slot_id(title):
    """Extract slot ID from a NEW entry title like '[TK-1] Apr 1 - 7AM WAT'."""
    m = SLOT_PREFIX_RE.match(title)
    return m.group(1) if m else None

# Properties to transfer from old → new
TRANSFER_KEYS = [
    "Title", "Hook Used", "Notes", "Content", "Content Type",
    "Goal", "Status", "Priority", "Production Status",
    "Source Skill", "Monetization",
]

# ---------------------------------------------------------------------------
# 3.  Group entries by date
# ---------------------------------------------------------------------------

old_by_date = defaultdict(list)
for props in old_entries:
    d = extract_date(props)
    if d:
        old_by_date[d].append(props)

new_by_date = defaultdict(list)
for props in new_entries:
    d = extract_date(props)
    if d:
        new_by_date[d].append(props)

# ---------------------------------------------------------------------------
# 4.  Match per day
# ---------------------------------------------------------------------------

start_date = date(2026, 4, 1)
end_date   = date(2026, 6, 30)
num_days   = (end_date - start_date).days + 1  # 91

total_matched = 0
total_overflow = 0
total_empty = 0
total_old = 0
days_with_overflow = []

for day_idx in range(num_days):
    current = start_date + timedelta(days=day_idx)
    date_str = current.isoformat()
    day_num = day_idx + 1  # 1-based

    day_old = old_by_date.get(date_str, [])
    day_new = new_by_date.get(date_str, [])

    total_old += len(day_old)

    # Build a dict: slot_id → new entry (preserving order)
    available_new = {}
    for nprops in day_new:
        sid = new_slot_id(nprops["Title"])
        if sid:
            available_new[sid] = nprops

    matches = []
    matched_old = set()  # indices of matched old entries
    used_new_slots = set()

    # --- Pass 1: prefix-based matching ---
    for oi, oprops in enumerate(day_old):
        slot_id, content_part = extract_slot_id(oprops.get("Title", ""))
        if slot_id and slot_id in available_new and slot_id not in used_new_slots:
            nprops = available_new[slot_id]
            # Build transfer dict
            transfer = {}
            # Title: use [NEW_SLOT] + old content
            transfer["Title"] = f"[{slot_id}] {content_part}" if content_part else oprops.get("Title", "")
            for key in TRANSFER_KEYS:
                if key == "Title":
                    continue  # already handled
                val = oprops.get(key)
                if val is not None and val != "":
                    transfer[key] = val

            matches.append({
                "new_slot_title": nprops["Title"],
                "old_entry_title": oprops["Title"],
                "old_entry_platform": oprops.get("Platform", ""),
                "transfer_properties": transfer,
            })
            matched_old.add(oi)
            used_new_slots.add(slot_id)

    # --- Pass 2: platform-based matching for remaining old entries ---
    for oi, oprops in enumerate(day_old):
        if oi in matched_old:
            continue
        platform = oprops.get("Platform", "")
        slot_order = PLATFORM_SLOT_ORDER.get(platform, [])
        placed = False
        for sid in slot_order:
            if sid in available_new and sid not in used_new_slots:
                nprops = available_new[sid]
                _, content_part = extract_slot_id(oprops.get("Title", ""))
                transfer = {}
                transfer["Title"] = f"[{sid}] {content_part}" if content_part else oprops.get("Title", "")
                for key in TRANSFER_KEYS:
                    if key == "Title":
                        continue
                    val = oprops.get(key)
                    if val is not None and val != "":
                        transfer[key] = val

                matches.append({
                    "new_slot_title": nprops["Title"],
                    "old_entry_title": oprops["Title"],
                    "old_entry_platform": platform,
                    "transfer_properties": transfer,
                })
                matched_old.add(oi)
                used_new_slots.add(sid)
                placed = True
                break

    # Gather results
    unmatched_new = [
        nprops["Title"]
        for sid, nprops in available_new.items()
        if sid not in used_new_slots
    ]
    overflow = [
        day_old[oi]["Title"]
        for oi in range(len(day_old))
        if oi not in matched_old
    ]

    total_matched += len(matches)
    total_overflow += len(overflow)
    total_empty += len(unmatched_new)

    if overflow:
        days_with_overflow.append(date_str)

    # Write day file
    day_data = {
        "date": date_str,
        "matches": matches,
        "unmatched_new_slots": unmatched_new,
        "overflow_old_entries": overflow,
        "stats": {
            "matched": len(matches),
            "unmatched_new": len(unmatched_new),
            "overflow": len(overflow),
        },
    }
    out_path = os.path.join(SCRIPTS_DIR, f"migration_day_{day_num:03d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(day_data, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# 5.  Summary
# ---------------------------------------------------------------------------

summary = {
    "total_old_entries_processed": total_old,
    "total_matched": total_matched,
    "total_overflow": total_overflow,
    "total_new_slots_empty": total_empty,
    "days_with_overflow": days_with_overflow,
    "days_covered": num_days,
}

summary_path = os.path.join(SCRIPTS_DIR, "migration_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\n=== Migration Summary ===")
print(f"Days covered:              {num_days}")
print(f"Total old entries:         {total_old}")
print(f"Total matched:             {total_matched}")
print(f"Total overflow (no slot):  {total_overflow}")
print(f"Total new slots empty:     {total_empty}")
print(f"Days with overflow:        {len(days_with_overflow)}")
if days_with_overflow:
    print(f"  Overflow dates: {', '.join(days_with_overflow[:10])}{'...' if len(days_with_overflow) > 10 else ''}")
print(f"\nWrote {num_days} migration_day_*.json files + migration_summary.json")
