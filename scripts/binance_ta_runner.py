"""
Binance TA Runner — Standalone technical analysis engine.

Pulls live OHLCV data from Binance, runs all indicators and ICT analysis,
saves structured results to binance_ta_summary.json. Zero LLM involvement.

Usage:
    python scripts/binance_ta_runner.py
    python scripts/binance_ta_runner.py --pair BTCUSDT
    python scripts/binance_ta_runner.py --timeframe 1h
"""

import os
import sys
import json
import argparse
import time
import requests
from datetime import datetime, timezone

# Ensure scripts directory is on path
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from market_data import (
    get_binance_client,
    fetch_binance_klines,
    fetch_binance_24h,
    calculate_indicators,
    detect_ict_concepts,
    get_kill_zone,
    SYMBOL_TO_COINGECKO,
)

# --- CoinGecko Fallback ---

# CoinGecko free /ohlc granularity: 1-2 days=30min, 3-30 days=4h, 31+ days=daily
# Map timeframes to days that produce meaningfully DIFFERENT candle granularity
COINGECKO_DAYS_MAP = {
    '1m': 1, '5m': 1, '15m': 1, '30m': 1,
    '1h': 2, '4h': 30, '1d': 90, '1w': 365,
}

_binance_unavailable = False  # Set True after first 451/connection failure

# --- Bybit Fallback (public API, no geo-blocking, real volume) ---

BYBIT_INTERVAL_MAP = {
    '1m': '1', '5m': '5', '15m': '15', '30m': '30',
    '1h': '60', '4h': '240', '1d': 'D', '1w': 'W',
}


def fetch_bybit_klines(symbol, interval, limit=200):
    """Fetch OHLCV candles from Bybit public API (no auth, global access, real volume).
    Returns a DataFrame matching fetch_binance_klines format, or None on failure."""
    bybit_interval = BYBIT_INTERVAL_MAP.get(interval)
    if not bybit_interval:
        return None

    params = {
        'category': 'linear',
        'symbol': symbol,
        'interval': bybit_interval,
        'limit': limit,
    }

    # Try primary and fallback Bybit domains
    rows = None
    for base_url in ["https://api.bybit.com", "https://api.bytick.com"]:
        try:
            resp = requests.get(f"{base_url}/v5/market/kline", params=params, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            rows = result.get('result', {}).get('list', [])
            if rows:
                break
        except Exception:
            continue

    if not rows:
        return None

    if not rows or len(rows) < 10:
        return None

    # Bybit returns: [startTime, open, high, low, close, volume, turnover] newest first
    df = pd.DataFrame(rows, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 'quote_volume'
    ])
    df = df.iloc[::-1].reset_index(drop=True)  # Reverse to oldest-first
    df['open_time'] = pd.to_datetime(df['open_time'].astype(float), unit='ms')
    df['close_time'] = df['open_time']
    df['trades'] = 0
    df['taker_buy_base'] = 0.0
    df['taker_buy_quote'] = 0.0
    df['ignore'] = 0

    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
        df[col] = df[col].astype(float)

    return df


def _resolve_coingecko_id(symbol):
    """Try to resolve a Binance symbol to a CoinGecko coin ID via search API."""
    # Strip USDT suffix to get the ticker
    ticker = symbol.replace('USDT', '').lower()
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={'query': ticker}, timeout=15
        )
        resp.raise_for_status()
        coins = resp.json().get('coins', [])
        for coin in coins:
            if coin.get('symbol', '').lower() == ticker:
                coin_id = coin['id']
                # Cache it for the rest of this process
                SYMBOL_TO_COINGECKO[symbol] = coin_id
                print(f"  CoinGecko auto-resolved {symbol} -> {coin_id}")
                return coin_id
    except Exception as e:
        print(f"  CoinGecko search failed for {symbol}: {e}")
    return None


def fetch_coingecko_ohlcv(symbol, interval, limit=200):
    """Fetch OHLCV candles from CoinGecko free API.
    Returns a DataFrame matching fetch_binance_klines format, or None on failure."""
    coin_id = SYMBOL_TO_COINGECKO.get(symbol)
    if not coin_id:
        coin_id = _resolve_coingecko_id(symbol)
    if not coin_id:
        return None

    days = COINGECKO_DAYS_MAP.get(interval, 30)
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': 'usd', 'days': days}

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()  # [[timestamp, open, high, low, close], ...]
    except Exception as e:
        print(f"\n  CoinGecko fallback failed for {symbol}: {e}")
        return None

    if not data or len(data) < 10:
        return None

    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    # CoinGecko OHLC endpoint does not return volume; estimate with zeros
    df['volume'] = 0.0
    df['close_time'] = df['open_time']
    df['quote_volume'] = 0.0
    df['trades'] = 0
    df['taker_buy_base'] = 0.0
    df['taker_buy_quote'] = 0.0
    df['ignore'] = 0

    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].astype(float)

    # Trim to requested limit
    if len(df) > limit:
        df = df.tail(limit).reset_index(drop=True)

    return df


def fetch_coingecko_volume(symbol):
    """Fetch 24h volume from CoinGecko market_chart for a symbol. Returns float or 0."""
    coin_id = SYMBOL_TO_COINGECKO.get(symbol) or _resolve_coingecko_id(symbol)
    if not coin_id:
        return 0.0
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {'localization': 'false', 'tickers': 'false',
                  'community_data': 'false', 'developer_data': 'false'}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get('market_data', {}).get('total_volume', {}).get('usd', 0))
    except Exception:
        return 0.0


def _is_binance_geo_blocked(e):
    """Check if an exception indicates Binance 451 geo-block or connection failure."""
    msg = str(e).lower()
    return '451' in msg or 'unavailable' in msg or 'connection' in msg or 'banned' in msg


# --- Config ---

CORE_PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
MIN_ALTCOIN_VOLUME = 50_000_000  # $50M 24H volume
MAX_ALTCOINS = 17
TIMEFRAMES = ['1h', '4h', '1d']
CORE_TIMEFRAMES = ['1h', '4h', '1d']  # Core pairs get all 3
ALT_TIMEFRAMES = ['4h']  # Altcoins get 4H only to save API calls

INTERVAL_MAP = {
    '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
    '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w',
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'binance_ta_summary.json')

# Stablecoins to skip
STABLECOINS = {'USDCUSDT', 'USDTUSDC', 'BUSDUSDT', 'FDUSDUSDT', 'USD1USDT',
               'TUSDUSDT', 'DAIUSDT', 'EURUSDT'}


# --- Additional Indicators (not in market_data.py) ---

def calculate_rsi(df, period=14):
    """Calculate RSI (Relative Strength Index)."""
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def detect_rsi_divergence(df, lookback=20):
    """Detect bullish/bearish RSI divergence using swing highs/lows.
    Returns: 'bullish', 'bearish', or None."""
    if len(df) < lookback or 'rsi' not in df.columns:
        return None

    close = df['close'].iloc[-lookback:].values
    rsi = df['rsi'].iloc[-lookback:].values

    if np.any(np.isnan(rsi)):
        return None

    # Find swing lows (2-bar pivot) for bullish divergence
    swing_lows = []
    for i in range(2, len(close) - 2):
        if close[i] <= close[i-1] and close[i] <= close[i-2] and close[i] <= close[i+1] and close[i] <= close[i+2]:
            swing_lows.append(i)

    if len(swing_lows) >= 2:
        a, b = swing_lows[-2], swing_lows[-1]
        # Price lower low but RSI higher low = bullish divergence
        if close[b] < close[a] and rsi[b] > rsi[a]:
            return 'bullish'

    # Find swing highs for bearish divergence
    swing_highs = []
    for i in range(2, len(close) - 2):
        if close[i] >= close[i-1] and close[i] >= close[i-2] and close[i] >= close[i+1] and close[i] >= close[i+2]:
            swing_highs.append(i)

    if len(swing_highs) >= 2:
        a, b = swing_highs[-2], swing_highs[-1]
        # Price higher high but RSI lower high = bearish divergence
        if close[b] > close[a] and rsi[b] < rsi[a]:
            return 'bearish'

    return None


def calculate_atr(df, period=14):
    """Calculate ATR (Average True Range)."""
    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, min_periods=period).mean()
    return atr


