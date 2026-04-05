"""
Generate personalized BD outreach drafts for all "Not Contacted" contacts.
Reads CSV, generates tiered cold emails, saves to 06-Drafts/outreach/emails/,
updates CSV status to "Outreach Draft Ready".
"""
import csv
import os
import re
from datetime import datetime

BASE = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain"
CSV_PATH = os.path.join(BASE, "10-Niche-Knowledge", "partnerships", "crypto-exchange-bd-contacts.csv")
EMAILS_DIR = os.path.join(BASE, "06-Drafts", "outreach", "emails")
DMS_DIR = os.path.join(BASE, "06-Drafts", "outreach", "dms")

os.makedirs(EMAILS_DIR, exist_ok=True)
os.makedirs(DMS_DIR, exist_ok=True)

DATE = datetime.now().strftime("%Y-%m-%d")

# ── Role classification ──
def classify_role(role: str, name: str) -> str:
    """Tier contacts by seniority for personalization depth."""
    r = role.lower() if role else ""
    n = name.lower() if name else ""
    if any(x in r for x in ["head of", "co-founder", "coo", "ceo", "cmo", "chief", "director", "c-level"]):
        return "executive"
    if any(x in r for x in ["senior", "lead", "team lead"]):
        return "senior"
    if any(x in r for x in ["kol", "influencer", "affiliate"]):
        return "kol_focused"
    if any(x in r for x in ["listing"]):
        return "listing"
    if any(x in r for x in ["community", "ambassador", "moderator", "social media", "event", "marketing"]):
        return "community"
    if "n/a" in r or "n/a" in n:
        return "skip"
    return "bd_manager"

def is_valid_contact(row: dict) -> bool:
    """Filter out N/A and fallback entries."""
    name = row.get("Name", "").strip()
    role = row.get("Role", "").strip()
    if not name or name.startswith("N/A"):
        return False
    if "No verified" in name or "not available" in role.lower():
        return False
    if role.startswith("N/A"):
        return False
    return True

def get_first_name(name: str) -> str:
    """Extract first name."""
    parts = name.strip().split()
    if parts:
        # Handle initials like "DD" or single-char names
        return parts[0]
    return name

def get_region_hook(relevance: str) -> str:
    """Extract region for personalization."""
    r = relevance.lower()
    if "nigeria" in r or "africa" in r or "lagos" in r:
        return "Africa"
    if "dubai" in r or "uae" in r or "mena" in r:
        return "MENA"
    if "india" in r or "south asia" in r or "pakistan" in r:
        return "South Asia"
    if "singapore" in r or "hong kong" in r or "japan" in r or "indonesia" in r or "korea" in r or "malaysia" in r or "sea" in r:
        return "Asia-Pacific"
    if "brazil" in r or "latam" in r or "colombia" in r or "argentina" in r or "venezuela" in r:
        return "LATAM"
    if "uk" in r or "london" in r or "germany" in r or "europe" in r or "spain" in r or "italy" in r or "croatia" in r or "switzerland" in r or "cyprus" in r or "netherlands" in r or "malta" in r or "ukraine" in r or "russia" in r or "moscow" in r or "turkey" in r or "kosovo" in r or "albania" in r or "barcelona" in r:
        return "Europe"
    if "us" in r or "san francisco" in r or "seattle" in r:
        return "US"
    return ""

# ── Email templates by tier ──

def generate_executive_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]
    role = row["Role"]
    region = get_region_hook(row.get("Relevance", ""))

    region_line = f" I've been watching {exchange}'s growth in {region} closely." if region else f" I've been watching {exchange}'s growth closely."

    return f"""Subject: KOL Partnership — Quivira x {exchange}

{name},

I'll keep this direct.{region_line}

I'm Quivira (@big_quiv) — crypto KOL and builder across X, LinkedIn, Instagram, and TikTok. My AI signal system scans 50 pairs every 4 hours and delivers filtered setups to an active trading community. I create daily content that breaks down markets, trades, and Web3 strategy for an engaged audience of traders and builders.

What I bring to a partnership:
- Multi-platform content (threads, carousels, reels, scripts) — not just a retweet
- AI-powered signal distribution to an active Telegram community
- Educational content that drives real trading volume, not vanity metrics
- Consistent weekly output — this is a system, not a side project

I'm looking for a structured KOL or affiliate partnership with {exchange}. Not a one-off post. A real collaboration that drives volume and user acquisition.

Worth a 15-minute call this week?

— Quivira
@big_quiv | X · LinkedIn · Instagram · TikTok
"""

