# Polymarket Bot — Setup & Operations Guide

## Overview

The Polymarket Signal Bot scans prediction markets every hour, applies multi-factor analysis, and distributes high-edge signals through a Telegram approval flow before posting to Hustler's Krib, dedicated Poly channel, and X/Twitter.

---

## 1. Environment Variables

Add these to your `.env` file:

```
# Already configured:
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<hustlers-krib-chat-id>

# New — add these:
TELEGRAM_POLY_CHANNEL_ID=<dedicated-polymarket-channel-id>
TELEGRAM_APPROVAL_CHANNEL_ID=<private-approval-channel-id>
```

### How to get channel IDs:
1. Create two new Telegram channels/groups:
   - **Polymarket Signals** (public or private, for subscribers)
   - **Signal Approval** (private, just you + the bot)
2. Add your bot to both channels as admin
3. Send a message in each channel
4. Run: `curl "https://api.telegram.org/bot<TOKEN>/getUpdates"` to find the chat IDs

---

## 2. Dependencies

Only `requests` is needed (already installed if other scripts work):

```bash
pip install requests python-dotenv
```

---

## 3. Testing

### Test API connectivity:
```bash
python scripts/polymarket_scanner.py --test
```

### Test Telegram bot:
```bash
python scripts/polymarket_bot.py --test
```

### View top markets:
```bash
python scripts/polymarket_scanner.py --top 10
```

### Run a test scan:
```bash
python scripts/polymarket_scanner.py --scan
```

### Analyze a specific market:
```bash
python scripts/polymarket_scanner.py --market <condition_id_or_slug>
```

---

## 4. Daily Operations

### Manual scan + approve flow:
```bash
# 1. Scan for signals
python scripts/polymarket_scanner.py --scan --json > /tmp/signals.json

# 2. Send to approval channel
python scripts/polymarket_bot.py --send-signal /tmp/signals.json

# 3. Approve/reject via Telegram buttons or:
python scripts/polymarket_bot.py --approve <message_id>

# 4. Check active signals
python scripts/polymarket_tracker.py --status

# 5. Auto-resolve closed markets
python scripts/polymarket_tracker.py --resolve
```

### Automated hourly scan:
```bash
python scripts/polymarket_cron.py
```

---

## 5. Scheduling (Windows Task Scheduler)

### Create a scheduled task:
1. Open Task Scheduler
2. Create Basic Task: "Polymarket Hourly Scan"
3. Trigger: Daily, repeat every 1 hour
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain\scripts\polymarket_cron.py`
   - Start in: `C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain`

### Or use a batch file:
Create `run_polymarket_scan.bat`:
```batch
@echo off
cd /d C:\Users\Bigquiv\OneDrive\Desktop\ContentBrain
python scripts\polymarket_cron.py >> logs\polymarket-cron.log 2>&1
```

---

## 6. Signal Filters

Default filters (configurable in `polymarket_scanner.py`):

| Filter | Value | Rationale |
|--------|-------|-----------|
| Min 24h Volume | $50,000 | Ensures liquidity |
| Resolution Window | 30 days | Keeps signals actionable |
| Exclude Odds | <10% or >90% | Extreme odds = no edge |
| Min Liquidity | $10,000 | Order book depth |
| Min Edge | 10% | Model vs market difference |
| Min Confidence | 65/100 | Multi-factor threshold |

---

## 7. Multi-Factor Analysis

| Factor | Weight | Method |
|--------|--------|--------|
| Odds Movement | 25% | 7-day price slope + reversal detection |
| Volume Surge | 20% | 24h vs average daily volume ratio |
| News Catalyst | 20% | Keyword scoring for time-sensitive events |
| Sentiment | 15% | Market lean + volume-weighted conviction |
| Historical Patterns | 20% | Category base rates + resolution proximity |

---

## 8. Distribution Flow

```
Scanner finds signal (edge >= 10%, confidence >= 65)
    → Format signal card
    → Send to APPROVAL channel (private)
    → User approves (button or reply)
    → Distribute to:
        ├── Hustler's Krib (TELEGRAM_CHAT_ID)
        ├── Poly Channel (TELEGRAM_POLY_CHANNEL_ID)
        ├── X/Twitter draft (06-Drafts/polymarket/)
        └── Signal tracker (polymarket-signals-log.md)
```

---

## 9. Performance Tracking

```bash
# View performance metrics
python scripts/polymarket_tracker.py --performance

# Generate weekly report
python scripts/polymarket_tracker.py --weekly

# Auto-resolve closed markets
python scripts/polymarket_tracker.py --resolve
```

Reports saved to: `07-Analytics/polymarket/`

---

## 10. Integration with Other Commands

| Command | Integration |
|---------|-------------|
| `/ghostwriter` | Auto-generates tweet drafts from approved signals |
| `/signal-tracker` | Logs signals with `source: polymarket` |
| `/data-analyst` | Weekly performance data feed |
| `/technical-analyst` | Shares multi-channel distribution pattern |

---

## 11. Troubleshooting

| Issue | Fix |
|-------|-----|
| No markets returned | Check API: `python scripts/polymarket_scanner.py --test` |
| Bot can't send | Verify bot is admin in channels, check `--test` |
| No signals found | Lower MIN_EDGE or MIN_CONFIDENCE in scanner.py |
| Rate limited | Increase sleep between requests (currently 0.3s) |
| Approval not working | Check `--poll` or use `--approve <msg_id>` manually |

---

## Budget

- Polymarket API: **$0** (free, no auth needed)
- Telegram Bot: **$0** (existing bot)
- Compute: **$0** (runs locally or on existing infra)
- **Total: $0/month** (well under $1,000 budget)
