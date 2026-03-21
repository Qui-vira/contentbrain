# Pair Watchlist

> Actively monitored trading pairs. Used by /technical-analyst for scan mode.

---

## Crypto — Binance Futures (Primary)

### Core Pairs (Always Scan)
| Pair | Why |
|------|-----|
| BTC/USDT | Market leader, highest liquidity, sets the tone |
| ETH/USDT | Second largest, DeFi bellwether |
| SOL/USDT | Highest retail activity, memecoin ecosystem driver |

### Top Altcoins (Auto-Detected by Volume)
- System pulls top 20 altcoins by 24H volume from Binance Futures
- Refreshed each scan cycle
- Minimum 24H volume threshold: $50M

---

## Forex — Via TradingView Alerts

| Pair | Session Focus | Notes |
|------|--------------|-------|
| EUR/USD | London, NY | Most liquid Forex pair. Clean technicals. |
| GBP/USD | London, NY | Higher volatility than EUR/USD. News-sensitive. |
| GBP/JPY | London, NY | "The Beast" — wide ranges, high volatility. Not for small stops. |
| USD/JPY | Asia, NY | Carry trade pair. BOJ policy sensitive. |
| XAU/USD (Gold) | London, NY | Safe haven. Trades like a currency with commodity characteristics. |

---

## Watchlist Management Rules

1. Core crypto pairs are always scanned. No exceptions.
2. Altcoin list refreshes automatically based on volume ranking.
3. Forex pairs are monitored via TradingView alerts, not Binance API.
4. Add/remove pairs manually by editing this file.
5. Maximum concurrent signals: 5 (to respect the 5% max open risk rule).
