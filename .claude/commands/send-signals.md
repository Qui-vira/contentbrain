---
voice: see 08-Templates/voice-rules.md
description: "Send qualifying crypto TA signals to Telegram approval channel. Triggers: '/send-signals', 'send signals for approval', 'send ta signals'"
allowed-tools: ["Bash"]
---

# /send-signals — Send TA Signals for Approval

Send all qualifying trading signals (3+ confluences) from the latest TA scan to the Telegram approval channel. You must approve each signal before it distributes to Hustler's Krib and X/Twitter.

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/polymarket_bot.py --send-ta
```

After running:
1. Report how many signals were sent to the approval channel
2. Remind the user to check their Telegram bot DM to approve or reject each signal
3. If no signals were sent, suggest running `/scan-all` first to generate fresh data

## FALLBACK F8: Telegram Bot API / polymarket_bot.py unavailable

If the script fails (Telegram API down, bot not running, connection error):
1. Read `binance_ta_summary.json` directly to find qualifying signals (3+ confluences).
2. For each qualifying signal, save to `06-Drafts/[date]-manual-telegram-signal.md`:
   ```
   ---
   status: MANUAL_REQUIRED
   platform: Telegram
   content_type: Signal
   reason: Telegram Bot API unavailable
   ---

   [Full formatted signal: pair, direction, entry, SL, TP1/TP2/TP3, confluence details]
   ```
3. Log: "FALLBACK: Telegram Bot unavailable. [N] signals saved to 06-Drafts/ for manual send."
4. Show all signals in the terminal output so the user can copy-paste to Telegram manually.
5. Do NOT mark signals as sent or approved — they need manual handling.
