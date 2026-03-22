---
description: "Run full forex TA scan — all pairs, all timeframes. Generates forex_ta_summary.json. Triggers: '/forex-scan', 'scan forex', 'forex scan all'"
allowed-tools: ["Bash", "Read"]
---

# /forex-scan — Full Forex TA Scan

Run a full technical analysis scan across all 8 forex pairs (EUR/USD, GBP/USD, USD/JPY, GBP/JPY, XAU/USD, AUD/USD, USD/CAD, EUR/JPY) on all timeframes (1h, 4h, 1d).

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/forex_ta_runner.py
```

After the scan completes:
1. Read `forex_ta_summary.json` and summarize the results
2. Report: total analyses run, signals found (3+ confluences), strongest setups
3. If signals were found, show top 3 by strength (pair, direction, strength, confluence count)
4. Ask: "Want me to send these signals for approval? (use /send-signals)"