def calculate_volume_profile(df, periods=24):
    """Calculate volume profile: POC, value area high/low, HVN/LVN."""
    recent = df.tail(periods)
    if len(recent) < 5:
        return {'poc': None, 'value_area_high': None, 'value_area_low': None,
                'hvn': [], 'lvn': []}

    # Create price bins
    price_min = recent['low'].min()
    price_max = recent['high'].max()
    n_bins = min(20, len(recent))
    bins = np.linspace(price_min, price_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    # Distribute volume across bins based on candle range
    vol_profile = np.zeros(n_bins)
    for _, row in recent.iterrows():
        for j in range(n_bins):
            if row['low'] <= bin_centers[j] <= row['high']:
                vol_profile[j] += row['volume']

    if vol_profile.sum() == 0:
        return {'poc': float(recent['close'].iloc[-1]), 'value_area_high': None,
                'value_area_low': None, 'hvn': [], 'lvn': []}

    # POC = price level with highest volume
    poc_idx = vol_profile.argmax()
    poc = float(bin_centers[poc_idx])

    # Value area: 70% of total volume centered on POC
    total_vol = vol_profile.sum()
    target_vol = total_vol * 0.70
    cumulative = 0
    va_low_idx = poc_idx
    va_high_idx = poc_idx
    cumulative += vol_profile[poc_idx]

    while cumulative < target_vol and (va_low_idx > 0 or va_high_idx < n_bins - 1):
        low_vol = vol_profile[va_low_idx - 1] if va_low_idx > 0 else 0
        high_vol = vol_profile[va_high_idx + 1] if va_high_idx < n_bins - 1 else 0
        if low_vol >= high_vol and va_low_idx > 0:
            va_low_idx -= 1
            cumulative += vol_profile[va_low_idx]
        elif va_high_idx < n_bins - 1:
            va_high_idx += 1
            cumulative += vol_profile[va_high_idx]
        else:
            va_low_idx -= 1
            cumulative += vol_profile[va_low_idx]

    # HVN = bins with volume > 1.5x average, LVN = bins with volume < 0.5x average
    avg_vol = vol_profile.mean()
    hvn = [float(bin_centers[i]) for i in range(n_bins) if vol_profile[i] > avg_vol * 1.5]
    lvn = [float(bin_centers[i]) for i in range(n_bins) if 0 < vol_profile[i] < avg_vol * 0.5]

    return {
        'poc': poc,
        'value_area_high': float(bin_centers[va_high_idx]),
        'value_area_low': float(bin_centers[va_low_idx]),
        'hvn': hvn[:5],
        'lvn': lvn[:5],
    }


def detect_support_resistance(df, lookback=50):
    """Detect key support and resistance levels from swing points."""
    recent = df.tail(lookback)
    high = recent['high'].values
    low = recent['low'].values
    close_val = recent['close'].values

    levels = []

    # Find swing highs and lows (resistance and support)
    for i in range(2, len(recent) - 2):
        # Swing high = resistance
        if high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i+1] and high[i] > high[i+2]:
            levels.append({'type': 'resistance', 'price': float(high[i])})
        # Swing low = support
        if low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i+1] and low[i] < low[i+2]:
            levels.append({'type': 'support', 'price': float(low[i])})

    # Cluster nearby levels (within 0.5% of each other)
    clustered = []
    used = set()
    for i, lvl in enumerate(levels):
        if i in used:
            continue
        cluster = [lvl]
        for j, other in enumerate(levels):
            if j != i and j not in used:
                if abs(lvl['price'] - other['price']) / lvl['price'] < 0.005:
                    cluster.append(other)
                    used.add(j)
        used.add(i)
        avg_price = sum(l['price'] for l in cluster) / len(cluster)
        # Type = whichever appears more
        types = [l['type'] for l in cluster]
        level_type = max(set(types), key=types.count)
        clustered.append({
            'type': level_type,
            'price': round(avg_price, 6),
            'touches': len(cluster),
        })

    # Sort by price descending
    clustered.sort(key=lambda x: x['price'], reverse=True)

    current_price = float(close_val[-1])
    resistances = [l for l in clustered if l['price'] > current_price]
    supports = [l for l in clustered if l['price'] <= current_price]

    return {
        'resistance': resistances[:5],
        'support': supports[:5],
    }


def detect_chart_patterns(df):
    """Detect common chart patterns in recent price action."""
    patterns = []
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    n = len(close)

    if n < 30:
        return patterns

    recent_20 = close[-20:]
    recent_high = high[-20:]
    recent_low = low[-20:]

    # Double top: two highs within 0.5% of each other with a valley between
    peaks = []
    for i in range(1, len(recent_high) - 1):
        if recent_high[i] > recent_high[i-1] and recent_high[i] > recent_high[i+1]:
            peaks.append((i, recent_high[i]))
    if len(peaks) >= 2:
        p1, p2 = peaks[-2], peaks[-1]
        if abs(p1[1] - p2[1]) / p1[1] < 0.005 and p2[0] - p1[0] >= 3:
            patterns.append({
                'pattern': 'double_top',
                'direction': 'bearish',
                'level': round(float((p1[1] + p2[1]) / 2), 6),
            })

    # Double bottom: two lows within 0.5% of each other with a peak between
    troughs = []
    for i in range(1, len(recent_low) - 1):
        if recent_low[i] < recent_low[i-1] and recent_low[i] < recent_low[i+1]:
            troughs.append((i, recent_low[i]))
    if len(troughs) >= 2:
        t1, t2 = troughs[-2], troughs[-1]
        if abs(t1[1] - t2[1]) / t1[1] < 0.005 and t2[0] - t1[0] >= 3:
            patterns.append({
                'pattern': 'double_bottom',
                'direction': 'bullish',
                'level': round(float((t1[1] + t2[1]) / 2), 6),
            })

    # Higher highs + higher lows = ascending channel
    if len(peaks) >= 2 and len(troughs) >= 2:
        if peaks[-1][1] > peaks[-2][1] and troughs[-1][1] > troughs[-2][1]:
            patterns.append({'pattern': 'ascending_channel', 'direction': 'bullish'})
        elif peaks[-1][1] < peaks[-2][1] and troughs[-1][1] < troughs[-2][1]:
            patterns.append({'pattern': 'descending_channel', 'direction': 'bearish'})

    # Bollinger squeeze (if available)
    if 'bb_width' in df.columns:
        bb_width = df['bb_width'].values
        if len(bb_width) >= 20:
            current_width = bb_width[-1]
            avg_width = np.nanmean(bb_width[-20:])
            if not np.isnan(current_width) and not np.isnan(avg_width):
                if current_width < avg_width * 0.6:
                    patterns.append({'pattern': 'bollinger_squeeze', 'direction': 'neutral'})

    # Engulfing candles (last 3 candles)
    opens = df['open'].values
    if n >= 2:
        # Bullish engulfing
        if (close[-2] < opens[-2] and  # Previous bearish
            close[-1] > opens[-1] and  # Current bullish
            close[-1] > opens[-2] and opens[-1] < close[-2]):
            patterns.append({'pattern': 'bullish_engulfing', 'direction': 'bullish'})
        # Bearish engulfing
        if (close[-2] > opens[-2] and  # Previous bullish
            close[-1] < opens[-1] and  # Current bearish
            close[-1] < opens[-2] and opens[-1] > close[-2]):
            patterns.append({'pattern': 'bearish_engulfing', 'direction': 'bearish'})

    return patterns


# --- Confluence Scoring ---

