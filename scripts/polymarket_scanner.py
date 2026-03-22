"""
Polymarket Scanner — Core scanner + multi-factor analysis engine.

Scans Polymarket prediction markets, applies 7-factor analysis
(price momentum, volume analysis, market efficiency, smart money,
time decay, odds compression, contrarian), and generates signal cards
for markets with >= 5% edge. Includes Claude AI independent probability assessment.

Usage:
    python scripts/polymarket_scanner.py --scan              # Full scan, output signals
    python scripts/polymarket_scanner.py --market <id>       # Analyze single market
    python scripts/polymarket_scanner.py --json              # JSON output for piping
    python scripts/polymarket_scanner.py --test              # API connectivity test
    python scripts/polymarket_scanner.py --top <N>           # Show top N markets by volume
"""

import os
import sys
import json
import argparse
import time
import math
import hashlib
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

from claude_estimator import ClaudeEstimator

# Initialize Claude estimator (lazy — only fails if actually called without API key)
_claude_estimator = None

def _get_claude_estimator():
    global _claude_estimator
    if _claude_estimator is None:
        try:
            _claude_estimator = ClaudeEstimator()
        except (ValueError, ImportError) as e:
            print(f"Claude Estimator unavailable: {e}")
            return None
    return _claude_estimator

# --- Constants ---

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Cache to reduce API calls (market_id -> (timestamp, data))
_cache = {}
CACHE_TTL = 180  # 3 minutes

# Filter thresholds
MIN_VOLUME_24H = 50000       # $50K+ daily volume
MAX_RESOLUTION_DAYS = 30     # Within 30 days
MIN_ODDS = 0.10              # Exclude < 10%
MAX_ODDS = 0.90              # Exclude > 90%
MIN_EDGE = 0.05              # 5% minimum edge (manual review catches weak ones)
MIN_CONFIDENCE = 65          # Minimum confidence score
MIN_LIQUIDITY = 10000        # $10K+ liquidity

# Factor weights for 7-factor scoring
FACTOR_WEIGHTS = {
    "price_momentum": 0.30,     # Strongest, most consistent signal
    "volume_analysis": 0.15,
    "market_efficiency": 0.05,  # Rarely fires on liquid markets
    "smart_money": 0.20,        # Sharp moves are real signal
    "time_decay": 0.15,         # Consistent, was underweighted
    "odds_compression": 0.05,   # Edge case, rarely activates
    "contrarian": 0.10,         # Narrow activation band
}

MAX_SINGLE_FACTOR_SHIFT = 0.20
MAX_TOTAL_SHIFT = 0.35
CONFIDENCE_DISAGREEMENT_PENALTY = 0.15

# Category keywords for auto-classification
CATEGORY_KEYWORDS = {
    "crypto": ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "sol",
               "defi", "nft", "token", "blockchain", "altcoin", "binance",
               "coinbase", "memecoin", "stablecoin"],
    "politics": ["president", "election", "congress", "senate", "trump", "biden",
                 "democrat", "republican", "vote", "governor", "political",
                 "legislation", "supreme court", "impeach"],
    "sports": ["nba", "nfl", "mlb", "nhl", "soccer", "football", "basketball",
               "baseball", "championship", "playoff", "super bowl", "world cup",
               "match", "game", "tournament", "ufc", "boxing"],
    "science": ["climate", "space", "nasa", "spacex", "fda", "vaccine",
                "scientific", "research", "discovery", "pandemic", "ai model",
                "technology breakthrough"],
    "culture": ["oscar", "grammy", "movie", "film", "celebrity", "entertainment",
                "music", "album", "viral", "tiktok", "social media"],
}


# --- Math Helpers (pure Python, no numpy/pandas) ---

