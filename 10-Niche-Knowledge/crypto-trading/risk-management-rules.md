# Risk Management Rules

> Position sizing, drawdown limits, and capital protection rules. Used by /technical-analyst and /signal-tracker.

---

## Core Risk Parameters

| Parameter | Value |
|-----------|-------|
| Risk per trade | 1% of total capital |
| Maximum open risk | 5% of total capital (max 5 positions at 1% each) |
| Minimum risk-to-reward | 1:2 (risking 1 to make 2) |
| Maximum drawdown before pause | 5% of capital |
| Consecutive loss limit | 3 losses in a row = pause and review |

---

## Position Sizing Formula

```
Position Size = (Account Balance × Risk %) / (Entry Price - Stop Loss Price)
```

**Example:**
- Account: $10,000
- Risk: 1% = $100
- Entry: $67,450
- Stop Loss: $66,800
- Distance: $650
- Position Size: $100 / $650 = 0.1538 BTC (~$10,376 notional)

---

## Stop Loss Rules

1. **Every trade must have a stop loss.** No exceptions.
2. **Stop loss placement:** Below/above the nearest order block, swing low/high, or invalidation level. Never arbitrary.
3. **Minimum distance:** Stop must be at least 0.5% from entry to avoid noise/wicks.
4. **No moving stops to breakeven too early.** Wait until TP1 is hit, then move SL to entry.
5. **No widening stops.** If the original SL level is hit, the trade is wrong. Accept it.

## Take Profit Rules

1. **TP1:** 1:2 R:R — Take 40% of position off.
2. **TP2:** 1:3 R:R — Take 30% of position off.
3. **TP3:** 1:5 R:R or next major resistance/support — Close remaining 30%.
4. **After TP1:** Move stop loss to breakeven (entry price).
5. **After TP2:** Trail stop loss behind the most recent swing point.

## Drawdown Protocol

| Drawdown Level | Action |
|----------------|--------|
| 2% of capital | Review recent signals for pattern errors. Continue trading. |
| 3% of capital | Reduce position size to 0.5% risk per trade. |
| 5% of capital | **PAUSE all trading.** Full review of last 10 signals. Identify what went wrong. Resume only after review is complete. |
| 7% of capital | System lockout. Manual review required before any new signals. |

## Performance Targets

| Metric | Target |
|--------|--------|
| Win rate | 60-75% |
| Average R:R achieved | 1:2 or better |
| Monthly return | 5-15% of capital (compounding) |
| Maximum monthly drawdown | 5% |

---

## Rules of Engagement

1. Never risk more than 1% on a single trade, regardless of confidence level.
2. Never enter a trade without a predefined stop loss and at least TP1.
3. Never add to a losing position (no averaging down).
4. Never revenge trade after a loss. Wait for the next valid setup.
5. Log every trade in /signal-tracker. No exceptions.
6. If the system is in drawdown pause, no signals go out. Protect the community's trust.
