"""Generate a final CSV for Notion import. Merges old content into new 12-slot structure."""
import json, csv, os
from collections import Counter

SCRIPTS = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain\scripts"

# Load all new calendar batches
new_slots = []
for i in range(11):
    with open(os.path.join(SCRIPTS, f"calendar_batch_{i}.json"), encoding="utf-8") as f:
        new_slots.extend(json.load(f))

# Build lookup: new_slot_title -> properties
new_lookup = {s["properties"]["Title"]: s["properties"] for s in new_slots}

# Load all migration day files and process matches
rows = []
matched_titles = set()

for i in range(1, 92):
    with open(os.path.join(SCRIPTS, f"migration_day_{i:03d}.json"), encoding="utf-8") as f:
        day = json.load(f)
    for m in day["matches"]:
        new_title = m["new_slot_title"]
        t = m["transfer_properties"]
        np = new_lookup.get(new_title, {})
        rows.append({
            "Title": t.get("Title", new_title),
            "Platform": np.get("Platform", m.get("old_entry_platform", "")),
            "Content Type": t.get("Content Type", np.get("Content Type", "")),
            "Goal": t.get("Goal", np.get("Goal", "")),
            "Status": t.get("Status", "Draft"),
            "Priority": t.get("Priority", "Normal"),
            "Personality Marker": np.get("Personality Marker", ""),
            "Recurring": "One-Time",
            "Post Date": np.get("date:Post Date:start", ""),
            "Hook Used": t.get("Hook Used", ""),
            "Notes": t.get("Notes", ""),
        })
        matched_titles.add(new_title)

# Add unmatched new slots (Telegram etc)
for s in new_slots:
    title = s["properties"]["Title"]
    if title not in matched_titles:
        p = s["properties"]
        rows.append({
            "Title": title, "Platform": p.get("Platform",""),
            "Content Type": p.get("Content Type",""), "Goal": p.get("Goal",""),
            "Status": "Draft", "Priority": "Normal",
            "Personality Marker": p.get("Personality Marker",""),
            "Recurring": "One-Time", "Post Date": p.get("date:Post Date:start",""),
            "Hook Used": "", "Notes": "",
        })

rows.sort(key=lambda r: r["Post Date"])
csv_path = os.path.join(SCRIPTS, "content_calendar_final.csv")
fields = ["Title","Platform","Content Type","Goal","Status","Priority","Personality Marker","Recurring","Post Date","Hook Used","Notes"]
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"Total rows: {len(rows)}")
print(f"Matched (with content): {len(matched_titles)}")
print(f"Empty slots: {len(rows) - len(matched_titles)}")
platforms = Counter(r["Platform"] for r in rows)
print(f"\nPlatform breakdown:")
for p, c in sorted(platforms.items()):
    print(f"  {p}: {c}")
