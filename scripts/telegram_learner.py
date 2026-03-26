"""
Telegram Learner — Passive learning agent that watches Telegram channels.

Analyzes chart images (via Claude Vision) and signal text dropped in monitored
groups. Extracts structured pattern cards, stores in Supabase, and periodically
aggregates learnings into signal_weights for gate adjustment.

Requires ANTHROPIC_API_KEY in environment.
"""

import os
import sys
import json
import re
import base64
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

import requests

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from supabase import create_client as _supabase_create_client
    _SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    _SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    _supabase = _supabase_create_client(_SUPABASE_URL, _SUPABASE_KEY) if _SUPABASE_URL and _SUPABASE_KEY else None
except ImportError:
    _supabase = None

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Pairs the bot knows about — used for text signal detection
KNOWN_PAIRS = {
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT',
    'ADAUSDT', 'LINKUSDT', 'AVAXUSDT', 'SUIUSDT', 'ARBUSDT', 'NEARUSDT',
    'OPUSDT', 'BTC', 'ETH', 'SOL',
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'XAU/USD', 'AUD/USD',
    'USD/CAD', 'EUR/JPY', 'EURUSD', 'GBPUSD', 'USDJPY', 'GBPJPY',
    'XAUUSD', 'AUDUSD', 'USDCAD', 'EURJPY',
}

# Signal-like keywords for text detection
SIGNAL_KEYWORDS = re.compile(
    r'\b(long|short|buy|sell|entry|sl|tp|stop.?loss|take.?profit|target|signal)\b',
    re.IGNORECASE
)

# Outcome keywords
OUTCOME_KEYWORDS = re.compile(
    r'\b(hit\s*tp[123]?|stopped?\s*out|sl\s*hit|take\s*profit\s*hit|tp[123]\s*hit|win|loss|closed|banked)\b',
    re.IGNORECASE
)

MODEL_ID = "claude-sonnet-4-20250514"

WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), '..', '07-Analytics',
                            'signal-performance', 'signal_weights.json')


# --- Claude API Client ---

def _get_client():
    """Get or create Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or Anthropic is None:
        return None
    return Anthropic(api_key=api_key)


# --- Chart Image Analysis ---

CHART_ANALYSIS_PROMPT = """You are an expert ICT/Smart Money trader analyzing a chart screenshot.

