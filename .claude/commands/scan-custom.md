---
description: "Scan a crypto pair on specific timeframes. Usage: /scan-custom ETHUSDT 1h,4h. Triggers: '/scan-custom [PAIR] [TIMEFRAMES]'"
allowed-tools: ["Bash", "Read"]
---

# /scan-custom — Custom Pair + Timeframe Crypto TA Scan

Scan a specific crypto pair on specific timeframes.

**Usage:** `/scan-custom ETHUSDT 1h,4h` or `/scan-custom BTCUSDT 4h`

Extract the pair and timeframe arguments from the user's message. If either is missing, ask for it.

- First argument: pair (e.g., `BTCUSDT`, `SOLUSDT`) — uppercase, no slashes
- Second argument: timeframes — comma-separated, no spaces (e.g., `1h,4h,1d` or just `4h`)

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/binance_ta_runner.py --pair $PAIR --timeframe $TIMEFRAMES
```

Replace `$PAIR` and `$TIMEFRAMES` with the user's arguments.

After the scan completes:
1. Read `binance_ta_summary.json` and filter for the requested pair/timeframes
2. Report: pair, timeframes analyzed, signals found (3+ confluences), strength scores
3. If a signal was found, show a brief summary (direction, strength, confluence count)
4. Ask: "Want me to send this signal for approval? (use /send-signals)"
