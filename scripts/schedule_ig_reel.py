"""
Schedule an Instagram Reel with custom cover via Graph API (resumable upload).

Usage:
  python scripts/schedule_ig_reel.py <video_path> "<caption>" <cover_url> <publish_time_utc>

  publish_time_utc format: "2026-04-03T15:30:00" (ISO 8601, UTC)
  If publish_time_utc is "now", publishes immediately.

Env vars required: IG_USER_ID, IG_ACCESS_TOKEN
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
API_VERSION = "v22.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"


def schedule_reel(video_path: str, caption: str, cover_url: str = None, publish_time_utc: str = "now") -> dict:
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    file_size = video_path.stat().st_size
    print(f"[1/5] Creating media container for {video_path.name} ({file_size / 1e6:.1f} MB)...")

    # Step 1: Create resumable upload container
    payload = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption,
    }
    if cover_url:
        payload["cover_url"] = cover_url
        print(f"  Cover URL: {cover_url[:80]}...")

    resp = requests.post(
        f"{BASE}/{IG_USER_ID}/media",
        headers={"Authorization": f"Bearer {IG_ACCESS_TOKEN}"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    container_id = data["id"]
    upload_uri = data["uri"]
    print(f"  Container: {container_id}")

    # Step 2: Upload video binary
    print(f"[2/5] Uploading video...")
    with open(video_path, "rb") as f:
        upload_resp = requests.post(
            upload_uri,
            headers={
                "Authorization": f"OAuth {IG_ACCESS_TOKEN}",
                "offset": "0",
                "file_size": str(file_size),
            },
            data=f,
            timeout=300,
        )
    upload_resp.raise_for_status()
    print(f"  Upload response: {upload_resp.json()}")

    # Step 3: Poll for processing completion
    print("[3/5] Waiting for processing...")
    for i in range(30):
        time.sleep(10)
        status_resp = requests.get(
            f"{BASE}/{container_id}",
            params={
                "fields": "id,status,status_code,video_status",
                "access_token": IG_ACCESS_TOKEN,
            },
            timeout=15,
        )
        status_data = status_resp.json()
        status_code = status_data.get("status_code", "UNKNOWN")
        print(f"  Status: {status_code} ({(i + 1) * 10}s)")

        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            raise RuntimeError(f"Processing failed: {status_data}")
    else:
        raise TimeoutError("Processing timed out after 5 minutes")

    # Step 4: Wait for scheduled publish time
    if publish_time_utc != "now":
        target = datetime.fromisoformat(publish_time_utc).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        wait_seconds = (target - now).total_seconds()

        if wait_seconds > 0:
            print(f"[4/5] Waiting {wait_seconds:.0f}s until {publish_time_utc} UTC...")
            time.sleep(wait_seconds)
        else:
            print(f"[4/5] Target time already passed, publishing now...")
    else:
        print("[4/5] Publishing immediately...")

    # Step 5: Publish
    print("[5/5] Publishing Reel...")
    publish_resp = requests.post(
        f"{BASE}/{IG_USER_ID}/media_publish",
        headers={"Authorization": f"Bearer {IG_ACCESS_TOKEN}"},
        data={"creation_id": container_id},
        timeout=30,
    )
    publish_resp.raise_for_status()
    media_id = publish_resp.json()["id"]
    print(f"  Published! Media ID: {media_id}")

    return {"media_id": media_id, "container_id": container_id}


if __name__ == "__main__":
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("ERROR: Set IG_USER_ID and IG_ACCESS_TOKEN in .env")
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Usage:")
        print('  python scripts/schedule_ig_reel.py <video> "<caption>" [cover_url] [publish_time_utc|now]')
        sys.exit(1)

    video = sys.argv[1]
    caption = sys.argv[2]
    cover = sys.argv[3] if len(sys.argv) > 3 else None
    pub_time = sys.argv[4] if len(sys.argv) > 4 else "now"

    result = schedule_reel(video, caption, cover, pub_time)
    print(f"\nDone. Media ID: {result['media_id']}")
