---
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
