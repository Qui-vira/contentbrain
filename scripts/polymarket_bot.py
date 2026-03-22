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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

from polymarket_scanner import format_signal_card, format_trading_signal_card

# --- HTTP Session with retry ---

def _build_session():
    """Build a requests session with retry logic."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
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
        # Fallback to curl
        try:
            cmd = ["curl", "-s", "--connect-timeout", "30", url]
            if method == "post" and "json" in kwargs:
                cmd = ["curl", "-s", "--connect-timeout", "30",
                       "-X", "POST", "-H", "Content-Type: application/json",
                       "-d", json.dumps(kwargs["json"]), url]
            elif "params" in kwargs:
                params_str = "&".join(f"{k}={v}" for k, v in kwargs["params"].items())
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


def push_to_typefully(tweet_text):
    """Push a tweet draft to Typefully. Returns draft ID or None."""
    if not TYPEFULLY_API_KEY:
        return None

    social_set_id = _get_typefully_social_set_id()
    if not social_set_id:
        print("Typefully: no social set ID available. Set TYPEFULLY_SOCIAL_SET_ID in .env or check API key.")
        return None

    payload = {
        "platforms": {
            "x": {
                "enabled": True,
                "posts": [{"text": tweet_text}],
            }
        }
    }

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
            return draft_id
        else:
            body = resp.text[:200]
            print(f"Typefully: draft creation failed (HTTP {resp.status_code}): {body}")
    except Exception as e:
        print(f"Typefully: error pushing draft: {e}")

    return None


# --- Telegram Helpers ---

def send_message(chat_id, text, parse_mode="Markdown", reply_markup=None):
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
            payload["parse_mode"] = None
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

def save_pending_signal(signal, message_id):
    """Save signal to pending approvals file."""
    pending = load_pending_signals()
    pending[str(message_id)] = {
        "signal": signal,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, default=str)


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
    """Send signal to approval channel with approve/reject buttons."""
    if signal.get('signal_type') == 'trading':
        card = format_trading_signal_card(signal, for_telegram=True)
        callback_id = f"{signal['pair']}_{signal['timeframe']}"[:20]
    else:
        card = format_signal_card(signal, for_telegram=True)
        callback_id = signal['market_id'][:20]

    # Add approval prompt
    card += "\n\n---\nReply with 'APPROVE' or 'REJECT' to this signal."

    # Inline keyboard for approval
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{callback_id}"},
                {"text": "❌ Reject", "callback_data": f"reject_{callback_id}"},
            ]
        ]
    }

    # Priority: approval channel > admin DM > Krib fallback
    approval_dest = APPROVAL_CHANNEL_ID or ADMIN_CHAT_ID or KRIB_CHAT_ID

    result = send_message(
        approval_dest,
        card,
        reply_markup=reply_markup,
    )

    if result and result.get("ok"):
        msg_id = result["result"]["message_id"]
        save_pending_signal(signal, msg_id)
        print(f"Signal sent to approval channel (message_id: {msg_id})")
        return msg_id
    else:
        print("Failed to send signal to approval channel")
        return None


def distribute_signal(signal):
    """Distribute approved signal to all channels."""
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

    # 3. Queue draft for X/Twitter + push to Typefully
    if is_trading:
        draft_path, tweet_text = create_trading_twitter_draft(signal)
    else:
        draft_path, tweet_text = create_twitter_draft(signal)
    if draft_path:
        results["twitter_draft"] = "QUEUED"
        print(f"  X/Twitter Draft: QUEUED at {draft_path}")

        # Push to Typefully as draft (no auto-publish)
        typefully_id = push_to_typefully(tweet_text)
        if typefully_id:
            results["typefully"] = "DRAFTED"
            print(f"  Typefully: DRAFTED (id: {typefully_id})")
        elif TYPEFULLY_API_KEY:
            results["typefully"] = "FAIL"
            print(f"  Typefully: FAIL")

    # 4. Log to tracker
    if is_trading:
        log_trading_to_tracker(signal)
    else:
        log_to_tracker(signal)
    results["tracker"] = "LOGGED"
    print(f"  Signal Tracker: LOGGED")

    return results


def create_twitter_draft(signal):
    """Create a tweet draft from signal for ghostwriter pickup. Returns (filepath, tweet_text)."""
    os.makedirs(DRAFTS_DIR, exist_ok=True)

    yes_pct = round(signal["current_odds"]["yes"] * 100, 1)
    no_pct = round(signal["current_odds"]["no"] * 100, 1)
    edge_pct = round(signal["edge"] * 100, 1)
    rec = signal["recommendation"]
    rec_odds = yes_pct if rec == "YES" else no_pct
    model_pct = round(signal["model_probability"] * 100, 1)

    # Generate tweet content
    tweet = (
        f"New prediction market signal 🔮\n\n"
        f"{signal['market_question']}\n\n"
        f"Market says: {rec_odds}%\n"
        f"My model says: {model_pct}%\n"
        f"Edge: +{edge_pct}%\n\n"
        f"Recommendation: {rec}\n"
        f"Confidence: {signal['confidence']:.0f}/100\n\n"
        f"Full breakdown in the Krib 👇\n\n"
        f"#polymarket #{signal['category']} #predictions"
    )

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

    sidecar_path = os.path.join(details_dir, f"{next_num}-{now}.json")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, default=str)


TRADING_DRAFTS_DIR = os.path.join(VAULT_DIR, "06-Drafts", "trading")
TRADING_LOG_PATH = os.path.join(
    VAULT_DIR, "07-Analytics", "signal-performance", "trading-signals-log.md"
)


def create_trading_twitter_draft(signal):
    """Create a tweet draft from a trading signal for ghostwriter pickup. Returns (filepath, tweet_text)."""
    os.makedirs(TRADING_DRAFTS_DIR, exist_ok=True)

    pair = signal.get('pair', 'UNKNOWN')
    direction = signal.get('direction', 'NEUTRAL')
    entry = signal.get('entry', 0)
    tp1 = signal.get('tp1', 0)
    sl = signal.get('stop_loss', 0)
    strength = signal.get('strength_score', 0)
    conf_count = signal.get('confluence_count', 0)

    tweet = (
        f"New trading signal\n\n"
        f"{pair} {direction}\n\n"
        f"Entry: {entry}\n"
        f"SL: {sl}\n"
        f"TP1: {tp1}\n\n"
        f"Strength: {strength}/10 | {conf_count} confluences\n\n"
        f"Full levels and analysis in the Krib\n\n"
        f"#crypto #trading #{pair.replace('USDT', '').lower()}"
    )

    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y-%m-%d')}-ta-{pair}-{signal.get('timeframe', '4h')}.md"
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


def log_trading_to_tracker(signal):
    """Log approved trading signal to trading-signals-log.md."""
    log_dir = os.path.dirname(TRADING_LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)

    # Create log file with header if it doesn't exist
    if not os.path.exists(TRADING_LOG_PATH):
        header = (
            "# Trading Signals Log\n\n"
            "| # | Date | Pair | TF | Direction | Entry | SL | TP1 | TP2 | TP3 | Strength | Confluences | Status | Result |\n"
            "|---|------|------|----|-----------|-------|----|-----|-----|-----|----------|-------------|--------|--------|\n"
        )
        with open(TRADING_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(header)

    # Read current log to get next signal number
    with open(TRADING_LOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    signal_count = sum(1 for line in lines if line.startswith("|") and line[1:2].strip().isdigit())
    next_num = signal_count + 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source = signal.get('source', 'manual')
    row = (
        f"| {next_num} | {now} | {signal.get('pair', '')} | {signal.get('timeframe', '')} | "
        f"{signal.get('direction', '')} | {signal.get('entry', '')} | {signal.get('stop_loss', '')} | "
        f"{signal.get('tp1', '')} | {signal.get('tp2', '')} | {signal.get('tp3', '')} | "
        f"{signal.get('strength_score', '')}/10 | {signal.get('confluence_count', '')} | {source} | ACTIVE | — |\n"
    )

    with open(TRADING_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(row)


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

            # Check for callback queries (inline button presses)
            callback = update.get("callback_query")
            if callback:
                data = callback.get("data", "")
                msg_id = str(callback.get("message", {}).get("message_id", ""))

                if msg_id in pending:
                    signal_data = pending[msg_id]
                    signal = signal_data["signal"]

                    _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                    if data.startswith("approve_"):
                        print(f"\nAPPROVED: {_label}")
                        print("Distributing to all channels...")
                        distribute_signal(signal)
                        signal_data["status"] = "approved"
                    elif data.startswith("reject_"):
                        print(f"\nREJECTED: {_label}")
                        signal_data["status"] = "rejected"

                    # Save updated status
                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                        json.dump(pending, f, indent=2, default=str)

            # Check for text replies (APPROVE/REJECT)
            msg = update.get("message", {})
            text = (msg.get("text") or "").strip().upper()
            reply_to = msg.get("reply_to_message", {})
            reply_id = str(reply_to.get("message_id", ""))

            if reply_id in pending and text in ("APPROVE", "REJECT"):
                signal_data = pending[reply_id]
                signal = signal_data["signal"]
                _label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]

                if text == "APPROVE":
                    print(f"\nAPPROVED: {_label}")
                    distribute_signal(signal)
                    signal_data["status"] = "approved"
                else:
                    print(f"\nREJECTED: {_label}")
                    signal_data["status"] = "rejected"

                with open(PENDING_FILE, "w", encoding="utf-8") as f:
                    json.dump(pending, f, indent=2, default=str)

    print("\nPolling complete.")


def manual_approve(message_id):
    """Manually approve a pending signal by message ID."""
    pending = load_pending_signals()
    msg_id = str(message_id)

    if msg_id not in pending:
        print(f"No pending signal found for message_id {msg_id}")
        print(f"Pending IDs: {list(pending.keys())}")
        return

    signal_data = pending[msg_id]
    signal = signal_data["signal"]

    print(f"Approving: {signal.get('market_question', signal.get('pair', 'Signal'))[:60]}")
    print("Distributing to all channels...")
    results = distribute_signal(signal)

    signal_data["status"] = "approved"
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
    {"command": "send_signals", "description": "Send TA signals to approval channel"},
    {"command": "send_signals_direct", "description": "Send TA signals directly (skip approval)"},
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
        "*Welcome to the Polymarket Signal Bot* \n\n"
        "I scan prediction markets every hour and find signals "
        "with +10% edge for you to approve.\n\n"
        "*Commands:*\n"
        "/scan — Scan Polymarket for signals\n"
        "/ta — Send crypto TA signals for approval\n"
        "/scan\\_all — Full crypto scan (all pairs, all TFs)\n"
        "/scan\\_pair BTCUSDT — Scan one pair\n"
        "/scan\\_custom ETHUSDT 1h,4h — Custom scan\n"
        "/send\\_signals — Send TA signals for approval\n"
        "/send\\_signals\\_direct — Send directly (skip approval)\n"
        "/top — Top 10 markets by volume\n"
        "/status — Your active signals\n"
        "/performance — Win rate & metrics\n"
        "/resolve — Check if markets resolved\n"
        "/setcap N — Set daily auto-signal cap\n"
        "/help — Show this menu\n\n"
        "When I find a signal, I'll send it here with "
        "Approve/Reject buttons. Tap to decide.\n\n"
        "_Powered by Quivira_"
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

        send_message(chat_id, f"Found *{len(signals)} signal(s)*. Sending for review...")

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

        lines = ["*Top 10 Polymarket Markets*\n"]
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
    """Handle /status — show active signals."""
    try:
        from polymarket_tracker import parse_signals_log
        signals = parse_signals_log()
        active = [s for s in signals if s["status"] == "ACTIVE"]

        if not active:
            send_message(chat_id, "No active Polymarket signals right now.")
            return

        lines = [f"*Active Signals ({len(active)})*\n"]
        for s in active:
            lines.append(
                f"#{s['num']} | {s['market'][:35]}\n"
                f"   {s['recommendation']} | Edge: {s['edge_pct']} | Conf: {s['confidence']}"
            )
        send_message(chat_id, "\n".join(lines))

    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_performance(chat_id):
    """Handle /performance — show metrics."""
    try:
        from polymarket_tracker import calculate_performance

        m = calculate_performance()
        text = (
            "*Polymarket Signal Performance*\n\n"
            f"Total Signals: {m['total_signals']}\n"
            f"Active: {m['active']}\n"
            f"Resolved: {m['resolved']}\n"
            f"Win Rate: {m['win_rate']}%\n"
            f"Record: {m['wins']}W / {m['losses']}L\n"
            f"Avg Confidence: {m['avg_confidence']}\n"
            f"Avg Edge: +{m['avg_edge']}%"
        )

        if m["categories"]:
            text += "\n\n*By Category:*"
            for cat, data in m["categories"].items():
                total = data["wins"] + data["losses"]
                wr = data["wins"] / total * 100 if total > 0 else 0
                text += f"\n  {cat.upper()}: {data['wins']}W/{data['losses']}L ({wr:.0f}%)"

        send_message(chat_id, text)

    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_resolve(chat_id):
    """Handle /resolve — auto-resolve closed markets."""
    send_message(chat_id, "Checking for resolved markets...")

    try:
        from polymarket_tracker import auto_resolve
        updates = auto_resolve()

        if not updates:
            send_message(chat_id, "No signals resolved in this check.")
        else:
            lines = [f"*{len(updates)} signal(s) resolved:*\n"]
            for u in updates:
                lines.append(f"#{u['signal']} {u['market'][:30]} — *{u['new_status']}* ({u['pnl']})")
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
                "Run `python scripts/binance_ta_runner.py` first, or data may be stale (>60 min)."
            )
            return

        send_message(chat_id, f"Found *{len(signals)} trading signal(s)*. Sending for review...")

        for signal in signals:
            send_to_approval(signal)

    except Exception as e:
        send_message(chat_id, f"TA signal error: {e}")


def handle_setcap(chat_id, text=""):
    """Handle /setcap — set daily auto-signal cap."""
    parts = text.strip().split()
    if len(parts) < 2:
        send_message(chat_id, "Usage: `/setcap 5` — sets daily auto-signal cap to 5")
        return

    try:
        new_cap = int(parts[1])
        if new_cap < 0 or new_cap > 50:
            send_message(chat_id, "Cap must be between 0 and 50.")
            return
    except ValueError:
        send_message(chat_id, "Invalid number. Usage: `/setcap 5`")
        return

    try:
        from unified_auto_scanner import update_cap, load_state
        actual_cap = update_cap(new_cap)
        state = load_state()
        send_message(
            chat_id,
            f"Daily auto-signal cap set to *{actual_cap}*.\n"
            f"Today's usage: {state['signals_sent']}/{actual_cap}"
        )
    except Exception as e:
        send_message(chat_id, f"Error setting cap: {e}")


def _run_ta_script(chat_id, args_list, label):
    """Run binance_ta_runner.py with given args via subprocess, report results."""
    script_path = os.path.join(os.path.dirname(__file__), "binance_ta_runner.py")
    if not os.path.exists(script_path):
        send_message(chat_id, f"Error: `binance_ta_runner.py` not found.")
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
            send_message(chat_id, f"[{label}] Scan failed:\n`{err}`")
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
    """Load TA signals from JSON and send qualifying ones for approval."""
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        if not signals:
            send_message(chat_id, "No qualifying signals (3+ confluences) in latest scan.")
            return 0
        send_message(chat_id, f"Found *{len(signals)}* qualifying signal(s). Sending for approval...")
        sent = 0
        for signal in signals:
            msg_id = send_to_approval(signal)
            if msg_id:
                sent += 1
        send_message(chat_id, f"Sent *{sent}* signal(s) to approval channel. Review and approve/reject.")
        return sent
    except Exception as e:
        send_message(chat_id, f"Signal load error: {e}")
        return 0


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
        send_message(chat_id, "Usage: `/scan_pair BTCUSDT`")
        return
    pair = parts[1].upper()
    send_message(chat_id, f"Scanning *{pair}* on all timeframes (1h, 4h, 1d)...")
    ok = _run_ta_script(chat_id, ["--pair", pair], f"SCAN {pair}")
    if ok:
        _send_ta_signals_to_approval(chat_id)


def handle_scan_custom(chat_id, text=""):
    """Handle /scan_custom ETHUSDT 1h,4h — scan pair on specific timeframes, then send signals."""
    parts = text.strip().split()
    if len(parts) < 3:
        send_message(chat_id, "Usage: `/scan_custom ETHUSDT 1h,4h`")
        return
    pair = parts[1].upper()
    timeframes = parts[2]
    send_message(chat_id, f"Scanning *{pair}* on *{timeframes}*...")
    ok = _run_ta_script(chat_id, ["--pair", pair, "--timeframe", timeframes], f"SCAN {pair} {timeframes}")
    if ok:
        _send_ta_signals_to_approval(chat_id)


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
            distribute_signal(signal)
            sent += 1
        send_message(chat_id, f"Distributed *{sent}* signal(s) directly to all channels.")
    except Exception as e:
        send_message(chat_id, f"Error: {e}")


def handle_chatid(chat_id):
    """Reply with the chat ID — useful for finding group/channel IDs."""
    send_message(chat_id, f"`{chat_id}`")


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
    "/send_signals": handle_send_signals,
    "/send_signals_direct": handle_send_signals_direct,
    "/help": handle_start,
}

# Commands that need the full text (for argument parsing)
_COMMANDS_WITH_ARGS = {"/setcap", "/scan_pair", "/scan_custom"}


def _unified_cron_cycle():
    """Run the unified auto-scanner, falling back to polymarket-only."""
    try:
        from unified_auto_scanner import run_auto_scan
        run_auto_scan()
    except ImportError:
        from polymarket_cron import run_full_cycle
        run_full_cycle()


def _auto_ta_scan_cycle():
    """Run full crypto TA scan and send qualifying signals to approval channel."""
    scan_interval = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))
    admin = ADMIN_CHAT_ID or APPROVAL_CHANNEL_ID
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"[AUTO-SCAN] Starting scheduled TA scan at {ts}")

    # Run the TA scanner
    script_path = os.path.join(os.path.dirname(__file__), "binance_ta_runner.py")
    if not os.path.exists(script_path):
        print("[AUTO-SCAN] binance_ta_runner.py not found — skipping.")
        return

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=300,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        if result.returncode != 0:
            # Combine stderr+stdout, grab last 600 chars for full traceback
            combined = (result.stderr or '') + (result.stdout or '')
            err = combined.strip()[-600:] if combined.strip() else "Unknown error"
            print(f"[AUTO-SCAN] Scan failed: {err}")
            if admin:
                send_message(admin, f"[AUTO-SCAN] Scan failed at {ts}:\n`{err}`")
            return
    except subprocess.TimeoutExpired:
        print("[AUTO-SCAN] Scan timed out after 5 minutes.")
        if admin:
            send_message(admin, f"[AUTO-SCAN] Scan timed out at {ts}")
        return
    except Exception as e:
        print(f"[AUTO-SCAN] Scan error: {e}")
        return

    # Load signals and send qualifying ones to approval
    try:
        from binance_ta_runner import load_ta_signals
        signals = load_ta_signals(max_age_minutes=90)
        if not signals:
            print(f"[AUTO-SCAN] No qualifying signals (3+ confluences).")
            if admin:
                send_message(admin, f"[AUTO-SCAN] Scan complete at {ts} — no qualifying signals.")
            return

        sent = 0
        for signal in signals:
            signal['source'] = 'auto'
            msg_id = send_to_approval(signal)
            if msg_id:
                sent += 1

        print(f"[AUTO-SCAN] Sent {sent}/{len(signals)} signal(s) to approval channel.")
        if admin:
            send_message(admin, f"[AUTO-SCAN] Scan complete at {ts}\n{sent} signal(s) sent for approval.")
    except Exception as e:
        print(f"[AUTO-SCAN] Signal load error: {e}")
        if admin:
            send_message(admin, f"[AUTO-SCAN] Signal load error at {ts}: {e}")


def _cron_loop():
    """Background thread: runs scheduled scans."""
    scan_interval = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))

    # Initial TA scan 30s after startup
    time.sleep(30)
    print("[CRON] Running initial TA scan...")
    try:
        _auto_ta_scan_cycle()
    except Exception as e:
        print(f"[CRON] Initial TA scan error: {e}")

    # Schedule TA scans every N hours (default 4)
    schedule.every(scan_interval).hours.do(_auto_ta_scan_cycle)
    print(f"[CRON] TA auto-scan scheduled every {scan_interval} hours.")

    # Keep existing polymarket/unified cycle running hourly
    schedule.every(1).hours.do(_unified_cron_cycle)
    print("[CRON] Hourly unified scanner started.")

    while True:
        schedule.run_pending()
        time.sleep(30)


def run_bot():
    """Run the bot in persistent polling mode — listens for commands and approvals."""
    print("Starting Polymarket Signal Bot...")
    print("Registering commands with Telegram...")
    register_bot_commands()

    # Start embedded cron scheduler if enabled
    enable_cron = os.getenv("ENABLE_CRON", "true").lower() in ("true", "1", "yes")
    if enable_cron and schedule is not None:
        cron_thread = threading.Thread(target=_cron_loop, daemon=True)
        cron_thread.start()
        scan_interval = int(os.getenv("TA_SCAN_INTERVAL_HOURS", "4"))
        print(f"Embedded cron scheduler started (TA scan every {scan_interval}h, polymarket hourly).")
    elif enable_cron and schedule is None:
        print("WARNING: 'schedule' package not installed — cron disabled.")
    else:
        print("Cron scheduler disabled (ENABLE_CRON=false).")

    print("Bot is running. Press Ctrl+C to stop.\n")

    offset = None

    while True:
        try:
            updates = get_updates(offset=offset, timeout=30)

            for update in updates:
                offset = update["update_id"] + 1

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
                        # Handle reply-based approval
                        reply_to = msg.get("reply_to_message", {})
                        reply_id = str(reply_to.get("message_id", ""))
                        pending = load_pending_signals()

                        if reply_id in pending:
                            signal_data = pending[reply_id]
                            signal = signal_data["signal"]

                            if text.upper() == "APPROVE":
                                send_message(chat_id, "Approved. Distributing to all channels...")
                                distribute_signal(signal)
                                signal_data["status"] = "approved"
                            else:
                                send_message(chat_id, "Signal rejected.")
                                signal_data["status"] = "rejected"

                            with open(PENDING_FILE, "w", encoding="utf-8") as f:
                                json.dump(pending, f, indent=2, default=str)

                # Handle inline button callbacks (Approve/Reject buttons)
                callback = update.get("callback_query")
                if callback:
                    data = callback.get("data", "")
                    cb_msg_id = str(callback.get("message", {}).get("message_id", ""))
                    cb_chat_id = callback.get("message", {}).get("chat", {}).get("id")
                    pending = load_pending_signals()

                    if cb_msg_id in pending:
                        signal_data = pending[cb_msg_id]
                        signal = signal_data["signal"]

                        if data.startswith("approve_"):
                            label = signal.get('market_question', signal.get('pair', 'Signal'))[:50]
                            send_message(cb_chat_id, f"Approved: {label}\nDistributing...")
                            distribute_signal(signal)
                            signal_data["status"] = "approved"
                        elif data.startswith("reject_"):
                            send_message(cb_chat_id, "Signal rejected.")
                            signal_data["status"] = "rejected"

                        with open(PENDING_FILE, "w", encoding="utf-8") as f:
                            json.dump(pending, f, indent=2, default=str)

                    # Answer callback to remove loading state
                    _telegram_request("post", "answerCallbackQuery",
                                     json={"callback_query_id": callback["id"]})

        except KeyboardInterrupt:
            print("\nBot stopped.")
            break
        except Exception as e:
            print(f"Error in polling loop: {e}")
            import time
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
        print("Fetching your chat ID from recent bot messages...\n")
        print("(Make sure you've sent /start or any message to the bot first)\n")
        updates = get_updates(timeout=5)
        found = set()
        for u in updates:
            msg = u.get("message", {})
            chat = msg.get("chat", {})
            if chat.get("type") == "private":
                cid = chat["id"]
                name = chat.get("first_name", "")
                found.add((cid, name))
        if found:
            for cid, name in found:
                print(f"  Chat ID: {cid}  ({name})")
            print(f"\nAdd this to your .env file:")
            cid = list(found)[0][0]
            print(f"  TELEGRAM_ADMIN_CHAT_ID={cid}")
        else:
            print("No private messages found. Send /start to your bot first, then re-run.")
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
                distribute_signal(sig)
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
                distribute_signal(sig)
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
        print("Broadcasting to all channels...")
        for name, chat_id in [("Krib", KRIB_CHAT_ID), ("Poly", POLY_CHANNEL_ID)]:
            if chat_id:
                result = send_message(chat_id, args.broadcast)
                status = "OK" if result and result.get("ok") else "FAIL"
                print(f"  {name}: {status}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
