"""
Polymarket Telegram Bot — Multi-channel distribution with approval flow.

Sends Polymarket and trading signals to approval channel, then distributes
approved signals to Hustler's Krib, dedicated channels, and queues for X/Twitter.

Usage:
    python scripts/polymarket_bot.py --send-signal <json_file>    # Send signal from JSON file
    python scripts/polymarket_bot.py --send-signal -              # Read signal JSON from stdin
    python scripts/polymarket_bot.py --send-ta                    # Send TA trading signals for approval
    python scripts/polymarket_bot.py --test                       # Test bot connectivity
    python scripts/polymarket_bot.py --approve <message_id>       # Manually approve a signal
    python scripts/polymarket_bot.py --poll                       # Poll for approval callbacks
    python scripts/polymarket_bot.py --broadcast <message>        # Send message to all channels
"""

import os
import sys
import json
import argparse
import threading
import time
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import schedule
except ImportError:
    schedule = None

import subprocess

try:
    from supabase import create_client as _supabase_create_client
    _SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    _SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    _supabase = _supabase_create_client(_SUPABASE_URL, _SUPABASE_KEY) if _SUPABASE_URL and _SUPABASE_KEY else None
except ImportError:
    _supabase = None
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from polymarket_scanner import format_signal_card, format_trading_signal_card

# --- HTTP Session with retry ---

def _build_session():
    """Build a requests session with retry logic for GET only.

    POST requests (sendMessage etc.) are NOT idempotent — if a 502/503/504
    arrives after Telegram already processed the request, an automatic retry
    sends the message again, causing duplicate messages.  Restrict retries
    to GET so only safe operations like getUpdates are retried.
    """
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET"],        # Only retry GET, never POST
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

_session = _build_session()


