"""
Generate empty Notion calendar slot JSON batches.
Date range: April 1 – June 30, 2026 (91 days)
12 slots/day = 1,092 total entries
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# --- Slot definitions: (slot_id, platform, content_type, wat_hour, wat_minute) ---
SLOTS = [
    ("TK-1", "TikTok",    "TikTok Script",    7,  0),
    ("IG-1", "Instagram",  "Reel Script",      8,  0),
    ("X-1",  "X/Twitter",  "Tweet",            9,  0),
    ("TG-1", "Telegram",   "Community Post",   9,  0),
    ("LI-1", "LinkedIn",   "LinkedIn Post",    10, 0),
    ("TK-2", "TikTok",    "TikTok Script",    12, 0),
    ("X-2",  "X/Twitter",  "Tweet",            13, 0),
    ("TK-3", "TikTok",    "TikTok Script",    17, 0),
    ("LI-2", "LinkedIn",   "LinkedIn Post",    17, 0),
    ("TG-2", "Telegram",   "Community Post",   17, 0),
    ("IG-2", "Instagram",  "Reel Script",      18, 0),
    ("TK-4", "TikTok",    "TikTok Script",    20, 0),
]

# Goal rotation across the 12 daily slots (cycles through 5 goals)
GOALS = ["Sales", "Reach", "Community", "Leads", "Authority"]

# Fixed daily personality pattern (12 entries)
PERSONALITY_PATTERN = [
    "Hot Take", "Story", "Polarizing Stand", "Enemy",
    "Callout", "Mythology", "Polarizing Stand", "Hot Take",
    "Story", "Enemy", "Callout", "Mythology",
]

MONTH_ABBR = {4: "Apr", 5: "May", 6: "Jun"}
BATCH_SIZE = 100
OUTPUT_DIR = Path(__file__).parent


def format_time_12h(hour_24: int) -> str:
    """Convert 24h hour to '7AM' style string."""
    if hour_24 == 0:
        return "12AM"
    elif hour_24 < 12:
        return f"{hour_24}AM"
    elif hour_24 == 12:
        return "12PM"
    else:
        return f"{hour_24 - 12}PM"


def generate_pages():
    pages = []
    start = datetime(2026, 4, 1)
    end = datetime(2026, 6, 30)
    day = start

    while day <= end:
        mon = MONTH_ABBR[day.month]
        for i, (slot_id, platform, content_type, wat_h, wat_m) in enumerate(SLOTS):
            # Title: "[TK-1] Apr 1 - 7AM WAT"
            time_str = format_time_12h(wat_h)
            title = f"[{slot_id}] {mon} {day.day} - {time_str} WAT"

            # UTC = WAT - 1h
            utc_h = wat_h - 1
            utc_dt = day.replace(hour=utc_h, minute=wat_m, second=0)
            iso_str = utc_dt.strftime("%Y-%m-%dT%H:%M:%S")

            # Goal: rotate through 5 goals across the 12 slots
            goal = GOALS[i % len(GOALS)]

            # Personality marker: fixed pattern
            personality = PERSONALITY_PATTERN[i]

            page = {
                "properties": {
                    "Title": title,
                    "Platform": platform,
                    "Content Type": content_type,
                    "Goal": goal,
                    "Status": "Draft",
                    "Priority": "Normal",
                    "Personality Marker": personality,
                    "Recurring": "One-Time",
                    "date:Post Date:start": iso_str,
                    "date:Post Date:is_datetime": 1,
                }
            }
            pages.append(page)

        day += timedelta(days=1)

    return pages


def write_batches(pages):
    total = len(pages)
    batch_count = (total + BATCH_SIZE - 1) // BATCH_SIZE
    files_written = []

    for b in range(batch_count):
        chunk = pages[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]
        path = OUTPUT_DIR / f"calendar_batch_{b}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
        files_written.append((path.name, len(chunk)))

    return files_written


def main():
    pages = generate_pages()
    batches = write_batches(pages)

    print(f"Total pages:  {len(pages)}")
    print(f"Batches:      {len(batches)}")
    print("Breakdown:")
    for name, count in batches:
        print(f"  {name}: {count} pages")


if __name__ == "__main__":
    main()
