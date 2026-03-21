"""
Signal Monitor — checks active signals against current market prices.

Parses signals-log.md for ACTIVE signals, fetches current prices via CoinGecko,
and reports which signals have hit SL or TP levels.

Usage:
    python scripts/signal_monitor.py --check        # Check all active signals
    python scripts/signal_monitor.py --summary      # One-line-per-signal summary
    python scripts/signal_monitor.py --json         # Output as JSON
"""

import os
import sys
import re
import json
import argparse

# Add scripts dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from market_data import (
    fetch_coingecko_price, SYMBOL_TO_COINGECKO,
    is_forex_pair, fetch_twelvedata_price, normalize_forex_symbol,
    get_pip_size, price_to_pips
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Path to signals log
SIGNALS_LOG = os.path.join(
    os.path.dirname(__file__), '..', '07-Analytics', 'signal-performance', 'signals-log.md'
)


def parse_signals_log(filepath=None):
    """Parse the signals-log.md markdown table for signals with a given status."""
    filepath = filepath or SIGNALS_LOG

    if not os.path.exists(filepath):
        print(f"ERROR: signals-log.md not found at {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    signals = []
    in_table = False

    for line in content.split('\n'):
        line = line.strip()

        # Detect table rows (starts with | and has multiple columns)
        if line.startswith('|') and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]  # Strip outer pipes

            # Skip header row
            if cells and cells[0] == '#':
                in_table = True
                continue

            if in_table and len(cells) >= 14:
                try:
                    signal = {
                        'number': cells[0].strip(),
                        'date': cells[1].strip(),
                        'pair': cells[2].strip(),
                        'direction': cells[3].strip(),
                        'timeframe': cells[4].strip(),
                        'entry': parse_price(cells[5]),
                        'sl': parse_price(cells[6]),
                        'tp1': parse_price(cells[7]),
                        'tp2': parse_price(cells[8]),
                        'tp3': parse_price(cells[9]),
                        'confluence': cells[10].strip(),
                        'confidence': cells[11].strip(),
                        'status': cells[12].strip(),
                        'result': cells[13].strip(),
                    }
                    if len(cells) > 14:
                        signal['r_achieved'] = cells[14].strip()
                    signals.append(signal)
                except (IndexError, ValueError):
                    continue

    return signals


def parse_price(text):
    """Extract numeric price from text like '$84,250.00' or '84250'."""
    text = text.strip().replace('$', '').replace(',', '')
    try:
        return float(text)
    except ValueError:
        return None


def get_active_signals(filepath=None):
    """Return only ACTIVE signals (and TP1 HIT, TP2 HIT — still live)."""
    all_signals = parse_signals_log(filepath)
    active_statuses = {'ACTIVE', 'TP1 HIT', 'TP2 HIT'}
    return [s for s in all_signals if s['status'].upper() in active_statuses]


def pair_to_coingecko_id(pair):
    """Convert pair like 'BTC/USDT' or 'BTCUSDT' to CoinGecko ID."""
    normalized = pair.upper().replace('/', '')
    return SYMBOL_TO_COINGECKO.get(normalized)


def check_signal(signal, current_price):
    """
    Check if a signal has hit SL or any TP level.
    Returns a status dict with hit levels and P&L info.
    """
    direction = signal['direction'].upper()
    entry = signal['entry']
    sl = signal['sl']
    tp1 = signal['tp1']
    tp2 = signal['tp2']
    tp3 = signal['tp3']

    if entry is None or current_price is None:
        return {'status': 'ERROR', 'message': 'Missing price data'}

    result = {
        'pair': signal['pair'],
        'direction': direction,
        'entry': entry,
        'current_price': current_price,
        'sl': sl,
        'tp1': tp1,
        'tp2': tp2,
        'tp3': tp3,
        'current_status': signal['status'],
        'hits': [],
    }

    if direction == 'LONG':
        # LONG: price goes up = profit, price goes down = loss
        if sl and current_price <= sl:
            result['hits'].append('SL HIT')
        if tp1 and current_price >= tp1:
            result['hits'].append('TP1 HIT')
        if tp2 and current_price >= tp2:
            result['hits'].append('TP2 HIT')
        if tp3 and current_price >= tp3:
            result['hits'].append('TP3 HIT')

        # P&L percentage
        result['pnl_pct'] = ((current_price - entry) / entry) * 100

    elif direction == 'SHORT':
        # SHORT: price goes down = profit, price goes up = loss (inverted)
        if sl and current_price >= sl:
            result['hits'].append('SL HIT')
        if tp1 and current_price <= tp1:
            result['hits'].append('TP1 HIT')
        if tp2 and current_price <= tp2:
            result['hits'].append('TP2 HIT')
        if tp3 and current_price <= tp3:
            result['hits'].append('TP3 HIT')

        # P&L percentage (inverted for shorts)
        result['pnl_pct'] = ((entry - current_price) / entry) * 100

    # Determine recommended new status
    if 'SL HIT' in result['hits']:
        result['recommended_status'] = 'STOPPED OUT'
    elif 'TP3 HIT' in result['hits']:
        result['recommended_status'] = 'TP3 HIT'
    elif 'TP2 HIT' in result['hits']:
        result['recommended_status'] = 'TP2 HIT'
    elif 'TP1 HIT' in result['hits']:
        result['recommended_status'] = 'TP1 HIT'
    else:
        result['recommended_status'] = signal['status']

    return result