If this image is NOT a trading chart (it's a meme, screenshot of text, photo, etc.), respond with exactly:
{"is_chart": false}

If it IS a trading chart, extract the following into JSON:

{
  "is_chart": true,
  "pair": "BTCUSDT or EUR/USD etc — best guess from chart",
  "timeframe": "1m/5m/15m/1h/4h/1d — best guess from candle spacing",
  "direction": "LONG or SHORT — what setup is shown",
  "setup_type": "order_block_bounce / sweep_reversal / fvg_fill / breakout_retest / double_bottom / channel_break / other",
  "entry_price": null or float,
  "stop_loss": null or float,
  "take_profit": null or float,
  "key_levels": [{"type": "support/resistance/ob/fvg", "price": float}],
  "rsi_zone": "oversold/neutral/overbought or null if not visible",
  "displacement_present": true/false,
  "observations": "1-2 sentence summary of what you see — structure, liquidity, key pattern",
  "confluence_factors": ["list", "of", "visible", "confluences"],
  "outcome": "WIN/LOSS/PENDING — if markup shows result, otherwise PENDING"
}

Be precise. Only include what you can actually see on the chart. Return ONLY valid JSON, no markdown."""


def analyze_chart_image(image_url=None, image_base64=None, image_media_type="image/jpeg"):
    """Send a chart image to Claude Vision for analysis. Returns pattern card dict or None."""
    client = _get_client()
    if not client:
        print("  [LEARNER] No Anthropic client available")
        return None

    # Build image content block
    if image_base64:
        image_content = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_media_type,
                "data": image_base64,
            }
        }
    elif image_url:
        image_content = {
            "type": "image",
            "source": {
                "type": "url",
                "url": image_url,
            }
        }
    else:
        return None

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    image_content,
                    {"type": "text", "text": CHART_ANALYSIS_PROMPT}
                ]
            }]
        )

        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

        result = json.loads(text)

        if not result.get("is_chart"):
            print("  [LEARNER] Image is not a trading chart — skipped")
            return None

        print(f"  [LEARNER] Chart analyzed: {result.get('pair')} {result.get('timeframe')} "
              f"{result.get('direction')} — {result.get('setup_type')}")
        return result

    except Exception as e:
        print(f"  [LEARNER] Chart analysis error: {e}")
        return None


# --- Signal Text Parsing ---

SIGNAL_PARSE_PROMPT = """Extract the trading signal from this message into JSON.

Message: {text}

Return ONLY valid JSON:
{{
  "pair": "BTCUSDT or EUR/USD etc",
  "direction": "LONG or SHORT",
  "timeframe": "1h/4h/1d or null",
  "entry_price": float or null,
  "stop_loss": float or null,
  "take_profit": float or null,
  "observations": "brief summary of the setup mentioned",
  "outcome": "WIN/LOSS/PENDING"
}}

If you cannot parse a valid signal, return: {{"pair": null}}"""


def parse_signal_text(text):
    """Parse a signal-like text message. Returns extracted dict or None."""
    client = _get_client()
    if not client:
        return None

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": SIGNAL_PARSE_PROMPT.format(text=text)
            }]
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result = json.loads(result_text)

        if not result.get("pair"):
            return None

        result['input_type'] = 'signal_text'
        print(f"  [LEARNER] Signal parsed: {result.get('pair')} {result.get('direction')}")
        return result

    except Exception as e:
        print(f"  [LEARNER] Signal parse error: {e}")
        return None


# --- Outcome Text Parsing ---

OUTCOME_PARSE_PROMPT = """Extract the trade outcome from this message.

Message: {text}

Return ONLY valid JSON:
{{
  "pair": "BTCUSDT or EUR/USD etc — if mentioned",
  "direction": "LONG or SHORT — if mentioned",
  "outcome": "WIN or LOSS",
  "observations": "what happened"
}}

If you cannot determine the outcome, return: {{"outcome": null}}"""


def parse_outcome_text(text):
    """Parse a trade outcome message. Returns dict or None."""
    client = _get_client()
    if not client:
        return None

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": OUTCOME_PARSE_PROMPT.format(text=text)
            }]
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        result = json.loads(result_text)

        if not result.get("outcome"):
            return None

        result['input_type'] = 'outcome_text'
        print(f"  [LEARNER] Outcome parsed: {result.get('pair')} → {result.get('outcome')}")
        return result

    except Exception as e:
        print(f"  [LEARNER] Outcome parse error: {e}")
        return None


# --- Message Classification ---

def classify_message(text):
    """Classify a text message as signal, outcome, or irrelevant."""
    if not text or len(text) < 10:
        return 'irrelevant'

    text_upper = text.upper()
    has_pair = any(p in text_upper for p in KNOWN_PAIRS)
    has_outcome_kw = bool(OUTCOME_KEYWORDS.search(text))
    has_signal_kw = bool(SIGNAL_KEYWORDS.search(text))

    # Outcome keywords are more specific — check first, wins over signal
    if has_outcome_kw:
        return 'outcome'

    # Signal keywords + pair mention
    if has_signal_kw and has_pair:
        return 'signal'

    # Pair + price pattern (e.g., "BTC 85200")
    if has_pair and re.search(r'\d{2,}\.?\d*', text):
        return 'signal'

    return 'irrelevant'


# --- Telegram Image Download ---

def download_telegram_photo(file_id):
    """Download a photo from Telegram by file_id. Returns (base64_data, media_type) or (None, None)."""
    if not BOT_TOKEN:
        return None, None

    try:
        # Get file path
        resp = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=15
        )
        data = resp.json()
        if not data.get("ok"):
            return None, None

        file_path = data["result"]["file_path"]

        # Download file
        file_resp = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}",
            timeout=30
        )
        if file_resp.status_code != 200:
            return None, None

        b64 = base64.standard_b64encode(file_resp.content).decode("utf-8")

        # Determine media type
        if file_path.endswith(".png"):
            media_type = "image/png"
        elif file_path.endswith(".webp"):
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"

        return b64, media_type

    except Exception as e:
        print(f"  [LEARNER] Photo download error: {e}")
        return None, None


# --- Supabase Storage ---

def store_learning(pattern_card, source_chat_id=None, source_chat_name=None,
                   source_message_id=None, image_file_id=None):
    """Store a learning pattern card in Supabase. Returns True on success."""
    if not _supabase:
        print("  [LEARNER] No Supabase — learning not stored")
        return False

    row = {
        'source_chat_id': str(source_chat_id) if source_chat_id else None,
        'source_chat_name': source_chat_name,
        'source_message_id': str(source_message_id) if source_message_id else None,
        'input_type': pattern_card.get('input_type', 'chart_image'),
        'pair': pattern_card.get('pair'),
        'timeframe': pattern_card.get('timeframe'),
        'direction': pattern_card.get('direction'),
        'setup_type': pattern_card.get('setup_type'),
        'entry_price': pattern_card.get('entry_price'),
        'stop_loss': pattern_card.get('stop_loss'),
        'take_profit': pattern_card.get('take_profit'),
        'outcome': pattern_card.get('outcome'),
        'rsi_zone': pattern_card.get('rsi_zone'),
        'key_levels': json.dumps(pattern_card.get('key_levels', [])),
        'observations': pattern_card.get('observations'),
        'displacement_present': pattern_card.get('displacement_present'),
        'confluence_factors': json.dumps(pattern_card.get('confluence_factors', [])),
        'raw_extraction': json.dumps(pattern_card),
        'image_file_id': image_file_id,
    }

    try:
        _supabase.table('telegram_learnings').insert(row).execute()
        print(f"  [LEARNER] Stored: {row['pair']} {row['direction']} {row['setup_type']}")
        return True
    except Exception as e:
        print(f"  [LEARNER] Store error: {e}")
        return False


def update_learning_outcome(pair, direction, outcome):
    """Update the most recent PENDING learning for a pair with its outcome."""
    if not _supabase:
        return False

    try:
        # Find most recent pending learning for this pair
        resp = (_supabase.table('telegram_learnings')
                .select('id')
                .eq('pair', pair)
                .eq('outcome', 'PENDING')
                .order('learned_at', desc=True)
                .limit(1)
                .execute())

        if resp.data:
            learning_id = resp.data[0]['id']
            _supabase.table('telegram_learnings').update({
                'outcome': outcome,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', learning_id).execute()
            print(f"  [LEARNER] Updated {pair} outcome → {outcome}")
            return True
        else:
            # If direction provided, try matching with direction
            if direction:
                resp = (_supabase.table('telegram_learnings')
                        .select('id')
                        .eq('pair', pair)
                        .eq('direction', direction)
                        .eq('outcome', 'PENDING')
                        .order('learned_at', desc=True)
                        .limit(1)
                        .execute())
                if resp.data:
                    _supabase.table('telegram_learnings').update({
                        'outcome': outcome,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', resp.data[0]['id']).execute()
                    return True
        return False
    except Exception as e:
        print(f"  [LEARNER] Outcome update error: {e}")
        return False


# --- Learning Aggregation ---

def aggregate_learnings():
    """Analyze all closed learnings, compute win rates by feature, update signal_weights."""
    if not _supabase:
        return None

    try:
        # Fetch all learnings with outcomes
        resp = (_supabase.table('telegram_learnings')
                .select('*')
                .in_('outcome', ['WIN', 'LOSS'])
                .execute())

        rows = resp.data or []
        if len(rows) < 10:
            return {'status': 'insufficient_data', 'count': len(rows),
                    'message': f'Need 10+ closed learnings, have {len(rows)}'}

        # Compute win rates by dimension
        weights = {}

        # --- By pair ---
        pair_stats = {}
        for r in rows:
            p = r.get('pair') or 'UNKNOWN'
            if p not in pair_stats:
                pair_stats[p] = {'wins': 0, 'losses': 0}
            if r['outcome'] == 'WIN':
                pair_stats[p]['wins'] += 1
            else:
                pair_stats[p]['losses'] += 1

        pair_bias = {}
        for p, s in pair_stats.items():
            total = s['wins'] + s['losses']
            if total >= 3:  # Need min sample
                wr = s['wins'] / total
                pair_bias[p] = round(wr, 3)
        weights['pair_win_rates'] = pair_bias

        # --- By setup type ---
        setup_stats = {}
        for r in rows:
            st = r.get('setup_type') or 'unknown'
            if st not in setup_stats:
                setup_stats[st] = {'wins': 0, 'losses': 0}
            if r['outcome'] == 'WIN':
                setup_stats[st]['wins'] += 1
            else:
                setup_stats[st]['losses'] += 1

        setup_win_rates = {}
        for st, s in setup_stats.items():
            total = s['wins'] + s['losses']
            if total >= 3:
                wr = s['wins'] / total
                setup_win_rates[st] = round(wr, 3)
        weights['setup_win_rates'] = setup_win_rates

        # --- By timeframe ---
        tf_stats = {}
        for r in rows:
            tf = r.get('timeframe') or 'unknown'
            if tf not in tf_stats:
                tf_stats[tf] = {'wins': 0, 'losses': 0}
            if r['outcome'] == 'WIN':
                tf_stats[tf]['wins'] += 1
            else:
                tf_stats[tf]['losses'] += 1

        tf_win_rates = {}
        for tf, s in tf_stats.items():
            total = s['wins'] + s['losses']
            if total >= 3:
                wr = s['wins'] / total
                tf_win_rates[tf] = round(wr, 3)
        weights['timeframe_win_rates'] = tf_win_rates

        # --- By direction ---
        dir_stats = {'LONG': {'wins': 0, 'losses': 0}, 'SHORT': {'wins': 0, 'losses': 0}}
        for r in rows:
            d = r.get('direction')
            if d in dir_stats:
                if r['outcome'] == 'WIN':
                    dir_stats[d]['wins'] += 1
                else:
                    dir_stats[d]['losses'] += 1

        dir_win_rates = {}
        for d, s in dir_stats.items():
            total = s['wins'] + s['losses']
            if total >= 3:
                dir_win_rates[d] = round(s['wins'] / total, 3)
        weights['direction_win_rates'] = dir_win_rates

        # --- Best/worst confluence factors ---
        factor_stats = {}
        for r in rows:
            factors = r.get('confluence_factors')
            if isinstance(factors, str):
                try:
                    factors = json.loads(factors)
                except (json.JSONDecodeError, TypeError):
                    factors = []
            if not factors:
                continue
            for f in factors:
                if f not in factor_stats:
                    factor_stats[f] = {'wins': 0, 'losses': 0}
                if r['outcome'] == 'WIN':
                    factor_stats[f]['wins'] += 1
                else:
                    factor_stats[f]['losses'] += 1

        factor_win_rates = {}
        for f, s in factor_stats.items():
            total = s['wins'] + s['losses']
            if total >= 3:
                factor_win_rates[f] = round(s['wins'] / total, 3)
        weights['factor_win_rates'] = factor_win_rates

        # --- Overall stats ---
        total_wins = sum(1 for r in rows if r['outcome'] == 'WIN')
        total_losses = sum(1 for r in rows if r['outcome'] == 'LOSS')
        weights['overall'] = {
            'total': len(rows),
            'wins': total_wins,
            'losses': total_losses,
            'win_rate': round(total_wins / len(rows), 3) if rows else 0,
        }
        weights['updated_at'] = datetime.now(timezone.utc).isoformat()

        # Save locally
        os.makedirs(os.path.dirname(WEIGHTS_FILE), exist_ok=True)
        with open(WEIGHTS_FILE, 'w') as f:
            json.dump(weights, f, indent=2)

        # Save to Supabase
        for key, value in weights.items():
            if key == 'updated_at':
                continue
            try:
                _supabase.table('signal_weights').upsert({
                    'weight_key': key,
                    'weight_value': json.dumps(value) if not isinstance(value, str) else value,
                    'sample_size': len(rows),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                }).execute()
            except Exception:
                pass

        print(f"  [LEARNER] Aggregated {len(rows)} learnings → signal_weights.json")
        return weights

    except Exception as e:
        print(f"  [LEARNER] Aggregation error: {e}")
        return None


def load_signal_weights():
    """Load learned signal weights from file. Returns dict or empty dict."""
    if os.path.exists(WEIGHTS_FILE):
        try:
            with open(WEIGHTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# --- Insights Formatting ---

def format_insights():
    """Format learnings into a readable Telegram message."""
    if not _supabase:
        return "No Supabase connection — cannot retrieve learnings."

    try:
        # Count totals
        all_resp = _supabase.table('telegram_learnings').select('id', count='exact').execute()
        total = all_resp.count or 0

        win_resp = (_supabase.table('telegram_learnings')
                    .select('id', count='exact')
                    .eq('outcome', 'WIN').execute())
        wins = win_resp.count or 0

        loss_resp = (_supabase.table('telegram_learnings')
                     .select('id', count='exact')
                     .eq('outcome', 'LOSS').execute())
        losses = loss_resp.count or 0

        pending_resp = (_supabase.table('telegram_learnings')
                        .select('id', count='exact')
                        .eq('outcome', 'PENDING').execute())
        pending = pending_resp.count or 0

        closed = wins + losses
        win_rate = round(wins / closed * 100, 1) if closed > 0 else 0

        lines = [
            "<b>🧠 Learning Insights</b>",
            "",
            f"Total learnings: <b>{total}</b>",
            f"Closed: <b>{closed}</b> ({wins}W / {losses}L)",
            f"Pending: <b>{pending}</b>",
            f"Win rate: <b>{win_rate}%</b>" if closed > 0 else "Win rate: N/A (no closed trades)",
            "",
        ]

        # Load weights if available
        weights = load_signal_weights()
        if weights and weights.get('overall', {}).get('total', 0) >= 10:
            lines.append("<b>Learned Patterns:</b>")

            # Best/worst pairs
            pair_wr = weights.get('pair_win_rates', {})
            if pair_wr:
                best = sorted(pair_wr.items(), key=lambda x: -x[1])[:3]
                worst = sorted(pair_wr.items(), key=lambda x: x[1])[:3]
                lines.append("\nBest pairs:")
                for p, wr in best:
                    lines.append(f"  {p}: {wr*100:.0f}% WR")
                lines.append("\nWorst pairs:")
                for p, wr in worst:
                    lines.append(f"  {p}: {wr*100:.0f}% WR")

            # Best setup types
            setup_wr = weights.get('setup_win_rates', {})
            if setup_wr:
                best_setups = sorted(setup_wr.items(), key=lambda x: -x[1])[:5]
                lines.append("\nBest setups:")
                for s, wr in best_setups:
                    lines.append(f"  {s}: {wr*100:.0f}% WR")

            # Direction bias
            dir_wr = weights.get('direction_win_rates', {})
            if dir_wr:
                lines.append("\nDirection:")
                for d, wr in dir_wr.items():
                    lines.append(f"  {d}: {wr*100:.0f}% WR")
        else:
            needed = max(0, 10 - (weights.get('overall', {}).get('total', 0)))
            lines.append(f"<i>Need {needed} more closed trades for pattern analysis</i>")

        return "\n".join(lines)

    except Exception as e:
        return f"Error loading insights: {e}"


# --- Main Processing Entry Point ---

def process_telegram_photo(update):
    """Process a photo from a Telegram update. Returns True if analyzed."""
    msg = update.get("message", {})
    photos = msg.get("photo", [])
    if not photos:
        return False

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    chat_name = chat.get("title") or chat.get("username") or str(chat_id)
    message_id = msg.get("message_id")
    caption = (msg.get("caption") or "").strip()

    # Use largest photo (last in array)
    file_id = photos[-1]["file_id"]

    print(f"  [LEARNER] Photo detected in {chat_name} (msg {message_id})")

    # Download image
    b64_data, media_type = download_telegram_photo(file_id)
    if not b64_data:
        print("  [LEARNER] Could not download photo")
        return False

    # Analyze with Claude Vision
    result = analyze_chart_image(image_base64=b64_data, image_media_type=media_type)
    if not result:
        return False

    # Enrich with caption if present
    if caption:
        msg_type = classify_message(caption)
        if msg_type == 'outcome' and result.get('outcome') == 'PENDING':
            outcome_data = parse_outcome_text(caption)
            if outcome_data and outcome_data.get('outcome'):
                result['outcome'] = outcome_data['outcome']
        elif msg_type == 'signal':
            signal_data = parse_signal_text(caption)
            if signal_data:
                # Merge caption data into chart analysis
                for key in ('entry_price', 'stop_loss', 'take_profit'):
                    if signal_data.get(key) and not result.get(key):
                        result[key] = signal_data[key]

    result['input_type'] = 'chart_image'

    # Store
    store_learning(result, source_chat_id=chat_id, source_chat_name=chat_name,
                   source_message_id=message_id, image_file_id=file_id)
    return True


def process_telegram_text(update):
    """Process a text message for signal/outcome content. Returns True if learned."""
    msg = update.get("message", {})
    text = (msg.get("text") or "").strip()
    if not text or len(text) < 15:
        return False

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    chat_name = chat.get("title") or chat.get("username") or str(chat_id)
    message_id = msg.get("message_id")

    msg_type = classify_message(text)

    if msg_type == 'outcome':
        result = parse_outcome_text(text)
        if result and result.get('outcome'):
            # Try to update existing pending learning
            pair = result.get('pair')
            direction = result.get('direction')
            if pair:
                updated = update_learning_outcome(pair, direction, result['outcome'])
                if updated:
                    return True
            # If no match, store as standalone outcome
            store_learning(result, source_chat_id=chat_id, source_chat_name=chat_name,
                           source_message_id=message_id)
            return True

    elif msg_type == 'signal':
        result = parse_signal_text(text)
        if result and result.get('pair'):
            store_learning(result, source_chat_id=chat_id, source_chat_name=chat_name,
                           source_message_id=message_id)
            return True

    return False
