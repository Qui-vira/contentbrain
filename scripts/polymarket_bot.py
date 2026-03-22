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

# Pending approvals file
VAULT_DIR = os.path.join(os.path.dirname(__file__), "..")
PENDING_FILE = os.path.join(VAULT_DIR, "07-Analytics", "signal-performance", "pending-poly-signals.json")

# Drafts directory for ghostwriter integration
DRAFTS_DIR = os.path.join(VAULT_DIR, "06-Drafts", "polymarket")


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

    # 2. Send to relevant channel
    if not is_trading and POLY_CHANNEL_ID:
        result = send_message(POLY_CHANNEL_ID, card)
        results["poly"] = "OK" if result and result.get("ok") else "FAIL"
        print(f"  Poly Channel: {results['poly']}")

    # 3. Queue draft for X/Twitter
    if is_trading:
        draft = create_trading_twitter_draft(signal)
    else:
        draft = create_twitter_draft(signal)
    if draft:
        results["twitter_draft"] = "QUEUED"
        print(f"  X/Twitter Draft: QUEUED at {draft}")

    # 4. Log to tracker
    if is_trading:
        log_trading_to_tracker(signal)
    else:
        log_to_tracker(signal)
    results["tracker"] = "LOGGED"
    print(f"  Signal Tracker: LOGGED")

    return results


def create_twitter_draft(signal):
    """Create a tweet draft from signal for ghostwriter pickup."""
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

    return filepath


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
    row = (
        f"| {next_num} | {now} | {signal['market_question'][:40]} | "
        f"{signal['recommendation']} | {yes_pct}%/{no_pct}% | "
        f"{model_pct}% | +{edge_pct}% | {signal['confidence']:.0f} | "
        f"ACTIVE | — | — |\n"
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
    """Create a tweet draft from a trading signal for ghostwriter pickup."""
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

    return filepath


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
    row = (
        f"| {next_num} | {now} | {signal.get('pair', '')} | {signal.get('timeframe', '')} | "
        f"{signal.get('direction', '')} | {signal.get('entry', '')} | {signal.get('stop_loss', '')} | "
        f"{signal.get('tp1', '')} | {signal.get('tp2', '')} | {signal.get('tp3', '')} | "
        f"{signal.get('strength_score', '')}/10 | {signal.get('confluence_count', '')} | ACTIVE | — |\n"
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
    {"command": "top", "description": "Show top 10 markets by volume"},
    {"command": "status", "description": "Show active signals"},
    {"command": "performance", "description": "Win rate and metrics"},
    {"command": "resolve", "description": "Auto-resolve closed markets"},
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
        "/scan — Scan markets for new signals\n"
        "/ta — Crypto trading signals\n"
        "/top — Top 10 markets by volume\n"
        "/status — Your active signals\n"
        "/performance — Win rate & metrics\n"
        "/resolve — Check if markets resolved\n"
        "/help — Show this menu\n\n"
        "When I find a signal, I'll send it here with "
        "Approve/Reject buttons. Tap to decide.\n\n"
        "_Powered by Quivira_"
    )
    reply_markup = {
        "keyboard": [
            [{"text": "/scan"}, {"text": "/top"}],
            [{"text": "/status"}, {"text": "/performance"}],
            [{"text": "/resolve"}, {"text": "/help"}],
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


COMMAND_HANDLERS = {
    "/start": handle_start,
    "/scan": handle_scan,
    "/top": handle_top,
    "/status": handle_status,
    "/performance": handle_performance,
    "/resolve": handle_resolve,
    "/ta": handle_ta,
    "/help": handle_start,
}


def _cron_loop():
    """Background thread: runs polymarket_cron.run_full_cycle() on a schedule."""
    from polymarket_cron import run_full_cycle

    # Initial scan 30s after startup
    time.sleep(30)
    print("[CRON] Running initial scan...")
    try:
        run_full_cycle()
    except Exception as e:
        print(f"[CRON] Initial scan error: {e}")

    # Schedule hourly scans
    schedule.every(1).hours.do(lambda: run_full_cycle())
    print("[CRON] Hourly scan scheduler started.")

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
        print("Embedded cron scheduler started (hourly scans).")
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