def score_confluences(df, ict, vol_profile, sr_levels, patterns, session_info, trend='UNKNOWN'):
    """Score confluences and determine signal direction + strength."""
    last = df.iloc[-1]
    price = float(last['close'])
    confluences = []

    # 1. ICT Concepts
    ict_found = False
    for ob in ict.get('order_blocks', [])[-5:]:
        if ob['type'] == 'bullish' and ob['low'] <= price <= ob['high'] * 1.005:
            confluences.append({'factor': 'ICT', 'detail': f"Bullish order block at {ob['low']:.2f}-{ob['high']:.2f}", 'direction': 'bullish'})
            ict_found = True
            break
        elif ob['type'] == 'bearish' and ob['low'] * 0.995 <= price <= ob['high']:
            confluences.append({'factor': 'ICT', 'detail': f"Bearish order block at {ob['low']:.2f}-{ob['high']:.2f}", 'direction': 'bearish'})
            ict_found = True
            break

    if not ict_found:
        for fvg in ict.get('fvgs', [])[-5:]:
            if fvg['type'] == 'bullish' and fvg['bottom'] <= price <= fvg['top']:
                confluences.append({'factor': 'ICT', 'detail': f"Bullish FVG at {fvg['bottom']:.2f}-{fvg['top']:.2f}", 'direction': 'bullish'})
                ict_found = True
                break
            elif fvg['type'] == 'bearish' and fvg['bottom'] <= price <= fvg['top']:
                confluences.append({'factor': 'ICT', 'detail': f"Bearish FVG at {fvg['bottom']:.2f}-{fvg['top']:.2f}", 'direction': 'bearish'})
                ict_found = True
                break

    if not ict_found:
        for mss in ict.get('mss_bos', []):
            direction = 'bullish' if 'bullish' in mss['type'] else 'bearish'
            confluences.append({'factor': 'ICT', 'detail': f"{mss['type']} at {mss['price']:.2f}", 'direction': direction})
            break

    for sweep in ict.get('liquidity_sweeps', []):
        direction = 'bullish' if 'bullish' in sweep['type'] else 'bearish'
        confluences.append({'factor': 'ICT_sweep', 'detail': f"{sweep['type']} of {sweep['swept_level']:.2f}", 'direction': direction})
        break

    # 2. EMA alignment
    ema21 = last.get('ema_21')
    ema50 = last.get('ema_50')
    ema200 = last.get('ema_200')
    if not pd.isna(ema21) and not pd.isna(ema50):
        if price > ema21 > ema50:
            confluences.append({'factor': 'EMA', 'detail': f"Price > EMA21 ({ema21:.2f}) > EMA50 ({ema50:.2f})", 'direction': 'bullish'})
        elif price < ema21 < ema50:
            confluences.append({'factor': 'EMA', 'detail': f"Price < EMA21 ({ema21:.2f}) < EMA50 ({ema50:.2f})", 'direction': 'bearish'})

    # 3. MACD
    macd_val = last.get('macd')
    macd_sig = last.get('macd_signal')
    macd_hist = last.get('macd_histogram')
    if not pd.isna(macd_val) and not pd.isna(macd_sig):
        if macd_val > macd_sig and macd_hist > 0:
            confluences.append({'factor': 'MACD', 'detail': 'Bullish crossover, positive histogram', 'direction': 'bullish'})
        elif macd_val < macd_sig and macd_hist < 0:
            confluences.append({'factor': 'MACD', 'detail': 'Bearish crossover, negative histogram', 'direction': 'bearish'})

    # 4. Bollinger Bands
    bb_lower = last.get('bb_lower')
    bb_upper = last.get('bb_upper')
    bb_width = last.get('bb_width')
    if not pd.isna(bb_lower) and not pd.isna(bb_upper):
        if price <= bb_lower * 1.005:
            confluences.append({'factor': 'BB', 'detail': f"Price at lower band ({bb_lower:.2f})", 'direction': 'bullish'})
        elif price >= bb_upper * 0.995:
            confluences.append({'factor': 'BB', 'detail': f"Price at upper band ({bb_upper:.2f})", 'direction': 'bearish'})
        if not pd.isna(bb_width):
            avg_width = df['bb_width'].tail(20).mean()
            if not pd.isna(avg_width) and bb_width < avg_width * 0.6:
                confluences.append({'factor': 'BB_squeeze', 'detail': 'Bollinger squeeze detected', 'direction': 'neutral'})

    # 5. Volume (skip if no real volume data, e.g. CoinGecko fallback where volume=0)
    if 'volume' in df.columns:
        vol_avg = df['volume'].tail(20).mean()
        vol_recent = df['volume'].tail(5).mean()
        if vol_avg > 100 and vol_recent > vol_avg * 1.5:
            confluences.append({'factor': 'Volume', 'detail': f"Volume surge {vol_recent/vol_avg:.1f}x average", 'direction': 'neutral'})

    # 6. Fibonacci OTE
    fib_618 = df.attrs.get('fib_0.618')
    fib_786 = df.attrs.get('fib_0.786')
    if fib_618 and fib_786:
        ote_low = min(fib_618, fib_786)
        ote_high = max(fib_618, fib_786)
        if ote_low <= price <= ote_high:
            confluences.append({'factor': 'Fibonacci', 'detail': f"Price in OTE zone ({ote_low:.2f}-{ote_high:.2f})", 'direction': 'neutral'})
        else:
            for name, val in [('0.382', df.attrs.get('fib_0.382')),
                              ('0.5', df.attrs.get('fib_0.5')),
                              ('0.618', fib_618)]:
                if val and abs(price - val) / price < 0.005:
                    confluences.append({'factor': 'Fibonacci', 'detail': f"Price at Fib {name} ({val:.2f})", 'direction': 'neutral'})
                    break

    # 7. Kill zone
    session, in_kz = session_info
    if in_kz:
        confluences.append({'factor': 'KillZone', 'detail': f"{session} kill zone active", 'direction': 'neutral'})

    # 8. Support/Resistance (require 2+ touches — 1 touch is not real S/R)
    nearest_support = sr_levels['support'][0] if sr_levels['support'] else None
    nearest_resistance = sr_levels['resistance'][-1] if sr_levels['resistance'] else None
    if nearest_support and nearest_support.get('touches', 0) >= 2 and abs(price - nearest_support['price']) / price < 0.005:
        confluences.append({'factor': 'SR', 'detail': f"At support {nearest_support['price']:.2f} ({nearest_support['touches']} touches)", 'direction': 'bullish'})
    if nearest_resistance and nearest_resistance.get('touches', 0) >= 2 and abs(price - nearest_resistance['price']) / price < 0.005:
        confluences.append({'factor': 'SR', 'detail': f"At resistance {nearest_resistance['price']:.2f} ({nearest_resistance['touches']} touches)", 'direction': 'bearish'})

    # 9. Market Structure (CHOCH + HH/HL/LH/LL)
    for ch in ict.get('choch', []):
        direction = 'bullish' if 'bullish' in ch['type'] else 'bearish'
        confluences.append({'factor': 'Structure', 'detail': f"{ch['type'].upper()} — broke {ch['broken_level']:.2f}", 'direction': direction})
        break
    if not any(c['factor'] == 'Structure' for c in confluences):
        labels = ict.get('structure_labels', [])
        if len(labels) >= 2:
            last_two = [l['type'] for l in labels[-2:]]
            if last_two == ['HH', 'HL'] or last_two == ['HL', 'HH']:
                confluences.append({'factor': 'Structure', 'detail': f"Bullish structure: {'+'.join(last_two)}", 'direction': 'bullish'})
            elif last_two == ['LH', 'LL'] or last_two == ['LL', 'LH']:
                confluences.append({'factor': 'Structure', 'detail': f"Bearish structure: {'+'.join(last_two)}", 'direction': 'bearish'})

    # 10. Liquidity Pools (equal highs/lows being targeted)
    for pool in ict.get('liquidity_pools', []):
        dist = abs(price - pool['price']) / price if price > 0 else 1
        if dist < 0.01:  # Within 1% of liquidity pool
            if pool['side'] == 'buyside' and price < pool['price']:
                confluences.append({'factor': 'Liquidity', 'detail': f"Equal highs liquidity at {pool['price']:.2f} (buyside target)", 'direction': 'bullish'})
            elif pool['side'] == 'sellside' and price > pool['price']:
                confluences.append({'factor': 'Liquidity', 'detail': f"Equal lows liquidity at {pool['price']:.2f} (sellside target)", 'direction': 'bearish'})
            break

    # 11. Protected Highs / Lows (untouched swing points = resting liquidity)
    for ph in ict.get('protected_highs', []):
        if ph['status'] == 'protected':
            dist = abs(price - ph['price']) / price if price > 0 else 1
            if dist < 0.015:  # Within 1.5% of protected high
                confluences.append({'factor': 'Protected', 'detail': f"Protected high at {ph['price']:.2f} — buyside liquidity untouched", 'direction': 'bearish'})
                break
    for pl in ict.get('protected_lows', []):
        if pl['status'] == 'protected':
            dist = abs(price - pl['price']) / price if price > 0 else 1
            if dist < 0.015:  # Within 1.5% of protected low
                confluences.append({'factor': 'Protected', 'detail': f"Protected low at {pl['price']:.2f} — sellside liquidity untouched", 'direction': 'bullish'})
                break

    # 12. Breaker Blocks (failed OBs acting as S/R in opposite direction)
    for bb in ict.get('breaker_blocks', []):
        if bb['type'] == 'bullish_breaker' and bb['low'] <= price <= bb['high'] * 1.005:
            confluences.append({'factor': 'Breaker', 'detail': f"Bullish breaker block at {bb['low']:.2f}-{bb['high']:.2f}", 'direction': 'bullish'})
            break
        elif bb['type'] == 'bearish_breaker' and bb['low'] * 0.995 <= price <= bb['high']:
            confluences.append({'factor': 'Breaker', 'detail': f"Bearish breaker block at {bb['low']:.2f}-{bb['high']:.2f}", 'direction': 'bearish'})
            break

    # 12. RSI Divergence (price vs RSI disagreement = reversal signal)
    rsi_div = detect_rsi_divergence(df)
    if rsi_div == 'bullish':
        confluences.append({'factor': 'RSI_divergence', 'detail': 'Bullish RSI divergence (price lower low, RSI higher low)', 'direction': 'bullish'})
    elif rsi_div == 'bearish':
        confluences.append({'factor': 'RSI_divergence', 'detail': 'Bearish RSI divergence (price higher high, RSI lower high)', 'direction': 'bearish'})

    # Count unique factor categories (max 1 per category)
    # Context factors don't count toward the confluence threshold
    CONTEXT_FACTORS = {'KillZone', 'Fibonacci'}
    seen_factors = set()
    unique_confluences = []
    for c in confluences:
        base_factor = c['factor'].split('_')[0]  # Group ICT_sweep with ICT, BB_squeeze with BB
        if base_factor not in seen_factors:
            seen_factors.add(base_factor)
            unique_confluences.append(c)

    # Directional confluences only — exclude context AND neutral-direction factors
    # (BB_squeeze, Volume surges are context, not directional conviction)
    directional = [c for c in unique_confluences
                   if c['factor'] not in CONTEXT_FACTORS and c['direction'] != 'neutral']

    # Determine majority direction
    bullish = sum(1 for c in directional if c['direction'] == 'bullish')
    bearish = sum(1 for c in directional if c['direction'] == 'bearish')
    direction = 'LONG' if bullish > bearish else 'SHORT' if bearish > bullish else 'NEUTRAL'

    # Only count confluences that AGREE with the dominant direction
    # (3 bullish + 2 bearish should be count=3, not count=5)
    if direction == 'LONG':
        count = bullish
    elif direction == 'SHORT':
        count = bearish
    else:
        count = 0

    # --- Contradiction check: chart patterns that oppose the signal direction ---
    # A double top / descending channel should block a LONG signal
    # A double bottom / ascending channel should block a SHORT signal
    bearish_patterns = {'double_top', 'descending_channel', 'bearish_engulfing'}
    bullish_patterns = {'double_bottom', 'ascending_channel', 'bullish_engulfing'}
    pattern_names = {p.get('pattern', '') for p in patterns}

    contradiction = False
    contradiction_detail = []
    if direction == 'LONG' and pattern_names & bearish_patterns:
        contradiction = True
        contradiction_detail = list(pattern_names & bearish_patterns)
    elif direction == 'SHORT' and pattern_names & bullish_patterns:
        contradiction = True
        contradiction_detail = list(pattern_names & bullish_patterns)

    # Also check: MSS/BOS opposing direction
    for mss in ict.get('mss_bos', []):
        if direction == 'LONG' and 'bearish' in mss['type']:
            contradiction = True
            contradiction_detail.append(mss['type'])
        elif direction == 'SHORT' and 'bullish' in mss['type']:
            contradiction = True
            contradiction_detail.append(mss['type'])

    # Trend opposition: never trade against the trend
    if direction == 'LONG' and trend == 'BEARISH':
        contradiction = True
        contradiction_detail.append('LONG_against_BEARISH_trend')
    elif direction == 'SHORT' and trend == 'BULLISH':
        contradiction = True
        contradiction_detail.append('SHORT_against_BULLISH_trend')

    # If contradicted: reduce count by number of opposing signals, cap confidence
    if contradiction:
        count = max(0, count - len(contradiction_detail))

    # RANGING trend needs higher conviction — no clear momentum to ride
    min_count = 6 if trend in ('RANGING', 'UNKNOWN') else 5

    # Confidence — uses dynamic threshold based on trend clarity
    if contradiction:
        confidence = 'LOW'  # Never HIGH/MEDIUM with active contradictions
    elif count >= min_count + 2:
        confidence = 'HIGH'
    elif count >= min_count:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    return {
        'confluences': [{'factor': c['factor'], 'detail': c['detail'], 'direction': c['direction']} for c in unique_confluences],
        'min_count': min_count,
        'confluence_count': count,
        'direction': direction,
        'confidence': confidence,
        'bullish_count': bullish,
        'bearish_count': bearish,
        'contradiction': contradiction,
        'contradiction_detail': contradiction_detail,
    }


