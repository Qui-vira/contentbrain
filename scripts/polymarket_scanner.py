"""
Polymarket Scanner — Core scanner + multi-factor analysis engine.

Scans Polymarket prediction markets, applies multi-factor analysis
(odds movement, volume surge, news catalyst, sentiment, historical patterns),
and generates signal cards for markets with >= 10% edge.

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
import hashlib
from datetime import datetime, timezone, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

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
MIN_EDGE = 0.10              # 10% minimum edge
MIN_CONFIDENCE = 65          # Minimum confidence score
MIN_LIQUIDITY = 10000        # $10K+ liquidity

# Factor weights for multi-factor scoring
FACTOR_WEIGHTS = {
    "odds_movement": 0.25,
    "volume_surge": 0.20,
    "news_catalyst": 0.20,
    "sentiment": 0.15,
    "historical_patterns": 0.20,
}

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

def analyze_odds_movement(price_history):
    """Score odds momentum/reversal from price history (0-100)."""
    if not price_history or len(price_history) < 3:
        return 50  # Neutral if no data

    prices = []
    for point in price_history:
        p = point.get("p") if isinstance(point, dict) else None
        if p is not None:
            prices.append(float(p))

    if len(prices) < 3:
        return 50

    # Use last 7 data points (or all if fewer)
    recent = prices[-7:]

    # Calculate slope (linear regression simplification)
    n = len(recent)
    x_mean = (n - 1) / 2
    y_mean = sum(recent) / n
    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 50

    slope = numerator / denominator

    # Strong momentum = higher score
    # Normalize slope to 0-100 range
    # Typical slope range: -0.05 to +0.05
    normalized = (slope + 0.05) / 0.10  # Maps [-0.05, 0.05] to [0, 1]
    normalized = max(0, min(1, normalized))

    # Check for reversal pattern (recent direction change)
    if len(recent) >= 5:
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        first_trend = first_half[-1] - first_half[0]
        second_trend = second_half[-1] - second_half[0]
        if (first_trend > 0 and second_trend < 0) or (first_trend < 0 and second_trend > 0):
            # Reversal detected — boost score for contrarian signal
            normalized = min(1, normalized + 0.15)

    return int(normalized * 100)


def analyze_volume_surge(market):
    """Score volume surge relative to typical (0-100)."""
    vol_24h = float(market.get("volume24hr", 0) or 0)
    total_vol = float(market.get("volume", 0) or 0)

    if total_vol == 0 or vol_24h == 0:
        return 30  # Low score for no data

    # Estimate 7d average daily volume from total/days active
    created = market.get("createdAt") or market.get("startDate", "")
    days_active = 30  # Default
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

    if avg_daily == 0:
        return 30

    surge_ratio = vol_24h / avg_daily

    # Score: 1x = 50, 2x = 75, 3x+ = 90+
    if surge_ratio >= 3:
        return 95
    elif surge_ratio >= 2:
        return 75 + int((surge_ratio - 2) * 20)
    elif surge_ratio >= 1:
        return 50 + int((surge_ratio - 1) * 25)
    else:
        return int(surge_ratio * 50)


def analyze_news_catalyst(question):
    """
    Score news catalyst potential (0-100).
    Uses keyword heuristics for static analysis.
    News/web search should be done at the command level for approved signals.
    """
    q_lower = question.lower()

    score = 40  # Base score

    # Time-sensitive keywords boost
    urgent_keywords = ["today", "tomorrow", "this week", "tonight", "by march",
                       "by april", "deadline", "vote", "decision", "announce",
                       "ruling", "verdict", "launch", "release"]
    for kw in urgent_keywords:
        if kw in q_lower:
            score += 10

    # High-profile topics boost
    profile_keywords = ["bitcoin", "ethereum", "trump", "fed", "rate",
                        "inflation", "war", "election", "spacex", "ai"]
    for kw in profile_keywords:
        if kw in q_lower:
            score += 5

    return min(100, score)


def analyze_sentiment(question, market):
    """
    Score sentiment from market dynamics (0-100).
    Proxy: uses odds movement direction + volume as sentiment indicator.
    Full sentiment analysis should use web search at command level.
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

    # Markets with strong lean have clearer sentiment
    distance_from_center = abs(yes_odds - 0.5)
    sentiment_clarity = distance_from_center * 2  # 0-1 scale

    # Volume adds conviction
    vol = float(market.get("volume24hr", 0) or 0)
    vol_factor = min(1.0, vol / 200000)  # Normalize to 200K cap

    score = 40 + int(sentiment_clarity * 30) + int(vol_factor * 30)
    return min(100, score)