def generate_senior_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]
    role = row["Role"]
    region = get_region_hook(row.get("Relevance", ""))

    region_line = f" Especially the push in {region}." if region else ""

    return f"""Subject: KOL Partnership Inquiry — @big_quiv x {exchange}

{name},

Reaching out because I've been following {exchange}'s BD moves.{region_line}

Quick intro — I'm @big_quiv (Quivira). I run a multi-platform crypto brand focused on trading education, AI-powered signals, and Web3 content. My system scans 50 pairs every 4 hours, filters for confluence, and delivers setups to an active community on Telegram.

Content goes out daily across X, LinkedIn, Instagram, and TikTok — threads, carousels, reels, video scripts. Not recycled tweets. Original, platform-native content that drives engagement and trading activity.

I'm exploring KOL and affiliate partnerships with exchanges that value consistent volume over one-time promotions. {exchange} is on that list.

Happy to share my media kit and performance data. What's the best way to continue this conversation on your end?

— Quivira
@big_quiv
"""

def generate_kol_focused_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]
    role = row["Role"]
    region = get_region_hook(row.get("Relevance", ""))

    return f"""Subject: KOL Collab — @big_quiv x {exchange}

{name},

Saw you handle KOL partnerships at {exchange}. This should land right in your lane.

I'm @big_quiv — crypto KOL running an AI-powered signal system and content engine across X, LinkedIn, Instagram, and TikTok. My scanner checks 50 pairs every 4 hours and delivers filtered setups to a live Telegram community. Content drops daily — not just tweets, but threads, carousels, reels, and educational breakdowns.

What makes this different from a typical KOL pitch:
- Volume is system-driven, not hype-driven. My community trades consistently.
- Content is multi-platform and original. Each platform gets native format.
- I have a built audience of traders and builders who trust signal over noise.

I'd like to explore a KOL partnership or affiliate program with {exchange}. Can you share the process or connect me with the right person?

— Quivira
@big_quiv
"""

def generate_bd_manager_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]
    role = row["Role"]
    region = get_region_hook(row.get("Relevance", ""))

    region_line = f" I've seen {exchange} making moves in {region} — solid positioning." if region else ""

    return f"""Subject: Partnership Inquiry — @big_quiv x {exchange}

{name},

Quick intro — I'm @big_quiv (Quivira), crypto KOL and builder with an active presence across X, LinkedIn, Instagram, and TikTok.{region_line}

I run an AI-powered signal system that scans 50 pairs every 4 hours and delivers filtered trade setups to my Telegram community. On the content side, I produce daily threads, carousels, reels, and educational breakdowns that drive engagement and trading activity.

I'm looking to establish a KOL or affiliate partnership with {exchange}. Interested in a structured collaboration — not a one-off post, but consistent volume-driving content and community activation.

Would you be the right person to discuss this with, or could you point me to the BD/KOL team?

— Quivira
@big_quiv
"""

def generate_listing_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]

    return f"""Subject: KOL Partnership — @big_quiv x {exchange}

{name},

I know your focus is listings, but I wanted to reach out in case there's crossover with KOL partnerships at {exchange}.

I'm @big_quiv — crypto KOL running an AI signal system and multi-platform content engine (X, LinkedIn, Instagram, TikTok). My community actively trades on major exchanges and I'm expanding partnership conversations.

If {exchange} has a KOL or affiliate program, I'd appreciate a warm intro to the right person on the BD side. Happy to share my media kit.

— Quivira
@big_quiv
"""