def calculate_strength_score(confluence_result, rsi_val, macd_hist, trend, patterns):
    """Calculate a 1-10 strength score based on all factors."""
    score = 0

    # Confluence count (0-4 points)
    cc = confluence_result['confluence_count']
    if cc >= 6:
        score += 4
    elif cc >= 5:
        score += 3.5
    elif cc >= 4:
        score += 3
    elif cc >= 3:
        score += 2
    elif cc >= 2:
        score += 1

    # Direction agreement strength (0-2 points)
    total_dir = confluence_result['bullish_count'] + confluence_result['bearish_count']
    if total_dir > 0:
        agreement = max(confluence_result['bullish_count'], confluence_result['bearish_count']) / total_dir
        score += agreement * 2

    # RSI confirmation (0-1.5 points)
    direction = confluence_result['direction']
    if rsi_val is not None and not np.isnan(rsi_val):
        if direction == 'LONG' and rsi_val < 40:
            score += 1.5  # Oversold + bullish setup
        elif direction == 'LONG' and rsi_val < 50:
            score += 0.75
        elif direction == 'SHORT' and rsi_val > 60:
            score += 1.5  # Overbought + bearish setup
        elif direction == 'SHORT' and rsi_val > 50:
            score += 0.75

    # MACD histogram strength (0-1 point)
    if macd_hist is not None and not np.isnan(macd_hist):
        if (direction == 'LONG' and macd_hist > 0) or (direction == 'SHORT' and macd_hist < 0):
            score += 1

    # Trend alignment (0-1 point)
    if (direction == 'LONG' and trend == 'BULLISH') or (direction == 'SHORT' and trend == 'BEARISH'):
        score += 1

    # Chart patterns (0-0.5 points)
    for p in patterns:
        if (direction == 'LONG' and p.get('direction') == 'bullish') or \
           (direction == 'SHORT' and p.get('direction') == 'bearish'):
            score += 0.5
            break

    # RSI divergence bonus (0-1 point) — strong reversal signal
    rsi_div_factors = [c for c in confluence_result['confluences'] if c['factor'] == 'RSI_divergence']
    for c in rsi_div_factors:
        if (direction == 'LONG' and c['direction'] == 'bullish') or \
           (direction == 'SHORT' and c['direction'] == 'bearish'):
            score += 1
            break

    # Institutional factors bonus (0-1.5 points)
    # CHOCH, liquidity pools, breaker blocks — nephew_sam_ methodology
    institutional_factors = {'Structure', 'Liquidity', 'Breaker', 'Protected'}
    inst_count = sum(1 for c in confluence_result['confluences'] if c['factor'] in institutional_factors)
    score += inst_count * 0.5  # 0.5 per institutional factor (max 1.5)

    # Contradiction penalty (-2 points)
    if confluence_result.get('contradiction'):
        score -= 2

    return max(1, min(10, round(score)))


# --- Trend Detection ---

def determine_trend(df):
    """Determine trend from EMA alignment."""
    last = df.iloc[-1]
    ema21 = last.get('ema_21')
    ema50 = last.get('ema_50')
    ema200 = last.get('ema_200')
    price = float(last['close'])

    # Primary: EMA50 + EMA200
    if not pd.isna(ema50) and not pd.isna(ema200):
        if price > ema50 > ema200:
            return 'BULLISH'
        elif price < ema50 < ema200:
            return 'BEARISH'
        else:
            return 'RANGING'

    # Fallback: EMA21 + EMA50 (when EMA200 unavailable)
    if not pd.isna(ema21) and not pd.isna(ema50):
        if price > ema21 > ema50:
            return 'BULLISH'
        elif price < ema21 < ema50:
            return 'BEARISH'
        else:
            return 'RANGING'

    return 'UNKNOWN'


# --- Auto-discover top altcoins ---

def discover_top_altcoins(client):
    """Pull top altcoins by 24H USDT volume from Binance."""
    try:
        tickers = client.get_ticker()
        usdt_pairs = []
        for t in tickers:
            sym = t['symbol']
            if not sym.endswith('USDT'):
                continue
            if sym in STABLECOINS:
                continue
            if sym in [f'{c}' for c in CORE_PAIRS]:
                continue
            vol = float(t.get('quoteVolume', 0))
            if vol >= MIN_ALTCOIN_VOLUME:
                usdt_pairs.append({'symbol': sym, 'volume_24h': vol})

        usdt_pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
        return [p['symbol'] for p in usdt_pairs[:MAX_ALTCOINS]]
    except Exception as e:
        print(f"  Warning: Could not discover altcoins: {e}")
        # Fallback to known list
        return ['BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT', 'LINKUSDT',
                'AVAXUSDT', 'SUIUSDT', 'ARBUSDT', 'NEARUSDT', 'OPUSDT']


