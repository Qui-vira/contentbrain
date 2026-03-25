"""
Forex TA Runner — Standalone technical analysis engine for forex pairs.

Pulls OHLC data from Twelve Data API, runs all indicators and ICT analysis,
saves structured results to forex_ta_summary.json. Zero LLM involvement.

Usage:
    python scripts/forex_ta_runner.py
    python scripts/forex_ta_runner.py --pair EUR/USD
    python scripts/forex_ta_runner.py --timeframe 4h
"""

import os
import sys
import json
import argparse
import time
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
    fetch_twelvedata_time_series,
    calculate_indicators,
    detect_ict_concepts,
    get_kill_zone,
    normalize_forex_symbol,
    get_pip_size,
    price_to_pips,
)

from binance_ta_runner import (
    calculate_rsi,
    calculate_atr,
    calculate_volume_profile,
    detect_support_resistance,
    detect_chart_patterns,
    score_confluences,
    calculate_strength_score,
    determine_trend,
    calculate_trade_levels,
    build_trading_signal,
)

# --- Config ---

FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY',
    'XAU/USD', 'AUD/USD', 'USD/CAD', 'EUR/JPY',
]

TIMEFRAMES = ['1h', '4h', '1d']

# Twelve Data free plan: 8 calls/min. 8 pairs x 3 TFs = 24 calls total.
RATE_LIMIT_DELAY = 8  # seconds between API calls

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'forex_ta_summary.json')


# --- Analyze a single forex pair on a single timeframe ---

def analyze_forex_pair_tf(symbol, timeframe):
    """Full analysis for one forex pair on one timeframe. Returns structured dict."""
    normalized = normalize_forex_symbol(symbol)

    try:
        df = fetch_twelvedata_time_series(normalized, timeframe, outputsize=200)
    except Exception as e:
        return {'error': str(e)}

    if df is None or len(df) < 50:
        return {'error': 'Insufficient data'}

    # Core indicators from market_data.py
    df = calculate_indicators(df)

    # Additional indicators
    df['rsi'] = calculate_rsi(df)
    df['atr'] = calculate_atr(df)

    # ICT concepts
    ict = detect_ict_concepts(df)

    # Volume profile (forex has volume=0, handled gracefully by vol_avg > 0 guard)
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

    # Fib levels
    fib_levels = {}
    for key in ['fib_0.236', 'fib_0.382', 'fib_0.5', 'fib_0.618', 'fib_0.786']:
        val = df.attrs.get(key)
        if val is not None:
            fib_levels[key] = round(float(val), 6)

    # Pip info
    pip_size = get_pip_size(normalized)
    swing_range = df.attrs.get('swing_high', 0) - df.attrs.get('swing_low', 0)
    range_pips = price_to_pips(normalized, swing_range)

    return {
        'pair': normalized,
        'timeframe': timeframe,
        'current_price': round(price, 6),
        'market_type': 'FOREX',
        'trend': trend,
        'assessment': assessment,
        'strength_score': strength,
        'pip_size': pip_size,
        'range_pips': round(range_pips, 1),

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
            'swing_highs': ict.get('swing_highs', [])[-3:],
            'swing_lows': ict.get('swing_lows', [])[-3:],
        },

        # Chart patterns
        'patterns': patterns,

        # Confluence
        'confluence': confluence_result,
    }


# --- Main Runner ---

def run(pairs_override=None, timeframes_override=None):
    """Run full forex TA scan and save to JSON."""
    start_time = time.time()

    pairs = pairs_override or FOREX_PAIRS
    timeframes = timeframes_override or TIMEFRAMES

    session, in_kz = get_kill_zone()
    print(f"Session: {session} ({'active' if in_kz else 'off-session'})")
    print(f"Scanning {len(pairs)} forex pairs x {len(timeframes)} timeframes "
          f"({len(pairs) * len(timeframes)} calls, ~{len(pairs) * len(timeframes) * RATE_LIMIT_DELAY // 60} min)")

    results = []
    errors = []
    total_calls = len(pairs) * len(timeframes)
    call_num = 0

    for pair in pairs:
        for tf in timeframes:
            call_num += 1
            sys.stdout.write(f"\r  [{call_num}/{total_calls}] {pair} {tf}...")
            sys.stdout.flush()

            result = analyze_forex_pair_tf(pair, tf)

            if 'error' in result:
                errors.append(f"{pair} {tf}: {result['error']}")
            else:
                results.append(result)

            # Rate limit (skip delay on last call)
            if call_num < total_calls:
                time.sleep(RATE_LIMIT_DELAY)

    # Build output
    output = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'session': session,
        'in_kill_zone': in_kz,
        'pairs_scanned': len(pairs),
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


def load_forex_signals(max_age_minutes=60):
    """Read forex_ta_summary.json, check freshness, filter 3+ confluences, return signal dicts."""
    output_path = os.path.abspath(OUTPUT_FILE)
    if not os.path.exists(output_path):
        print(f"Forex TA summary not found: {output_path}")
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
                print(f"Forex TA data is {age_minutes:.0f} minutes old (max {max_age_minutes}). "
                      f"Run forex_ta_runner.py first.")
                return []
        except (ValueError, TypeError):
            pass

    results = data.get('results', [])
    signals = []

    for result in results:
        confluence = result.get('confluence', {})
        min_count = confluence.get('min_count', 4)
        if confluence.get('confluence_count', 0) < min_count:
            continue
        if confluence.get('direction') == 'NEUTRAL':
            continue
        if confluence.get('contradiction'):
            continue

        signal = build_trading_signal(result)
        if signal:
            signal['generated_at'] = generated_at
            signal['market_type'] = 'FOREX'
            signals.append(signal)

    print(f"Loaded {len(signals)} forex signals from TA summary ({len(results)} total analyses)")
    return signals


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description='Forex TA Runner - Standalone technical analysis via Twelve Data')
    parser.add_argument('--pair', type=str, help='Analyze a single pair (e.g., EUR/USD)')
    parser.add_argument('--timeframe', type=str, help='Override timeframes (comma-separated, e.g., 1h,4h,1d)')
    args = parser.parse_args()

    pairs = [normalize_forex_symbol(args.pair)] if args.pair else None
    timeframes = args.timeframe.split(',') if args.timeframe else None

    run(pairs_override=pairs, timeframes_override=timeframes)


if __name__ == '__main__':
    main()