def generate_community_email(row: dict) -> str:
    name = get_first_name(row["Name"])
    exchange = row["Exchange"]
    role = row["Role"]

    return f"""Subject: Quick Question — KOL Partnerships at {exchange}

{name},

I'm @big_quiv — crypto KOL with an active community and multi-platform content operation. I'm looking to set up a KOL or affiliate partnership with {exchange}.

Could you point me to the right person on the BD or partnerships team? I'd appreciate the connect.

— Quivira
@big_quiv
"""

# ── Template router ──
GENERATORS = {
    "executive": generate_executive_email,
    "senior": generate_senior_email,
    "kol_focused": generate_kol_focused_email,
    "bd_manager": generate_bd_manager_email,
    "listing": generate_listing_email,
    "community": generate_community_email,
}

# ── Main ──
def main():
    # Read CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    fieldnames = reader.fieldnames

    # Track stats
    stats = {"total": 0, "generated": 0, "skipped": 0, "by_tier": {}, "by_exchange": {}}

    # Group by exchange for file output
    exchange_emails = {}

    for i, row in enumerate(rows):
        stats["total"] += 1

        if row.get("Outreach Status", "").strip() != "Not Contacted":
            continue

        if not is_valid_contact(row):
            stats["skipped"] += 1
            continue

        tier = classify_role(row.get("Role", ""), row.get("Name", ""))
        if tier == "skip":
            stats["skipped"] += 1
            continue

        # Generate email
        generator = GENERATORS.get(tier, generate_bd_manager_email)
        email_text = generator(row)

        exchange = row["Exchange"].strip()
        name = row["Name"].strip()

        if exchange not in exchange_emails:
            exchange_emails[exchange] = []

        exchange_emails[exchange].append({
            "name": name,
            "role": row.get("Role", ""),
            "tier": tier,
            "email": email_text,
        })

        # Update status
        rows[i]["Outreach Status"] = "Outreach Draft Ready"

        stats["generated"] += 1
        stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1
        stats["by_exchange"][exchange] = stats["by_exchange"].get(exchange, 0) + 1

    # Save emails grouped by exchange
    for exchange, contacts in exchange_emails.items():
        slug = re.sub(r'[^a-z0-9]+', '-', exchange.lower()).strip('-')
        filepath = os.path.join(EMAILS_DIR, f"{slug}-outreach.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {exchange} — BD Outreach Drafts\n")
            f.write(f"Generated: {DATE}\n")
            f.write(f"Total contacts: {len(contacts)}\n")
            f.write(f"Status: DRAFT — Do not send without review\n\n")
            f.write("---\n\n")

            for c in contacts:
                f.write(f"## {c['name']}\n")
                f.write(f"**Role:** {c['role']}  \n")
                f.write(f"**Tier:** {c['tier']}  \n\n")
                f.write("```\n")
                f.write(c["email"].strip())
                f.write("\n```\n\n")
                f.write("---\n\n")

    # Write updated CSV (temp file then replace to handle OneDrive locks)
    import shutil, tempfile
    tmp_csv = os.path.join(os.path.dirname(CSV_PATH), "bd-contacts-tmp.csv")
    with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    try:
        shutil.move(tmp_csv, CSV_PATH)
    except PermissionError:
        print(f"\nWARNING: Could not overwrite original CSV (OneDrive lock).")
        print(f"Updated CSV saved to: {tmp_csv}")
        print(f"Manually replace the original when OneDrive releases the lock.")

    # Print summary
    print(f"=== OUTREACH DRAFT GENERATION COMPLETE ===")
    print(f"Total contacts: {stats['total']}")
    print(f"Drafts generated: {stats['generated']}")
    print(f"Skipped (N/A or invalid): {stats['skipped']}")
    print(f"\nBy tier:")
    for tier, count in sorted(stats["by_tier"].items(), key=lambda x: -x[1]):
        print(f"  {tier}: {count}")
    print(f"\nBy exchange:")
    for ex, count in sorted(stats["by_exchange"].items(), key=lambda x: -x[1]):
        print(f"  {ex}: {count}")
    print(f"\nFiles saved to: {EMAILS_DIR}")
    print(f"CSV updated: {CSV_PATH}")

if __name__ == "__main__":
    main()