def _detect_displacement(df, atr_val):
    """Check last 3 candles for displacement (body > 1.5x ATR). Returns dict."""
    if df is None or len(df) < 3 or not atr_val or atr_val <= 0:
        return {'detected': False, 'direction': None, 'body_atr_ratio': None}
    threshold = 1.5 * atr_val
    for i in range(-1, -4, -1):
        candle = df.iloc[i]
        body = abs(float(candle['close']) - float(candle['open']))
        if body >= threshold:
            direction = 'bullish' if candle['close'] > candle['open'] else 'bearish'
            return {'detected': True, 'direction': direction, 'body_atr_ratio': round(body / atr_val, 2)}
    return {'detected': False, 'direction': None, 'body_atr_ratio': None}


# --- Analyze a single pair on a single timeframe ---

def analyze_pair_tf(client, symbol, timeframe):
    """Full analysis for one pair on one timeframe. Returns structured dict."""
    global _binance_unavailable
    interval = INTERVAL_MAP.get(timeframe, '4h')
    data_source = 'binance'

    df = None
    # Try Binance first (skip if already known to be geo-blocked)
    if client and not _binance_unavailable:
        try:
            df = fetch_binance_klines(client, symbol, interval, limit=200)
        except Exception as e:
            if _is_binance_geo_blocked(e):
                print(f"\n  Binance geo-blocked (451). Switching to Bybit fallback.")
                _binance_unavailable = True
            else:
                pass  # Try fallbacks below

    # Fallback 1: Bybit (public API, no geo-blocking, real volume data)
    if df is None or len(df) < 10:
        df = fetch_bybit_klines(symbol, interval, limit=200)
        if df is not None and len(df) >= 10:
            data_source = 'bybit'

    # Fallback 2: CoinGecko (no volume, rate-limited, last resort)
    if df is None or len(df) < 10:
        df = fetch_coingecko_ohlcv(symbol, interval, limit=200)
        data_source = 'coingecko'

    if df is None or len(df) < 50:
        return {'error': f'Insufficient data (tried {data_source})'}

    # Staleness check — reject if latest candle is too old for the timeframe
    if data_source == 'coingecko' and 'timestamp' in df.columns:
        last_ts = pd.to_datetime(df['timestamp'].iloc[-1], utc=True)
        age_hours = (pd.Timestamp.now(tz='UTC') - last_ts).total_seconds() / 3600
        max_age = {'1h': 3, '4h': 6, '1d': 36}.get(timeframe, 6)
        if age_hours > max_age:
            return {'error': f'Stale data ({data_source}): last candle is {age_hours:.1f}h old'}

    # Core indicators from market_data.py
    df = calculate_indicators(df)

    # Additional indicators
    df['rsi'] = calculate_rsi(df)
    df['atr'] = calculate_atr(df)

    # ICT concepts
    ict = detect_ict_concepts(df)

    # Volume profile
    vol_profile = calculate_volume_profile(df)

    # Support/resistance
    sr_levels = detect_support_resistance(df)

    # Chart patterns
    patterns = detect_chart_patterns(df)

    # Kill zone
    session_info = get_kill_zone()

    # Trend (must be computed before confluence scoring for trend filter)
    trend = determine_trend(df)

    # Confluence scoring
    confluence_result = score_confluences(df, ict, vol_profile, sr_levels, patterns, session_info, trend)

    # Last values
    last = df.iloc[-1]
    price = float(last['close'])
    rsi_val = float(last['rsi']) if not pd.isna(last.get('rsi')) else None
    atr_val = float(last['atr']) if not pd.isna(last.get('atr')) else None
    macd_hist = float(last.get('macd_histogram')) if not pd.isna(last.get('macd_histogram')) else None

    # Strength score (1-10)
    strength = calculate_strength_score(confluence_result, rsi_val, macd_hist, trend, patterns)

    # Assessment
    if confluence_result['direction'] == 'LONG':
        assessment = 'bullish'
    elif confluence_result['direction'] == 'SHORT':
        assessment = 'bearish'
    else:
        assessment = 'neutral'

    # 24H stats from candle data
    vol_24h = float(df['volume'].tail(6 if timeframe == '4h' else 24 if timeframe == '1h' else 1).sum())

    # Fib levels
    fib_levels = {}
    for key in ['fib_0.236', 'fib_0.382', 'fib_0.5', 'fib_0.618', 'fib_0.786']:
        val = df.attrs.get(key)
        if val is not None:
            fib_levels[key] = round(float(val), 6)

    return {
        'pair': symbol,
        'timeframe': timeframe,
        'data_source': data_source,
        'current_price': round(price, 6),
        'volume_24h_approx': round(vol_24h, 2),
        'trend': trend,
        'assessment': assessment,
        'strength_score': strength,

        # Indicators
        'indicators': {
            'ema_21': round(float(last['ema_21']), 6) if not pd.isna(last.get('ema_21')) else None,
            'ema_50': round(float(last['ema_50']), 6) if not pd.isna(last.get('ema_50')) else None,
            'ema_200': round(float(last['ema_200']), 6) if not pd.isna(last.get('ema_200')) else None,
            'rsi': round(rsi_val, 2) if rsi_val else None,
            'macd': round(float(last['macd']), 6) if not pd.isna(last.get('macd')) else None,
            'macd_signal': round(float(last['macd_signal']), 6) if not pd.isna(last.get('macd_signal')) else None,
            'macd_histogram': round(macd_hist, 6) if macd_hist else None,
            'bb_upper': round(float(last['bb_upper']), 6) if not pd.isna(last.get('bb_upper')) else None,
            'bb_middle': round(float(last['bb_middle']), 6) if not pd.isna(last.get('bb_middle')) else None,
            'bb_lower': round(float(last['bb_lower']), 6) if not pd.isna(last.get('bb_lower')) else None,
            'bb_width': round(float(last['bb_width']), 6) if not pd.isna(last.get('bb_width')) else None,
            'atr': round(atr_val, 6) if atr_val else None,
        },

        # Fibonacci
        'fibonacci': {
            'swing_high': round(float(df.attrs.get('swing_high', 0)), 6),
            'swing_low': round(float(df.attrs.get('swing_low', 0)), 6),
            **fib_levels,
        },

        # Volume profile
        'volume_profile': vol_profile,

        # Support/resistance
        'support_resistance': sr_levels,

        # ICT concepts
        'ict_concepts': {
            'order_blocks': ict.get('order_blocks', [])[-3:],
            'fvgs': ict.get('fvgs', [])[-3:],
            'mss_bos': ict.get('mss_bos', []),
            'liquidity_sweeps': ict.get('liquidity_sweeps', []),
            'protected_highs': ict.get('protected_highs', []),
            'protected_lows': ict.get('protected_lows', []),
            'swing_highs': ict.get('swing_highs', [])[-3:],
            'swing_lows': ict.get('swing_lows', [])[-3:],
            'structure_labels': ict.get('structure_labels', [])[-6:],
        },

        # Displacement detection — large impulsive candle in last 3 bars
        'displacement': _detect_displacement(df, atr_val),

        # Chart patterns
        'patterns': patterns,

        # Confluence
        'confluence': confluence_result,
    }


# --- Main Runner ---

