---
description: "Send qualifying crypto TA signals directly — skip approval, distribute immediately. Triggers: '/send-signals-direct', 'send signals direct', 'distribute signals now'"
allowed-tools: ["Bash"]
---

# /send-signals-direct — Direct Signal Distribution (Skip Approval)

Send all qualifying trading signals (3+ confluences) directly to Hustler's Krib and X/Twitter draft — **skipping the approval step**.

**Warning:** This bypasses the approval flow. Signals will be distributed immediately without review.

Confirm with the user before running: "This will distribute signals directly without approval. Proceed?"

If confirmed:

```bash
cd C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain && python scripts/polymarket_bot.py --send-ta --direct
```

After running:
1. Report how many signals were distributed
2. List which pairs/directions were sent
3. If no signals were sent, suggest running `/scan-all` first to generate fresh data
