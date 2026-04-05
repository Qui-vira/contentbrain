---
voice: see 08-Templates/voice-rules.md
description: "Autonomous Trading Signal Pipeline. Scans crypto + forex, filters for high-confluence setups, sends to approval channel, logs to tracker. Triggers: '/produce-signals', 'run signal pipeline', 'scan and send signals', 'trading pipeline'"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch"]
---

# SKILL: /produce-signals — Autonomous Trading Signal Pipeline

## ROLE
You are the Signal Pipeline Orchestrator. When Big Quiv runs /produce-signals, you execute the full trading signal pipeline from market scan to signal distribution without stopping. Scan, analyze, filter, send, log. One command.

## TRIGGER
- `/produce-signals` — run full crypto + forex pipeline
- `/produce-signals crypto` — crypto only (skip forex)
- `/produce-signals forex` — forex only (skip crypto)
- `run signal pipeline` / `scan and send signals` / `trading pipeline`

## CONTEXT FILES TO READ FIRST
- CLAUDE.md (identity, rules)
- 10-Niche-Knowledge/crypto-trading/pair-watchlist.md (which pairs to scan)
- 10-Niche-Knowledge/crypto-trading/risk-management-rules.md (drawdown thresholds)
- 07-Analytics/signal-performance/signals-log.md (active signals, win rate)

---

## THE PIPELINE (execute in order)

### STEP 1: DRAWDOWN CHECK

1. Read `07-Analytics/signal-performance/signals-log.md`.
2. Calculate current drawdown from peak capital.
3. If drawdown >= 5%: **STOP. Do not scan. Do not send signals.**
   - Output: "SYSTEM PAUSED: [X]% drawdown. Signal generation halted until manual review."
   - This is the ONLY hard stop in the pipeline.
4. If drawdown >= 3%: Log warning, continue but reduce position size note to 0.5%.
5. If drawdown < 3%: Proceed normally.

### STEP 2: SCAN MARKETS

Run scans based on mode:

**Crypto (default or `crypto`):**
```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/binance_ta_runner.py
```
- Output: `binance_ta_summary.json`
- If script fails: check if cached file exists and is < 30 minutes old. Use with staleness warning. If > 30 min, skip crypto. Log: "FALLBACK: Binance API unavailable. Crypto scan skipped."

**Forex (default or `forex`):**
```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/forex_ta_runner.py
```
- Output: `forex_ta_summary.json`
- If script fails: check cached file age. Same 30-minute rule. Log: "FALLBACK: TwelveData API unavailable. Forex scan skipped."

**Never generate signals from stale data (> 30 minutes). Stale signals are dangerous.**

### STEP 3: ANALYZE & FILTER

1. Read `binance_ta_summary.json` and/or `forex_ta_summary.json`.
2. Run `/technical-analyst` logic:
   - Filter for setups with 3+ indicator confluences.
   - For each qualifying setup, generate a full signal: pair, direction, entry, SL, TP1/TP2/TP3, confidence level, confluence details.
3. Check against active signals in signals-log.md:
   - Do NOT send a signal for a pair that already has an ACTIVE signal in the same direction.
   - If a pair has an active signal in the OPPOSITE direction, flag it as a potential reversal but still require approval.
4. Respect `AUTO_SIGNAL_CAP` from .env (default: 3 signals per run).

**Output:** List of qualifying signals with full details.

### STEP 4: SEND TO APPROVAL

1. Run `/send-signals` logic:
   ```bash
   cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/polymarket_bot.py --send-ta
   ```
2. If Telegram Bot API fails (F8):
   - Save each signal to `06-Drafts/[date]-manual-telegram-signal.md` with `status: MANUAL_REQUIRED`.
   - Display all signals in terminal output for manual copy-paste.
   - Log: "FALLBACK: Telegram Bot unavailable. [N] signals saved for manual send."
3. Do NOT send to public channels. All signals go to approval channel first.

### STEP 5: LOG

1. Log each sent signal to `07-Analytics/signal-performance/signals-log.md`:
   - Pair, Direction, Entry, SL, TP1/TP2/TP3, Confidence, Confluence count, Timestamp, Status: ACTIVE
2. Report total signals found, sent, and any skipped (duplicate pair, stale data, API down).

---

## OUTPUT FORMAT

```
SIGNAL PIPELINE — [DATE] [TIME]
---

Scans completed:
- Crypto: [N] pairs scanned | [N] analyses | [time elapsed]
- Forex: [N] pairs scanned | [N] analyses | [time elapsed]

Signals found: [N] (3+ confluences)
Signals sent to approval: [N]
Signals skipped: [N] (reason per skip)

Drawdown status: [OK / WARNING / PAUSED]
Active signals: [N] total

### Qualifying Signals
| # | Pair | Direction | Entry | SL | TP1 | TP2 | TP3 | Confidence | Confluences |
|---|------|-----------|-------|----|-----|-----|-----|------------|-------------|

### Next Steps
- [ ] Check Telegram bot DM to approve/reject each signal
- [ ] Approved signals auto-distribute to Hustler's Krib + X
---
```

## RULES
1. NEVER send signals from data older than 30 minutes.
2. NEVER send to public channels without approval step.
3. NEVER generate signals during a 5%+ drawdown pause.
4. If both crypto and forex scans fail, report and exit. Do not fabricate signals.
5. Respect AUTO_SIGNAL_CAP per run.
6. Every signal must have a defined SL. No signal without risk management.
