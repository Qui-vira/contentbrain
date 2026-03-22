---
description: "Scan a single crypto pair across all timeframes. Usage: /scan-pair BTCUSDT. Triggers: '/scan-pair [PAIR]', 'scan BTC', 'scan ETHUSDT'"
allowed-tools: ["Bash", "Read"]
---

# /scan-pair — Single Pair Crypto TA Scan

Scan one crypto pair across all timeframes (1h, 4h, 1d).

**Usage:** `/scan-pair BTCUSDT` or `/scan-pair ETHUSDT`

Extract the pair argument from the user's message. If no pair is given, ask for one.

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/binance_ta_runner.py --pair $PAIR
```

Replace `$PAIR` with the pair from the user's message (e.g., `BTCUSDT`, `SOLUSDT`). The pair should be uppercase with no slashes.

After the scan completes:
1. Read `binance_ta_summary.json` and filter for the requested pair
2. Report: pair, timeframes analyzed, signals found (3+ confluences), strength scores
3. If a signal was found, show a brief summary (direction, strength, confluence count)
4. Ask: "Want me to send this signal for approval? (use /send-signals)"