def format_check_result(result):
    """Format a single check result for display."""
    pair = result['pair']
    direction = result['direction']
    entry = result['entry']
    current = result['current_price']
    pnl = result.get('pnl_pct', 0)
    pnl_str = f"+{pnl:.2f}%" if pnl >= 0 else f"{pnl:.2f}%"
    hits = ', '.join(result['hits']) if result['hits'] else 'No hits'

    lines = [
        f"  {pair} ({direction})",
        f"    Entry: ${entry:,.2f} -> Current: ${current:,.2f} ({pnl_str})",
        f"    SL: ${result['sl']:,.2f} | TP1: ${result['tp1']:,.2f} | TP2: ${result['tp2']:,.2f} | TP3: ${result['tp3']:,.2f}" if all(v is not None for v in [result['sl'], result['tp1'], result['tp2'], result['tp3']]) else "    (some levels missing)",
        f"    Status: {result['current_status']} -> {hits}",
    ]

    if result['recommended_status'] != result['current_status']:
        lines.append(f"    !! RECOMMEND UPDATE: {result['current_status']} -> {result['recommended_status']}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Monitor active trading signals')
    parser.add_argument('--check', action='store_true', help='Check all active signals against current prices')
    parser.add_argument('--summary', action='store_true', help='One-line summary per signal')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--file', type=str, default=None, help='Path to signals-log.md (override default)')
    args = parser.parse_args()

    if not (args.check or args.summary or args.json):
        args.check = True  # Default to --check

    active = get_active_signals(args.file)

    if not active:
        print("No active signals found in signals-log.md")
        return

    print(f"\nChecking {len(active)} active signal(s)...\n")

    results = []
    for signal in active:
        pair = signal['pair']
        current_price = None

        if is_forex_pair(pair):
            # Forex: use Twelve Data
            try:
                current_price = fetch_twelvedata_price(pair)
            except Exception as e:
                print(f"  ERROR fetching forex price for {pair}: {e}")
                continue
        else:
            # Crypto: use CoinGecko
            coin_id = pair_to_coingecko_id(pair)
            if not coin_id:
                print(f"  SKIP: No price source for {pair}")
                continue
            try:
                price_data = fetch_coingecko_price(coin_id)
                current_price = price_data[coin_id]['usd']
            except Exception as e:
                print(f"  ERROR fetching price for {pair}: {e}")
                continue

        if current_price is None:
            continue

        result = check_signal(signal, current_price)
        # Add pip info for forex
        if is_forex_pair(pair) and result.get('entry'):
            result['pnl_pips'] = price_to_pips(pair, current_price - result['entry'])
        results.append(result)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    if args.summary:
        for r in results:
            pnl = r.get('pnl_pct', 0)
            pnl_str = f"+{pnl:.2f}%" if pnl >= 0 else f"{pnl:.2f}%"
            hits = ', '.join(r['hits']) if r['hits'] else 'holding'
            print(f"  {r['pair']} {r['direction']} | {pnl_str} | {hits}")
        return

    # Full check output
    for r in results:
        print(format_check_result(r))
        print()

    # Summary
    hit_signals = [r for r in results if r['hits']]
    if hit_signals:
        print(f"ACTION NEEDED: {len(hit_signals)} signal(s) hit a level. Use /signal-tracker to update.")
    else:
        print("All signals within range. No updates needed.")


if __name__ == '__main__':
    main()
