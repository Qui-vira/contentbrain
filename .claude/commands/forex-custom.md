---
voice: see 08-Templates/voice-rules.md
description: "Scan a forex pair on specific timeframes. Usage: /forex-custom EUR/USD 1h,4h. Triggers: '/forex-custom [PAIR] [TIMEFRAMES]'"
allowed-tools: ["Bash", "Read"]
---

# /forex-custom — Custom Forex Pair + Timeframe Scan

Scan a specific forex pair on specific timeframes.

**Usage:** `/forex-custom EUR/USD 1h,4h` or `/forex-custom XAU/USD 4h`

Extract the pair and timeframe arguments from the user's message. If either is missing, ask for it.

- First argument: pair (e.g., `EUR/USD`, `GBP/JPY`) — keep the slash format
- Second argument: timeframes — comma-separated, no spaces (e.g., `1h,4h,1d` or just `4h`)

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/forex_ta_runner.py --pair $PAIR --timeframe $TIMEFRAMES
```

Replace `$PAIR` and `$TIMEFRAMES` with the user's arguments.

After the scan completes:
1. Read `forex_ta_summary.json` and filter for the requested pair/timeframes
2. Report: pair, timeframes analyzed, signals found (3+ confluences), strength scores
3. If a signal was found, show a brief summary (direction, strength, confluence count)
4. Ask: "Want me to send this signal for approval? (use /send-signals)"
