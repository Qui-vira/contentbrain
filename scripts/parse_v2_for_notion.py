"""
Parse unified-content-calendar-v2.md into JSON batches for Notion upload.
Each batch is max 100 pages.
"""
import re
import json
from datetime import date

CONTENT_TYPE_MAP = {
    "Sales": "TikTok Script",
    "Reach": "TikTok Script",
    "Community": "TikTok Script",
    "Authority": "TikTok Script",
    "Reel": "Reel Script",
    "Carousel": "Carousel",
    "Static": "Community Post",
    "Story": "Community Post",
    "Story series": "Community Post",
    "Video": "Video - AI Generated",
    "Thread": "Thread",
    "Tweet": "Tweet",
    "Tweet + Video": "Tweet",
    "Tweet + Screenshot": "Tweet",
    "Tweet + Carousel": "Tweet",
    "Thread + Video": "Thread",
    "Tweet (live)": "Tweet",
    "Thread (recap)": "Thread",
    "Post": "LinkedIn Post",
}

PLATFORM_MAP = {
    "TikTok": "TikTok",
    "Instagram": "Instagram",
    "X/Twitter": "X/Twitter",
    "LinkedIn": "LinkedIn",
}

def parse_calendar():
    with open(r"C:\Users\Bigquiv\onedrive\desktop\contentbrain\06-Drafts\unified-content-calendar-v2.md", encoding="utf-8") as f:
        content = f.read()

    pages = []
    current_date = None
    current_phase = None

    # Match day headers like "### Apr 1 (Wed) | Phase 1"
    day_pattern = re.compile(r"### (\w+) (\d+) \((\w+)\) \| Phase (\d+)")
    # Match table rows
    row_pattern = re.compile(r"\| (TK-[1-4]|IG-[12]|X-AM|X-PM|LI-[12]) \| (\w+(?:/\w+)?) \| ([^|]+)\| ([^|]+)\| ([^|]+)\| ([^|]+)\|")

    month_map = {"Apr": 4, "May": 5, "Jun": 6}

    for line in content.split("\n"):
        day_match = day_pattern.search(line)
        if day_match:
            month_str, day_str, _, phase_str = day_match.groups()
            month = month_map.get(month_str, 4)
            current_date = date(2026, month, int(day_str))
            current_phase = int(phase_str)
            continue

        row_match = row_pattern.search(line)
        if row_match and current_date:
            slot, platform, type_str, topic, goal, source = [g.strip() for g in row_match.groups()]

            # Clean up topic - remove quotes
            topic_clean = topic.strip('"').strip()

            # Determine content type for Notion
            if platform == "TikTok":
                content_type = "TikTok Script"
            elif platform == "LinkedIn":
                content_type = "LinkedIn Post"
            else:
                content_type = CONTENT_TYPE_MAP.get(type_str.strip(), "Tweet")

            # Determine status tag
            is_draft_ready = "[DRAFT READY]" in source
            is_topic_only = "[TOPIC ONLY]" in source

            # Clean source
            source_clean = source.replace("[DRAFT READY]", "").replace("[TOPIC ONLY]", "").strip()

            # Priority
            priority = "High" if is_draft_ready else "Normal"

            # Status
            status = "Draft"

            # Build title: slot + short topic
            title_topic = topic_clean[:80] + "..." if len(topic_clean) > 80 else topic_clean
            title = f"[{slot}] {title_topic}"

            # Notes
            tag = "DRAFT READY" if is_draft_ready else "TOPIC ONLY" if is_topic_only else "v1 hook"
            notes = f"Phase {current_phase} | {slot} | {source_clean} | [{tag}] | v2"

            # Goal mapping - normalize
            goal_clean = goal.strip()
            if goal_clean not in ("Sales", "Reach", "Leads", "Authority", "Community"):
                # Map Story -> Authority, etc.
                goal_map = {"Story": "Authority"}
                goal_clean = goal_map.get(goal_clean, "Authority")

            page = {
                "properties": {
                    "Title": title,
                    "Platform": PLATFORM_MAP.get(platform, platform),
                    "Content Type": content_type,
                    "Goal": goal_clean,
                    "Status": status,
                    "Priority": priority,
                    "Hook Used": topic_clean if is_draft_ready or (not is_topic_only) else "",
                    "Notes": notes,
                    "date:Post Date:start": current_date.isoformat(),
                    "date:Post Date:is_datetime": 0,
                    "Recurring": "One-Time",
                }
            }
            pages.append(page)

    # Split into batches of 100
    batches = []
    for i in range(0, len(pages), 100):
        batches.append(pages[i:i+100])

    # Write batches
    for i, batch in enumerate(batches):
        path = rf"C:\Users\Bigquiv\onedrive\desktop\contentbrain\scripts\notion_batch_{i}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(batch, f, indent=2)

    print(f"Total pages: {len(pages)}")
    print(f"Batches: {len(batches)}")
    for i, b in enumerate(batches):
        print(f"  Batch {i}: {len(b)} pages")

    return batches


if __name__ == "__main__":
    parse_calendar()
