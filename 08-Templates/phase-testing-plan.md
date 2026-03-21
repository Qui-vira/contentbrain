# Phase 4-6 Testing Plan

> End-to-end test cases for the Quivira Technical Analyst System.

---

## Test 1: Single Pair Analysis

**Command:** `/technical-analyst analyze BTC/USDT on 4H`

**Expected:**
- Fetches 200 candles from Binance (or CoinGecko fallback)
- Calculates EMA 21/50/200, MACD, Bollinger Bands, Fibonacci
- Detects ICT concepts (order blocks, FVGs, MSS/BOS, liquidity sweeps)
- Returns confluence count, confidence level, and direction
- Outputs formatted signal if confidence >= MEDIUM

**Verify:**
- [ ] No API errors
- [ ] All indicator values populated
- [ ] Confluence count matches listed confluences
- [ ] Direction aligns with bullish/bearish confluence majority

---

## Test 2: Scan Mode

**Command:** `/technical-analyst scan all pairs`

**Expected:**
- Scans BTC, ETH, SOL (core pairs) on 4H
- Returns ranked results by confluence count
- Highlights any HIGH confidence setups

**Verify:**
- [ ] All 3 pairs return results (no errors)
- [ ] Results sorted by confidence/confluence
- [ ] Each pair shows direction + confluence count

---

## Test 3: Webhook → Fetch Pipeline

**Steps:**
1. Send test POST via curl:
```bash
curl -X POST "https://iwiqldudksmbbjxpqgsj.supabase.co/functions/v1/tradingview-webhook?secret=YOUR_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "ETHUSDT",
    "timeframe": "240",
    "direction": "LONG",
    "alert_name": "EMA Cross",
    "alert_message": "ETH bullish EMA crossover on 4H"
  }'
```

2. Fetch the alert:
```bash
python scripts/fetch_alerts.py
```

3. Mark as processed:
```bash
python scripts/fetch_alerts.py --mark-processed <UUID_FROM_STEP_2>
```

**Verify:**
- [ ] curl returns `{"success": true, "id": "..."}`
- [ ] fetch_alerts.py shows the alert as PENDING
- [ ] After marking processed, alert no longer appears in default view
- [ ] `--all` flag still shows the processed alert

---

## Test 4: Signal Approval → Content Pipeline

**Steps:**
1. Generate signal: `/technical-analyst analyze SOL/USDT on 1H`
2. Approve the signal (user says "approved")
3. /signal-tracker logs it to signals-log.md
4. /ghostwriter creates content from the signal

**Verify:**
- [ ] Signal appears in signals-log.md with ACTIVE status
- [ ] All fields populated (entry, SL, TP1-3)
- [ ] /ghostwriter produces tweet/thread from the signal data

---

## Test 5: Signal Monitor + Performance

**Steps:**
1. Ensure at least 1 ACTIVE signal exists in signals-log.md
2. Run: `python scripts/signal_monitor.py --check`
3. Run: `/signal-tracker show performance`

**Verify:**
- [ ] signal_monitor.py fetches current price for the pair
- [ ] Correctly identifies if SL/TP levels have been hit
- [ ] P&L percentage is accurate (positive for profitable direction)
- [ ] SHORT signals use inverted logic (price down = profit)
- [ ] /signal-tracker performance stats match the log data

---

## Test 6: Market Report

**Command:** `/market-report generate daily report`

**Expected:**
- Pulls global market data from CoinGecko
- Includes BTC/ETH/SOL price + 24h change
- Shows trending coins
- Integrates any active signals or recent setups

**Verify:**
- [ ] No API errors
- [ ] All data sections populated
- [ ] Report is formatted and ready for content use

---

## Quick Validation Commands

```bash
# API connectivity
python scripts/market_data.py --test

# Webhook pipeline
curl -X POST "WEBHOOK_URL?secret=SECRET" -H "Content-Type: application/json" -d '{"pair":"BTCUSDT","direction":"LONG","alert_name":"Test"}'
python scripts/fetch_alerts.py

# Signal monitor
python scripts/signal_monitor.py --check

# Fetch alerts as JSON
python scripts/fetch_alerts.py --json
```
