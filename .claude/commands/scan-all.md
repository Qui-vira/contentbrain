---
description: "Run full crypto TA scan — all pairs, all timeframes. Generates binance_ta_summary.json. Triggers: '/scan-all', 'run full scan', 'scan all crypto'"
allowed-tools: ["Bash", "Read"]
---

# /scan-all — Full Crypto TA Scan

Run the Binance TA runner to scan all watchlist pairs across all timeframes (1h, 4h, 1d).

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/binance_ta_runner.py
```

After the scan completes:
1. Read `binance_ta_summary.json` to check how many results and signals were generated
2. Report: pairs scanned, total analyses, signals found (3+ confluences), errors, and time elapsed
3. If signals were found, ask: "Want me to send these signals for approval? (use /send-signals)"
