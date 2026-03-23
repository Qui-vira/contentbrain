"""
Market Data Module for Quivira Technical Analyst System.
Pulls price data from Binance API (crypto) with CoinGecko fallback.
Pulls forex data from Twelve Data API.
Calculates technical indicators using the ta library.

Usage:
    python scripts/market_data.py --pair BTCUSDT --timeframe 4h
    python scripts/market_data.py --pair EUR/USD --timeframe 4h
    python scripts/market_data.py --scan
    python scripts/market_data.py --scan-forex
    python scripts/market_data.py --test
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

import pandas as pd
import numpy as np

# Suppress pandas warnings
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Data Source: Binance ---

def get_binance_client():
    """Initialize Binance client. Returns None if unavailable."""
    try:
        from binance.client import Client
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_SECRET_KEY', '')
        client = Client(api_key, api_secret)
        client.ping()
        return client
    except Exception:
        return None


def fetch_binance_klines(client, symbol, interval, limit=200):
    """Fetch candlestick data from Binance."""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
        df[col] = df[col].astype(float)
    return df


def fetch_binance_24h(client, symbol=None):
    """Fetch 24H ticker data from Binance."""
    if symbol:
        return client.get_ticker(symbol=symbol)
    return client.get_all_tickers()


def fetch_binance_spot_price(symbol):
    """Get current spot price from Binance. Returns float or None."""
    client = get_binance_client()
    if not client:
        return None
    try:
        ticker = client.get_ticker(symbol=symbol)
        return float(ticker['lastPrice'])
    except Exception:
        return None


def fetch_binance_funding(client, symbol='BTCUSDT'):
    """Fetch funding rate from Binance Futures."""
    try:
        return client.futures_funding_rate(symbol=symbol, limit=1)
    except Exception:
        return None


def fetch_binance_open_interest(client, symbol='BTCUSDT'):
    """Fetch open interest from Binance Futures."""
    try:
        return client.futures_open_interest(symbol=symbol)
    except Exception:
        return None


# --- Data Source: Twelve Data (Forex) ---

FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'GBP/JPY', 'USD/JPY',
    'XAU/USD', 'USD/CHF', 'AUD/USD', 'NZD/USD',
]

# Pip value per pair (most forex = 0.0001, JPY pairs = 0.01, gold = 0.01)
PIP_SIZE = {
    'EUR/USD': 0.0001, 'GBP/USD': 0.0001, 'USD/CHF': 0.0001,
    'AUD/USD': 0.0001, 'NZD/USD': 0.0001,
    'USD/JPY': 0.01, 'GBP/JPY': 0.01, 'EUR/JPY': 0.01,
    'XAU/USD': 0.10,
}


def is_forex_pair(symbol):
    """Check if a symbol is a forex pair (contains / or matches known forex patterns)."""
    if '/' in symbol:
        return True
    # Normalize: GBPUSD -> GBP/USD
    normalized = normalize_forex_symbol(symbol)
    return normalized in [p.replace('/', '') for p in FOREX_PAIRS] or normalized in FOREX_PAIRS


def normalize_forex_symbol(symbol):
    """Normalize forex symbol to Twelve Data format (e.g., GBPUSD -> GBP/USD)."""
    symbol = symbol.upper().strip()
    if '/' in symbol:
        return symbol
    # Try known 6-char forex pairs
    if len(symbol) == 6:
        return f"{symbol[:3]}/{symbol[3:]}"
    # XAU/USD special case
    if symbol.startswith('XAU'):
        return f"XAU/{symbol[3:]}"
    return symbol


def get_pip_size(symbol):
    """Get pip size for a forex pair."""
    normalized = normalize_forex_symbol(symbol)
    return PIP_SIZE.get(normalized, 0.0001)


def price_to_pips(symbol, price_diff):
    """Convert a price difference to pips."""
    return abs(price_diff) / get_pip_size(symbol)


def fetch_twelvedata_time_series(symbol, interval='4h', outputsize=200):
    """Fetch OHLC time series data from Twelve Data."""
    import requests
    api_key = os.getenv('TWELVEDATA_API_KEY', '')
    if not api_key:
        return None

    interval_map = {
        '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
        '1h': '1h', '4h': '4h', '1d': '1day', '1w': '1week',
        'daily': '1day', 'weekly': '1week',
    }
    td_interval = interval_map.get(interval.lower(), '4h')
    normalized = normalize_forex_symbol(symbol)

    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': normalized,
        'interval': td_interval,
        'outputsize': outputsize,
        'apikey': api_key,
        'timezone': 'UTC',
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if data.get('status') == 'error':
        raise Exception(data.get('message', 'Twelve Data API error'))

    values = data.get('values', [])
    if not values:
        return None

    # Twelve Data returns newest first, reverse to oldest first
    values.reverse()

    df = pd.DataFrame(values)
    df['open_time'] = pd.to_datetime(df['datetime'])
    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].astype(float)
    # Forex has no volume from Twelve Data
    df['volume'] = 0.0

    return df


def fetch_twelvedata_price(symbol):
    """Fetch current price from Twelve Data."""
    import requests
    api_key = os.getenv('TWELVEDATA_API_KEY', '')
    if not api_key:
        return None

    normalized = normalize_forex_symbol(symbol)
    url = "https://api.twelvedata.com/price"
    params = {'symbol': normalized, 'apikey': api_key}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if 'price' not in data:
        raise Exception(data.get('message', 'No price returned'))

    return float(data['price'])


def fetch_twelvedata_quote(symbol):
    """Fetch detailed quote from Twelve Data."""
    import requests
    api_key = os.getenv('TWELVEDATA_API_KEY', '')
    if not api_key:
        return None

    normalized = normalize_forex_symbol(symbol)
    url = "https://api.twelvedata.com/quote"
    params = {'symbol': normalized, 'apikey': api_key}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data.get('code'):
        raise Exception(data.get('message', 'Twelve Data quote error'))

    return data


# --- Data Source: CoinGecko (Fallback) ---

def fetch_coingecko_ohlc(coin_id, vs_currency='usd', days=90):
    """Fetch OHLC data from CoinGecko as fallback."""
    import requests
    api_key = os.getenv('COINGECKO_API_KEY', '')
    headers = {'x-cg-demo-api-key': api_key} if api_key else {}
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': vs_currency, 'days': days}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
    df['open_time'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['volume'] = 0.0  # CoinGecko OHLC doesn't include volume
    return df


def fetch_coingecko_price(coin_id='bitcoin', vs_currency='usd'):
    """Fetch current price from CoinGecko."""
    import requests
    api_key = os.getenv('COINGECKO_API_KEY', '')
    headers = {'x-cg-demo-api-key': api_key} if api_key else {}
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': coin_id,
        'vs_currencies': vs_currency,
        'include_24hr_change': 'true',
        'include_24hr_vol': 'true',
        'include_market_cap': 'true'
    }
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_coingecko_global():
    """Fetch global market data from CoinGecko."""
    import requests
    api_key = os.getenv('COINGECKO_API_KEY', '')
    headers = {'x-cg-demo-api-key': api_key} if api_key else {}
    url = "https://api.coingecko.com/api/v3/global"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_coingecko_trending():
    """Fetch trending coins from CoinGecko."""
    import requests
    api_key = os.getenv('COINGECKO_API_KEY', '')
    headers = {'x-cg-demo-api-key': api_key} if api_key else {}
    url = "https://api.coingecko.com/api/v3/search/trending"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# --- Symbol Mapping ---

SYMBOL_TO_COINGECKO = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'SOLUSDT': 'solana',
    'BNBUSDT': 'binancecoin',
    'XRPUSDT': 'ripple',
    'ADAUSDT': 'cardano',
    'DOGEUSDT': 'dogecoin',
    'DOTUSDT': 'polkadot',
    'AVAXUSDT': 'avalanche-2',
    'LINKUSDT': 'chainlink',
    'MATICUSDT': 'matic-network',
    'NEARUSDT': 'near',
    'ARBUSDT': 'arbitrum',
    'OPUSDT': 'optimism',
    'SUIUSDT': 'sui',
    'APTUSDT': 'aptos',
    'INJUSDT': 'injective-protocol',
    'TIAUSDT': 'celestia',
    'SEIUSDT': 'sei-network',
    'JUPUSDT': 'jupiter-exchange-solana',
}


# --- Indicator Calculations ---

def calculate_indicators(df):
    """Calculate all primary indicators on a DataFrame with OHLCV data."""
    from ta.trend import EMAIndicator, MACD as MACD_indicator
    from ta.volatility import BollingerBands

    close = df['close']
    high = df['high']
    low = df['low']

    # EMAs
    df['ema_21'] = EMAIndicator(close=close, window=21).ema_indicator()
    df['ema_50'] = EMAIndicator(close=close, window=50).ema_indicator()
    df['ema_200'] = EMAIndicator(close=close, window=200).ema_indicator()

    # MACD
    macd = MACD_indicator(close=close, window_slow=26, window_fast=12, window_sign=9)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_histogram'] = macd.macd_diff()

    # Bollinger Bands
    bb = BollingerBands(close=close, window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_middle'] = bb.bollinger_mavg()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_width'] = bb.bollinger_wband()

    # Fibonacci (auto from recent swing high/low over last 50 candles)
    recent = df.tail(50)
    swing_high = recent['high'].max()
    swing_low = recent['low'].min()
    fib_range = swing_high - swing_low
    df.attrs['swing_high'] = swing_high
    df.attrs['swing_low'] = swing_low
    df.attrs['fib_0.236'] = swing_high - fib_range * 0.236
    df.attrs['fib_0.382'] = swing_high - fib_range * 0.382
    df.attrs['fib_0.5'] = swing_high - fib_range * 0.5
    df.attrs['fib_0.618'] = swing_high - fib_range * 0.618
    df.attrs['fib_0.786'] = swing_high - fib_range * 0.786

    return df


def detect_ict_concepts(df):
    """Detect ICT Smart Money concepts in the data."""
    results = {}
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_price = df['open'].values

    # --- Order Blocks ---
    order_blocks = []
    for i in range(2, len(df)):
        # Bullish OB: bearish candle followed by strong bullish impulse
        if close[i-1] < open_price[i-1] and close[i] > open_price[i]:
            impulse = (close[i] - open_price[i]) / open_price[i]
            if impulse > 0.003:  # 0.3% minimum impulse
                order_blocks.append({
                    'type': 'bullish',
                    'index': i-1,
                    'high': high[i-1],
                    'low': low[i-1],
                    'price': (high[i-1] + low[i-1]) / 2
                })
        # Bearish OB: bullish candle followed by strong bearish impulse
        if close[i-1] > open_price[i-1] and close[i] < open_price[i]:
            impulse = (open_price[i] - close[i]) / open_price[i]
            if impulse > 0.003:
                order_blocks.append({
                    'type': 'bearish',
                    'index': i-1,
                    'high': high[i-1],
                    'low': low[i-1],
                    'price': (high[i-1] + low[i-1]) / 2
                })
    results['order_blocks'] = order_blocks[-5:]  # Last 5

    # --- Fair Value Gaps ---
    fvgs = []
    for i in range(2, len(df)):
        # Bullish FVG: gap between candle 1 high and candle 3 low
        if low[i] > high[i-2]:
            fvgs.append({
                'type': 'bullish',
                'index': i,
                'top': low[i],
                'bottom': high[i-2],
                'midpoint': (low[i] + high[i-2]) / 2
            })
        # Bearish FVG: gap between candle 1 low and candle 3 high
        if high[i] < low[i-2]:
            fvgs.append({
                'type': 'bearish',
                'index': i,
                'top': low[i-2],
                'bottom': high[i],
                'midpoint': (low[i-2] + high[i]) / 2
            })
    results['fvgs'] = fvgs[-5:]  # Last 5

    # --- Market Structure (MSS/BOS) ---
    swing_highs = []
    swing_lows = []
    for i in range(2, len(df) - 2):
        if high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i+1] and high[i] > high[i+2]:
            swing_highs.append({'index': i, 'price': high[i]})
        if low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i+1] and low[i] < low[i+2]:
            swing_lows.append({'index': i, 'price': low[i]})

    mss_bos = []
    if len(swing_highs) >= 2:
        last_sh = swing_highs[-1]
        prev_sh = swing_highs[-2]
        if last_sh['price'] > prev_sh['price']:
            mss_bos.append({'type': 'BOS_bullish', 'price': last_sh['price']})
        elif last_sh['price'] < prev_sh['price']:
            mss_bos.append({'type': 'MSS_bearish', 'price': last_sh['price']})

    if len(swing_lows) >= 2:
        last_sl = swing_lows[-1]
        prev_sl = swing_lows[-2]
        if last_sl['price'] < prev_sl['price']:
            mss_bos.append({'type': 'BOS_bearish', 'price': last_sl['price']})
        elif last_sl['price'] > prev_sl['price']:
            mss_bos.append({'type': 'MSS_bullish', 'price': last_sl['price']})

    results['mss_bos'] = mss_bos
    results['swing_highs'] = swing_highs[-3:]
    results['swing_lows'] = swing_lows[-3:]

    # --- Liquidity Sweeps ---
    sweeps = []
    if len(swing_lows) >= 2 and len(df) > 5:
        prev_low = swing_lows[-2]['price'] if len(swing_lows) >= 2 else None
        recent_low = min(low[-5:])
        recent_close = close[-1]
        if prev_low and recent_low < prev_low and recent_close > prev_low:
            sweeps.append({'type': 'bullish_sweep', 'swept_level': prev_low, 'current': recent_close})

    if len(swing_highs) >= 2 and len(df) > 5:
        prev_high = swing_highs[-2]['price'] if len(swing_highs) >= 2 else None
        recent_high = max(high[-5:])
        recent_close = close[-1]
        if prev_high and recent_high > prev_high and recent_close < prev_high:
            sweeps.append({'type': 'bearish_sweep', 'swept_level': prev_high, 'current': recent_close})

    results['liquidity_sweeps'] = sweeps

    return results


def get_kill_zone():
    """Determine current kill zone based on US Eastern time (DST-aware)."""
    now = datetime.now(timezone.utc)
    # US Eastern: UTC-5 (EST, Nov-Mar) or UTC-4 (EDT, Mar-Nov)
    month, day = now.month, now.day
    if 4 <= month <= 10:
        offset = 4  # EDT (Apr-Oct)
    elif month == 3:
        offset = 4 if day >= 14 else 5  # EDT starts ~2nd Sunday of March
    elif month == 11:
        offset = 5 if day >= 7 else 4   # EST starts ~1st Sunday of November
    else:
        offset = 5  # EST (Dec-Feb)
    et_hour = (now.hour - offset) % 24

    if 19 <= et_hour <= 21:
        return 'Asia', True
    elif 2 <= et_hour <= 5:
        return 'London', True
    elif 7 <= et_hour <= 10:
        return 'New York', True
    else:
        return 'Off-session', False


def analyze_pair(symbol, timeframe='4h', data_source='auto'):
    """
    Full analysis of a single pair.
    Auto-detects forex vs crypto and routes to the correct data source.
    Returns a dict with all indicator values, ICT concepts, and confluence score.
    """
    df = None
    source_used = None
    forex = is_forex_pair(symbol)

    # --- Forex pairs: use Twelve Data ---
    if forex and data_source in ('auto', 'twelvedata'):
        try:
            df = fetch_twelvedata_time_series(symbol, timeframe, outputsize=200)
            source_used = 'TwelveData'
        except Exception as e:
            return {'error': f'Twelve Data fetch failed: {e}'}

    # --- Crypto pairs: use Binance (primary) ---
    if not forex and data_source in ('auto', 'binance'):
        client = get_binance_client()
        if client:
            try:
                interval_map = {
                    '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                    '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w',
                    'daily': '1d', 'weekly': '1w'
                }
                interval = interval_map.get(timeframe.lower(), '4h')
                df = fetch_binance_klines(client, symbol, interval, limit=200)
                source_used = 'Binance'
            except Exception as e:
                if data_source == 'binance':
                    return {'error': f'Binance fetch failed: {e}'}

    # --- Crypto fallback: CoinGecko ---
    if df is None and not forex and data_source in ('auto', 'coingecko'):
        coin_id = SYMBOL_TO_COINGECKO.get(symbol.upper())
        if coin_id:
            try:
                days_map = {'1h': 2, '4h': 14, '1d': 90, '1w': 365}
                days = days_map.get(timeframe.lower(), 14)
                df = fetch_coingecko_ohlc(coin_id, days=days)
                source_used = 'CoinGecko'
            except Exception as e:
                return {'error': f'CoinGecko fetch failed: {e}'}
        else:
            return {'error': f'No data source mapping for {symbol}'}

    if df is None or len(df) < 50:
        return {'error': 'Insufficient data retrieved'}

    # Calculate indicators
    df = calculate_indicators(df)

    # Detect ICT concepts
    ict = detect_ict_concepts(df)

    # Get current values
    last = df.iloc[-1]
    price = last['close']

    # Kill zone
    session, in_kill_zone = get_kill_zone()

    # --- Confluence Scoring ---
    confluences = []

    # 1. ICT Concepts
    recent_obs = [ob for ob in ict['order_blocks'] if ob['index'] > len(df) - 20]
    recent_fvgs = [fvg for fvg in ict['fvgs'] if fvg['index'] > len(df) - 20]

    for ob in recent_obs:
        if ob['type'] == 'bullish' and ob['low'] <= price <= ob['high'] * 1.005:
            confluences.append(f"Bullish order block at ${ob['low']:.2f}-${ob['high']:.2f}")
            break
        elif ob['type'] == 'bearish' and ob['low'] * 0.995 <= price <= ob['high']:
            confluences.append(f"Bearish order block at ${ob['low']:.2f}-${ob['high']:.2f}")
            break

    for fvg in recent_fvgs:
        if fvg['type'] == 'bullish' and fvg['bottom'] <= price <= fvg['top']:
            confluences.append(f"Bullish FVG filled at ${fvg['bottom']:.2f}-${fvg['top']:.2f}")
            break
        elif fvg['type'] == 'bearish' and fvg['bottom'] <= price <= fvg['top']:
            confluences.append(f"Bearish FVG at ${fvg['bottom']:.2f}-${fvg['top']:.2f}")
            break

    for mss in ict['mss_bos']:
        confluences.append(f"{mss['type'].replace('_', ' ')} at ${mss['price']:.2f}")
        break

    for sweep in ict['liquidity_sweeps']:
        confluences.append(f"{sweep['type'].replace('_', ' ').title()} of ${sweep['swept_level']:.2f}")
        break

    # 2. EMA
    if not pd.isna(last.get('ema_21')) and not pd.isna(last.get('ema_50')):
        if price > last['ema_21'] > last['ema_50']:
            confluences.append(f"EMA 21 (${last['ema_21']:.2f}) acting as dynamic support")
        elif price < last['ema_21'] < last['ema_50']:
            confluences.append(f"EMA 21 (${last['ema_21']:.2f}) acting as dynamic resistance")

    # 3. MACD
    if not pd.isna(last.get('macd')) and not pd.isna(last.get('macd_signal')):
        if last['macd'] > last['macd_signal'] and last['macd_histogram'] > 0:
            confluences.append("MACD bullish crossover confirmed")
        elif last['macd'] < last['macd_signal'] and last['macd_histogram'] < 0:
            confluences.append("MACD bearish crossover confirmed")

    # 4. Bollinger Bands
    if not pd.isna(last.get('bb_lower')) and not pd.isna(last.get('bb_upper')):
        if price <= last['bb_lower'] * 1.005:
            confluences.append(f"Price at lower Bollinger Band (${last['bb_lower']:.2f})")
        elif price >= last['bb_upper'] * 0.995:
            confluences.append(f"Price at upper Bollinger Band (${last['bb_upper']:.2f})")
        if last['bb_width'] < df['bb_width'].quantile(0.2):
            confluences.append("Bollinger Band squeeze (low volatility, breakout imminent)")

    # 5. Fibonacci
    fib_618 = df.attrs.get('fib_0.618')
    fib_786 = df.attrs.get('fib_0.786')
    if fib_618 and fib_786:
        if min(fib_618, fib_786) <= price <= max(fib_618, fib_786):
            confluences.append(f"Price in OTE zone (${min(fib_618, fib_786):.2f}-${max(fib_618, fib_786):.2f})")
        else:
            for level_name, level_val in [('0.382', df.attrs.get('fib_0.382')),
                                           ('0.5', df.attrs.get('fib_0.5')),
                                           ('0.618', fib_618)]:
                if level_val and abs(price - level_val) / price < 0.005:
                    confluences.append(f"Price at Fibonacci {level_name} level (${level_val:.2f})")
                    break

    # 6. Kill Zone
    if in_kill_zone:
        confluences.append(f"{session} kill zone active")

    # Determine direction
    bullish_count = sum(1 for c in confluences if any(w in c.lower() for w in ['bullish', 'support', 'lower bollinger', 'bullish sweep']))
    bearish_count = sum(1 for c in confluences if any(w in c.lower() for w in ['bearish', 'resistance', 'upper bollinger', 'bearish sweep']))
    direction = 'LONG' if bullish_count >= bearish_count else 'SHORT'

    # Confidence
    n = len(confluences)
    if n >= 5:
        confidence = 'HIGH'
    elif n >= 3:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    # Trend
    if not pd.isna(last.get('ema_50')) and not pd.isna(last.get('ema_200')):
        if last['ema_50'] > last['ema_200']:
            trend = 'BULLISH'
        elif last['ema_50'] < last['ema_200']:
            trend = 'BEARISH'
        else:
            trend = 'RANGING'
    else:
        trend = 'UNKNOWN'

    result = {
        'symbol': normalize_forex_symbol(symbol) if forex else symbol,
        'market': 'forex' if forex else 'crypto',
        'timeframe': timeframe,
        'price': price,
        'trend': trend,
        'direction': direction,
        'confluences': confluences,
        'confluence_count': n,
        'confidence': confidence,
        'session': session,
        'in_kill_zone': in_kill_zone,
        'source': source_used,
        'ema_21': float(last.get('ema_21', 0)) if not pd.isna(last.get('ema_21')) else None,
        'ema_50': float(last.get('ema_50', 0)) if not pd.isna(last.get('ema_50')) else None,
        'ema_200': float(last.get('ema_200', 0)) if not pd.isna(last.get('ema_200')) else None,
        'macd': float(last.get('macd', 0)) if not pd.isna(last.get('macd')) else None,
        'macd_signal': float(last.get('macd_signal', 0)) if not pd.isna(last.get('macd_signal')) else None,
        'bb_upper': float(last.get('bb_upper', 0)) if not pd.isna(last.get('bb_upper')) else None,
        'bb_lower': float(last.get('bb_lower', 0)) if not pd.isna(last.get('bb_lower')) else None,
        'swing_high': df.attrs.get('swing_high'),
        'swing_low': df.attrs.get('swing_low'),
        'fib_0.618': df.attrs.get('fib_0.618'),
        'fib_0.786': df.attrs.get('fib_0.786'),
        'ict': {
            'order_blocks': len(ict['order_blocks']),
            'fvgs': len(ict['fvgs']),
            'mss_bos': ict['mss_bos'],
            'liquidity_sweeps': ict['liquidity_sweeps']
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    # Add pip info for forex
    if forex:
        result['pip_size'] = get_pip_size(symbol)
        swing_range = df.attrs.get('swing_high', 0) - df.attrs.get('swing_low', 0)
        result['range_pips'] = price_to_pips(symbol, swing_range)

    return result


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='Quivira Market Data Module')
    parser.add_argument('--pair', type=str, help='Trading pair (e.g., BTCUSDT or EUR/USD)')
    parser.add_argument('--timeframe', type=str, default='4h', help='Timeframe (1h, 4h, 1d)')
    parser.add_argument('--scan', action='store_true', help='Scan crypto watchlist pairs')
    parser.add_argument('--scan-forex', action='store_true', help='Scan forex watchlist pairs')
    parser.add_argument('--scan-all', action='store_true', help='Scan both crypto and forex pairs')
    parser.add_argument('--test', action='store_true', help='Test API connectivity')
    parser.add_argument('--price', type=str, help='Get current price (coingecko id or forex pair)')
    parser.add_argument('--global-data', action='store_true', help='Get global market data')
    args = parser.parse_args()

    if args.test:
        print("Testing API connectivity...")
        print()

        # Binance
        client = get_binance_client()
        if client:
            print("  Binance: CONNECTED")
        else:
            print("  Binance: UNAVAILABLE (geo-blocked or network issue)")

        # CoinGecko
        try:
            data = fetch_coingecko_price('bitcoin')
            btc_price = data['bitcoin']['usd']
            print(f"  CoinGecko: CONNECTED (BTC: ${btc_price:,.2f})")
        except Exception as e:
            print(f"  CoinGecko: FAILED ({e})")

        # Twelve Data
        try:
            eur_price = fetch_twelvedata_price('EUR/USD')
            if eur_price:
                print(f"  TwelveData: CONNECTED (EUR/USD: {eur_price:.5f})")
            else:
                print("  TwelveData: NO API KEY (add TWELVEDATA_API_KEY to .env)")
        except Exception as e:
            print(f"  TwelveData: FAILED ({e})")

        session, active = get_kill_zone()
        print(f"  Current session: {session} ({'ACTIVE' if active else 'inactive'})")
        return

    if args.global_data:
        data = fetch_coingecko_global()
        print(json.dumps(data, indent=2))
        return

    if args.price:
        # Auto-detect forex vs crypto
        if is_forex_pair(args.price):
            try:
                p = fetch_twelvedata_price(args.price)
                print(f"{normalize_forex_symbol(args.price)}: {p:.5f}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            data = fetch_coingecko_price(args.price)
            print(json.dumps(data, indent=2))
        return

    if args.pair:
        result = analyze_pair(args.pair, args.timeframe)
        print(json.dumps(result, indent=2, default=str))
        return

    if args.scan or args.scan_all:
        print("=== CRYPTO PAIRS ===")
        core_crypto = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        for pair in core_crypto:
            result = analyze_pair(pair, '4h')
            if 'error' not in result:
                print(f"  {pair}: {result['confidence']} ({result['confluence_count']} confluences) - {result['direction']}")
            else:
                print(f"  {pair}: {result['error']}")

    if args.scan_forex or args.scan_all:
        print("=== FOREX PAIRS ===")
        for pair in FOREX_PAIRS:
            result = analyze_pair(pair, '4h')
            if 'error' not in result:
                pips_info = f" | Range: {result.get('range_pips', 0):.0f} pips" if result.get('range_pips') else ''
                print(f"  {pair}: {result['confidence']} ({result['confluence_count']} confluences) - {result['direction']}{pips_info}")
            else:
                print(f"  {pair}: {result['error']}")

    if not (args.scan or args.scan_forex or args.scan_all):
        parser.print_help()


if __name__ == '__main__':
    main()