def _mean(values):
    """Return arithmetic mean of a list of numbers."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std_dev(values):
    """Return population standard deviation."""
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def _linear_regression(values):
    """Return (slope, intercept) for y=values indexed by 0..n-1."""
    n = len(values)
    if n < 2:
        return 0.0, (_mean(values) if values else 0.0)
    x_mean = (n - 1) / 2.0
    y_mean = _mean(values)
    numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    if denominator == 0:
        return 0.0, y_mean
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _ema(values, span):
    """Return exponential moving average series."""
    if not values:
        return []
    alpha = 2.0 / (span + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    return result


def _extract_prices(price_history):
    """Extract float price list from price history dicts."""
    prices = []
    for point in price_history:
        p = point.get("p") if isinstance(point, dict) else None
        if p is not None:
            prices.append(float(p))
    return prices


# --- API Client ---

def _cached_get(url, params=None, cache_key=None):
    """GET with simple in-memory cache."""
    key = cache_key or hashlib.md5(f"{url}{params}".encode()).hexdigest()
    now = time.time()
    if key in _cache and (now - _cache[key][0]) < CACHE_TTL:
        return _cache[key][1]

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        _cache[key] = (now, data)
        return data
    except requests.RequestException as e:
        print(f"API ERROR: {e}")
        return None


def fetch_active_markets(limit=100):
    """Fetch active markets sorted by 24h volume."""
    url = f"{GAMMA_API}/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": str(limit),
        "order": "volume24hr",
        "ascending": "false",
    }
    data = _cached_get(url, params, cache_key="active_markets")
    if data is None:
        return []
    # Gamma API returns a list directly
    return data if isinstance(data, list) else data.get("data", data.get("markets", []))


def fetch_price_history(token_id, interval="1d", fidelity=60):
    """Fetch price history for a market token."""
    url = f"{CLOB_API}/prices-history"
    params = {
        "market": token_id,
        "interval": interval,
        "fidelity": str(fidelity),
    }
    data = _cached_get(url, params)
    if data is None:
        return []
    # Returns {"history": [{"t": timestamp, "p": price}, ...]}
    return data.get("history", data) if isinstance(data, dict) else data


def fetch_market_detail(condition_id):
    """Fetch detailed info for a single market."""
    url = f"{GAMMA_API}/markets/{condition_id}"
    return _cached_get(url, cache_key=f"market_{condition_id}")


def test_api_connectivity():
    """Test API connectivity to Polymarket."""
    results = {}

    # Test Gamma API
    try:
        resp = requests.get(f"{GAMMA_API}/markets", params={"limit": "1"}, timeout=10)
        results["gamma_api"] = {
            "status": resp.status_code,
            "ok": resp.status_code == 200,
            "markets_available": len(resp.json()) if resp.status_code == 200 else 0,
        }
    except Exception as e:
        results["gamma_api"] = {"status": "error", "ok": False, "error": str(e)}

    # Test CLOB API
    try:
        resp = requests.get(f"{CLOB_API}/prices-history",
                          params={"market": "test", "interval": "1d", "fidelity": "60"},
                          timeout=10)
        # Even a 400/404 means the API is reachable
        results["clob_api"] = {
            "status": resp.status_code,
            "ok": resp.status_code in (200, 400, 404, 422),
            "reachable": True,
        }
    except Exception as e:
        results["clob_api"] = {"status": "error", "ok": False, "error": str(e)}

    return results


# --- Filter Engine ---

def classify_category(question):
    """Auto-classify market category from question text."""
    q_lower = question.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "other"


def apply_filters(markets):
    """Apply user-defined filters to market list."""
    filtered = []
    for m in markets:
        # Volume filter
        vol = float(m.get("volume24hr", 0) or 0)
        if vol < MIN_VOLUME_24H:
            continue

        # Resolution window filter
        end_date_str = m.get("endDate") or m.get("end_date_iso", "")
        if end_date_str:
            try:
                # Handle various date formats
                end_date_str = end_date_str.replace("Z", "+00:00")
                end_date = datetime.fromisoformat(end_date_str)
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_to_resolve = (end_date - now).days
                if days_to_resolve > MAX_RESOLUTION_DAYS or days_to_resolve < 0:
                    continue
            except (ValueError, TypeError):
                pass  # Keep markets with unparseable dates

        # Odds filter — check outcomePrices
        outcome_prices = m.get("outcomePrices", "")
        if outcome_prices:
            try:
                if isinstance(outcome_prices, str):
                    prices = json.loads(outcome_prices)
                else:
                    prices = outcome_prices
                if isinstance(prices, list) and len(prices) >= 2:
                    yes_odds = float(prices[0])
                    no_odds = float(prices[1])
                    best_odds = max(yes_odds, no_odds)
                    worst_odds = min(yes_odds, no_odds)
                    if worst_odds < MIN_ODDS or best_odds > MAX_ODDS:
                        continue
            except (json.JSONDecodeError, TypeError, IndexError):
                pass

        # Liquidity filter
        liquidity = float(m.get("liquidity", 0) or 0)
        if liquidity < MIN_LIQUIDITY:
            continue

        filtered.append(m)

    return filtered


# --- Multi-Factor Analysis Engine ---

def analyze_price_momentum(price_history):
    """
    Factor 1: Price momentum from full price history.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "slope": float,
             "acceleration": float, "volatility": float}.
    """
    prices = _extract_prices(price_history)
    neutral = {"score": 50, "direction": 0.0, "slope": 0.0,
               "acceleration": 0.0, "volatility": 0.0}
    if len(prices) < 5:
        return neutral

    # Long-term slope (full history)
    long_slope, _ = _linear_regression(prices)

    # Short-term slope (last 15 points)
    short_window = prices[-15:] if len(prices) >= 15 else prices
    short_slope, _ = _linear_regression(short_window)

    # Acceleration = difference between short and long slope
    acceleration = short_slope - long_slope

    # Volatility
    volatility = _std_dev(prices)

    # Support / resistance from recent window
    recent = prices[-20:] if len(prices) >= 20 else prices
    support = min(recent)
    resistance = max(recent)
    price_range = resistance - support if resistance > support else 0.001
    current = prices[-1]
    position_in_range = (current - support) / price_range  # 0=at support, 1=at resistance

    # Direction: continuous via tanh — positive slope = bullish
    direction = math.tanh(short_slope * 20)

    # Score: stronger slope + acceleration = higher score
    slope_score = abs(short_slope) * 500  # Normalize: 0.02 slope -> 10 pts
    accel_score = abs(acceleration) * 300
    vol_bonus = min(15, volatility * 100)  # Some volatility = opportunity

    raw_score = 50 + slope_score + accel_score + vol_bonus
    # Boost if price is near support with upward momentum (or near resistance with downward)
    if direction > 0 and position_in_range < 0.3:
        raw_score += 10  # Bouncing off support
    elif direction < 0 and position_in_range > 0.7:
        raw_score += 10  # Rejecting resistance

    score = max(0, min(100, int(raw_score)))

    return {"score": score, "direction": direction, "slope": short_slope,
            "acceleration": acceleration, "volatility": volatility}


def analyze_volume_analysis(market, price_history):
    """
    Factor 2: Volume analysis — surge ratio + volume trend proxy.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "surge_ratio": float}.
    """
    vol_24h = float(market.get("volume24hr", 0) or 0)
    total_vol = float(market.get("volume", 0) or 0)

    neutral = {"score": 30, "direction": 0.0, "surge_ratio": 0.0}

    if total_vol == 0 or vol_24h == 0:
        return neutral

    # Estimate average daily volume
    created = market.get("createdAt") or market.get("startDate", "")
    days_active = 30
    if created:
        try:
            created_str = created.replace("Z", "+00:00")
            created_dt = datetime.fromisoformat(created_str)
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            days_active = max(1, (datetime.now(timezone.utc) - created_dt).days)
        except (ValueError, TypeError):
            pass

    avg_daily = total_vol / days_active if days_active > 0 else vol_24h
    surge_ratio = vol_24h / avg_daily if avg_daily > 0 else 0.0

    # Volume trend proxy: compare volatility of first half vs second half of prices
    prices = _extract_prices(price_history)
    vol_trend = 0.0
    if len(prices) >= 10:
        mid = len(prices) // 2
        first_vol = _std_dev(prices[:mid])
        second_vol = _std_dev(prices[mid:])
        if first_vol > 0:
            vol_trend = (second_vol - first_vol) / first_vol  # positive = increasing activity

    # Price drift for direction
    price_drift = 0.0
    if len(prices) >= 5:
        slope, _ = _linear_regression(prices[-10:] if len(prices) >= 10 else prices)
        price_drift = math.tanh(slope * 20)

    # Combine drift + volume trend for direction
    direction = math.tanh(price_drift + vol_trend * 0.5)

    # Score from surge ratio
    if surge_ratio >= 3:
        score = 95
    elif surge_ratio >= 2:
        score = 75 + int((surge_ratio - 2) * 20)
    elif surge_ratio >= 1:
        score = 50 + int((surge_ratio - 1) * 25)
    else:
        score = max(10, int(surge_ratio * 50))

    # Boost if volume trend is increasing
    if vol_trend > 0.3:
        score = min(100, score + 10)

    return {"score": score, "direction": direction, "surge_ratio": round(surge_ratio, 2)}


def analyze_market_efficiency(market):
    """
    Factor 3: Market efficiency — spread, liquidity, age.
    Entirely data-driven, no keyword hacking.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "spread_inefficiency": float}.
    """
    outcome_prices = market.get("outcomePrices", "")
    try:
        if isinstance(outcome_prices, str):
            prices = json.loads(outcome_prices)
        else:
            prices = outcome_prices
        yes_odds = float(prices[0]) if prices else 0.5
        no_odds = float(prices[1]) if len(prices) > 1 else (1 - yes_odds)
    except (json.JSONDecodeError, TypeError, IndexError):
        yes_odds, no_odds = 0.5, 0.5

    # Spread inefficiency: deviation from perfect pricing (yes + no = 1.0)
    spread_inefficiency = abs(yes_odds + no_odds - 1.0)

    # Liquidity depth ratio
    liquidity = float(market.get("liquidity", 0) or 0)
    vol_24h = float(market.get("volume24hr", 0) or 0)
    liq_depth = liquidity / vol_24h if vol_24h > 0 else 10.0  # High ratio = deep/stable

    # Age: young markets more likely mispriced
    created = market.get("createdAt") or market.get("startDate", "")
    days_active = 30
    if created:
        try:
            created_str = created.replace("Z", "+00:00")
            created_dt = datetime.fromisoformat(created_str)
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            days_active = max(1, (datetime.now(timezone.utc) - created_dt).days)
        except (ValueError, TypeError):
            pass

    # Score: higher = more likely mispriced
    score = 40
    # Spread inefficiency bonus (> 2% spread = significant)
    score += min(20, int(spread_inefficiency * 500))
    # Thin liquidity bonus
    if liq_depth < 0.5:
        score += 20  # Very thin — likely mispriced
    elif liq_depth < 1.0:
        score += 10
    # Young market bonus
    if days_active < 7:
        score += 15
    elif days_active < 14:
        score += 8

    score = max(0, min(100, score))

    # Direction: lean toward the underpriced side
    # If yes is cheap relative to a fair 50/50, direction is positive
    direction = math.tanh((0.5 - yes_odds) * 2) if spread_inefficiency > 0.01 else 0.0

    return {"score": score, "direction": direction,
            "spread_inefficiency": round(spread_inefficiency, 4)}


def analyze_smart_money(market, price_history):
    """
    Factor 4: Smart money detection — sharp moves + divergences.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "sharp_moves": int}.
    """
    prices = _extract_prices(price_history)
    neutral = {"score": 40, "direction": 0.0, "sharp_moves": 0}

    if len(prices) < 10:
        return neutral

    # Calculate period-over-period changes
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    change_std = _std_dev(changes)

    if change_std == 0:
        return neutral

    # Sharp move detection: single-period changes > 2 sigma
    sharp_moves = []
    for i, c in enumerate(changes):
        if abs(c) > 2 * change_std:
            sharp_moves.append((i, c))

    # Direction from most recent sharp move
    direction = 0.0
    if sharp_moves:
        last_sharp = sharp_moves[-1][1]
        direction = math.tanh(last_sharp / change_std)

    # Price/volume divergence: slope up + volatility down = bearish divergence
    slope, _ = _linear_regression(prices)
    recent_vol = _std_dev(prices[-15:] if len(prices) >= 15 else prices)
    overall_vol = _std_dev(prices)

    divergence = 0.0
    if overall_vol > 0:
        vol_ratio = recent_vol / overall_vol
        if slope > 0 and vol_ratio < 0.7:
            divergence = -0.5  # Bearish divergence: price up, volatility dropping
        elif slope < 0 and vol_ratio < 0.7:
            divergence = 0.5   # Bullish divergence: price down, volatility dropping

    # Blend sharp move direction with divergence
    if divergence != 0:
        direction = math.tanh(direction + divergence)

    # Score: more sharp moves + divergence = higher score
    score = 40 + len(sharp_moves) * 10 + int(abs(divergence) * 30)
    score = max(0, min(100, score))

    return {"score": score, "direction": direction, "sharp_moves": len(sharp_moves)}


def analyze_time_decay(market):
    """
    Factor 5: Time decay — phase-based scoring.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "days_left": int, "phase": str}.
    """
    end_date_str = market.get("endDate") or market.get("end_date_iso", "")
    days_left = 15  # Default if no end date
    if end_date_str:
        try:
            end_date_str_clean = end_date_str.replace("Z", "+00:00")
            end_date = datetime.fromisoformat(end_date_str_clean)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            days_left = max(0, (end_date - datetime.now(timezone.utc)).days)
        except (ValueError, TypeError):
            pass

    # Phase classification
    if days_left > 21:
        phase = "early"
        phase_intensity = 0.3
    elif days_left > 7:
        phase = "mid"
        phase_intensity = 0.5
    elif days_left > 2:
        phase = "late"
        phase_intensity = 0.8
    else:
        phase = "terminal"
        phase_intensity = 1.0

    # Exponential decay factor
    decay = math.exp(-days_left / 10.0)

    # Direction: trust market lean, scaled by phase intensity
    outcome_prices = market.get("outcomePrices", "")
    try:
        if isinstance(outcome_prices, str):
            prices = json.loads(outcome_prices)
        else:
            prices = outcome_prices
        yes_odds = float(prices[0]) if prices else 0.5
    except (json.JSONDecodeError, TypeError, IndexError):
        yes_odds = 0.5

    market_lean = yes_odds - 0.5  # Positive = YES lean
    direction = math.tanh(market_lean * 4) * phase_intensity

    # Score: closer to resolution + stronger lean = higher score
    score = 30 + int(decay * 40) + int(abs(market_lean) * 2 * 30)
    score = max(0, min(100, score))

    return {"score": score, "direction": direction, "days_left": days_left, "phase": phase}


def analyze_odds_compression(price_history):
    """
    Factor 6: Odds compression — consensus forming detection.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "compressing": bool}.
    """
    prices = _extract_prices(price_history)
    neutral = {"score": 40, "direction": 0.0, "compressing": False}

    if len(prices) < 20:
        return neutral

    # Check std_dev across 3 windows: early, mid, recent
    third = len(prices) // 3
    std_early = _std_dev(prices[:third])
    std_mid = _std_dev(prices[third:2 * third])
    std_recent = _std_dev(prices[2 * third:])

    # Compression: std_dev shrinking across windows
    compressing = std_early > std_mid > std_recent and std_recent < std_early * 0.7

    if not compressing:
        return neutral

    # Compression target = mean of recent prices
    recent_mean = _mean(prices[2 * third:])
    current = prices[-1]

    # Direction toward compression target
    direction = math.tanh((recent_mean - current) * 10)

    # Score: stronger compression = higher score
    compression_ratio = std_recent / std_early if std_early > 0 else 1.0
    score = 50 + int((1 - compression_ratio) * 50)
    score = max(0, min(100, score))

    return {"score": score, "direction": direction, "compressing": True}


def analyze_contrarian(market, price_history):
    """
    Factor 7: Contrarian — fires at extreme odds with thinning volume.
    Returns {"score": 0-100, "direction": -1.0 to 1.0, "extreme": bool}.
    """
    outcome_prices = market.get("outcomePrices", "")
    try:
        if isinstance(outcome_prices, str):
            prices_raw = json.loads(outcome_prices)
        else:
            prices_raw = outcome_prices
        yes_odds = float(prices_raw[0]) if prices_raw else 0.5
    except (json.JSONDecodeError, TypeError, IndexError):
        yes_odds = 0.5

    neutral = {"score": 30, "direction": 0.0, "extreme": False}

    # Check for extreme odds (>80 or <20)
    if 0.20 <= yes_odds <= 0.80:
        return neutral

    prices = _extract_prices(price_history)
    if len(prices) < 10:
        return neutral

    # Check for thinning volume (low recent volatility)
    recent_vol = _std_dev(prices[-10:])
    overall_vol = _std_dev(prices)

    vol_thinning = recent_vol < overall_vol * 0.6 if overall_vol > 0 else False

    if not vol_thinning:
        # Not enough contrarian signal without thinning
        return {"score": 35, "direction": 0.0, "extreme": True}

    # Direction opposes current lean
    if yes_odds > 0.80:
        direction = -0.6  # Push against YES
    else:
        direction = 0.6   # Push against NO

    # Score: more extreme + thinner = higher contrarian score
    extremity = abs(yes_odds - 0.5) - 0.3  # 0 at 80%, 0.2 at 100%
    score = 55 + int(extremity * 200)
    if vol_thinning:
        score += 15
    score = max(0, min(100, score))

    return {"score": score, "direction": direction, "extreme": True}


def calculate_model_probability(market, factor_results):
    """
    Bayesian-style model probability from 7-factor analysis.
    Starts from market odds as prior, each factor shifts via weighted direction.
    Returns (model_prob, confidence, agreement).
    """
    outcome_prices = market.get("outcomePrices", "")
    try:
        if isinstance(outcome_prices, str):
            prices = json.loads(outcome_prices)
        else:
            prices = outcome_prices
        yes_odds = float(prices[0]) if prices else 0.5
    except (json.JSONDecodeError, TypeError, IndexError):
        yes_odds = 0.5

    # Start from market odds as prior
    total_shift = 0.0
    directions = []

    for factor_name, weight in FACTOR_WEIGHTS.items():
        result = factor_results[factor_name]
        direction = result["direction"]
        # Strength: how far from neutral (50) the score is, normalized 0-1
        strength = abs(result["score"] - 50) / 50.0

        shift = weight * direction * strength * MAX_SINGLE_FACTOR_SHIFT
        total_shift += shift

        if abs(direction) > 0.1:
            directions.append(1 if direction > 0 else -1)

    # Factor agreement analysis
    if directions:
        positive_count = sum(1 for d in directions if d > 0)
        agreement_ratio = max(positive_count, len(directions) - positive_count) / len(directions)
    else:
        agreement_ratio = 0.5

    # Adjust shift based on agreement
    if agreement_ratio > 0.70:
        # Strong agreement — boost shift by up to 50%
        boost = 1.0 + (agreement_ratio - 0.70) * 1.67  # Max 1.5x at 100% agreement
        total_shift *= boost
    elif agreement_ratio < 0.30:
        # Strong disagreement — penalize
        total_shift *= (1.0 - CONFIDENCE_DISAGREEMENT_PENALTY)

    # Clamp total shift
    total_shift = max(-MAX_TOTAL_SHIFT, min(MAX_TOTAL_SHIFT, total_shift))

    model_prob = yes_odds + total_shift
    model_prob = max(0.05, min(0.95, model_prob))

    # Confidence: weighted average of factor scores, adjusted by agreement
    confidence = sum(
        factor_results[f]["score"] * FACTOR_WEIGHTS[f] for f in FACTOR_WEIGHTS
    )
    if agreement_ratio < 0.50:
        confidence *= (1.0 - CONFIDENCE_DISAGREEMENT_PENALTY)

    agreement_str = f"{sum(1 for d in directions if d > 0)}/{len(directions)}" if directions else "0/0"

    return model_prob, confidence, agreement_str


def analyze_market(market, price_history=None):
    """
    Run full multi-factor analysis on a single market.
    Returns signal dict if edge >= MIN_EDGE and confidence >= MIN_CONFIDENCE.
    """
    question = market.get("question", "")
    category = classify_category(question)
    condition_id = market.get("conditionId") or market.get("id", "")

    # Fetch price history if not provided
    # Use first token for price history
    tokens_str = market.get("clobTokenIds", "")
    token_id = None
    if tokens_str:
        try:
            if isinstance(tokens_str, str):
                tokens = json.loads(tokens_str)
            else:
                tokens = tokens_str
            if tokens:
                token_id = tokens[0]
        except (json.JSONDecodeError, TypeError):
            pass

    if price_history is None and token_id:
        price_history = fetch_price_history(token_id)

    # Run all 7 factors (each returns a dict with score, direction, etc.)
    ph = price_history or []
    factor_results = {
        "price_momentum": analyze_price_momentum(ph),
        "volume_analysis": analyze_volume_analysis(market, ph),
        "market_efficiency": analyze_market_efficiency(market),
        "smart_money": analyze_smart_money(market, ph),
        "time_decay": analyze_time_decay(market),
        "odds_compression": analyze_odds_compression(ph),
        "contrarian": analyze_contrarian(market, ph),
    }

    # Flat scores for backward compatibility
    factors = {name: result["score"] for name, result in factor_results.items()}

    # Calculate model probability, confidence, and agreement
    model_prob, confidence, agreement = calculate_model_probability(market, factor_results)

    # Parse current odds
    outcome_prices = market.get("outcomePrices", "")
    try:
        if isinstance(outcome_prices, str):
            prices = json.loads(outcome_prices)
        else:
            prices = outcome_prices
        yes_odds = float(prices[0]) if prices else 0.5
        no_odds = float(prices[1]) if len(prices) > 1 else (1 - yes_odds)
    except (json.JSONDecodeError, TypeError, IndexError):
        yes_odds, no_odds = 0.5, 0.5

    # Determine recommendation direction
    if model_prob > yes_odds:
        recommendation = "YES"
        edge = model_prob - yes_odds
        entry_odds = yes_odds
    else:
        recommendation = "NO"
        edge = (1 - model_prob) - no_odds
        entry_odds = no_odds

    # Build signal
    signal = {
        "market_id": condition_id,
        "market_question": question,
        "category": category,
        "current_odds": {"yes": round(yes_odds, 4), "no": round(no_odds, 4)},
        "recommendation": recommendation,
        "model_probability": round(model_prob, 4),
        "edge": round(edge, 4),
        "confidence": round(confidence, 1),
        "factors": factors,
        "factor_details": factor_results,
        "factor_agreement": agreement,
        "reasoning": generate_reasoning(factor_results, recommendation, question, edge, agreement),
        "resolution_date": market.get("endDate", "Unknown"),
        "volume_24h": float(market.get("volume24hr", 0) or 0),
        "liquidity": float(market.get("liquidity", 0) or 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "slug": market.get("slug", ""),
    }

    # --- Claude Estimator: independent AI probability check ---
    estimator = _get_claude_estimator()
    if estimator:
        claude_result = estimator.estimate(
            question=question,
            yes_odds=yes_odds,
            category=category,
            resolution_date=market.get("endDate", "Unknown"),
            model_prob=model_prob,
            model_edge=edge,
        )
        signal["claude_estimate"] = claude_result
        signal["combined_edge"] = claude_result["combined_edge"]
        signal["signal_strength"] = claude_result["signal_strength"]
        signal["claude_agrees"] = claude_result["agrees_with_model"]
    else:
        signal["claude_estimate"] = None
        signal["combined_edge"] = edge
        signal["signal_strength"] = "weak"
        signal["claude_agrees"] = None

    # Check thresholds
    signal["passes_threshold"] = (
        confidence >= MIN_CONFIDENCE and edge >= MIN_EDGE
    )

    return signal


def generate_reasoning(factor_results, recommendation, question, edge, agreement):
    """Generate conversational reasoning from 7-factor results."""
    parts = []

    # Price momentum
    pm = factor_results["price_momentum"]
    if pm["score"] > 70:
        dir_label = "bullish" if pm["direction"] > 0 else "bearish"
        parts.append(f"Price action is showing strong {dir_label} momentum right now")
    elif pm["score"] > 55:
        dir_label = "bullish" if pm["direction"] > 0 else "bearish"
        parts.append(f"There's moderate {dir_label} momentum building in the price")

    # Volume analysis
    va = factor_results["volume_analysis"]
    if va["score"] > 75:
        parts.append(f"Volume is surging at {va['surge_ratio']:.1f}x the average, which tells us new information is hitting this market")
    elif va["score"] > 50:
        parts.append(f"Volume is running above average at {va['surge_ratio']:.1f}x, adding conviction to the move")

    # Market efficiency
    me = factor_results["market_efficiency"]
    if me["score"] > 60:
        parts.append(f"We're seeing some inefficiency in the pricing here, which creates opportunity")

    # Smart money
    sm = factor_results["smart_money"]
    if sm["score"] > 60:
        parts.append(f"Smart money is active with {sm['sharp_moves']} sharp moves detected recently")

    # Time decay
    td = factor_results["time_decay"]
    if td["phase"] == "terminal":
        parts.append(f"This market resolves today, so the window to act is closing fast")
    elif td["phase"] == "late":
        parts.append(f"Only {td['days_left']} days left before resolution, time pressure is real")

    # Odds compression
    oc = factor_results["odds_compression"]
    if oc["compressing"]:
        parts.append(f"The odds are compressing, meaning the market is forming a consensus")

    # Contrarian
    ct = factor_results["contrarian"]
    if ct["extreme"]:
        dir_label = "YES" if ct["direction"] > 0 else "NO"
        parts.append(f"There's a contrarian play toward {dir_label} here since volume is thinning at extreme odds")

    # Agreement summary
    agree_dir = "bullish" if recommendation == "YES" else "bearish"
    parts.append(f"{agreement} of our factors agree on a {agree_dir} lean")

    if not parts:
        parts.append("Our multi-factor analysis is picking up a moderate edge on this one")

    parts.append(f"We're going {recommendation} with a +{edge*100:.1f}% edge over what the market is pricing")

    return ". ".join(parts) + "."


# --- Signal Formatting ---

def format_signal_card(signal, for_telegram=False):
    """Format signal as readable card."""
    yes_pct = round(signal["current_odds"]["yes"] * 100, 1)
    no_pct = round(signal["current_odds"]["no"] * 100, 1)
    model_pct = round(signal["model_probability"] * 100, 1)
    edge_pct = round(signal["edge"] * 100, 1)
    vol = signal["volume_24h"]

    if vol >= 1_000_000:
        vol_str = f"${vol/1_000_000:.1f}M"
    elif vol >= 1_000:
        vol_str = f"${vol/1_000:.0f}K"
    else:
        vol_str = f"${vol:.0f}"

    # Parse resolution date
    res_date = signal.get("resolution_date", "Unknown")
    if res_date and res_date != "Unknown":
        try:
            res_dt = datetime.fromisoformat(res_date.replace("Z", "+00:00"))
            res_date = res_dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            pass

    rec = signal["recommendation"]
    rec_odds = yes_pct if rec == "YES" else no_pct

    # Claude estimate fields
    claude_est = signal.get("claude_estimate")
    combined_edge_pct = round(signal.get("combined_edge", signal["edge"]) * 100, 1)
    signal_strength = signal.get("signal_strength", "N/A").upper()
    claude_agrees = signal.get("claude_agrees")

    if claude_est and not claude_est.get("error"):
        claude_prob_pct = round(claude_est["claude_probability"] * 100, 1)
        claude_conf = claude_est["confidence"].upper()
        agrees_str = "YES" if claude_agrees else "NO"
        claude_section = (
            f"\n*Claude AI Assessment:*\n"
            f"*Claude Probability:* {claude_prob_pct}%\n"
            f"*Claude Confidence:* {claude_conf}\n"
            f"*Agrees with Model:* {agrees_str}\n"
            f"*Combined Edge:* +{combined_edge_pct}%\n"
            f"*Signal Strength:* {signal_strength}\n"
        )
    else:
        claude_section = ""

    if for_telegram:
        # Telegram format — clean, no emojis, no hashtags
        card = (
            f"*POLYMARKET SIGNAL*\n\n"
            f"*Market:* {signal['market_question']}\n"
            f"*Category:* {signal['category'].upper()}\n"
            f"*Current Odds:* YES {yes_pct}% | NO {no_pct}%\n\n"
            f"*Recommendation:* {rec} @ {rec_odds}%\n"
            f"*Model Price:* {model_pct}%\n"
            f"*Edge:* +{edge_pct}%\n"
            f"*Confidence:* {signal['confidence']:.0f}/100\n"
            f"*Factor Agreement:* {signal.get('factor_agreement', 'N/A')}\n"
            f"{claude_section}\n"
            f"*Analysis:*\n{signal['reasoning']}\n\n"
            f"*Resolves:* {res_date}\n"
            f"*24h Volume:* {vol_str}"
        )
    else:
        # CLI format
        if claude_est and not claude_est.get("error"):
            claude_cli = (
                f"\n"
                f"  --- Claude AI Assessment ---\n"
                f"  Claude Prob:    {claude_prob_pct}%\n"
                f"  Claude Conf:    {claude_conf}\n"
                f"  Agrees w/Model: {agrees_str}\n"
                f"  Combined Edge:  +{combined_edge_pct}%\n"
                f"  Signal Strength:{signal_strength}\n"
            )
        else:
            claude_cli = ""

        card = (
            f"\n{'='*60}\n"
            f"  POLYMARKET SIGNAL\n"
            f"{'='*60}\n"
            f"  Market:         {signal['market_question']}\n"
            f"  Category:       {signal['category'].upper()}\n"
            f"  Current Odds:   YES {yes_pct}% | NO {no_pct}%\n"
            f"\n"
            f"  Recommendation: {rec} @ {rec_odds}%\n"
            f"  Model Price:    {model_pct}%\n"
            f"  Edge:           +{edge_pct}%\n"
            f"  Confidence:     {signal['confidence']:.0f}/100\n"
            f"  Agreement:      {signal.get('factor_agreement', 'N/A')}\n"
            f"{claude_cli}\n"
            f"  Analysis:\n"
            f"  {signal['reasoning']}\n"
            f"\n"
            f"  Resolves:       {res_date}\n"
            f"  24h Volume:     {vol_str}\n"
            f"{'='*60}\n"
        )

    return card


# --- Full Scan ---

def run_scan(json_output=False, top_n=None):
    """Run full scan: fetch markets, filter, analyze, return signals."""
    print("Fetching active markets from Polymarket...")
    markets = fetch_active_markets(limit=100)

    if not markets:
        print("ERROR: Could not fetch markets from Polymarket API")
        return []

    print(f"Fetched {len(markets)} markets. Applying filters...")
    filtered = apply_filters(markets)
    print(f"{len(filtered)} markets pass filters. Analyzing...")

    if top_n:
        # Just show top markets, no analysis
        for i, m in enumerate(filtered[:top_n], 1):
            vol = float(m.get("volume24hr", 0) or 0)
            question = m.get("question", "N/A")
            outcome_prices = m.get("outcomePrices", "")
            try:
                if isinstance(outcome_prices, str):
                    prices = json.loads(outcome_prices)
                else:
                    prices = outcome_prices
                yes_pct = round(float(prices[0]) * 100, 1)
            except Exception:
                yes_pct = "?"
            print(f"  {i}. [{yes_pct}%] {question} (Vol: ${vol:,.0f})")
        return []

    signals = []
    for i, market in enumerate(filtered):
        question = market.get("question", "N/A")
        sys.stdout.write(f"\r  Analyzing {i+1}/{len(filtered)}: {question[:50]}...")
        sys.stdout.flush()

        signal = analyze_market(market)
        if signal["passes_threshold"]:
            signals.append(signal)

        # Rate limiting: small delay between API calls
        time.sleep(0.3)

    print(f"\n\nScan complete. {len(signals)} signals found with edge >= {MIN_EDGE*100:.0f}%.\n")

    if json_output:
        print(json.dumps(signals, indent=2, default=str))
    else:
        if signals:
            # Sort by edge descending
            signals.sort(key=lambda s: s["edge"], reverse=True)
            for signal in signals:
                print(format_signal_card(signal))
        else:
            print("No markets currently meet the signal threshold.")
            print(f"  (Requires: confidence >= {MIN_CONFIDENCE}, edge >= {MIN_EDGE*100:.0f}%)")

    return signals


def analyze_single_market(market_id, json_output=False):
    """Analyze a single market by condition ID or slug."""
    print(f"Fetching market: {market_id}...")

    # Try as condition ID first
    market = fetch_market_detail(market_id)

    if not market:
        # Try searching by slug in active markets
        all_markets = fetch_active_markets(limit=100)
        for m in all_markets:
            if m.get("slug") == market_id or m.get("conditionId") == market_id:
                market = m
                break

    if not market:
        print(f"ERROR: Market '{market_id}' not found")
        return None

    signal = analyze_market(market)

    if json_output:
        print(json.dumps(signal, indent=2, default=str))
    else:
        print(format_signal_card(signal))
        if not signal["passes_threshold"]:
            print(f"  NOTE: Does not meet signal threshold "
                  f"(confidence: {signal['confidence']:.0f}, edge: {signal['edge']*100:.1f}%)")

    return signal


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Polymarket Scanner — Multi-factor prediction market analysis")
    parser.add_argument("--scan", action="store_true", help="Run full scan of active markets")
    parser.add_argument("--market", type=str, help="Analyze a single market by ID or slug")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test", action="store_true", help="Test API connectivity")
    parser.add_argument("--top", type=int, help="Show top N markets by volume")
    args = parser.parse_args()

    if args.test:
        print("Testing Polymarket API connectivity...\n")
        results = test_api_connectivity()
        for api, result in results.items():
            status = "OK" if result.get("ok") else "FAIL"
            print(f"  {api}: {status} (HTTP {result.get('status', '?')})")
            if result.get("error"):
                print(f"    Error: {result['error']}")
            if result.get("markets_available"):
                print(f"    Markets available: {result['markets_available']}")
        print()
        return

    if args.market:
        analyze_single_market(args.market, json_output=args.json)
        return

    if args.scan or args.top:
        run_scan(json_output=args.json, top_n=args.top)
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
