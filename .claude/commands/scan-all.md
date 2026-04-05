---
voice: see 08-Templates/voice-rules.md
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

## FALLBACK F10: Binance API unavailable

If the runner script fails (Binance API down, connection timeout, rate limit):
1. Check if `binance_ta_summary.json` already exists.
2. Read its `generated_at` timestamp.
3. If the file is less than 30 minutes old:
   - Log: "FALLBACK: Binance API unavailable. Using cached scan from [timestamp] ([N] minutes old)."
   - Use the cached data with a staleness warning on every signal: `⚠️ Based on cached data ([N]min old)`
4. If the file is older than 30 minutes:
   - Log: "FALLBACK: Binance API unavailable. Cached data too stale ([N] minutes). Scan skipped."
   - Do NOT generate signals from stale data. Stale signals are dangerous.
   - Suggest: "Try again in a few minutes, or check https://www.binance.com/en/trade for manual analysis."
5. Never silently use stale data for trading signals.
