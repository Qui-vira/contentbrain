# Indicator Confluence Rules

> Defines the indicator stack and how indicators combine for signal scoring. Used by /technical-analyst.

---

## Primary Indicator Stack

| Indicator | Settings | Purpose |
|-----------|----------|---------|
| EMA 21 | Period: 21 | Dynamic support/resistance, trend direction |
| EMA 50 | Period: 50 | Medium-term trend |
| EMA 200 | Period: 200 | Long-term trend, institutional level |
| MACD | 12, 26, 9 | Momentum and trend changes |
| Bollinger Bands | 20, 2 | Volatility and mean reversion |
| Volume Profile | 24 periods | High volume nodes, POC, value area |
| Fibonacci | Auto (swing high/low) | Retracement levels (0.618, 0.786, OTE zone) |

---

## Indicator Confluence Rules

### EMA Stack

- **Bullish:** Price above EMA 21 > EMA 50 > EMA 200 (aligned and ascending).
- **Bearish:** Price below EMA 21 < EMA 50 < EMA 200 (aligned and descending).
- **Dynamic S/R:** EMA 21 acts as first support/resistance. If broken, EMA 50 is next. EMA 200 is the "line in the sand."
- **Counts as 1 confluence** when price respects an EMA as support/resistance at the setup level.

### MACD

- **Bullish signal:** MACD line crosses above signal line, histogram turns positive.
- **Bearish signal:** MACD line crosses below signal line, histogram turns negative.
- **Divergence:** Price makes new high/low but MACD does not = potential reversal. Divergence is a high-value confluence.
- **Counts as 1 confluence** when MACD confirms the trade direction (crossover or divergence).

### Bollinger Bands

- **Squeeze:** Bands narrow = low volatility = breakout imminent. Direction determined by other indicators.
- **Band touch/rejection:** Price touches upper band and rejects = bearish signal. Lower band rejection = bullish.
- **Mean reversion:** Price tends to return to the middle band (20 SMA) after extreme moves.
- **Counts as 1 confluence** when BB confirms the setup (squeeze breakout direction, band rejection, or mean reversion).

### Volume Profile

- **Point of Control (POC):** The price level with the most traded volume. Acts as a magnet.
- **High Volume Node (HVN):** Levels where significant volume was traded. Act as support/resistance.
- **Low Volume Node (LVN):** Levels with little volume. Price moves through these quickly.
- **Value Area (VA):** The range where 70% of volume was traded. Price tends to stay within or return to the VA.
- **Counts as 1 confluence** when the entry aligns with a HVN/POC as support or an LVN for a fast move target.

### Fibonacci Retracement

- **Key levels:** 0.382 (shallow pullback), 0.5 (equilibrium), 0.618 (golden ratio), 0.786 (deep pullback).
- **OTE zone:** 0.618 to 0.786 — the highest probability reversal zone.
- **Counts as 1 confluence** when entry is at or near a key Fib level (especially if in OTE zone).

---

## Confluence Scoring

| # of Confirmations | Confidence Level | Action |
|---------------------|-----------------|--------|
| 1-2 | LOW | Do not signal. Log for observation only. |
| 3-4 | MEDIUM | Signal with caution note. Recommend smaller position size. |
| 5+ | HIGH | Full signal. Standard position size. |

### What Counts as a Confirmation

Each of these counts as 1 confirmation (max 1 per category):

1. **ICT Concept** — Order block, FVG, liquidity sweep, MSS/BOS, or OTE
2. **EMA** — Price respecting EMA as dynamic S/R
3. **MACD** — Crossover or divergence confirming direction
4. **Bollinger Bands** — Squeeze breakout, band rejection, or mean reversion
5. **Volume Profile** — HVN/POC alignment or LVN target
6. **Fibonacci** — Entry at key Fib level
7. **Kill Zone** — Entry during London or NY session
8. **Support/Resistance** — Key horizontal level alignment

**Maximum possible score: 8 confluences.**

---

## Indicator Hierarchy

When indicators conflict:

1. **Higher timeframe structure wins.** If Daily is bearish, do not take 1H longs regardless of indicator signals.
2. **ICT concepts > lagging indicators.** Order blocks and liquidity sweeps reflect real market mechanics. MACD and BB are mathematical derivatives.
3. **Volume confirms everything.** A signal without volume confirmation is suspect.
4. **When in doubt, sit out.** No trade is better than a forced trade.
