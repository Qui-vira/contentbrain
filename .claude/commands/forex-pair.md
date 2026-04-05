---
voice: see 08-Templates/voice-rules.md
description: "Scan a single forex pair across all timeframes. Usage: /forex-pair EUR/USD. Triggers: '/forex-pair [PAIR]', 'scan EUR/USD', 'scan GBP/JPY'"
allowed-tools: ["Bash", "Read"]
---

# /forex-pair — Single Forex Pair Scan

Scan one forex pair across all timeframes (1h, 4h, 1d).

**Usage:** `/forex-pair EUR/USD` or `/forex-pair XAU/USD`

Extract the pair argument from the user's message. If no pair is given, ask for one.

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/forex_ta_runner.py --pair $PAIR
```

Replace `$PAIR` with the pair from the user's message (e.g., `EUR/USD`, `GBP/JPY`). Keep the slash format.

After the scan completes:
1. Read `forex_ta_summary.json` and filter for the requested pair
2. Report: pair, timeframes analyzed, signals found (3+ confluences), strength scores
3. If a signal was found, show a brief summary (direction, strength, confluence count)
4. Ask: "Want me to send this signal for approval? (use /send-signals)"
