"""
Auto-post Instagram Reels via Graph API (resumable upload).

Usage:
  python scripts/post_reel.py <video_path> "<caption>"
  python scripts/post_reel.py --from-notion           # posts all "Ready to Post" Reels

Env vars required: IG_USER_ID, IG_ACCESS_TOKEN
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
API_VERSION = "v22.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"


def post_reel(video_path: str, caption: str = "") -> dict:
    """Upload and publish a Reel to Instagram via resumable upload."""
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    file_size = video_path.stat().st_size
    print(f"[1/4] Creating media container for {video_path.name} ({file_size / 1e6:.1f} MB)...")

    # Step 1: Create resumable upload container
    resp = requests.post(
        f"{BASE}/{IG_USER_ID}/media",
        headers={"Authorization": f"Bearer {IG_ACCESS_TOKEN}"},
        json={
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    container_id = data["id"]
    upload_uri = data["uri"]
    print(f"  Container: {container_id}")

    # Step 2: Upload video binary
    print(f"[2/4] Uploading video to {upload_uri[:60]}...")
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
    print("[3/4] Waiting for processing...")
    for i in range(30):  # max 5 minutes
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
        print(f"  Status: {status_code} ({i * 10}s)")

        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            raise RuntimeError(f"Processing failed: {status_data}")
    else:
        raise TimeoutError("Processing timed out after 5 minutes")

    # Step 4: Publish
    print("[4/4] Publishing Reel...")
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


def post_from_notion():
    """Find Notion entries with Production Status = 'Ready to Post' and post them."""
    # This requires the Notion API — for now, manual posting is supported
    # Future: integrate with Notion SDK to read Content Calendar
    print("Notion auto-posting not yet connected. Use manual mode:")
    print('  python scripts/post_reel.py <video_path> "<caption>"')


if __name__ == "__main__":
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("ERROR: Set IG_USER_ID and IG_ACCESS_TOKEN in .env")
        sys.exit(1)

    if len(sys.argv) >= 3:
        video = sys.argv[1]
        caption = sys.argv[2]
        result = post_reel(video, caption)
        print(f"\nDone. Media ID: {result['media_id']}")
    elif len(sys.argv) == 2 and sys.argv[1] == "--from-notion":
        post_from_notion()
    else:
        print("Usage:")
        print('  python scripts/post_reel.py <video_path> "<caption>"')
        print("  python scripts/post_reel.py --from-notion")