def run(pairs_override=None, timeframes_override=None):
    """Run full TA scan and save to JSON."""
    start_time = time.time()

    global _binance_unavailable
    client = get_binance_client()
    if not client:
        print("WARNING: Binance API unavailable. Using Bybit -> CoinGecko fallback.")
        _binance_unavailable = True

    session, in_kz = get_kill_zone()
    print(f"Session: {session} ({'active' if in_kz else 'off-session'})")

    # Build pair list
    if pairs_override:
        all_pairs = pairs_override
    else:
        if client and not _binance_unavailable:
            print("Discovering top altcoins by volume...")
            altcoins = discover_top_altcoins(client)
        else:
            print("Using default altcoin list (Binance unavailable)...")
            altcoins = ['BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT', 'LINKUSDT',
                        'AVAXUSDT', 'SUIUSDT', 'ARBUSDT', 'NEARUSDT', 'OPUSDT']
        all_pairs = CORE_PAIRS + [a for a in altcoins if a not in CORE_PAIRS]
        print(f"Scanning {len(all_pairs)} pairs ({len(CORE_PAIRS)} core + {len(altcoins)} alts)")

    results = []
    errors = []

    for i, pair in enumerate(all_pairs):
        is_core = pair in CORE_PAIRS
        timeframes = timeframes_override or (CORE_TIMEFRAMES if is_core else ALT_TIMEFRAMES)

        for tf in timeframes:
            sys.stdout.write(f"\r  [{i+1}/{len(all_pairs)}] {pair} {tf}...")
            sys.stdout.flush()

            result = analyze_pair_tf(client, pair, tf)

            if 'error' in result:
                errors.append(f"{pair} {tf}: {result['error']}")
            else:
                results.append(result)

            # CoinGecko free tier: ~10 req/min; Binance is faster
            time.sleep(7.0 if _binance_unavailable else 0.15)

    # Build output
    output = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'data_source': 'coingecko' if _binance_unavailable else 'binance',
        'session': session,
        'in_kill_zone': in_kz,
        'pairs_scanned': len(all_pairs),
        'total_analyses': len(results),
        'errors': errors,
        'results': results,
    }

    # Save
    output_path = os.path.abspath(OUTPUT_FILE)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    elapsed = time.time() - start_time
    signals = [r for r in results
               if r['confluence']['confluence_count'] >= r['confluence'].get('min_count', 4)
               and not r['confluence'].get('contradiction')]

    print(f"\nDone. {len(results)} analyses, {len(signals)} signals (qualifying), "
          f"{len(errors)} errors. Saved to {output_path} ({elapsed:.1f}s)")


# --- Signal Builder Functions ---

def calculate_trade_levels(result):
    """Compute Entry, SL, TP1/TP2/TP3 from price, ATR, and S/R levels."""
    price = result['current_price']
    atr = result['indicators'].get('atr')
    direction = result['confluence']['direction']
    sr = result.get('support_resistance', {})
    timeframe = result.get('timeframe', '4h')

    if not atr or direction == 'NEUTRAL':
        return None

    # Minimum SL distance scales by timeframe — 0.5% is noise for 4h crypto
    MIN_SL_PCT = {
        '1m': 0.003, '5m': 0.003, '15m': 0.005, '30m': 0.005,
        '1h': 0.01, '4h': 0.02, '1d': 0.03, '1w': 0.05,
    }
    min_sl_pct = MIN_SL_PCT.get(timeframe, 0.02)

    supports = sr.get('support', [])
    resistances = sr.get('resistance', [])

    # Stop loss: nearest support (longs) or resistance (shorts)
    if direction == 'LONG':
        # SL below nearest support
        if supports:
            sl_level = supports[0]['price']
        else:
            sl_level = price - atr
        # Enforce min distance by timeframe
        min_sl = price * (1 - min_sl_pct)
        if sl_level > min_sl:
            sl_level = min_sl
        # Cap at 1.5x ATR
        max_distance = 1.5 * atr
        if (price - sl_level) > max_distance:
            sl_level = price - max_distance
    else:  # SHORT
        # SL above nearest resistance
        if resistances:
            sl_level = resistances[-1]['price']
        else:
            sl_level = price + atr
        # Enforce min distance by timeframe
        min_sl = price * (1 + min_sl_pct)
        if sl_level < min_sl:
            sl_level = min_sl
        # Cap at 1.5x ATR
        max_distance = 1.5 * atr
        if (sl_level - price) > max_distance:
            sl_level = price + max_distance

    risk = abs(price - sl_level)
    if risk == 0:
        return None

    # Reject if SL is wider than 2x ATR (unreasonable risk)
    if risk > 2.0 * atr:
        return None

    # TPs at 1:2, 1:3, 1:5 R:R
    if direction == 'LONG':
        tp1 = price + risk * 2
        tp2 = price + risk * 3
        tp3 = price + risk * 5
    else:
        tp1 = price - risk * 2
        tp2 = price - risk * 3
        tp3 = price - risk * 5

    return {
        'entry': round(price, 6),
        'stop_loss': round(sl_level, 6),
        'tp1': round(tp1, 6),
        'tp2': round(tp2, 6),
        'tp3': round(tp3, 6),
        'risk': round(risk, 6),
        'rr_tp1': '1:2',
        'rr_tp2': '1:3',
        'rr_tp3': '1:5',
    }


def calculate_signal_score(result):
    """Weighted 0-10 institutional score. Categories: structure, key level,
    liquidity, momentum, entry precision. Each worth 0-2 points. Must be >= 8."""
    score = 0
    direction = result.get('confluence', {}).get('direction', 'NEUTRAL')
    dir_tag = 'bullish' if direction == 'LONG' else 'bearish'
    ict = result.get('ict_concepts', {})
    sr = result.get('support_resistance', {})
    price = result.get('current_price', 0)
    atr = result.get('indicators', {}).get('atr')
    rsi_val = result.get('indicators', {}).get('rsi')
    displacement = result.get('displacement', {})

    # --- 1. Structure alignment (0-2) ---
    labels = ict.get('structure_labels', [])
    if len(labels) >= 2:
        last_two = [l['type'] for l in labels[-2:]]
        if direction == 'LONG' and last_two in (['HH', 'HL'], ['HL', 'HH']):
            score += 2
        elif direction == 'SHORT' and last_two in (['LH', 'LL'], ['LL', 'LH']):
            score += 2
        elif last_two[0] in ('HH', 'HL') and direction == 'LONG':
            score += 1  # partial
        elif last_two[0] in ('LH', 'LL') and direction == 'SHORT':
            score += 1

    # --- 2. Key level — S/R or OB (0-2) ---
    supports = sr.get('support', [])
    resistances = sr.get('resistance', [])
    at_key_level = False
    if price and price > 0:
        for s in supports:
            if s.get('touches', 0) >= 2 and abs(price - s['price']) / price < 0.005:
                score += 2
                at_key_level = True
                break
        if not at_key_level:
            for r in resistances:
                if r.get('touches', 0) >= 2 and abs(price - r['price']) / price < 0.005:
                    score += 2
                    at_key_level = True
                    break
    if not at_key_level:
        # Check order blocks
        for ob in ict.get('order_blocks', []):
            if ob['type'] == dir_tag and ob['low'] <= price <= ob['high']:
                score += 2
                at_key_level = True
                break
        if not at_key_level:
            # FVG as weaker key level
            for fvg in ict.get('fvgs', []):
                if fvg['type'] == dir_tag and not fvg.get('filled') and fvg['bottom'] <= price <= fvg['top']:
                    score += 1
                    break

    # --- 3. Liquidity — sweep or breakout (0-2) ---
    sweeps = ict.get('liquidity_sweeps', [])
    has_sweep = any(dir_tag in s.get('type', '') for s in sweeps)
    has_displacement = displacement.get('detected') and displacement.get('direction') == dir_tag
    if has_sweep:
        score += 2
    elif has_displacement:
        # Breakout displacement path — still strong
        score += 2
    # No partial credit: sweep or breakout, or nothing

    # --- 4. Momentum — RSI + displacement (0-2) ---
    rsi_ok = False
    if rsi_val is not None:
        if direction == 'LONG' and rsi_val >= 55:
            rsi_ok = True
        elif direction == 'SHORT' and rsi_val <= 45:
            rsi_ok = True
    else:
        # RSI missing — do not score momentum points (per spec)
        pass
    if rsi_ok:
        score += 1
    if has_displacement:
        score += 1

    # --- 5. Entry precision (0-2) ---
    # LONG: near support or after breakout+retest. SHORT: near resistance.
    if price and price > 0 and atr and atr > 0:
        if direction == 'LONG':
            # At support?
            near_support = any(
                abs(price - s['price']) / price < 0.005
                for s in supports if s.get('touches', 0) >= 2
            )
            # Breakout retest: BOS_bullish + price near broken level
            bos_retest = False
            for mss in ict.get('mss_bos', []):
                if 'bullish' in mss['type'] and abs(price - mss['price']) / price < 0.01:
                    bos_retest = True
                    break
            if near_support or bos_retest:
                score += 2
            # Not near resistance = good entry (partial credit)
            elif resistances:
                nearest_res = min(r['price'] for r in resistances)
                if nearest_res > price and (nearest_res - price) >= atr:
                    score += 1
        elif direction == 'SHORT':
            near_resistance = any(
                abs(price - r['price']) / price < 0.005
                for r in resistances if r.get('touches', 0) >= 2
            )
            bos_retest = False
            for mss in ict.get('mss_bos', []):
                if 'bearish' in mss['type'] and abs(price - mss['price']) / price < 0.01:
                    bos_retest = True
                    break
            if near_resistance or bos_retest:
                score += 2
            elif supports:
                nearest_sup = max(s['price'] for s in supports)
                if nearest_sup < price and (price - nearest_sup) >= atr:
                    score += 1

    return min(10, max(0, score))