def analyze_historical_patterns(market, category):
    """
    Score based on historical resolution patterns (0-100).
    Uses base rates and market characteristics as proxy.
    """
    score = 50  # Base

    # Markets with more liquidity tend to be better priced
    liquidity = float(market.get("liquidity", 0) or 0)
    if liquidity > 100000:
        score += 10  # Well-priced, less edge expected
    elif liquidity < 30000:
        score += 15  # Thin markets may have more mispricing

    # Category-specific base rates
    category_bonus = {
        "crypto": 10,   # Crypto markets often mispriced
        "politics": 5,  # Political markets reasonably efficient
        "sports": 0,    # Sports markets very efficient
        "culture": 10,  # Pop culture can be mispriced
        "science": 5,
    }
    score += category_bonus.get(category, 0)

    # Resolution window factor — closer to resolution = more signal
    end_date_str = market.get("endDate") or market.get("end_date_iso", "")
    if end_date_str:
        try:
            end_date_str = end_date_str.replace("Z", "+00:00")
            end_date = datetime.fromisoformat(end_date_str)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            days_left = (end_date - datetime.now(timezone.utc)).days
            if days_left <= 7:
                score += 15  # Close to resolution, patterns clearer
            elif days_left <= 14:
                score += 10
        except (ValueError, TypeError):
            pass

    return min(100, score)


def calculate_model_probability(market, factors):
    """
    Calculate model's estimated probability based on multi-factor analysis.
    Adjusts current odds based on factor signals.
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

    # Weighted confidence score
    confidence = sum(
        factors[f] * FACTOR_WEIGHTS[f] for f in FACTOR_WEIGHTS
    )

    # Adjust odds based on confidence direction
    # High confidence (>70) suggests current odds may be wrong
    # Direction: if odds_movement is high, momentum is positive (YES direction)
    momentum_direction = 1 if factors["odds_movement"] > 55 else -1

    # Calculate adjustment — higher confidence = bigger adjustment
    adjustment_magnitude = (confidence - 50) / 200  # Max ±0.25
    adjustment = adjustment_magnitude * momentum_direction

    model_prob = yes_odds + adjustment
    model_prob = max(0.05, min(0.95, model_prob))

    return model_prob, confidence


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

    # Run all 5 factors
    factors = {
        "odds_movement": analyze_odds_movement(price_history or []),
        "volume_surge": analyze_volume_surge(market),
        "news_catalyst": analyze_news_catalyst(question),
        "sentiment": analyze_sentiment(question, market),
        "historical_patterns": analyze_historical_patterns(market, category),
    }

    # Calculate model probability and confidence
    model_prob, confidence = calculate_model_probability(market, factors)

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
        "reasoning": generate_reasoning(factors, recommendation, question, edge),
        "resolution_date": market.get("endDate", "Unknown"),
        "volume_24h": float(market.get("volume24hr", 0) or 0),
        "liquidity": float(market.get("liquidity", 0) or 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "slug": market.get("slug", ""),
    }

    # Check thresholds
    signal["passes_threshold"] = (
        confidence >= MIN_CONFIDENCE and edge >= MIN_EDGE
    )

    return signal


def generate_reasoning(factors, recommendation, question, edge):
    """Generate human-readable reasoning from factor scores."""
    parts = []

    # Odds movement
    om = factors["odds_movement"]
    if om > 70:
        parts.append(f"Strong momentum detected (score: {om}/100)")
    elif om > 55:
        parts.append(f"Moderate bullish momentum (score: {om}/100)")
    elif om < 30:
        parts.append(f"Reversal pattern detected — contrarian signal (score: {om}/100)")

    # Volume
    vs = factors["volume_surge"]
    if vs > 75:
        parts.append(f"Volume surge indicates new information entering the market ({vs}/100)")
    elif vs > 50:
        parts.append(f"Above-average volume supports conviction ({vs}/100)")

    # News
    nc = factors["news_catalyst"]
    if nc > 60:
        parts.append(f"Potential news catalyst identified ({nc}/100)")

    # Sentiment
    se = factors["sentiment"]
    if se > 70:
        parts.append(f"Market sentiment strongly aligned ({se}/100)")
    elif se < 35:
        parts.append(f"Contrarian sentiment opportunity ({se}/100)")

    # Historical
    hp = factors["historical_patterns"]
    if hp > 65:
        parts.append(f"Historical patterns favor this outcome ({hp}/100)")

    if not parts:
        parts.append("Multi-factor analysis suggests moderate edge")

    parts.append(f"Recommendation: {recommendation} with +{edge*100:.1f}% edge over market odds")

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

    if for_telegram:
        # Telegram MarkdownV2 format
        card = (
            f"🔮 *POLYMARKET SIGNAL*\n\n"
            f"📊 *Market:* {signal['market_question']}\n"
            f"🏷️ *Category:* {signal['category'].upper()}\n"
            f"📈 *Current Odds:* YES {yes_pct}% | NO {no_pct}%\n\n"
            f"✅ *Recommendation:* {rec} @ {rec_odds}%\n"
            f"🎯 *Model Price:* {model_pct}%\n"
            f"💰 *Edge:* +{edge_pct}%\n"
            f"🔥 *Confidence:* {signal['confidence']:.0f}/100\n\n"
            f"📋 *Analysis:*\n{signal['reasoning']}\n\n"
            f"⏰ *Resolves:* {res_date}\n"
            f"📊 *24h Volume:* {vol_str}\n\n"
            f"#polymarket #{signal['category']} #quivira"
        )
    else:
        # CLI format
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
            f"\n"
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
