"""
Rebuild BD contacts CSV from raw source.
Extracts: Best Outreach Angle, Cold DM Hook, Telegram handles, Emails.
Adds new columns: Email, Telegram Handle.
Generates Telegram DM scripts for contacts with TG handles.
Generates cold email for contacts with email addresses.
"""
import csv
import os
import re

BASE = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain"
RAW_CSV = r"C:\Users\Bigquiv\Downloads\Crypto Exchange BD & Partnerships Contacts - Sheet1.csv"
OUT_CSV = os.path.join(BASE, "10-Niche-Knowledge", "partnerships", "bd-contacts-rebuilt.csv")
EMAILS_DIR = os.path.join(BASE, "06-Drafts", "outreach", "emails")
DMS_DIR = os.path.join(BASE, "06-Drafts", "outreach", "dms")
os.makedirs(EMAILS_DIR, exist_ok=True)
os.makedirs(DMS_DIR, exist_ok=True)

# ── Parse raw CSV (tab-delimited inside quoted first column) ──
def parse_raw():
    contacts = []
    with open(RAW_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header

        for row in reader:
            if not row or not row[0].strip():
                continue

            # First column may contain tab-delimited data
            first_col = row[0].strip()
            if "\t" in first_col:
                fields = first_col.split("\t")
            else:
                # Plain CSV row - combine all non-empty fields
                fields = [c.strip() for c in row if c.strip()]

            if len(fields) < 6:
                continue

            exchange = fields[0].strip()
            name = fields[1].strip() if len(fields) > 1 else ""
            role = fields[2].strip() if len(fields) > 2 else ""
            platform = fields[3].strip() if len(fields) > 3 else ""
            profile_link = fields[4].strip() if len(fields) > 4 else ""
            relevance = fields[5].strip() if len(fields) > 5 else ""
            outreach_angle = fields[6].strip() if len(fields) > 6 else ""
            cold_dm_hook = fields[7].strip() if len(fields) > 7 else ""

            # Check remaining fields for extra Notes data
            # In the raw CSV, fields after Cold DM Hook may contain Outreach Status, Notes
            extra_notes = ""
            for i in range(8, len(fields)):
                if fields[i].strip() and fields[i].strip() != "Not Contacted":
                    extra_notes += " " + fields[i].strip()

            # Also check row columns beyond first for Notes
            for i in range(1, len(row)):
                val = row[i].strip()
                if val and val != "Not Contacted" and val not in [name, role, platform, profile_link, relevance, outreach_angle, cold_dm_hook]:
                    # Check if it contains useful data (TG handles, emails, etc.)
                    if any(x in val.lower() for x in ["telegram", "tg:", "@", "email", ".com"]):
                        extra_notes += " " + val

            # Extract Telegram handle from relevance + extra_notes
            all_text = relevance + " " + cold_dm_hook + " " + extra_notes
            tg_handle = ""
            tg_match = re.search(r'TG:\s*@?(\w+)|Telegram:\s*@?(\w+)', all_text, re.IGNORECASE)
            if tg_match:
                tg_handle = tg_match.group(1) or tg_match.group(2)
                tg_handle = "@" + tg_handle if not tg_handle.startswith("@") else tg_handle

            # Extract email
            email = ""
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', all_text)
            if email_match:
                email = email_match.group(0)

            # Skip N/A contacts
            if name.startswith("N/A") or "No verified" in name:
                continue

            contacts.append({
                "Exchange": exchange,
                "Name": name,
                "Role": role,
                "Platform": platform,
                "Profile Link": profile_link,
                "Relevance": relevance,
                "Best Outreach Angle": outreach_angle,
                "Cold DM Hook": cold_dm_hook,
                "Email": email,
                "Telegram": tg_handle,
                "Outreach Status": "Outreach Draft Ready",
                "Notes": extra_notes.strip(),
            })

    return contacts

# ── Generate Telegram DM scripts ──
def generate_tg_dm(contact):
    """Short Telegram DM — direct, @big_quiv voice."""
    name = contact["Name"].split()[0]
    exchange = contact["Exchange"]
    return f"""{name} — I'm @big_quiv, crypto KOL with an AI signal system scanning 50 pairs every 4h. Active community on TG, content across X/IG/TikTok/LinkedIn daily. Looking to explore a KOL partnership with {exchange}. Can we chat here?"""

# ── Generate direct email (for contacts with email addresses) ──
def generate_direct_email(contact):
    name = contact["Name"].split()[0]
    exchange = contact["Exchange"]
    email = contact["Email"]
    return f"""To: {email}
Subject: KOL Partnership — Quivira x {exchange}

{name},

I'll keep this direct.

I'm Quivira (@big_quiv) — crypto KOL and builder across X, LinkedIn, Instagram, and TikTok. I run an AI signal system that scans 50 pairs every 4 hours and delivers filtered setups to an active Telegram trading community.

What I bring:
- Multi-platform content daily (threads, carousels, reels, scripts)
- AI-powered signal distribution driving real trading volume
- Consistent output — this is a system, not a side project

I'm looking for a structured KOL or affiliate partnership with {exchange}. Not a one-off post — a real collaboration.

Worth a quick call this week?

— Quivira
@big_quiv | X · LinkedIn · Instagram · TikTok
"""

def main():
    contacts = parse_raw()

    # Deduplicate on (Exchange, Name)
    seen = set()
    unique = []
    dupes = 0
    for c in contacts:
        key = (c["Exchange"].lower(), c["Name"].lower())
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        unique.append(c)

    contacts = unique

    # Write rebuilt CSV
    fieldnames = ["Exchange", "Name", "Role", "Platform", "Profile Link", "Relevance",
                  "Best Outreach Angle", "Cold DM Hook", "Email", "Telegram",
                  "Outreach Status", "Notes"]

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)

    # ── Telegram DM scripts ──
    tg_contacts = [c for c in contacts if c["Telegram"]]
    if tg_contacts:
        tg_path = os.path.join(DMS_DIR, "telegram-outreach.md")
        with open(tg_path, "w", encoding="utf-8") as f:
            f.write("# Telegram BD Outreach — DM Scripts\n")
            f.write(f"Generated: 2026-03-25\n")
            f.write(f"Total contacts with TG handles: {len(tg_contacts)}\n")
            f.write("Status: DRAFT — Do not send without review\n\n---\n\n")
            for c in tg_contacts:
                dm = generate_tg_dm(c)
                f.write(f"## {c['Name']} ({c['Exchange']})\n")
                f.write(f"**Telegram:** {c['Telegram']}  \n")
                f.write(f"**Role:** {c['Role']}  \n\n")
                f.write(f"```\n{dm}\n```\n\n")
                # Also include the original Cold DM Hook from the raw data
                if c["Cold DM Hook"] and c["Cold DM Hook"] != "Not Contacted":
                    f.write(f"**Original DM Hook (from research):**\n> {c['Cold DM Hook']}\n\n")
                f.write("---\n\n")

    # ── Direct email for contacts with email addresses ──
    email_contacts = [c for c in contacts if c["Email"]]
    if email_contacts:
        email_path = os.path.join(EMAILS_DIR, "direct-emails.md")
        with open(email_path, "w", encoding="utf-8") as f:
            f.write("# Direct Email Outreach (Verified Email Addresses)\n")
            f.write(f"Generated: 2026-03-25\n")
            f.write(f"Total contacts with emails: {len(email_contacts)}\n")
            f.write("Status: DRAFT — Do not send without review\n\n---\n\n")
            for c in email_contacts:
                email_text = generate_direct_email(c)
                f.write(f"## {c['Name']} ({c['Exchange']})\n")
                f.write(f"**Email:** {c['Email']}  \n")
                f.write(f"**Role:** {c['Role']}  \n\n")
                f.write(f"```\n{email_text}\n```\n\n---\n\n")

    # ── Print summary ──
    print("=== REBUILD COMPLETE ===")
    print(f"Total valid contacts: {len(contacts)}")
    print(f"Duplicates removed: {dupes}")
    print(f"Contacts with Telegram: {len(tg_contacts)}")
    for c in tg_contacts:
        print(f"  - {c['Name']} ({c['Exchange']}) — {c['Telegram']}")
    print(f"Contacts with Email: {len(email_contacts)}")
    for c in email_contacts:
        print(f"  - {c['Name']} ({c['Exchange']}) — {c['Email']}")

    # Count contacts with Cold DM Hooks from original data
    dm_hooks = [c for c in contacts if c["Cold DM Hook"] and c["Cold DM Hook"] != "Not Contacted"]
    print(f"\nContacts with original Cold DM Hooks: {len(dm_hooks)}")
    print(f"\nCSV saved to: {OUT_CSV}")
    if tg_contacts:
        print(f"Telegram DMs saved to: {os.path.join(DMS_DIR, 'telegram-outreach.md')}")
    if email_contacts:
        print(f"Direct emails saved to: {os.path.join(EMAILS_DIR, 'direct-emails.md')}")

if __name__ == "__main__":
    main()