def apply_signal_gates(result, htf_trends, HTF_REQUIRED):
    """Institutional-grade signal filter. Returns (passed, reason | None).

    Nine gates — all must pass. Rejects >= 80% of setups.
    1. Structure   2. Mid-range   3. Entry location   4. ATR proximity
    5. Liquidity   6. Momentum    7. Score >= 8        8. HTF alignment
    9. Risk management
    """
    confluence = result.get('confluence', {})
    direction = confluence.get('direction', 'NEUTRAL')
    pair = result.get('pair', '')
    tf = result.get('timeframe', '')
    trend = result.get('trend', 'UNKNOWN')
    price = result.get('current_price', 0)
    rsi_val = result.get('indicators', {}).get('rsi')
    atr = result.get('indicators', {}).get('atr')
    sr = result.get('support_resistance', {})
    ict = result.get('ict_concepts', {})
    displacement = result.get('displacement', {})
    supports = sr.get('support', [])
    resistances = sr.get('resistance', [])

    # Pre-check: must have direction
    if direction == 'NEUTRAL':
        return False, f"[DIRECTION] {pair} {tf} — NEUTRAL direction"
    if confluence.get('contradiction'):
        return False, f"[CONTRADICTION] {pair} {tf} — {confluence.get('contradiction_detail', [])}"

    dir_tag = 'bullish' if direction == 'LONG' else 'bearish'

    # ── Gate 1: Structure Validation ──
    labels = ict.get('structure_labels', [])
    if trend in ('BULLISH', 'BEARISH'):
        # Trending: require HH+HL (long) or LH+LL (short)
        if len(labels) >= 2:
            types = [l['type'] for l in labels[-4:]]  # check last 4 labels
            if direction == 'LONG' and not ('HH' in types and 'HL' in types):
                return False, f"[STRUCTURE] {pair} {tf} LONG — no HH+HL in trending market"
            if direction == 'SHORT' and not ('LH' in types and 'LL' in types):
                return False, f"[STRUCTURE] {pair} {tf} SHORT — no LH+LL in trending market"
        else:
            return False, f"[STRUCTURE] {pair} {tf} — insufficient structure labels"
    elif trend == 'RANGING':
        # Ranging: need 2+ touches on both support and resistance
        has_strong_support = any(s.get('touches', 0) >= 2 for s in supports)
        has_strong_resistance = any(r.get('touches', 0) >= 2 for r in resistances)
        if not (has_strong_support and has_strong_resistance):
            return False, f"[STRUCTURE] {pair} {tf} — ranging market lacks 2-touch S/R"

    # ── Gate 2: Mid-Range Filter ──
    if supports and resistances and price and price > 0:
        nearest_sup = max(s['price'] for s in supports)
        nearest_res = min(r['price'] for r in resistances)
        if nearest_res > nearest_sup:  # valid range
            range_size = nearest_res - nearest_sup
            midpoint = nearest_sup + range_size / 2
            q1 = nearest_sup + range_size * 0.25
            q3 = nearest_sup + range_size * 0.75
            if q1 <= price <= q3:
                return False, (f"[MID-RANGE] {pair} {tf} {direction} — price {price:.6g} "
                               f"in middle 50% of range ({nearest_sup:.6g}-{nearest_res:.6g})")

    # ── Gate 3: Entry Location ──
    if price and price > 0:
        if direction == 'LONG':
            at_support = any(
                abs(price - s['price']) / price < 0.005 and s.get('touches', 0) >= 2
                for s in supports
            )
            # Breakout + retest: BOS_bullish and price near broken level
            breakout_retest = any(
                'bullish' in m['type'] and abs(price - m['price']) / price < 0.01
                for m in ict.get('mss_bos', [])
            )
            if not at_support and not breakout_retest:
                return False, f"[ENTRY] {pair} {tf} LONG — not at support or breakout+retest"
        elif direction == 'SHORT':
            at_resistance = any(
                abs(price - r['price']) / price < 0.005 and r.get('touches', 0) >= 2
                for r in resistances
            )
            breakdown_retest = any(
                'bearish' in m['type'] and abs(price - m['price']) / price < 0.01
                for m in ict.get('mss_bos', [])
            )
            if not at_resistance and not breakdown_retest:
                return False, f"[ENTRY] {pair} {tf} SHORT — not at resistance or breakdown+retest"

    # ── Gate 4: ATR-Based Proximity ──
    if atr and atr > 0 and price and price > 0:
        half_atr = 0.5 * atr
        if direction == 'LONG' and resistances:
            nearest_res = min(r['price'] for r in resistances)
            if nearest_res > price and (nearest_res - price) < half_atr:
                return False, (f"[PROXIMITY] {pair} {tf} LONG — distance to resistance "
                               f"{nearest_res:.6g} < 0.5×ATR ({half_atr:.6g})")
        if direction == 'SHORT' and supports:
            nearest_sup = max(s['price'] for s in supports)
            if nearest_sup < price and (price - nearest_sup) < half_atr:
                return False, (f"[PROXIMITY] {pair} {tf} SHORT — distance to support "
                               f"{nearest_sup:.6g} < 0.5×ATR ({half_atr:.6g})")

    # ── Gate 5: Liquidity Condition (Dual Path) ──
    sweeps = ict.get('liquidity_sweeps', [])
    has_sweep = any(dir_tag in s.get('type', '') for s in sweeps)
    has_displacement = displacement.get('detected') and displacement.get('direction') == dir_tag
    if not has_sweep and not has_displacement:
        return False, (f"[LIQUIDITY] {pair} {tf} {direction} — no sweep and no breakout "
                       f"displacement on signal timeframe")

    # ── Gate 6: Momentum Confirmation ──
    # RSI rule: LONG >= 55, SHORT <= 45, 45-55 = no trade
    if rsi_val is not None:
        if 45 <= rsi_val <= 55:
            return False, f"[RSI] {pair} {tf} {direction} — RSI {rsi_val:.1f} in neutral zone (45-55)"
        if direction == 'LONG' and rsi_val < 55:
            return False, f"[RSI] {pair} {tf} LONG — RSI {rsi_val:.1f} < 55"
        if direction == 'SHORT' and rsi_val > 45:
            return False, f"[RSI] {pair} {tf} SHORT — RSI {rsi_val:.1f} > 45"
    # Displacement rule: must have momentum candle OR expansion move
    if not has_displacement:
        # Check MACD histogram as fallback momentum indicator
        macd_hist = result.get('indicators', {}).get('macd_histogram')
        if macd_hist is not None:
            if direction == 'LONG' and macd_hist <= 0:
                return False, f"[MOMENTUM] {pair} {tf} LONG — no displacement and MACD histogram negative"
            if direction == 'SHORT' and macd_hist >= 0:
                return False, f"[MOMENTUM] {pair} {tf} SHORT — no displacement and MACD histogram positive"
        else:
            return False, f"[MOMENTUM] {pair} {tf} {direction} — no displacement candle and no MACD data"

    # ── Gate 7: Signal Score >= 8 ──
    score = calculate_signal_score(result)
    if score < 8:
        return False, f"[SCORE] {pair} {tf} {direction} — score {score}/10 < 8"

    # ── Gate 8: HTF Alignment ──
    for htf in HTF_REQUIRED.get(tf, []):
        htf_trend = htf_trends.get((pair, htf))
        if htf_trend and htf_trend != 'UNKNOWN' and htf_trend != 'RANGING':
            if (direction == 'LONG' and htf_trend == 'BEARISH') or \
               (direction == 'SHORT' and htf_trend == 'BULLISH'):
                return False, f"[HTF] {pair} {tf} {direction} — {htf} trend is {htf_trend}"

    # ── Gate 9: Risk Management ──
    levels = calculate_trade_levels(result)
    if not levels:
        return False, f"[RISK] {pair} {tf} {direction} — cannot compute trade levels"
    entry = levels['entry']
    sl = levels['stop_loss']
    tp1 = levels['tp1']
    if entry and sl and tp1:
        risk = abs(entry - sl)
        reward = abs(tp1 - entry)
        if risk <= 0 or reward / risk < 2.0:
            return False, f"[RISK] {pair} {tf} {direction} — RR {reward/risk:.1f}:1 < minimum 2:1"

    # All 9 gates passed — store score + feature snapshot for learning
    result['_signal_score'] = score
    result['_gate_features'] = {
        'rsi': rsi_val,
        'atr': atr,
        'signal_score': score,
        'confluence_count': confluence.get('confluence_count', 0),
        'displacement': displacement.get('detected', False),
        'displacement_ratio': displacement.get('body_atr_ratio'),
        'trend': trend,
        'direction': direction,
        'has_sweep': bool(any(dir_tag in s.get('type', '') for s in ict.get('liquidity_sweeps', []))),
        'structure_labels': [l['type'] for l in ict.get('structure_labels', [])[-4:]],
        'setup_factors': [c['factor'] for c in confluence.get('confluences', [])],
    }
    return True, None


