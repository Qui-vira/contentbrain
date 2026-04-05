"""Generate batch JSON files with merged content ready for Notion upload."""
import json, csv, os

SCRIPTS = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain\scripts"
csv_path = os.path.join(SCRIPTS, "content_calendar_final.csv")

rows = []
with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        page = {"properties": {
            "Title": r["Title"],
            "Platform": r["Platform"],
            "Content Type": r["Content Type"],
            "Goal": r["Goal"],
            "Status": r["Status"],
            "Priority": r["Priority"],
            "Personality Marker": r["Personality Marker"],
            "Recurring": r["Recurring"],
            "date:Post Date:start": r["Post Date"],
            "date:Post Date:is_datetime": 1,
        }}
        if r["Hook Used"]:
            page["properties"]["Hook Used"] = r["Hook Used"]
        if r["Notes"]:
            page["properties"]["Notes"] = r["Notes"]
        rows.append(page)

# Split into batches of 100
for i in range(0, len(rows), 100):
    batch = rows[i:i+100]
    path = os.path.join(SCRIPTS, f"final_batch_{i//100}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)

total_batches = (len(rows) + 99) // 100
print(f"Total rows: {len(rows)}")
print(f"Batches: {total_batches}")
for i in range(total_batches):
    path = os.path.join(SCRIPTS, f"final_batch_{i}.json")
    with open(path, encoding="utf-8") as f:
        batch = json.load(f)
    print(f"  final_batch_{i}.json: {len(batch)} pages")
