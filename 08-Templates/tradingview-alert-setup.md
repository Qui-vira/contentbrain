# TradingView Webhook Alert Setup

> Connect TradingView alerts to the Quivira signal pipeline via Supabase Edge Function.

---

## 1. Webhook URL

```
https://iwiqldudksmbbjxpqgsj.supabase.co/functions/v1/tradingview-webhook?secret=quivira-signals-2026
```

Paste this into TradingView's **Webhook URL** field when creating any alert.

---

## 2. Alert Message JSON Templates

### Market Structure Shift (MSS)
```json
{"pair": "{{ticker}}", "timeframe": "{{interval}}", "alert_type": "MSS", "direction": "{{strategy.order.action}}", "price": {{close}}, "high": {{high}}, "low": {{low}}, "time": "{{time}}"}
```

### Order Block Touch (OB)
```json
{"pair": "{{ticker}}", "timeframe": "{{interval}}", "alert_type": "OB", "direction": "LONG", "price": {{close}}, "high": {{high}}, "low": {{low}}, "time": "{{time}}"}
```

### Fair Value Gap Fill (FVG)
```json
{"pair": "{{ticker}}", "timeframe": "{{interval}}", "alert_type": "FVG", "direction": "LONG", "price": {{close}}, "high": {{high}}, "low": {{low}}, "time": "{{time}}"}
```

### EMA Cross
```json
{"pair": "{{ticker}}", "timeframe": "{{interval}}", "alert_type": "EMA_CROSS", "direction": "LONG", "price": {{close}}, "high": {{high}}, "low": {{low}}, "time": "{{time}}"}
```

### Kill Zone Entry
```json
{"pair": "{{ticker}}", "timeframe": "{{interval}}", "alert_type": "KILL_ZONE", "direction": "LONG", "price": {{close}}, "high": {{high}}, "low": {{low}}, "time": "{{time}}"}
```

> **Note:** Set `"direction"` manually to `"LONG"` or `"SHORT"` for non-strategy alerts. Only strategy-based alerts auto-fill `{{strategy.order.action}}`.

---

## 3. Setting Up Alerts on a Forex Chart (GBP/USD 4H Example)

### Step 1: Prepare the Chart
1. Open TradingView → search `GBPUSD` → switch to **4H** timeframe
2. Add indicators:
   - EMA (21), EMA (50), EMA (200)
   - MACD (12, 26, 9)
   - Bollinger Bands (20, 2)
3. Add community scripts (search in Indicators):
   - "Order Blocks ICT"
   - "FVG ICT" or "Fair Value Gap"
   - "Market Structure BOS CHoCH"
   - "ICT Kill Zones"

### Step 2: Create Your First Alert
1. Click the **Alerts** icon (clock) → **Create Alert**
2. Set condition (e.g., EMA 21 crosses above EMA 50)
3. Set expiration to **Open-ended**
4. Under **Notifications**, check **Webhook URL**
5. Paste the webhook URL from Section 1
6. In the **Message** field, paste the EMA_CROSS JSON template
7. Click **Create**

### Step 3: Add More Alerts
Repeat Step 2 for each alert type:
- MSS alert → use MSS template
- Order Block alert → use OB template
- FVG alert → use FVG template
- Kill Zone alert → use KILL_ZONE template

You can have up to **10 alerts per chart** and **100 total** on your Plus plan.

---

## 4. Recommended Alerts Per Forex Pair

| Alert # | Type | Condition | Template |
|---------|------|-----------|----------|
| 1 | EMA_CROSS | EMA 21 crosses EMA 50 | EMA Cross |
| 2 | MSS | Market structure break (BOS/CHoCH indicator) | MSS |
| 3 | OB | Price enters order block zone | OB |
| 4 | FVG | Price fills a fair value gap | FVG |
| 5 | KILL_ZONE | Time enters London/NY/Asia session | KILL_ZONE |

---

## 5. Processing Flow

```
TradingView Alert Fires
    ↓
Edge Function receives POST
    ↓
Validates secret, parses JSON
    ↓
Stores in Supabase webhook_alerts table
    ↓
python scripts/fetch_alerts.py
    ↓
Saves markdown to 03-Trends/tradingview-alerts/[pair]-[date].md
    ↓
/technical-analyst processes in alert mode
    ↓
Signal generated → you approve/reject
    ↓
fetch_alerts.py --mark-processed <id>
```

---

## 6. Testing the Webhook

```bash
curl -X POST "https://iwiqldudksmbbjxpqgsj.supabase.co/functions/v1/tradingview-webhook?secret=quivira-signals-2026" \
  -H "Content-Type: application/json" \
  -d '{"pair": "GBPUSD", "timeframe": "240", "alert_type": "EMA_CROSS", "direction": "LONG", "price": 1.2650, "high": 1.2680, "low": 1.2620, "time": "2026-03-21T14:00:00Z"}'
```

Then fetch and save:
```bash
python scripts/fetch_alerts.py
```

---

## 7. Forex Pairs to Set Up

| Pair | Priority |
|------|----------|
| GBP/USD | High |
| EUR/USD | High |
| USD/JPY | High |
| GBP/JPY | Medium |
| XAU/USD | Medium |
| USD/CHF | Medium |
| AUD/USD | Low |
| NZD/USD | Low |