def build_trading_signal(result):
    """Convert a TA result dict into a signal dict with signal_type='trading'."""
    levels = calculate_trade_levels(result)
    if not levels:
        return None

    confluence = result.get('confluence', {})
    confluences_list = [c['detail'] for c in confluence.get('confluences', [])]

    return {
        'signal_type': 'trading',
        'pair': result['pair'],
        'timeframe': result['timeframe'],
        'direction': confluence.get('direction', 'NEUTRAL'),
        'current_price': result['current_price'],
        'entry': levels['entry'],
        'stop_loss': levels['stop_loss'],
        'tp1': levels['tp1'],
        'tp2': levels['tp2'],
        'tp3': levels['tp3'],
        'risk': levels['risk'],
        'rr_tp1': levels['rr_tp1'],
        'rr_tp2': levels['rr_tp2'],
        'rr_tp3': levels['rr_tp3'],
        'confluences': confluences_list,
        'confluence_count': confluence.get('confluence_count', 0),
        'confidence': confluence.get('confidence', 'LOW'),
        'strength_score': result.get('strength_score', 0),
        'signal_score': result.get('_signal_score', 0),
        'trend': result.get('trend', 'UNKNOWN'),
        'rsi': result['indicators'].get('rsi'),
        'atr': result['indicators'].get('atr'),
        'displacement': result.get('displacement', {}).get('detected', False),
        'gate_features': result.get('_gate_features', {}),
        'generated_at': result.get('generated_at', datetime.now(timezone.utc).isoformat()),
    }


# Per-cycle cache for LTF ICT data — avoids re-fetching the same pair+timeframe
_ltf_ict_cache = {}


def clear_ltf_cache():
    """Clear the LTF ICT cache at the start of each signal loading cycle."""
    _ltf_ict_cache.clear()


def _get_cached_ltf_ict(pair, ltf, fetch_fn):
    """Fetch and cache LTF ICT data. Returns cached result on repeat calls for same pair+ltf."""
    cache_key = (pair, ltf)
    if cache_key in _ltf_ict_cache:
        return _ltf_ict_cache[cache_key]

    result = {'status': 'ok', 'ict': None}
    try:
        df = fetch_fn()
        if df is None or len(df) < 20:
            result = {'status': 'skip', 'ict': None}
        else:
            result = {'status': 'ok', 'ict': detect_ict_concepts(df)}
    except Exception as e:
        result = {'status': 'error', 'ict': None, 'error': str(e)}

    _ltf_ict_cache[cache_key] = result
    return result


def check_ltf_sweep_confirmation(pair, direction, signal_tf):
    """Check lower timeframe for sweep confirmation before entry.

    For LONG: require a bullish sweep (wick below prior low that reversed) on 15m/1h.
              This means sellside liquidity was taken — SL below is now protected.
    For SHORT: require a bearish sweep (wick above prior high that reversed) on 15m/1h.
               This means buyside liquidity was taken — SL above is now protected.

    Returns (confirmed: bool, detail: str)
    """
    # LTF to check: 1h signals check 15m, 4h/1d signals check 1h
    ltf = '15m' if signal_tf == '1h' else '1h'
    ltf_interval = BYBIT_INTERVAL_MAP.get(ltf, '60')

    cached = _get_cached_ltf_ict(pair, ltf, lambda: fetch_bybit_klines(pair, ltf_interval, limit=50))

    if cached['status'] == 'error':
        return True, f"LTF sweep check error: {cached.get('error')}"
    if cached['status'] == 'skip' or cached['ict'] is None:
        return True, f"LTF sweep check skipped (insufficient {ltf} data)"

    ict = cached['ict']
    sweeps = ict.get('liquidity_sweeps', [])
    protected_lows = [p for p in ict.get('protected_lows', []) if p['status'] == 'protected']
    protected_highs = [p for p in ict.get('protected_highs', []) if p['status'] == 'protected']

    if direction == 'LONG':
        has_bullish_sweep = any('bullish' in s['type'] for s in sweeps)
        all_lows_swept = len(protected_lows) == 0 and len(ict.get('swing_lows', [])) >= 2
        if has_bullish_sweep:
            swept_level = next(s['swept_level'] for s in sweeps if 'bullish' in s['type'])
            return True, f"Bullish sweep confirmed on {ltf} — swept {swept_level:.6g}, sellside liq taken"
        elif all_lows_swept:
            return True, f"All {ltf} swing lows already swept — sellside clear"
        else:
            return False, f"No bullish sweep on {ltf} — protected lows still untouched, high SL risk"

    elif direction == 'SHORT':
        has_bearish_sweep = any('bearish' in s['type'] for s in sweeps)
        all_highs_swept = len(protected_highs) == 0 and len(ict.get('swing_highs', [])) >= 2
        if has_bearish_sweep:
            swept_level = next(s['swept_level'] for s in sweeps if 'bearish' in s['type'])
            return True, f"Bearish sweep confirmed on {ltf} — swept {swept_level:.6g}, buyside liq taken"
        elif all_highs_swept:
            return True, f"All {ltf} swing highs already swept — buyside clear"
        else:
            return False, f"No bearish sweep on {ltf} — protected highs still untouched, high SL risk"

    return True, "Sweep check passed"


def load_ta_signals(max_age_minutes=60):
    """Read binance_ta_summary.json, check freshness, filter 3+ confluences, return signal dicts."""
    clear_ltf_cache()  # Fresh cache each cycle
    output_path = os.path.abspath(OUTPUT_FILE)
    if not os.path.exists(output_path):
        print(f"TA summary not found: {output_path}")
        return []

    with open(output_path, 'r') as f:
        data = json.load(f)

    # Check freshness
    generated_at = data.get('generated_at', '')
    if generated_at:
        try:
            gen_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            age_minutes = (datetime.now(timezone.utc) - gen_time).total_seconds() / 60
            if age_minutes > max_age_minutes:
                print(f"TA data is {age_minutes:.0f} minutes old (max {max_age_minutes}). Run binance_ta_runner.py first.")
                return []
        except (ValueError, TypeError):
            pass

    results = data.get('results', [])
    signals = []

    # Build HTF trend lookup for cross-timeframe alignment
    # Key: (pair, timeframe) → trend
    htf_trends = {}
    for r in results:
        if 'error' not in r:
            htf_trends[(r['pair'], r['timeframe'])] = r.get('trend', 'UNKNOWN')

    # HTF hierarchy: 1h must align with 4h+1d, 4h must align with 1d
    HTF_REQUIRED = {'1h': ['4h', '1d'], '4h': ['1d']}

    for result in results:
        # Run all rule-based gates (confluence, direction, contradiction,
        # confidence, RSI, proximity, ranging, signal-TF sweep, HTF alignment)
        passed, reason = apply_signal_gates(result, htf_trends, HTF_REQUIRED)
        if not passed:
            print(f"  {reason}")
            continue

        # LTF sweep confirmation — most expensive gate (API call), runs last
        pair = result.get('pair', '')
        tf = result.get('timeframe', '')
        direction = result.get('confluence', {}).get('direction', '')
        sweep_confirmed, sweep_detail = check_ltf_sweep_confirmation(pair, direction, tf)
        if not sweep_confirmed:
            print(f"  [SWEEP] Blocked {pair} {tf} {direction} — {sweep_detail}")
            continue

        signal = build_trading_signal(result)
        if signal:
            signal['generated_at'] = generated_at
            signal['sweep_confirmation'] = sweep_detail
            signals.append(signal)

    print(f"Loaded {len(signals)} trading signals from TA summary ({len(results)} total analyses)")
    return signals


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='Binance TA Runner - Standalone technical analysis')
    parser.add_argument('--pair', type=str, help='Analyze a single pair (e.g., BTCUSDT)')
    parser.add_argument('--timeframe', type=str, help='Override timeframes (comma-separated, e.g., 1h,4h,1d)')
    args = parser.parse_args()

    pairs = [args.pair.upper()] if args.pair else None
    timeframes = args.timeframe.split(',') if args.timeframe else None

    run(pairs_override=pairs, timeframes_override=timeframes)


if __name__ == '__main__':
    main()