def _telegram_request(method, endpoint, **kwargs):
    """Make a Telegram API request, falling back to curl if requests fails."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{endpoint}"
    kwargs.setdefault("timeout", 30)

    try:
        if method == "get":
            resp = _session.get(url, **kwargs)
        else:
            resp = _session.post(url, **kwargs)
        return resp.json()
    except requests.RequestException:
        # Only fallback to curl for GET requests — POST (sendMessage etc.) is not
        # idempotent: if requests sent the message but failed reading the response,
        # a curl retry would send a duplicate message.
        if method != "get":
            return None
        try:
            cmd = ["curl", "-s", "--connect-timeout", "30", url]
            if "params" in kwargs:
                from urllib.parse import urlencode
                params_str = urlencode(kwargs["params"])
                cmd = ["curl", "-s", "--connect-timeout", str(kwargs.get("timeout", 30)),
                       f"{url}?{params_str}"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            if result.stdout:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None


# --- Config ---

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
KRIB_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")                    # Hustler's Krib
POLY_CHANNEL_ID = os.getenv("TELEGRAM_POLY_CHANNEL_ID", "")         # Dedicated Poly channel
APPROVAL_CHANNEL_ID = os.getenv("TELEGRAM_APPROVAL_CHANNEL_ID", "") # Private approval
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")             # Your personal DM with bot
TEST_CHANNEL_ID = os.getenv("TELEGRAM_TEST_CHANNEL_ID", "")        # Signal testing/paper trade group

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Typefully
TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")
TYPEFULLY_SOCIAL_SET_ID = os.getenv("TYPEFULLY_SOCIAL_SET_ID", "")  # Auto-discovered if blank
TYPEFULLY_API_BASE = "https://api.typefully.com/v2"

# Pending approvals file
VAULT_DIR = os.path.join(os.path.dirname(__file__), "..")
PENDING_FILE = os.path.join(VAULT_DIR, "07-Analytics", "signal-performance", "pending-poly-signals.json")

# Drafts directory for ghostwriter integration
DRAFTS_DIR = os.path.join(VAULT_DIR, "06-Drafts", "polymarket")


# --- Subscriber Channels ---

def _get_subscriber_channels():
    """Return list of approved subscriber chat IDs from Supabase."""
    if not _supabase:
        return []
    try:
        resp = _supabase.table('subscriber_channels').select('chat_id').eq('status', 'approved').execute()
        return [r['chat_id'] for r in (resp.data or [])]
    except Exception as e:
        print(f"[Subscribers] Error fetching channels: {e}")
        return []


def _send_to_subscribers(text, parse_mode="HTML"):
    """Send a message to all approved subscriber channels. Returns count of successful sends."""
    channels = _get_subscriber_channels()
    if not channels:
        return 0
    sent = 0
    for chat_id in channels:
        try:
            result = send_message(chat_id, text, parse_mode=parse_mode)
            if result and result.get("ok"):
                sent += 1
            else:
                desc = result.get("description", "Unknown") if result else "No response"
                print(f"[Subscribers] FAIL sending to {chat_id}: {desc}")
        except Exception as e:
            print(f"[Subscribers] ERROR sending to {chat_id}: {e}")
    if sent:
        print(f"[Subscribers] Sent to {sent}/{len(channels)} subscriber channel(s).")
    return sent


# --- Typefully Integration ---

_typefully_social_set_id_cache = None


def _get_typefully_social_set_id():
    """Get the Typefully social set ID (cached). Auto-discovers from API if not in env."""
    global _typefully_social_set_id_cache

    if TYPEFULLY_SOCIAL_SET_ID:
        return TYPEFULLY_SOCIAL_SET_ID

    if _typefully_social_set_id_cache:
        return _typefully_social_set_id_cache

    try:
        resp = _session.get(
            f"{TYPEFULLY_API_BASE}/social-sets",
            headers={"Authorization": f"Bearer {TYPEFULLY_API_KEY}"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                _typefully_social_set_id_cache = results[0]["id"]
                return _typefully_social_set_id_cache
        print(f"Typefully: could not discover social set ID (HTTP {resp.status_code})")
    except Exception as e:
        print(f"Typefully: error discovering social set ID: {e}")

    return None


def push_to_typefully(tweet_text, publish=False):
    """Push a tweet to Typefully. If publish=True, publishes immediately via publish_at='now'.
    Returns draft ID or None."""
    if not TYPEFULLY_API_KEY:
        print("[Typefully] SKIP: TYPEFULLY_API_KEY not set.")
        return None

    social_set_id = _get_typefully_social_set_id()
    if not social_set_id:
        print("[Typefully] FAIL: no social set ID available. Set TYPEFULLY_SOCIAL_SET_ID in .env or check API key.")
        return None

    payload = {
        "platforms": {
            "x": {
                "enabled": True,
                "posts": [{"text": tweet_text}],
            }
        }
    }

    if publish:
        payload["publish_at"] = "now"

    action = "publish" if publish else "draft"
    print(f"[Typefully] Sending {action}: {tweet_text[:60]}...")

    try:
        resp = _session.post(
            f"{TYPEFULLY_API_BASE}/social-sets/{social_set_id}/drafts",
            headers={
                "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        if resp.status_code == 201:
            draft = resp.json()
            draft_id = draft.get("id", "unknown")
            print(f"[Typefully] OK: {action} created (id: {draft_id})")
            return draft_id
        else:
            body = resp.text[:300]
            print(f"[Typefully] FAIL: {action} creation failed (HTTP {resp.status_code}): {body}")
    except Exception as e:
        print(f"[Typefully] ERROR: {action} failed: {e}")

    return None


# --- Telegram Helpers ---

def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    """Send a message via Telegram Bot API."""
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return None

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup

    data = _telegram_request("post", "sendMessage", json=payload)
    if data and not data.get("ok"):
        print(f"Telegram API error: {data.get('description', 'Unknown error')}")
        # Retry without parse_mode if markdown fails
        if parse_mode:
            payload.pop("parse_mode", None)
            data = _telegram_request("post", "sendMessage", json=payload)
    return data


def get_updates(offset=None, timeout=30):
    """Get updates from Telegram (for polling approval responses)."""
    params = {"timeout": str(timeout)}
    if offset:
        params["offset"] = str(offset)

    data = _telegram_request("get", "getUpdates", params=params, timeout=timeout + 5)
    if data:
        return data.get("result", [])
    return []


def test_bot():
    """Test bot connectivity and channel access."""
    if not BOT_TOKEN:
        print("FAIL: TELEGRAM_BOT_TOKEN not set")
        return False

    # Test bot info
    data = _telegram_request("get", "getMe")
    if data and data.get("ok"):
        bot = data["result"]
        print(f"Bot: @{bot.get('username', 'unknown')} ({bot.get('first_name', '')})")
    else:
        print(f"FAIL: Could not reach Telegram API")
        return False

    # Test each destination
    channels = {
        "Hustler's Krib": KRIB_CHAT_ID,
        "Poly Channel": POLY_CHANNEL_ID,
        "Approval (channel)": APPROVAL_CHANNEL_ID,
        "Approval (your DM)": ADMIN_CHAT_ID,
        "Test Channel": TEST_CHANNEL_ID,
    }

    for name, chat_id in channels.items():
        if not chat_id:
            print(f"  {name}: NOT CONFIGURED (missing env var)")
            continue
        data = _telegram_request("get", "getChat", params={"chat_id": str(chat_id)})
        if data and data.get("ok"):
            chat = data["result"]
            print(f"  {name}: OK — {chat.get('title', chat.get('first_name', chat_id))}")
        else:
            desc = data.get("description", "Unknown") if data else "Connection failed"
            print(f"  {name}: FAIL — {desc}")

    return True


# --- Signal Distribution ---

def save_pending_signal(signal, callback_id, krib_msg_id=None, x_msg_id=None):
    """Save signal to pending approvals file, keyed by callback hash."""
    pending = load_pending_signals()
    pending[callback_id] = {
        "signal": signal,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "krib_status": "pending",
        "x_status": "pending",
        "typefully_id": None,
        "krib_msg_id": str(krib_msg_id) if krib_msg_id else None,
        "x_msg_id": str(x_msg_id) if x_msg_id else None,
    }

    os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, default=str)


def _find_pending_by_msg_id(msg_id):
    """Find a pending entry by either krib_msg_id or x_msg_id. Returns (callback_id, entry) or (None, None)."""
    pending = load_pending_signals()
    msg_id_str = str(msg_id)
    for cb_id, entry in pending.items():
        if entry.get("krib_msg_id") == msg_id_str or entry.get("x_msg_id") == msg_id_str:
            return cb_id, entry
        # Backward compat: old-format entries are keyed by msg_id directly
        if cb_id == msg_id_str and "status" in entry:
            return cb_id, entry
    return None, None


def load_pending_signals():
    """Load pending signals from file."""
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def send_to_approval(signal):
    """Send signal to approval channel with separate Krib and X approval messages."""
    if signal.get('signal_type') == 'trading':
        card = format_trading_signal_card(signal, for_telegram=True)
        raw_id = f"{signal['pair']}_{signal['timeframe']}_{int(datetime.now(timezone.utc).timestamp())}"
    else:
        card = format_signal_card(signal, for_telegram=True)
        raw_id = f"{signal['market_id']}_{int(datetime.now(timezone.utc).timestamp())}"
    # Bug #10: Use hash to avoid callback_data collisions (Telegram max 64 bytes)
    import hashlib
    callback_id = hashlib.md5(raw_id.encode()).hexdigest()[:16]

    approval_dest = APPROVAL_CHANNEL_ID or ADMIN_CHAT_ID or KRIB_CHAT_ID

    # --- Message 1: Krib approval (VIP group only) ---
    krib_card = f"📌 <b>Hustler's Krib (VIP)</b>\n\n{card}"
    krib_markup = {
        "inline_keyboard": [[
            {"text": "✅ Send to Krib", "callback_data": f"appkrib_{callback_id}"},
            {"text": "❌ Reject", "callback_data": f"rejkrib_{callback_id}"},
        ]]
    }
    krib_result = send_message(approval_dest, krib_card, reply_markup=krib_markup)
    krib_msg_id = krib_result["result"]["message_id"] if krib_result and krib_result.get("ok") else None

    # --- Message 2: Public channels (Poly + subscribers) ---
    pub_card = f"📢 <b>Public Channels (Alpha Plays + Subscribers)</b>\n\n{card}"
    pub_markup = {
        "inline_keyboard": [[
            {"text": "✅ Send Public", "callback_data": f"apppub_{callback_id}"},
            {"text": "❌ Skip Public", "callback_data": f"rejpub_{callback_id}"},
        ]]
    }
    pub_result = send_message(approval_dest, pub_card, reply_markup=pub_markup)
    pub_msg_id = pub_result["result"]["message_id"] if pub_result and pub_result.get("ok") else None

    # --- Message 3: X/Twitter approval (tweet preview) ---
    is_trading = signal.get('signal_type') == 'trading'
    tweet_text = _get_trading_tweet_text(signal) if is_trading else _get_poly_tweet_text(signal)
    x_card = f"🐦 <b>X/Twitter Preview</b>\n\n<pre>{tweet_text}</pre>"
    x_markup = {
        "inline_keyboard": [[
            {"text": "✅ Post to X", "callback_data": f"appx_{callback_id}"},
            {"text": "❌ Skip X", "callback_data": f"rejx_{callback_id}"},
        ]]
    }
    x_result = send_message(approval_dest, x_card, reply_markup=x_markup)
    x_msg_id = x_result["result"]["message_id"] if x_result and x_result.get("ok") else None

    if krib_msg_id or pub_msg_id or x_msg_id:
        save_pending_signal(signal, callback_id, krib_msg_id=krib_msg_id, x_msg_id=x_msg_id)
        print(f"Signal sent for approval (krib: {krib_msg_id}, pub: {pub_msg_id}, x: {x_msg_id}, hash: {callback_id})")
        return krib_msg_id
    else:
        print("Failed to send signal to approval channel")
        return None


def distribute_to_telegram(signal):
    """Distribute signal to Telegram channels (Krib, Poly, subscribers) + draft file + tracker."""
    is_trading = signal.get('signal_type') == 'trading'

    if is_trading:
        card = format_trading_signal_card(signal, for_telegram=True)
    else:
        card = format_signal_card(signal, for_telegram=True)

    results = {}

    # 1. Send to Hustler's Krib
    if KRIB_CHAT_ID:
        result = send_message(KRIB_CHAT_ID, card)
        results["krib"] = "OK" if result and result.get("ok") else "FAIL"
        print(f"  Hustler's Krib: {results['krib']}")

    # 2. Send to Poly channel (all signal types)
    if POLY_CHANNEL_ID:
        result = send_message(POLY_CHANNEL_ID, card)
        results["poly"] = "OK" if result and result.get("ok") else "FAIL"
        print(f"  Poly Channel: {results['poly']}")

    # 3. Queue tweet draft file (non-critical — don't block distribution on file errors)
    try:
        if is_trading:
            draft_path, _ = create_trading_twitter_draft(signal)
        else:
            draft_path, _ = create_twitter_draft(signal)
        if draft_path:
            results["twitter_draft"] = "QUEUED"
            print(f"  X/Twitter Draft: QUEUED at {draft_path}")
    except Exception as e:
        results["twitter_draft"] = "FAIL"
        print(f"  X/Twitter Draft: FAIL — {e}")

    # 4. Send to subscriber channels
    sub_count = _send_to_subscribers(card)
    if sub_count:
        results["subscribers"] = f"{sub_count} sent"

    # 5. Log to tracker
    if is_trading:
        log_trading_to_tracker(signal)
    else:
        log_to_tracker(signal)
    results["tracker"] = "LOGGED"
    print(f"  Signal Tracker: LOGGED")

    return results


def publish_to_x(signal, pending_entry=None):
    """Publish a signal to X/Twitter via Typefully. Deduplicates using typefully_id in pending_entry."""
    # Dedup: if already posted, skip
    if pending_entry and pending_entry.get("typefully_id"):
        print(f"[Typefully] Already posted (id: {pending_entry['typefully_id']}). Skipping.")
        return pending_entry["typefully_id"]

    is_trading = signal.get('signal_type') == 'trading'
    tweet_text = _get_trading_tweet_text(signal) if is_trading else _get_poly_tweet_text(signal)
    if not tweet_text:
        return None
    return push_to_typefully(tweet_text, publish=True)


def distribute_signal(signal, include_x=False):
    """Backward-compat wrapper: distribute to Telegram, optionally X."""
    results = distribute_to_telegram(signal)
    if include_x:
        typefully_id = publish_to_x(signal)
        if typefully_id:
            results["typefully"] = "PUBLISHED"
            print(f"  Typefully: PUBLISHED (id: {typefully_id})")
        elif TYPEFULLY_API_KEY:
            results["typefully"] = "FAIL"
            print(f"  Typefully: FAIL — check logs above for details")
    return results


def create_twitter_draft(signal):
    """Create a tweet draft from signal for ghostwriter pickup. Returns (filepath, tweet_text)."""
    os.makedirs(DRAFTS_DIR, exist_ok=True)

    tweet = _get_poly_tweet_text(signal)

    # Save as draft
    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y-%m-%d')}-poly-{signal['category']}-{signal['market_id'][:8]}.md"
    filepath = os.path.join(DRAFTS_DIR, filename)

    content = (
        f"---\n"
        f"status: pending\n"
        f"platform: X\n"
        f"content_type: tweet\n"
        f"goal: authority\n"
        f"source: polymarket-scanner\n"
        f"market_id: {signal['market_id']}\n"
        f"---\n\n"
        f"{tweet}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath, tweet


def log_to_tracker(signal):
    """Log approved signal to polymarket signals log + write JSON sidecar with factor details."""
    log_path = os.path.join(
        VAULT_DIR, "07-Analytics", "signal-performance", "polymarket-signals-log.md"
    )

    if not os.path.exists(log_path):
        # Will be created by polymarket_tracker.py
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yes_pct = round(signal["current_odds"]["yes"] * 100, 1)
    no_pct = round(signal["current_odds"]["no"] * 100, 1)
    model_pct = round(signal["model_probability"] * 100, 1)
    edge_pct = round(signal["edge"] * 100, 1)

    # Read current log to get next signal number
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Count existing signals
    lines = content.strip().split("\n")
    signal_count = sum(1 for line in lines if line.startswith("|") and line[1:2].strip().isdigit())
    next_num = signal_count + 1

    # Append signal row
    source = signal.get('source', 'manual')
    row = (
        f"| {next_num} | {now} | {signal['market_question'][:40]} | "
        f"{signal['recommendation']} | {yes_pct}%/{no_pct}% | "
        f"{model_pct}% | +{edge_pct}% | {signal['confidence']:.0f} | "
        f"{source} | ACTIVE | — | — |\n"
    )

    # Insert before the closing --- or at end
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(row)

    # Write JSON sidecar with full factor details for tuning analysis
    details_dir = os.path.join(
        VAULT_DIR, "07-Analytics", "signal-performance", "signal-details"
    )
    os.makedirs(details_dir, exist_ok=True)

    sidecar = {
        "signal_num": next_num,
        "date": now,
        "market_id": signal.get("market_id", ""),
        "market_question": signal.get("market_question", ""),
        "category": signal.get("category", ""),
        "recommendation": signal.get("recommendation", ""),
        "current_odds": signal.get("current_odds", {}),
        "model_probability": signal.get("model_probability", 0),
        "edge": signal.get("edge", 0),
        "confidence": signal.get("confidence", 0),
        "factor_agreement": signal.get("factor_agreement", ""),
        "factors": signal.get("factors", {}),
        "factor_details": signal.get("factor_details", {}),
    }

    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    sidecar_path = os.path.join(details_dir, f"{next_num}-{now_ts}.json")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, default=str)


TRADING_DRAFTS_DIR = os.path.join(VAULT_DIR, "06-Drafts", "trading")
TRADING_LOG_PATH = os.path.join(
    VAULT_DIR, "07-Analytics", "signal-performance", "trading-signals-log.md"
)


def _get_trading_tweet_text(signal):
    """Return tweet text for a trading signal with updated CTA."""
    pair = signal.get('pair', 'UNKNOWN')
    direction = signal.get('direction', 'NEUTRAL')
    entry = signal.get('entry', 0)
    tp1 = signal.get('tp1', 0)
    sl = signal.get('stop_loss', 0)
    strength = signal.get('strength_score', 0)
    conf_count = signal.get('confluence_count', 0)

    from polymarket_scanner import detect_market_type
    mtype = detect_market_type(signal)
    type_label = "Forex" if mtype == 'FOREX' else "Crypto"

    return (
        f"New {type_label.lower()} signal\n\n"
        f"{pair} {direction}\n\n"
        f"Entry: {entry}\n"
        f"SL: {sl}\n"
        f"TP1: {tp1}\n\n"
        f"Strength: {strength}/10 | {conf_count} confluences\n\n"
        f"Full levels and analysis in the VIP Hustlers Krib\n"
        f"Link to access in comments"
    )


def _get_poly_tweet_text(signal):
    """Return tweet text for a polymarket signal with updated CTA."""
    yes_pct = round(signal["current_odds"]["yes"] * 100, 1)
    no_pct = round(signal["current_odds"]["no"] * 100, 1)
    edge_pct = round(signal["edge"] * 100, 1)
    rec = signal["recommendation"]
    rec_odds = yes_pct if rec == "YES" else no_pct
    model_pct = round(signal["model_probability"] * 100, 1)

    return (
        f"New prediction market signal\n\n"
        f"{signal['market_question']}\n\n"
        f"Market says: {rec_odds}%\n"
        f"My model says: {model_pct}%\n"
        f"Edge: +{edge_pct}%\n\n"
        f"Recommendation: {rec}\n"
        f"Confidence: {signal['confidence']:.0f}/100\n\n"
        f"Full breakdown in the VIP Hustlers Krib\n"
        f"Link to access in comments"
    )


def create_trading_twitter_draft(signal):
    """Create a tweet draft from a trading signal for ghostwriter pickup. Returns (filepath, tweet_text)."""
    os.makedirs(TRADING_DRAFTS_DIR, exist_ok=True)

    tweet = _get_trading_tweet_text(signal)

    pair = signal.get('pair', 'UNKNOWN')
    safe_pair = pair.replace('/', '-')  # GBP/JPY -> GBP-JPY (avoid path separator in filename)
    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y-%m-%d')}-ta-{safe_pair}-{signal.get('timeframe', '4h')}.md"
    filepath = os.path.join(TRADING_DRAFTS_DIR, filename)

    content = (
        f"---\n"
        f"status: pending\n"
        f"platform: X\n"
        f"content_type: tweet\n"
        f"goal: authority\n"
        f"source: binance-ta-runner\n"
        f"pair: {pair}\n"
        f"timeframe: {signal.get('timeframe', '4h')}\n"
        f"---\n\n"
        f"{tweet}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath, tweet


def _safe_float(val):
    """Convert value to float, return None if not possible."""
    if val is None or val == '':
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def log_trading_to_tracker(signal):
    """Log approved trading signal to Supabase trading_signals table."""
    row = {
        'pair': signal.get('pair', ''),
        'timeframe': signal.get('timeframe', ''),
        'direction': signal.get('direction', ''),
        'entry_price': _safe_float(signal.get('entry')),
        'stop_loss': _safe_float(signal.get('stop_loss')),
        'tp1': _safe_float(signal.get('tp1')),
        'tp2': _safe_float(signal.get('tp2')),
        'tp3': _safe_float(signal.get('tp3')),
        'strength_score': _safe_float(signal.get('strength_score')),
        'confluence_count': int(signal['confluence_count']) if signal.get('confluence_count') is not None else None,
        'confluences': ', '.join(signal.get('confluences', [])) if isinstance(signal.get('confluences'), list) else signal.get('confluences', ''),
        'trend': signal.get('trend', ''),
        'source': signal.get('source', 'manual'),
        'status': 'PENDING_ENTRY',
    }

    if _supabase:
        try:
            _supabase.table('trading_signals').insert(row).execute()
            print(f"  Supabase: LOGGED ({row['pair']} {row['direction']})")
            return
        except Exception as e:
            print(f"  Supabase log error: {e}")

    # Fallback to local markdown if Supabase unavailable
    log_dir = os.path.dirname(TRADING_LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)
    if not os.path.exists(TRADING_LOG_PATH):
        header = (
            "# Trading Signals Log\n\n"
            "| # | Date | Pair | TF | Direction | Entry | SL | TP1 | TP2 | TP3 | Strength | Confluences | Status |\n"
            "|---|------|------|----|-----------|-------|----|-----|-----|-----|----------|-------------|--------|\n"
        )
        with open(TRADING_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(header)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_row = (
        f"| — | {now} | {row['pair']} | {row['timeframe']} | {row['direction']} | "
        f"{row['entry_price']} | {row['stop_loss']} | {row['tp1']} | {row['tp2']} | {row['tp3']} | "
        f"{row['strength_score']}/10 | {row['confluence_count']} | PENDING_ENTRY |\n"
    )
    with open(TRADING_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(md_row)


# --- Signal Monitor (Auto TP/SL Detection) ---

def _update_trading_signal_supabase(signal_id, updates):
    """Update a trading signal row in Supabase. Returns True/False."""
    if not _supabase:
        return False
    try:
        _supabase.table('trading_signals').update(updates).eq('id', signal_id).execute()
        return True
    except Exception as e:
        print(f"[MONITOR] Supabase update error for id={signal_id}: {e}")
        return False


def _check_signal_levels(signal, current_price):
    """
    Check if a Supabase trading_signals row has hit TP or SL levels.
    Returns dict with hits, recommended_status, pnl_pct.
    """
    direction = (signal.get('direction') or '').upper()
    entry = signal.get('entry_price')
    sl = signal.get('stop_loss')
    tp1 = signal.get('tp1')
    tp2 = signal.get('tp2')
    tp3 = signal.get('tp3')

    if entry is None or current_price is None:
        return {'hits': [], 'recommended_status': signal.get('status', 'ACTIVE'), 'pnl_pct': 0}

    # Bug #2: Prevent division by zero if entry is 0
    if entry == 0:
        print(f"[MONITOR] WARNING: entry price is 0 for {signal.get('pair', '?')}, skipping.")
        return {'hits': [], 'recommended_status': signal.get('status', 'ACTIVE'), 'pnl_pct': 0}

    current_status = signal.get('status', 'ACTIVE')

    # --- PENDING_ENTRY: wait for price to reach entry zone before tracking TP/SL ---
    if current_status == 'PENDING_ENTRY':
        if direction == 'LONG' and current_price >= entry * 0.998:
            return {'hits': ['ENTRY HIT'], 'recommended_status': 'ACTIVE', 'pnl_pct': 0}
        elif direction == 'SHORT' and current_price <= entry * 1.002:
            return {'hits': ['ENTRY HIT'], 'recommended_status': 'ACTIVE', 'pnl_pct': 0}
        return {'hits': [], 'recommended_status': 'PENDING_ENTRY', 'pnl_pct': 0}

    # --- ACTIVE / TP1 HIT / TP2 HIT: existing TP/SL tracking ---
    hits = []
    pnl_pct = 0.0  # Bug #1: Initialize before if/elif to prevent UnboundLocalError

    if direction == 'LONG':
        if sl and current_price <= sl:
            hits.append('SL HIT')
        if tp1 and current_price >= tp1:
            hits.append('TP1 HIT')
        if tp2 and current_price >= tp2:
            hits.append('TP2 HIT')
        if tp3 and current_price >= tp3:
            hits.append('TP3 HIT')
        pnl_pct = ((current_price - entry) / entry) * 100
    elif direction == 'SHORT':
        if sl and current_price >= sl:
            hits.append('SL HIT')
        if tp1 and current_price <= tp1:
            hits.append('TP1 HIT')
        if tp2 and current_price <= tp2:
            hits.append('TP2 HIT')
        if tp3 and current_price <= tp3:
            hits.append('TP3 HIT')
        pnl_pct = ((entry - current_price) / entry) * 100
    else:
        print(f"[MONITOR] WARNING: unexpected direction '{direction}' for {signal.get('pair', '?')}")

    # Determine recommended status (SL overrides everything)
    if 'SL HIT' in hits:
        recommended = 'STOPPED OUT'
    elif 'TP3 HIT' in hits:
        recommended = 'TP3 HIT'
    elif 'TP2 HIT' in hits:
        recommended = 'TP2 HIT'
    elif 'TP1 HIT' in hits:
        recommended = 'TP1 HIT'
    else:
        recommended = signal.get('status', 'ACTIVE')

    return {'hits': hits, 'recommended_status': recommended, 'pnl_pct': pnl_pct}


def _format_hit_notification(signal, current_price, new_status, check_result):
    """Format a Telegram notification card for a TP/SL hit."""
    pair = signal.get('pair', 'UNKNOWN')
    direction = signal.get('direction', '')
    entry = signal.get('entry_price', 0)
    pnl = check_result.get('pnl_pct', 0)
    pnl_str = f"+{pnl:.2f}%" if pnl >= 0 else f"{pnl:.2f}%"

    suppress_pnl = False

    if new_status == 'ACTIVE' and 'ENTRY HIT' in check_result.get('hits', []):
        header = "ENTRY HIT"
        status_line = "Entry price reached. Signal is now ACTIVE."
        suppress_pnl = True
    elif new_status == 'STOPPED OUT':
        header = "STOPPED OUT"
        status_line = "Signal closed at stop loss."
    elif new_status == 'TP3 HIT':
        header = "TP3 HIT — FULL WIN"
        status_line = "All targets hit. Signal closed."
    elif new_status == 'TP2 HIT':
        header = "TP2 HIT"
        status_line = "Trail your stop to TP1. Lock in profits. TP3 still active."
    elif new_status == 'TP1 HIT':
        header = "TP1 HIT"
        remaining = []
        if signal.get('tp2'):
            remaining.append('TP2')
        if signal.get('tp3'):
            remaining.append('TP3')
        remaining_str = f" {'/'.join(remaining)} still active." if remaining else ""
        status_line = f"Move your SL to entry (risk-free trade). Take partial profits.{remaining_str}"
    else:
        header = "SIGNAL UPDATE"
        status_line = ""

    # Detect market type for labeling
    from polymarket_scanner import detect_market_type
    mtype = detect_market_type(signal)
    if mtype == 'FOREX':
        type_label = "\U0001f4b1 FOREX"
    else:
        type_label = "\u20bf CRYPTO"

    # Format price display
    is_forex = mtype == 'FOREX'
    if is_forex:
        price_fmt = lambda p: f"{p:.5f}" if p else "—"
    elif entry and entry < 1:
        price_fmt = lambda p: f"{p:.6f}" if p else "—"
    else:
        price_fmt = lambda p: f"{p:,.2f}" if p else "—"

    sl = signal.get('stop_loss')
    tp1 = signal.get('tp1')
    tp2 = signal.get('tp2')
    tp3 = signal.get('tp3')

    lines = [
        f"<b>{type_label} SIGNAL UPDATE</b>\n",
        f"<b>{header}</b>\n",
        f"<b>Pair:</b> {pair}",
        f"<b>Direction:</b> {direction}",
        f"<b>Entry:</b> {price_fmt(entry)}",
        f"<b>Current:</b> {price_fmt(current_price)}",
        f"<b>SL:</b> {price_fmt(sl)}",
        f"<b>TP1:</b> {price_fmt(tp1)} | <b>TP2:</b> {price_fmt(tp2)} | <b>TP3:</b> {price_fmt(tp3)}",
        f"<b>P&amp;L:</b> {'—' if suppress_pnl else pnl_str}",
    ]

    if status_line:
        lines.append(f"\n{status_line}")

    return "\n".join(lines)


def _signal_monitor_cycle():
    """Check all active signals against live prices and notify on TP/SL hits."""
    if not _supabase:
        print("[MONITOR] Supabase unavailable, skipping monitor cycle.")
        return

    try:
        resp = _supabase.table('trading_signals').select('*').in_(
            'status', ['PENDING_ENTRY', 'ACTIVE', 'TP1 HIT', 'TP2 HIT']
        ).execute()
        signals = resp.data or []
    except Exception as e:
        print(f"[MONITOR] Error querying active signals: {e}")
        return

    if not signals:
        print("[MONITOR] No active signals to check.")
        return

    print(f"[MONITOR] Checking {len(signals)} active signal(s)...")

    from market_data import (
        fetch_binance_spot_price, is_forex_pair, normalize_forex_symbol,
        fetch_twelvedata_price, fetch_coingecko_price, SYMBOL_TO_COINGECKO
    )

    for signal in signals:
        pair = signal.get('pair', '')
        current_price = None

        try:
            if is_forex_pair(pair):
                current_price = fetch_twelvedata_price(pair)
            else:
                # Crypto: try Binance first, fallback to CoinGecko
                # Bug #17: Normalize to Binance format (e.g. BTC/USD -> BTCUSDT)
                binance_symbol = pair.upper().replace('/', '')
                if binance_symbol.endswith('USD') and not binance_symbol.endswith('USDT') and not binance_symbol.endswith('USDC'):
                    binance_symbol = binance_symbol + 'T'  # USD -> USDT
                current_price = fetch_binance_spot_price(binance_symbol)
                if current_price is None:
                    coin_id = SYMBOL_TO_COINGECKO.get(binance_symbol)
                    if coin_id:
                        price_data = fetch_coingecko_price(coin_id)
                        if price_data:
                            current_price = price_data.get(coin_id, {}).get('usd')
                            if current_price is None:
                                print(f"[MONITOR] CoinGecko returned no 'usd' price for {coin_id}. Response keys: {list(price_data.keys())}")
        except Exception as e:
            print(f"[MONITOR] Price fetch failed for {pair}: {e}")
            continue

        if current_price is None:
            print(f"[MONITOR] No price for {pair}, skipping.")
            continue

        check = _check_signal_levels(signal, current_price)
        old_status = signal.get('status', 'ACTIVE')
        new_status = check['recommended_status']

        # Skip if no status change (prevents duplicate notifications)
        if new_status == old_status:
            continue

        print(f"[MONITOR] {pair}: {old_status} -> {new_status} (P&L: {check['pnl_pct']:+.2f}%)")

        # Build Supabase update
        updates = {'status': new_status}
        now_iso = datetime.now(timezone.utc).isoformat()

        if 'ENTRY HIT' in check['hits']:
            updates['hit_entry'] = True
            updates['entry_hit_at'] = now_iso
        if 'TP1 HIT' in check['hits']:
            updates['hit_tp1'] = True
        if 'TP2 HIT' in check['hits']:
            updates['hit_tp2'] = True
        if 'TP3 HIT' in check['hits']:
            updates['hit_tp3'] = True
        if 'SL HIT' in check['hits']:
            updates['hit_sl'] = True

        if new_status == 'TP3 HIT':
            updates['result'] = 'WIN'
            updates['pnl_percent'] = check['pnl_pct']
            updates['closed_at'] = now_iso
        elif new_status == 'STOPPED OUT':
            updates['result'] = 'LOSS'
            updates['pnl_percent'] = check['pnl_pct']
            updates['closed_at'] = now_iso

        # Update Supabase
        signal_id = signal.get('id')
        if not _update_trading_signal_supabase(signal_id, updates):
            continue

        # Send notification to Krib, Poly channel, test channel, and subscribers
        notification = _format_hit_notification(signal, current_price, new_status, check)

        if KRIB_CHAT_ID:
            send_message(KRIB_CHAT_ID, notification)
        if POLY_CHANNEL_ID:
            send_message(POLY_CHANNEL_ID, notification)
        if TEST_CHANNEL_ID:
            send_message(TEST_CHANNEL_ID, notification)
        _send_to_subscribers(notification)

    # Also auto-resolve Polymarket signals
    try:
        from polymarket_tracker import auto_resolve
        resolved = auto_resolve()
        if resolved:
            lines = [f"<b>{len(resolved)} Polymarket signal(s) resolved:</b>\n"]
            for u in resolved:
                lines.append(f"#{u['signal']} {u['market'][:30]} — <b>{u['new_status']}</b> ({u['pnl']})")
            msg = "\n".join(lines)
            if KRIB_CHAT_ID:
                send_message(KRIB_CHAT_ID, msg)
            if POLY_CHANNEL_ID:
                send_message(POLY_CHANNEL_ID, msg)
            _send_to_subscribers(msg)
            print(f"[MONITOR] {len(resolved)} Polymarket signal(s) auto-resolved.")
    except ImportError:
        pass
    except Exception as e:
        print(f"[MONITOR] Polymarket auto-resolve error: {e}")

    print("[MONITOR] Cycle complete.")


# --- Approval Polling ---

def poll_approvals(timeout=60):
    """Poll for approval/rejection callbacks."""
    print(f"Polling for approval responses ({timeout}s timeout)...")
    pending = load_pending_signals()

    if not pending:
        print("No pending signals.")
        return

    print(f"{len(pending)} pending signal(s)")

    offset = None
    end_time = datetime.now(timezone.utc).timestamp() + timeout

    while datetime.now(timezone.utc).timestamp() < end_time:
        updates = get_updates(offset=offset, timeout=10)

        for update in updates:
            offset = update["update_id"] + 1

            # Reload pending each iteration (another instance may have updated it)
            pending = load_pending_signals()

            # Check for callback queries (inline button presses)
            callback = update.get("callback_query")
            if callback:
                data = callback.get("data", "")

                # --- New-format callbacks ---
                if data.startswith("appkrib_") or data.startswith("rejkrib_"):
                    cb_hash = data.split("_", 1)[1]
                    entry = pending.get(cb_hash)
                    if entry:
                        signal = entry["signal"]
                        _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                        if data.startswith("appkrib_"):
                            if entry.get("krib_status") != "pending":
                                print(f"\nSKIP Krib (already {entry.get('krib_status')}): {_label}")
                            else:
                                print(f"\nAPPROVED Krib: {_label}")
                                entry["krib_status"] = "approved"
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                try:
                                    distribute_to_telegram(signal)
                                except Exception as e:
                                    print(f"  Krib distribution FAILED: {e}")
                                    entry["krib_status"] = "failed"
                                    pending[cb_hash] = entry
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                        else:  # rejkrib_
                            print(f"\nREJECTED Krib: {_label}")
                            entry["krib_status"] = "rejected"
                            pending[cb_hash] = entry
                            with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                json.dump(pending, f, indent=2, default=str)

                elif data.startswith("appx_") or data.startswith("rejx_"):
                    cb_hash = data.split("_", 1)[1]
                    entry = pending.get(cb_hash)
                    if entry:
                        signal = entry["signal"]
                        _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                        if data.startswith("appx_"):
                            if entry.get("x_status") != "pending" or entry.get("typefully_id"):
                                print(f"\nSKIP X (already posted): {_label}")
                            else:
                                print(f"\nAPPROVED X: {_label}")
                                entry["x_status"] = "approved"
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                typefully_id = publish_to_x(signal, pending_entry=entry)
                                if typefully_id:
                                    entry["typefully_id"] = typefully_id
                                    print(f"  Typefully: PUBLISHED (id: {typefully_id})")
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                        else:  # rejx_
                            print(f"\nSKIPPED X: {_label}")
                            entry["x_status"] = "rejected"
                            pending[cb_hash] = entry
                            with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                json.dump(pending, f, indent=2, default=str)

                else:
                    # --- Backward compat: old approve_/reject_ callbacks ---
                    msg_id = str(callback.get("message", {}).get("message_id", ""))
                    if msg_id in pending:
                        signal_data = pending[msg_id]
                        signal = signal_data["signal"]
                        _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]

                        if signal_data.get("status") != "pending":
                            print(f"\nSKIP (already {signal_data['status']}): {_label}")
                        elif data.startswith("approve_"):
                            print(f"\nAPPROVED: {_label}")
                            print("Distributing to all channels (including X — poll mode)...")
                            signal_data["status"] = "approved"
                            try:
                                distribute_signal(signal, include_x=True)
                            except Exception as e:
                                print(f"  Distribution FAILED: {e}")
                                signal_data["status"] = "failed"
                        elif data.startswith("reject_"):
                            print(f"\nREJECTED: {_label}")
                            signal_data["status"] = "rejected"

                        with open(PENDING_FILE, "w", encoding="utf-8") as f:
                            json.dump(pending, f, indent=2, default=str)

            # Check for text replies (APPROVE/REJECT)
            msg = update.get("message", {})
            text = (msg.get("text") or "").strip().upper()
            reply_to = msg.get("reply_to_message", {})
            reply_id = str(reply_to.get("message_id", ""))

            if text in ("APPROVE", "REJECT"):
                cb_key, entry = _find_pending_by_msg_id(reply_id)
                if cb_key and entry:
                    signal = entry["signal"]
                    _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]

                    if text == "APPROVE":
                        print(f"\nAPPROVED (reply): {_label}")
                        # New format
                        if "krib_status" in entry:
                            if entry.get("krib_status") == "pending":
                                entry["krib_status"] = "approved"
                                pending[cb_key] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                distribute_to_telegram(signal)
                            if entry.get("x_status") == "pending":
                                entry["x_status"] = "approved"
                                typefully_id = publish_to_x(signal, pending_entry=entry)
                                if typefully_id:
                                    entry["typefully_id"] = typefully_id
                            pending[cb_key] = entry
                        else:
                            # Old format
                            entry["status"] = "approved"
                            pending[cb_key] = entry
                            try:
                                distribute_signal(signal, include_x=True)
                            except Exception as e:
                                print(f"  Distribution FAILED: {e}")
                                entry["status"] = "failed"
                                pending[cb_key] = entry
                    else:
                        print(f"\nREJECTED (reply): {_label}")
                        if "krib_status" in entry:
                            entry["krib_status"] = "rejected"
                            entry["x_status"] = "rejected"
                        else:
                            entry["status"] = "rejected"
                        pending[cb_key] = entry

                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                        json.dump(pending, f, indent=2, default=str)

    print("\nPolling complete.")


def manual_approve(message_id):
    """Manually approve a pending signal by message ID or callback hash."""
    pending = load_pending_signals()
    msg_id = str(message_id)

    # Try direct key first, then search by msg_id
    if msg_id in pending:
        cb_key = msg_id
        entry = pending[msg_id]
    else:
        cb_key, entry = _find_pending_by_msg_id(msg_id)

    if not cb_key or not entry:
        print(f"No pending signal found for message_id {msg_id}")
        print(f"Pending IDs: {list(pending.keys())}")
        return

    signal = entry["signal"]
    print(f"Approving: {signal.get('market_question', signal.get('pair', 'Signal'))[:60]}")

    # New format
    if "krib_status" in entry:
        print("Distributing to Krib...")
        if entry.get("krib_status") == "pending":
            entry["krib_status"] = "approved"
            pending[cb_key] = entry
            with open(PENDING_FILE, "w", encoding="utf-8") as f:
                json.dump(pending, f, indent=2, default=str)
            results = distribute_to_telegram(signal)
        else:
            results = {"krib": f"already {entry.get('krib_status')}"}

        print("Publishing to X...")
        if entry.get("x_status") == "pending" and not entry.get("typefully_id"):
            entry["x_status"] = "approved"
            typefully_id = publish_to_x(signal, pending_entry=entry)
            if typefully_id:
                entry["typefully_id"] = typefully_id
                results["typefully"] = "PUBLISHED"
        else:
            results["typefully"] = f"already {entry.get('x_status')} (id: {entry.get('typefully_id')})"

        pending[cb_key] = entry
    else:
        # Old format
        print("Distributing to all channels (including X)...")
        results = distribute_signal(signal, include_x=True)
        entry["status"] = "approved"
        pending[cb_key] = entry

    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, default=str)

    print(f"\nDistribution complete: {results}")


# --- Bot Command Handler (Interactive Mode) ---

BOT_COMMANDS = [
    {"command": "start", "description": "Welcome message + menu"},
    {"command": "scan", "description": "Scan Polymarket for signals"},
    {"command": "ta", "description": "Send crypto trading signals for approval"},
    {"command": "scan_all", "description": "Full crypto TA scan (all pairs, all TFs)"},
    {"command": "scan_pair", "description": "Scan one pair (e.g. /scan_pair BTCUSDT)"},
    {"command": "scan_custom", "description": "Custom scan (e.g. /scan_custom ETHUSDT 1h,4h)"},
    {"command": "test_signals", "description": "Send signals to test channel (paper trade)"},
    {"command": "send_signals", "description": "Send TA signals to approval channel"},
    {"command": "send_signals_direct", "description": "Send TA signals directly (skip approval)"},
    {"command": "forex_scan", "description": "Full forex scan (all pairs, all TFs)"},
    {"command": "forex_pair", "description": "Scan one forex pair (e.g. /forex_pair EUR/USD)"},
    {"command": "forex_custom", "description": "Custom forex scan (e.g. /forex_custom EUR/USD 1h,4h)"},
    {"command": "top", "description": "Show top 10 markets by volume"},
    {"command": "status", "description": "Show active signals"},
    {"command": "performance", "description": "Win rate and metrics"},
    {"command": "resolve", "description": "Auto-resolve closed markets"},
    {"command": "setcap", "description": "Set daily auto-signal cap (e.g. /setcap 5)"},
    {"command": "help", "description": "Show all commands"},
]


def register_bot_commands():
    """Register bot commands with Telegram (shows menu in bot chat)."""
    data = _telegram_request("post", "setMyCommands", json={"commands": BOT_COMMANDS})
    if data and data.get("ok"):
        print("Bot commands registered successfully.")
        return True
    else:
        desc = data.get("description", "Unknown") if data else "Connection failed"
        print(f"Failed to register commands: {desc}")
        return False


def handle_start(chat_id):
    """Handle /start command — welcome message with menu."""
    text = (
        "<b>Welcome to the Polymarket Signal Bot</b> \n\n"
        "I scan prediction markets every hour and find signals "
        "with +10% edge for you to approve.\n\n"
        "<b>Commands:</b>\n"
        "/scan — Scan Polymarket for signals\n"
        "/ta — Send crypto TA signals for approval\n"
        "/scan_all — Full crypto scan (all pairs, all TFs)\n"
        "/scan_pair BTCUSDT — Scan one pair\n"
        "/scan_custom ETHUSDT 1h,4h — Custom scan\n"
        "/test_signals — Send to test channel (paper trade)\n"
        "/send_signals — Send TA signals for approval\n"
        "/send_signals_direct — Send directly (skip approval)\n"
        "/top — Top 10 markets by volume\n"
        "/status — Your active signals\n"
        "/performance — Win rate &amp; metrics\n"
        "/resolve — Check if markets resolved\n"
        "/setcap N — Set daily auto-signal cap\n"
        "/help — Show this menu\n\n"
        "When I find a signal, I'll send it here with "
        "Approve/Reject buttons. Tap to decide.\n\n"
        "<i>Powered by Quivira</i>"
    )
    reply_markup = {
        "keyboard": [
            [{"text": "/scan_all"}, {"text": "/scan"}],
            [{"text": "/send_signals"}, {"text": "/ta"}],
            [{"text": "/top"}, {"text": "/status"}],
            [{"text": "/performance"}, {"text": "/resolve"}],
            [{"text": "/help"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }
    send_message(chat_id, text, reply_markup=reply_markup)


def handle_scan(chat_id):
    """Handle /scan — run market scan and send results."""
    send_message(chat_id, "Scanning Polymarket for signals... (this takes ~30 seconds)")

    try:
        from polymarket_scanner import run_scan, format_signal_card
        signals = run_scan(json_output=False)

        if not signals:
            send_message(chat_id,
                "Scan complete. No signals meet the threshold right now.\n\n"
                "Filters: edge >= 10%, confidence >= 65, volume >= $50K"
            )
            return

        # Auto-send to test channel if configured
        if TEST_CHANNEL_ID:
            test_sent = _send_to_test_channel(signals)
            if test_sent:
                send_message(chat_id, f"Auto-sent <b>{test_sent}</b> Polymarket signal(s) to test channel.")

        send_message(chat_id, f"Found <b>{len(signals)} signal(s)</b>. Sending for review...")

        for signal in signals:
            send_to_approval(signal)

    except Exception as e:
        send_message(chat_id, f"Scan error: {e}")


def handle_top(chat_id):
    """Handle /top — show top markets."""
    try:
        from polymarket_scanner import fetch_active_markets, apply_filters
        import json as _json

        markets = fetch_active_markets(limit=100)
        filtered = apply_filters(markets)

        if not filtered:
            send_message(chat_id, "Could not fetch markets. Try again later.")
            return

        lines = ["<b>Top 10 Polymarket Markets</b>\n"]
        for i, m in enumerate(filtered[:10], 1):
            vol = float(m.get("volume24hr", 0) or 0)
            question = m.get("question", "N/A")
            outcome_prices = m.get("outcomePrices", "")
            try:
                if isinstance(outcome_prices, str):
                    prices = _json.loads(outcome_prices)
                else:
                    prices = outcome_prices
                yes_pct = round(float(prices[0]) * 100, 1)
            except Exception:
                yes_pct = "?"

            if vol >= 1_000_000:
                vol_str = f"${vol/1_000_000:.1f}M"
            elif vol >= 1_000:
                vol_str = f"${vol/1_000:.0f}K"
            else:
                vol_str = f"${vol:.0f}"

            lines.append(f"{i}. [{yes_pct}%] {question}\n   Vol: {vol_str}")

        send_message(chat_id, "\n".join(lines))

    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_status(chat_id):
    """Handle /status — show active Polymarket, Crypto, and Forex signals."""
    parts = []

    # --- Active Polymarket signals ---
    try:
        from polymarket_tracker import parse_signals_log
        signals = parse_signals_log()
        active = [s for s in signals if s["status"] == "ACTIVE"]

        if active:
            lines = [f"<b>Active Polymarket Signals ({len(active)})</b>\n"]
            for s in active:
                lines.append(
                    f"#{s['num']} | {s['market'][:35]}\n"
                    f"   {s['recommendation']} | Edge: {s['edge_pct']} | Conf: {s['confidence']}"
                )
            parts.append("\n".join(lines))
        else:
            parts.append("<b>Active Polymarket Signals (0)</b>\nNo active signals.")
    except Exception as e:
        parts.append(f"Polymarket status error: {e}")

    # --- Active Crypto & Forex signals from Supabase ---
    if _supabase:
        try:
            resp = _supabase.table('trading_signals').select('*').in_(
                'status', ['PENDING_ENTRY', 'ACTIVE', 'TP1 HIT', 'TP2 HIT']
            ).execute()
            rows = resp.data or []
            _CRYPTO_QUOTES = {'USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD', 'USD'}
            def _is_crypto_pair(pair):
                if not pair:
                    return True  # default to crypto
                if '/' in pair:
                    quote = pair.split('/')[-1].upper()
                    return quote in _CRYPTO_QUOTES
                return True  # no slash = Binance format = crypto
            crypto_active = [r for r in rows if _is_crypto_pair(r.get('pair', ''))]
            forex_active = [r for r in rows if not _is_crypto_pair(r.get('pair', ''))]

            def _format_signal_line(r):
                status_tag = r.get('status', '?')
                return (
                    f"[{status_tag}] {r.get('pair', '?')} | {r.get('direction', '?')} | {r.get('timeframe', '?')}\n"
                    f"   Entry: {r.get('entry_price', '?')} | SL: {r.get('stop_loss', '?')} | Strength: {r.get('strength_score', '?')}/10"
                )

            # Crypto
            if crypto_active:
                lines = [f"<b>Crypto Signals ({len(crypto_active)})</b>\n"]
                for r in crypto_active:
                    lines.append(_format_signal_line(r))
                parts.append("\n".join(lines))
            else:
                parts.append("<b>Crypto Signals (0)</b>\nNo active signals.")

            # Forex
            if forex_active:
                lines = [f"<b>Forex Signals ({len(forex_active)})</b>\n"]
                for r in forex_active:
                    lines.append(_format_signal_line(r))
                parts.append("\n".join(lines))
            else:
                parts.append("<b>Forex Signals (0)</b>\nNo active signals.")

        except Exception as e:
            parts.append(f"Trading signals status error: {e}")

    send_message(chat_id, "\n\n---\n\n".join(parts) if parts else "No active signals.")


def _trading_performance_section(rows, label):
    """Build a performance section string for a set of trading signal rows."""
    total = len(rows)
    if total == 0:
        return f"<b>{label}</b>\n\nNo signals yet."

    pending = sum(1 for r in rows if r.get('status') == 'PENDING_ENTRY')
    active = sum(1 for r in rows if r.get('status') in ('ACTIVE', 'TP1 HIT', 'TP2 HIT'))
    wins = sum(1 for r in rows if r.get('result') == 'WIN')
    losses = sum(1 for r in rows if r.get('result') == 'LOSS')
    closed = wins + losses
    win_rate = round(wins / closed * 100, 1) if closed > 0 else 0
    avg_strength = round(sum(r.get('strength_score', 0) or 0 for r in rows) / total, 1) if total > 0 else 0

    section = (
        f"<b>{label}</b>\n\n"
        f"Total Signals: {total}\n"
        f"Pending Entry: {pending}\n"
        f"Active: {active}\n"
        f"Closed: {closed}\n"
        f"Win Rate: {win_rate}%\n"
        f"Record: {wins}W / {losses}L\n"
        f"Avg Strength: {avg_strength}/10"
    )

    # Per-pair breakdown (top 5 by count)
    pair_counts = {}
    for r in rows:
        p = r.get('pair', '?')
        if p not in pair_counts:
            pair_counts[p] = {'total': 0, 'wins': 0, 'losses': 0}
        pair_counts[p]['total'] += 1
        if r.get('result') == 'WIN':
            pair_counts[p]['wins'] += 1
        elif r.get('result') == 'LOSS':
            pair_counts[p]['losses'] += 1

    top_pairs = sorted(pair_counts.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
    if top_pairs:
        section += "\n\n<b>By Pair (top 5):</b>"
        for pair, d in top_pairs:
            pc = d['wins'] + d['losses']
            wr = round(d['wins'] / pc * 100) if pc > 0 else 0
            section += f"\n  {pair}: {d['total']} signals, {d['wins']}W/{d['losses']}L ({wr}%)"

    return section


def handle_performance(chat_id):
    """Handle /performance — show polymarket, crypto, and forex metrics."""
    parts = []

    # --- Polymarket signals ---
    try:
        from polymarket_tracker import calculate_performance
        m = calculate_performance()
        parts.append(
            f"<b>Polymarket Signal Performance</b>\n\n"
            f"Total Signals: {m['total_signals']}\n"
            f"Active: {m['active']}\n"
            f"Resolved: {m['resolved']}\n"
            f"Win Rate: {m['win_rate']}%\n"
            f"Record: {m['wins']}W / {m['losses']}L\n"
            f"Avg Confidence: {m['avg_confidence']}\n"
            f"Avg Edge: +{m['avg_edge']}%"
        )
        if m["categories"]:
            parts[-1] += "\n\n<b>By Category:</b>"
            for cat, data in m["categories"].items():
                total = data["wins"] + data["losses"]
                wr = data["wins"] / total * 100 if total > 0 else 0
                parts[-1] += f"\n  {cat.upper()}: {data['wins']}W/{data['losses']}L ({wr:.0f}%)"
    except Exception as e:
        parts.append(f"Polymarket error: {e}")

    # --- Crypto & Forex signals from Supabase ---
    if _supabase:
        try:
            resp = _supabase.table('trading_signals').select('*').execute()
            rows = resp.data or []
            _CQ = {'USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD', 'USD'}
            def _is_crypto(pair):
                if not pair:
                    return True
                if '/' in pair:
                    return pair.split('/')[-1].upper() in _CQ
                return True
            crypto_rows = [r for r in rows if _is_crypto(r.get('pair', ''))]
            forex_rows = [r for r in rows if not _is_crypto(r.get('pair', ''))]

            parts.append(_trading_performance_section(crypto_rows, "Crypto Signal Performance"))
            parts.append(_trading_performance_section(forex_rows, "Forex Signal Performance"))

        except Exception as e:
            parts.append(f"Trading signals error: {e}")

    send_message(chat_id, "\n\n---\n\n".join(parts) if parts else "No performance data yet.")


def handle_resolve(chat_id):
    """Handle /resolve — auto-resolve closed markets."""
    send_message(chat_id, "Checking for resolved markets...")

    try:
        from polymarket_tracker import auto_resolve
        updates = auto_resolve()

        if not updates:
            send_message(chat_id, "No signals resolved in this check.")
        else:
            lines = [f"<b>{len(updates)} signal(s) resolved:</b>\n"]
            for u in updates:
                sig_num = u.get('signal', '?')
                market = u.get('market', 'Unknown')[:30]
                status = u.get('new_status', '?')
                pnl = u.get('pnl', '?')
                lines.append(f"#{sig_num} {market} — <b>{status}</b> ({pnl})")
            send_message(chat_id, "\n".join(lines))

    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_ta(chat_id):
    """Handle /ta — load TA signals and send qualifying ones for approval."""
    send_message(chat_id, "Loading trading signals from TA analysis...")

    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=60)

        if not signals:
            send_message(chat_id,
                "No qualifying trading signals right now.\n\n"
                "Run <code>python scripts/binance_ta_runner.py</code> first, or data may be stale (&gt;60 min)."
            )
            return

        # Auto-send to test channel if configured
        if TEST_CHANNEL_ID:
            test_sent = _send_to_test_channel(signals)
            if test_sent:
                send_message(chat_id, f"Auto-sent <b>{test_sent}</b> crypto signal(s) to test channel.")

        send_message(chat_id, f"Found <b>{len(signals)} trading signal(s)</b>. Sending for review...")

        for signal in signals:
            send_to_approval(signal)

    except Exception as e:
        send_message(chat_id, f"TA signal error: {e}")


def handle_setcap(chat_id, text=""):
    """Handle /setcap — set daily auto-signal cap."""
    parts = text.strip().split()
    if len(parts) < 2:
        send_message(chat_id, "Usage: <code>/setcap 5</code> — sets daily auto-signal cap to 5")
        return

    try:
        new_cap = int(parts[1])
        if new_cap < 1 or new_cap > 50:
            send_message(chat_id, "Cap must be between 1 and 50.")
            return
    except ValueError:
        send_message(chat_id, "Invalid number. Usage: <code>/setcap 5</code>")
        return

    try:
        from unified_auto_scanner import update_cap, load_state
        actual_cap = update_cap(new_cap)
        state = load_state()
        send_message(
            chat_id,
            f"Daily auto-signal cap set to <b>{actual_cap}</b>.\n"
            f"Today's usage: {state['signals_sent']}/{actual_cap}"
        )
    except Exception as e:
        send_message(chat_id, f"Error setting cap: {e}")


def _run_ta_script(chat_id, args_list, label):
    """Run binance_ta_runner.py with given args via subprocess, report results."""
    script_path = os.path.join(os.path.dirname(__file__), "binance_ta_runner.py")
    if not os.path.exists(script_path):
        send_message(chat_id, f"Error: <code>binance_ta_runner.py</code> not found.")
        return False

    cmd = [sys.executable, script_path] + args_list
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        # Send last few lines of output as status
        lines = result.stdout.strip().split('\n') if result.stdout else []
        status_line = lines[-1] if lines else "Scan complete."
        if result.returncode != 0:
            err = result.stderr[:300] if result.stderr else "Unknown error"
            send_message(chat_id, f"[{label}] Scan failed:\n<code>{err}</code>")
            return False
        send_message(chat_id, f"[{label}] {status_line}")
        return True
    except subprocess.TimeoutExpired:
        send_message(chat_id, f"[{label}] Scan timed out after 5 minutes.")
        return False
    except Exception as e:
        send_message(chat_id, f"[{label}] Error: {e}")
        return False


def _send_ta_signals_to_approval(chat_id):
    """Load TA signals from JSON and send qualifying ones for approval + test channel."""
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        if not signals:
            send_message(chat_id, "No qualifying signals (3+ confluences) in latest scan.")
            return 0

        # Auto-send to test channel if configured (no approval needed, auto-tracked)
        if TEST_CHANNEL_ID:
            test_sent = _send_to_test_channel(signals)
            if test_sent:
                send_message(chat_id, f"Auto-sent <b>{test_sent}</b> signal(s) to test channel.")

        send_message(chat_id, f"Found <b>{len(signals)}</b> qualifying signal(s). Sending for approval...")
        sent = 0
        for signal in signals:
            msg_id = send_to_approval(signal)
            if msg_id:
                sent += 1
        send_message(chat_id, f"Sent <b>{sent}</b> signal(s) to approval channel. Review and approve/reject.")
        return sent
    except Exception as e:
        send_message(chat_id, f"Signal load error: {e}")
        return 0


def _run_forex_script(chat_id, args_list, label):
    """Run forex_ta_runner.py with given args via subprocess, report results."""
    script_path = os.path.join(os.path.dirname(__file__), "forex_ta_runner.py")
    if not os.path.exists(script_path):
        send_message(chat_id, f"Error: <code>forex_ta_runner.py</code> not found.")
        return False

    cmd = [sys.executable, script_path] + args_list
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        lines = result.stdout.strip().split('\n') if result.stdout else []
        status_line = lines[-1] if lines else "Scan complete."
        if result.returncode != 0:
            combined = (result.stderr or '') + (result.stdout or '')
            err = combined.strip()[-400:] if combined.strip() else "Unknown error"
            send_message(chat_id, f"[{label}] Scan failed:\n<code>{err}</code>")
            return False
        send_message(chat_id, f"[{label}] {status_line}")
        return True
    except subprocess.TimeoutExpired:
        send_message(chat_id, f"[{label}] Scan timed out after 10 minutes.")
        return False
    except Exception as e:
        send_message(chat_id, f"[{label}] Error: {e}")
        return False


def _send_forex_signals_to_approval(chat_id):
    """Load forex signals from JSON and send qualifying ones for approval + test channel."""
    try:
        from forex_ta_runner import load_forex_signals
        signals = load_forex_signals(max_age_minutes=90)
        if not signals:
            send_message(chat_id, "No qualifying forex signals (3+ confluences) in latest scan.")
            return 0

        # Auto-send to test channel if configured
        if TEST_CHANNEL_ID:
            test_sent = _send_to_test_channel(signals)
            if test_sent:
                send_message(chat_id, f"Auto-sent <b>{test_sent}</b> forex signal(s) to test channel.")

        send_message(chat_id, f"Found <b>{len(signals)}</b> qualifying forex signal(s). Sending for approval...")
        sent = 0
        for signal in signals:
            msg_id = send_to_approval(signal)
            if msg_id:
                sent += 1
        send_message(chat_id, f"Sent <b>{sent}</b> forex signal(s) to approval channel. Review and approve/reject.")
        return sent
    except Exception as e:
        send_message(chat_id, f"Forex signal load error: {e}")
        return 0


def handle_forex_scan(chat_id):
    """Handle /forex_scan — full forex scan, then send signals for approval."""
    send_message(chat_id, "Running full forex TA scan (8 pairs, all timeframes)... This takes ~3 minutes.")
    ok = _run_forex_script(chat_id, [], "FOREX SCAN ALL")
    if ok:
        _send_forex_signals_to_approval(chat_id)


def handle_forex_pair(chat_id, text=""):
    """Handle /forex_pair EUR/USD — scan one forex pair, then send signals for approval."""
    parts = text.strip().split()
    if len(parts) < 2:
        send_message(chat_id, "Usage: <code>/forex_pair EUR/USD</code>")
        return
    pair = parts[1].upper()
    send_message(chat_id, f"Scanning forex pair <b>{pair}</b> on all timeframes (1h, 4h, 1d)...")
    ok = _run_forex_script(chat_id, ["--pair", pair], f"FOREX {pair}")
    if ok:
        _send_forex_signals_to_approval(chat_id)


def handle_forex_custom(chat_id, text=""):
    """Handle /forex_custom EUR/USD 1h,4h — scan forex pair on specific timeframes."""
    parts = text.strip().split()
    if len(parts) < 3:
        send_message(chat_id, "Usage: <code>/forex_custom EUR/USD 1h,4h</code>")
        return
    pair = parts[1].upper()
    timeframes = parts[2]
    send_message(chat_id, f"Scanning forex <b>{pair}</b> on <b>{timeframes}</b>...")
    ok = _run_forex_script(chat_id, ["--pair", pair, "--timeframe", timeframes], f"FOREX {pair} {timeframes}")
    if ok:
        _send_forex_signals_to_approval(chat_id)


def handle_scan_all(chat_id):
    """Handle /scan_all — full crypto TA scan, then send signals for approval."""
    send_message(chat_id, "Running full crypto TA scan (all pairs, all timeframes)... This takes ~60 seconds.")
    ok = _run_ta_script(chat_id, [], "SCAN ALL")
    if ok:
        _send_ta_signals_to_approval(chat_id)


def handle_scan_pair(chat_id, text=""):
    """Handle /scan_pair BTCUSDT — scan one pair, then send signals for approval."""
    parts = text.strip().split()
    if len(parts) < 2:
        send_message(chat_id, "Usage: <code>/scan_pair BTCUSDT</code>")
        return
    pair = parts[1].upper()
    send_message(chat_id, f"Scanning <b>{pair}</b> on all timeframes (1h, 4h, 1d)...")
    ok = _run_ta_script(chat_id, ["--pair", pair], f"SCAN {pair}")
    if ok:
        _send_ta_signals_to_approval(chat_id)


def handle_scan_custom(chat_id, text=""):
    """Handle /scan_custom ETHUSDT 1h,4h — scan pair on specific timeframes, then send signals."""
    parts = text.strip().split()
    if len(parts) < 3:
        send_message(chat_id, "Usage: <code>/scan_custom ETHUSDT 1h,4h</code>")
        return
    pair = parts[1].upper()
    timeframes = parts[2]
    send_message(chat_id, f"Scanning <b>{pair}</b> on <b>{timeframes}</b>...")
    ok = _run_ta_script(chat_id, ["--pair", pair, "--timeframe", timeframes], f"SCAN {pair} {timeframes}")
    if ok:
        _send_ta_signals_to_approval(chat_id)


def _send_to_test_channel(signals, chat_id=None):
    """Send signals to test channel and log to tracker for automatic monitoring.
    Returns number of signals sent. If chat_id provided, sends status messages there."""
    if not TEST_CHANNEL_ID:
        if chat_id:
            send_message(chat_id, "No test channel configured. Set TELEGRAM_TEST_CHANNEL_ID env var.")
        return 0

    sent = 0
    for signal in signals:
        if signal.get('signal_type') == 'trading':
            card = format_trading_signal_card(signal, for_telegram=True)
        else:
            card = format_signal_card(signal, for_telegram=True)

        trend = signal.get('trend', '?')
        header = f"🧪 <b>TEST SIGNAL</b>\n<b>Trend:</b> {trend}\n\n"
        card = header + card

        result = send_message(TEST_CHANNEL_ID, card)
        if result and result.get("ok"):
            sent += 1
            # Log to tracker so the monitor auto-tracks TP/SL hits
            try:
                if signal.get('signal_type') == 'trading':
                    log_trading_to_tracker(signal)
                else:
                    log_to_tracker(signal)
            except Exception as e:
                print(f"  [TEST] Tracker log error: {e}")

    return sent


def handle_test_signals(chat_id):
    """Handle /test_signals — send signal cards to test channel for paper trading verification."""
    send_message(chat_id, "Loading signals for test channel...")
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        if not signals:
            send_message(chat_id, "No qualifying signals (3+ confluences) in latest scan.")
            return
        sent = _send_to_test_channel(signals, chat_id)
        send_message(chat_id, f"Sent <b>{sent}</b> signal(s) to test channel. Monitor will auto-track TP/SL hits.")
    except Exception as e:
        send_message(chat_id, f"Test signal error: {e}")


def handle_send_signals(chat_id):
    """Handle /send_signals — send qualifying TA signals to approval channel."""
    send_message(chat_id, "Loading latest TA signals...")
    _send_ta_signals_to_approval(chat_id)


def handle_send_signals_direct(chat_id):
    """Handle /send_signals_direct — send TA signals directly, skip approval."""
    send_message(chat_id, "Loading and distributing TA signals directly (skipping approval)...")
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        if not signals:
            send_message(chat_id, "No qualifying signals (3+ confluences) in latest scan.")
            return
        sent = 0
        for signal in signals:
            distribute_signal(signal, include_x=True)
            sent += 1
        send_message(chat_id, f"Distributed <b>{sent}</b> signal(s) directly to all channels.")
    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_chatid(chat_id):
    """Reply with the chat ID — useful for finding group/channel IDs."""
    send_message(chat_id, f"<code>{chat_id}</code>")


# --- Subscriber Channel Commands ---

def _is_admin(chat_id):
    """Check if a chat_id is the bot admin."""
    admin = ADMIN_CHAT_ID or APPROVAL_CHANNEL_ID
    return str(chat_id) == str(admin)


def handle_subscribe(chat_id):
    """Handle /subscribe — request to receive signals in this group/channel."""
    if not _supabase:
        send_message(chat_id, "Subscription system unavailable.")
        return

    chat_id_str = str(chat_id)

    # Check if already registered
    try:
        existing = _supabase.table('subscriber_channels').select('*').eq('chat_id', chat_id_str).execute()
        if existing.data:
            row = existing.data[0]
            if row['status'] == 'approved':
                send_message(chat_id, "This channel is already subscribed and receiving signals.")
                return
            elif row['status'] == 'pending':
                send_message(chat_id, "Your subscription request is pending approval. Hang tight.")
                return
            elif row['status'] == 'removed':
                # Re-request
                _supabase.table('subscriber_channels').update({
                    'status': 'pending',
                    'added_at': datetime.now(timezone.utc).isoformat()
                }).eq('chat_id', chat_id_str).execute()
                send_message(chat_id, "Subscription re-requested. Waiting for admin approval.")
                # Notify admin
                admin_dest = ADMIN_CHAT_ID or APPROVAL_CHANNEL_ID
                if admin_dest:
                    send_message(admin_dest, f"<b>Re-subscription request</b> from <code>{chat_id_str}</code>\nApprove with: <code>/approve_channel {chat_id_str}</code>")
                return  # Bug #4: Must return here to prevent duplicate INSERT
    except Exception as e:
        send_message(chat_id, f"Error: {e}")
        return

    # Get chat name
    chat_name = chat_id_str
    try:
        data = _telegram_request("get", "getChat", params={"chat_id": chat_id_str})
        if data and data.get("ok"):
            chat_info = data["result"]
            chat_name = chat_info.get("title", chat_info.get("first_name", chat_id_str))
    except Exception:
        pass

    # Insert pending subscription
    try:
        _supabase.table('subscriber_channels').insert({
            'chat_id': chat_id_str,
            'name': chat_name,
            'status': 'pending',
        }).execute()
    except Exception as e:
        send_message(chat_id, f"Error registering: {e}")
        return

    send_message(chat_id, "Subscription request sent. You'll receive signals once approved by @Big_Quiv.")

    # Notify admin
    admin_dest = ADMIN_CHAT_ID or APPROVAL_CHANNEL_ID
    if admin_dest:
        send_message(
            admin_dest,
            f"<b>New subscriber request</b>\n\n"
            f"<b>Channel:</b> {chat_name}\n"
            f"<b>Chat ID:</b> <code>{chat_id_str}</code>\n\n"
            f"Approve with:\n<code>/approve_channel {chat_id_str}</code>"
        )


def handle_approve_channel(chat_id, text=""):
    """Handle /approve_channel <chat_id> — admin approves a subscriber channel."""
    if not _is_admin(chat_id):
        send_message(chat_id, "Only the bot admin can approve channels.")
        return

    parts = text.strip().split()
    if len(parts) < 2:
        # Show pending channels
        if not _supabase:
            send_message(chat_id, "Supabase unavailable.")
            return
        try:
            resp = _supabase.table('subscriber_channels').select('*').eq('status', 'pending').execute()
            pending = resp.data or []
            if not pending:
                send_message(chat_id, "No pending subscriber requests.")
                return
            lines = ["<b>Pending subscriber requests:</b>\n"]
            for p in pending:
                lines.append(f"- {p.get('name', '?')} (<code>{p['chat_id']}</code>)")
            lines.append(f"\nApprove with: <code>/approve_channel &lt;chat_id&gt;</code>")
            send_message(chat_id, "\n".join(lines))
        except Exception as e:
            send_message(chat_id, f"Error: {e}")
        return

    target_id = parts[1].strip()

    if not _supabase:
        send_message(chat_id, "Supabase unavailable.")
        return

    try:
        existing = _supabase.table('subscriber_channels').select('*').eq('chat_id', target_id).execute()
        if not existing.data:
            send_message(chat_id, f"No subscription request found for <code>{target_id}</code>.")
            return

        _supabase.table('subscriber_channels').update({
            'status': 'approved',
            'approved_at': datetime.now(timezone.utc).isoformat()
        }).eq('chat_id', target_id).execute()

        channel_name = existing.data[0].get('name', target_id)
        send_message(chat_id, f"Approved <b>{channel_name}</b> (<code>{target_id}</code>). They will now receive all signals.")

        # Notify the subscriber channel
        send_message(target_id, "Your subscription has been approved! You will now receive trading signals from @Big_Quiv.")

    except Exception as e:
        send_message(chat_id, f"Error approving: {e}")


def handle_remove_channel(chat_id, text=""):
    """Handle /remove_channel <chat_id> — admin removes a subscriber channel."""
    if not _is_admin(chat_id):
        send_message(chat_id, "Only the bot admin can remove channels.")
        return

    parts = text.strip().split()
    if len(parts) < 2:
        # Show approved channels
        if not _supabase:
            send_message(chat_id, "Supabase unavailable.")
            return
        try:
            resp = _supabase.table('subscriber_channels').select('*').eq('status', 'approved').execute()
            approved = resp.data or []
            if not approved:
                send_message(chat_id, "No active subscriber channels.")
                return
            lines = ["<b>Active subscriber channels:</b>\n"]
            for a in approved:
                lines.append(f"- {a.get('name', '?')} (<code>{a['chat_id']}</code>)")
            lines.append(f"\nRemove with: <code>/remove_channel &lt;chat_id&gt;</code>")
            send_message(chat_id, "\n".join(lines))
        except Exception as e:
            send_message(chat_id, f"Error: {e}")
        return

    target_id = parts[1].strip()

    if not _supabase:
        send_message(chat_id, "Supabase unavailable.")
        return

    try:
        _supabase.table('subscriber_channels').update({
            'status': 'removed'
        }).eq('chat_id', target_id).execute()

        send_message(chat_id, f"Removed <code>{target_id}</code> from subscriber list. They will no longer receive signals.")
    except Exception as e:
        send_message(chat_id, f"Error removing: {e}")


def handle_subscribers(chat_id):
    """Handle /subscribers — list all subscriber channels and their status."""
    if not _is_admin(chat_id):
        send_message(chat_id, "Only the bot admin can view subscribers.")
        return

    if not _supabase:
        send_message(chat_id, "Supabase unavailable.")
        return

    try:
        resp = _supabase.table('subscriber_channels').select('*').order('added_at').execute()
        rows = resp.data or []
        if not rows:
            send_message(chat_id, "No subscriber channels registered.")
            return

        lines = ["<b>Subscriber Channels:</b>\n"]
        for r in rows:
            status = r.get('status', '?').upper()
            name = r.get('name', '?')
            cid = r.get('chat_id', '?')
            lines.append(f"- {name} (<code>{cid}</code>) — <b>{status}</b>")

        send_message(chat_id, "\n".join(lines))
    except Exception as e:
        send_message(chat_id, f"Error: {e}")


COMMAND_HANDLERS = {
    "/start": handle_start,
    "/chatid": handle_chatid,
    "/scan": handle_scan,
    "/top": handle_top,
    "/status": handle_status,
    "/performance": handle_performance,
    "/resolve": handle_resolve,
    "/ta": handle_ta,
    "/setcap": handle_setcap,
    "/scan_all": handle_scan_all,
    "/scan_pair": handle_scan_pair,
    "/scan_custom": handle_scan_custom,
    "/test_signals": handle_test_signals,
    "/send_signals": handle_send_signals,
    "/send_signals_direct": handle_send_signals_direct,
    "/forex_scan": handle_forex_scan,
    "/forex_pair": handle_forex_pair,
    "/forex_custom": handle_forex_custom,
    "/subscribe": handle_subscribe,
    "/approve_channel": handle_approve_channel,
    "/remove_channel": handle_remove_channel,
    "/subscribers": handle_subscribers,
    "/help": handle_start,
}

# Commands that need the full text (for argument parsing)
_COMMANDS_WITH_ARGS = {"/setcap", "/scan_pair", "/scan_custom", "/forex_pair", "/forex_custom",
                       "/approve_channel", "/remove_channel"}


def _unified_cron_cycle():
    """Run the unified auto-scanner, falling back to polymarket-only."""
    try:
        from unified_auto_scanner import run_auto_scan
        run_auto_scan()
    except ImportError:
        from polymarket_cron import run_full_cycle
        run_full_cycle()


def _cron_loop():
    """Background thread: runs unified auto-scanner every N hours."""
    scan_interval = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))

    # Brief wait to let bot stabilize before first scan
    time.sleep(5)
    print("[CRON] Running initial unified scan...")
    try:
        _unified_cron_cycle()
    except Exception as e:
        print(f"[CRON] Initial scan error: {e}")

    # Single schedule: unified scanner every N hours (crypto + forex + polymarket)
    schedule.every(scan_interval).hours.do(_unified_cron_cycle)
    print(f"[CRON] Unified auto-scan scheduled every {scan_interval} hours.")

    # Signal monitor: check TP/SL hits every 30 minutes
    schedule.every(30).minutes.do(_signal_monitor_cycle)
    print("[CRON] Signal monitor scheduled every 30 minutes.")

    # Run initial monitor check after first scan
    try:
        _signal_monitor_cycle()
    except Exception as e:
        print(f"[CRON] Initial monitor check error: {e}")

    while True:
        schedule.run_pending()
        time.sleep(30)


def run_bot():
    """Run the bot in polling mode, or cron-only mode if BOT_MODE=cron.

    BOT_MODE env var controls behaviour:
      - "full" (default): polling for commands + embedded cron scheduler
      - "cron": only the auto-scanner cron loop, NO getUpdates polling.
        Use this on a second Railway service so it can auto-scan without
        fighting the primary instance for Telegram updates.
    """
    bot_mode = os.getenv("BOT_MODE", "full").lower().strip()
    print(f"Starting Polymarket Signal Bot (mode={bot_mode})...")

    # --- Cron-only mode: just run the scanner loop, no Telegram polling ---
    if bot_mode == "cron":
        if schedule is None:
            print("FATAL: 'schedule' package not installed — cannot run cron mode.")
            return
        print("Cron-only mode — no command polling. Running auto-scanner loop.")
        _cron_loop()          # blocks forever (runs scheduled jobs)
        return                # unreachable, but explicit

    # --- Full mode: polling + cron ---

    # Clear any stale webhook so polling works cleanly (prevents duplicate
    # delivery if a webhook was ever set, e.g. during testing)
    _telegram_request("post", "deleteWebhook", json={"drop_pending_updates": False})

    print("Registering commands with Telegram...")
    register_bot_commands()

    # Start embedded cron scheduler if enabled
    enable_cron = os.getenv("ENABLE_CRON", "true").lower() in ("true", "1", "yes")
    if enable_cron and schedule is not None:
        cron_thread = threading.Thread(target=_cron_loop, daemon=True)
        cron_thread.start()
        scan_interval = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))
        print(f"Embedded cron scheduler started (unified scan every {scan_interval}h).")
    elif enable_cron and schedule is None:
        print("WARNING: 'schedule' package not installed — cron disabled.")
    else:
        print("Cron scheduler disabled (ENABLE_CRON=false).")

    # Flush stale updates so we don't re-process commands from before this
    # startup (e.g. after Railway restart/redeploy).  offset=-1 tells Telegram
    # to return only the most recent update; we use its ID to seed our offset.
    flush = get_updates(offset=-1, timeout=0)
    if flush:
        offset = flush[-1]["update_id"] + 1
        print(f"Flushed {len(flush)} stale update(s). Starting from offset {offset}.")
    else:
        offset = None

    # Dedup set — prevents double-processing when two instances briefly overlap
    # during Railway rolling deploys.  Keeps last 200 update IDs in memory.
    _processed_ids = set()
    _DEDUP_MAX = 200

    print("Bot is running. Press Ctrl+C to stop.\n")

    while True:
        try:
            updates = get_updates(offset=offset, timeout=30)

            for update in updates:
                uid = update["update_id"]
                offset = uid + 1

                # Skip if already processed (rolling-deploy overlap guard)
                if uid in _processed_ids:
                    continue
                _processed_ids.add(uid)
                if len(_processed_ids) > _DEDUP_MAX:
                    # Trim oldest IDs (update IDs are monotonically increasing)
                    oldest = sorted(_processed_ids)[:_DEDUP_MAX // 2]
                    _processed_ids.difference_update(oldest)

                # Handle text commands
                msg = update.get("message", {})
                text = (msg.get("text") or "").strip()
                chat_id = msg.get("chat", {}).get("id")

                if chat_id and text:
                    # Extract command (handle @botname suffix)
                    cmd = text.split()[0].split("@")[0].lower()

                    if cmd in COMMAND_HANDLERS:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M')}] {cmd} from {chat_id}")
                        if cmd in _COMMANDS_WITH_ARGS:
                            COMMAND_HANDLERS[cmd](chat_id, text)
                        else:
                            COMMAND_HANDLERS[cmd](chat_id)
                    elif text.upper() in ("APPROVE", "REJECT"):
                        # Handle reply-based approval (approves both Krib + X)
                        reply_to = msg.get("reply_to_message", {})
                        reply_id = str(reply_to.get("message_id", ""))
                        pending = load_pending_signals()

                        # New format: find by msg_id
                        cb_key, entry = _find_pending_by_msg_id(reply_id)
                        if cb_key and entry:
                            signal = entry["signal"]
                            already_done = entry.get("krib_status") not in ("pending", None) and entry.get("x_status") not in ("pending", None)
                            # Backward compat: old format uses "status"
                            if "status" in entry and "krib_status" not in entry:
                                already_done = entry.get("status") != "pending"

                            if already_done:
                                send_message(chat_id, "Already processed. Skipping.")
                            elif text.upper() == "APPROVE":
                                send_message(chat_id, "Approved. Distributing to Krib + X...")
                                try:
                                    if entry.get("krib_status") == "pending":
                                        entry["krib_status"] = "approved"
                                        pending[cb_key] = entry
                                        with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                            json.dump(pending, f, indent=2, default=str)
                                        distribute_to_telegram(signal)
                                    if entry.get("x_status") == "pending":
                                        entry["x_status"] = "approved"
                                        typefully_id = publish_to_x(signal, pending_entry=entry)
                                        if typefully_id:
                                            entry["typefully_id"] = typefully_id
                                    # Backward compat
                                    if "status" in entry:
                                        entry["status"] = "approved"
                                    pending[cb_key] = entry
                                except Exception as e:
                                    print(f"  Distribution FAILED: {e}")
                                    send_message(chat_id, f"Distribution failed: {e}")
                            else:
                                entry["krib_status"] = "rejected"
                                entry["x_status"] = "rejected"
                                if "status" in entry:
                                    entry["status"] = "rejected"
                                pending[cb_key] = entry
                                send_message(chat_id, "Signal rejected.")

                            with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                json.dump(pending, f, indent=2, default=str)

                # Handle inline button callbacks (Approve/Reject buttons)
                callback = update.get("callback_query")
                if callback:
                    data = callback.get("data", "")
                    if not isinstance(data, str):  # Bug #19: validate data is string
                        data = ""
                    cb_msg_id = str(callback.get("message", {}).get("message_id", ""))
                    cb_chat_id = callback.get("message", {}).get("chat", {}).get("id")
                    pending = load_pending_signals()

                    # --- New-format callbacks: appkrib_, rejkrib_, apppub_, rejpub_, appx_, rejx_ ---
                    if data.startswith("appkrib_") or data.startswith("rejkrib_"):
                        cb_hash = data.split("_", 1)[1]
                        entry = pending.get(cb_hash)
                        if entry:
                            signal = entry["signal"]
                            label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                            if data.startswith("appkrib_"):
                                if entry.get("krib_status") != "pending":
                                    send_message(cb_chat_id, f"Krib already {entry.get('krib_status')}. Skipping.")
                                else:
                                    entry["krib_status"] = "approved"
                                    # Send ONLY to Krib + log to tracker
                                    is_trading = signal.get('signal_type') == 'trading'
                                    if is_trading:
                                        card = format_trading_signal_card(signal, for_telegram=True)
                                    else:
                                        card = format_signal_card(signal, for_telegram=True)
                                    krib_ok = False
                                    if KRIB_CHAT_ID:
                                        r = send_message(KRIB_CHAT_ID, card)
                                        krib_ok = r and r.get("ok")
                                    # Log to tracker (once, on first approval)
                                    if not entry.get("tracked"):
                                        try:
                                            if is_trading:
                                                log_trading_to_tracker(signal)
                                            else:
                                                log_to_tracker(signal)
                                            entry["tracked"] = True
                                        except Exception as e:
                                            print(f"  Tracker log error: {e}")
                                    # Save draft (once)
                                    if not entry.get("draft_saved"):
                                        try:
                                            if is_trading:
                                                create_trading_twitter_draft(signal)
                                            else:
                                                create_twitter_draft(signal)
                                            entry["draft_saved"] = True
                                        except Exception as e:
                                            print(f"  Draft save error: {e}")
                                    status = "Sent to Krib" if krib_ok else "Krib send failed"
                                    send_message(cb_chat_id, f"{status}: {label}")
                                    pending[cb_hash] = entry
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                            else:  # rejkrib_
                                entry["krib_status"] = "rejected"
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                send_message(cb_chat_id, "Krib signal rejected.")
                        else:
                            send_message(cb_chat_id, "Signal not found in pending list.")

                    elif data.startswith("apppub_") or data.startswith("rejpub_"):
                        cb_hash = data.split("_", 1)[1]
                        entry = pending.get(cb_hash)
                        if entry:
                            signal = entry["signal"]
                            label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                            if data.startswith("apppub_"):
                                if entry.get("pub_status") not in (None, "pending"):
                                    send_message(cb_chat_id, f"Public already {entry.get('pub_status')}. Skipping.")
                                else:
                                    entry["pub_status"] = "approved"
                                    is_trading = signal.get('signal_type') == 'trading'
                                    if is_trading:
                                        card = format_trading_signal_card(signal, for_telegram=True)
                                    else:
                                        card = format_signal_card(signal, for_telegram=True)
                                    sent_to = []
                                    if POLY_CHANNEL_ID:
                                        r = send_message(POLY_CHANNEL_ID, card)
                                        if r and r.get("ok"):
                                            sent_to.append("Alpha Plays")
                                    sub_count = _send_to_subscribers(card)
                                    if sub_count:
                                        sent_to.append(f"{sub_count} subscribers")
                                    status = f"Sent to: {', '.join(sent_to)}" if sent_to else "No public channels configured"
                                    send_message(cb_chat_id, f"{status}: {label}")
                                    pending[cb_hash] = entry
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                            else:  # rejpub_
                                entry["pub_status"] = "skipped"
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                send_message(cb_chat_id, f"Public channels skipped: {label}")
                        else:
                            send_message(cb_chat_id, "Signal not found in pending list.")

                    elif data.startswith("appx_") or data.startswith("rejx_"):
                        cb_hash = data.split("_", 1)[1]
                        entry = pending.get(cb_hash)
                        if entry:
                            signal = entry["signal"]
                            if data.startswith("appx_"):
                                if entry.get("x_status") != "pending":
                                    send_message(cb_chat_id, f"X already {entry.get('x_status')}. Skipping.")
                                elif entry.get("typefully_id"):
                                    send_message(cb_chat_id, f"Already posted to X (id: {entry['typefully_id']}). Skipping.")
                                else:
                                    entry["x_status"] = "approved"
                                    pending[cb_hash] = entry
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                                    typefully_id = publish_to_x(signal, pending_entry=entry)
                                    if typefully_id:
                                        entry["typefully_id"] = typefully_id
                                        send_message(cb_chat_id, f"Posted to X via Typefully (id: {typefully_id})")
                                    else:
                                        send_message(cb_chat_id, "Failed to post to X. Check Typefully API key.")
                                    pending[cb_hash] = entry
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                            else:  # rejx_
                                entry["x_status"] = "rejected"
                                pending[cb_hash] = entry
                                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                    json.dump(pending, f, indent=2, default=str)
                                send_message(cb_chat_id, "Skipped X/Twitter.")
                        else:
                            send_message(cb_chat_id, "Signal not found in pending list.")

                    # --- Backward compat: old approve_/reject_ and postx_ callbacks ---
                    elif data.startswith("postx_yes_") or data.startswith("postx_no_"):
                        original_id = data.split("_", 2)[-1]
                        if original_id in pending:
                            signal = pending[original_id]["signal"]
                            if data.startswith("postx_yes_"):
                                typefully_id = publish_to_x(signal, pending_entry=pending[original_id])
                                if typefully_id:
                                    pending[original_id]["typefully_id"] = typefully_id
                                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                        json.dump(pending, f, indent=2, default=str)
                                    send_message(cb_chat_id, f"Posted to X/Twitter via Typefully (id: {typefully_id})")
                                else:
                                    send_message(cb_chat_id, "Failed to post to X. Check Typefully API key.")
                            else:
                                send_message(cb_chat_id, "Skipped X/Twitter.")
                        else:
                            send_message(cb_chat_id, "Signal not found in pending list.")

                    elif cb_msg_id in pending:
                        # Old-format: keyed by message_id
                        signal_data = pending[cb_msg_id]
                        signal = signal_data["signal"]

                        if signal_data.get("status") != "pending":
                            send_message(cb_chat_id, f"Already {signal_data['status']}. Skipping.")
                        elif data.startswith("approve_"):
                            label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                            signal_data["status"] = "approved"
                            send_message(cb_chat_id, f"Approved: {label}\nDistributing to Krib + X...")
                            try:
                                distribute_signal(signal, include_x=True)
                            except Exception as e:
                                print(f"  Distribution FAILED: {e}")
                                signal_data["status"] = "failed"
                                send_message(cb_chat_id, f"Distribution failed: {e}")
                        elif data.startswith("reject_"):
                            signal_data["status"] = "rejected"
                            send_message(cb_chat_id, "Signal rejected.")

                        with open(PENDING_FILE, "w", encoding="utf-8") as f:
                            json.dump(pending, f, indent=2, default=str)

                    # Answer callback to remove loading state
                    cb_id = callback.get("id")
                    if cb_id:
                        ack = _telegram_request("post", "answerCallbackQuery",
                                               json={"callback_query_id": cb_id})
                        if ack and not ack.get("ok"):
                            print(f"[BOT] answerCallbackQuery failed: {ack.get('description', '?')}")

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(5)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Polymarket Telegram Bot — Multi-channel distribution")
    parser.add_argument("--send-signal", type=str, help="Send signal from JSON file (use '-' for stdin)")
    parser.add_argument("--test", action="store_true", help="Test bot connectivity")
    parser.add_argument("--approve", type=str, help="Manually approve signal by message_id")
    parser.add_argument("--poll", action="store_true", help="Poll for approval callbacks")
    parser.add_argument("--poll-timeout", type=int, default=60, help="Poll timeout in seconds")
    parser.add_argument("--broadcast", type=str, help="Send message to all channels")
    parser.add_argument("--direct", action="store_true", help="Skip approval, distribute directly")
    parser.add_argument("--my-chat-id", action="store_true",
                        help="Get your personal chat ID (message the bot first, then run this)")
    parser.add_argument("--run", action="store_true",
                        help="Start bot in interactive mode (listens for commands, handles approvals)")
    parser.add_argument("--setup", action="store_true",
                        help="Register bot commands with Telegram (run once)")
    parser.add_argument("--send-ta", action="store_true",
                        help="Load TA signals and send qualifying ones for approval")
    args = parser.parse_args()

    if args.run:
        run_bot()
        return

    if args.setup:
        print("Registering bot commands with Telegram...\n")
        register_bot_commands()
        return

    if args.my_chat_id:
        print("Fetching chat IDs from recent bot messages...\n")
        print("(Make sure you've sent /start or any message to the bot first)\n")
        updates = get_updates(timeout=5)
        found = []
        seen = set()
        for u in updates:
            # Check message, channel_post, and my_chat_member events
            for key in ("message", "channel_post", "my_chat_member"):
                event = u.get(key, {})
                # Bug #28: my_chat_member has chat at top level, not nested under message
                chat = event.get("chat", {})
                cid = chat.get("id")
                if cid and cid not in seen:
                    seen.add(cid)
                    ctype = chat.get("type", "unknown")
                    name = chat.get("title") or chat.get("first_name") or ""
                    found.append((cid, name, ctype))
        if found:
            for cid, name, ctype in found:
                print(f"  Chat ID: {cid}  ({name}) [{ctype}]")
            privates = [f for f in found if f[2] == "private"]
            if privates:
                print(f"\nYour admin chat ID:")
                print(f"  TELEGRAM_ADMIN_CHAT_ID={privates[0][0]}")
        else:
            print("No messages found. Send /start to the bot, then re-run immediately.")
        return

    if args.test:
        print("Testing Telegram Bot connectivity...\n")
        test_bot()
        return

    if args.send_ta:
        print("Loading trading signals from TA analysis...\n")
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=60)
        if not signals:
            print("No qualifying trading signals. Run binance_ta_runner.py first.")
            return
        print(f"Sending {len(signals)} trading signal(s) for approval...\n")
        for sig in signals:
            if args.direct:
                print(f"Direct distribution: {sig['pair']} {sig['timeframe']} {sig['direction']}")
                distribute_signal(sig, include_x=True)
            else:
                send_to_approval(sig)
        return

    if args.send_signal:
        # Load signal
        if args.send_signal == "-":
            signal = json.load(sys.stdin)
        else:
            with open(args.send_signal, "r", encoding="utf-8") as f:
                signal = json.load(f)

        # Handle list of signals
        signals = signal if isinstance(signal, list) else [signal]

        for sig in signals:
            if args.direct:
                print(f"Direct distribution: {sig.get('market_question', sig.get('pair', 'Signal'))[:50]}")
                distribute_signal(sig, include_x=True)
            else:
                send_to_approval(sig)

        return

    if args.approve:
        manual_approve(args.approve)
        return

    if args.poll:
        poll_approvals(timeout=args.poll_timeout)
        return

    if args.broadcast:
        # Send only to approval channel or admin DM — NOT to all channels
        dest = APPROVAL_CHANNEL_ID or ADMIN_CHAT_ID
        if not dest:
            print("ERROR: No TELEGRAM_APPROVAL_CHANNEL_ID or TELEGRAM_ADMIN_CHAT_ID set in .env")
            return
        dest_name = "Approval Channel" if APPROVAL_CHANNEL_ID else "Admin DM"
        print(f"Sending to {dest_name}...")
        result = send_message(dest, args.broadcast)
        status = "OK" if result and result.get("ok") else "FAIL"
        print(f"  {dest_name}: {status}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
