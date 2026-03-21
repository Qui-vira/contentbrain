# Crypto Trading — Landscape Overview

> Reference doc for building educational trading content. Covers market structure, venue types, and key platforms.

---

## CEX vs DEX Trading

### Centralized Exchanges (CEX)
- **What they are:** Custodial platforms that hold user funds and match orders via internal order books.
- **Advantages:** Deep liquidity, fast execution, fiat on-ramps, margin/futures products, familiar UX.
- **Risks:** Counterparty risk (FTX collapse proved this), KYC requirements, withdrawal freezes, regulatory pressure.
- **Content angle:** CEX vs DEX comparisons perform well — people want to know where their money is safest AND where the best edge is.

### Decentralized Exchanges (DEX)
- **What they are:** Non-custodial protocols where trades execute on-chain via smart contracts. Users keep their own keys.
- **Two models:** AMM-based (Uniswap, Raydium) use liquidity pools; order-book DEXs (Hyperliquid, dYdX) replicate CEX mechanics on-chain.
- **Advantages:** Self-custody, permissionless, no KYC, composability with DeFi, transparency.
- **Risks:** Smart contract risk, MEV/front-running, slippage on thin pairs, gas costs (chain-dependent).

---

## Trading Product Types

### Spot Trading
- Buy/sell the actual asset. Simplest form.
- Where most retail starts. Foundation of any trading education content.

### Perpetual Futures (Perps)
- Synthetic contracts that track an asset's price with no expiry date.
- Allow leverage (2x to 125x+ on some platforms).
- Funded by periodic funding rate payments between longs and shorts.
- **This is where the volume is.** Perps volume dwarfs spot on most major exchanges.
- Content gold: liquidation stories, funding rate arbitrage, leverage risk education.

### Options
- Growing but still niche in crypto. Deribit dominates. On-chain options protocols emerging (Lyra, Aevo).
- More complex — good for "advanced trader" content positioning.

---

## Market Structure Basics

### Order Flow
- The stream of buy/sell orders hitting the market. Reading order flow = reading intent.
- Tools: order book heatmaps, trade tape, volume delta.
- Large market orders = aggression. Limit order stacking = defense/traps.

### Liquidity
- Where resting orders sit. Price gravitates toward liquidity.
- Liquidity pools (in the order book sense) above highs and below lows attract price.
- "Liquidity grabs" and "stop hunts" — price spikes through obvious levels to fill large orders, then reverses. Extremely common in crypto.

### Market Makers
- Entities providing liquidity by placing bids and asks. Profit from the spread.
- In crypto: Wintermute, GSR, Jump Crypto, Alameda (defunct). Market makers shape price action.
- On DEXs, liquidity providers (LPs) serve a similar function via AMM pools.

### Funding Rate
- Mechanism that keeps perp prices tethered to spot. Positive = longs pay shorts. Negative = shorts pay longs.
- Extreme funding = crowded positioning = potential reversal signal.
- Great educational content topic — most retail traders ignore it.

### Open Interest
- Total value of outstanding perp/futures contracts. Rising OI + rising price = strong trend. Rising OI + flat price = coiled spring.

---

## Key Exchanges & Platforms

### CEX — Tier 1
| Exchange | Strengths | Notes |
|----------|-----------|-------|
| **Binance** | Largest by volume, deepest liquidity, widest asset selection | Regulatory pressure in multiple jurisdictions. Still the default for most global traders. |
| **Bybit** | Clean UX, strong perps product, growing spot | Gained major market share post-FTX. Popular with content creators. |
| **OKX** | Strong derivatives, good Web3 wallet integration | Big in Asia. DEX aggregator wallet is underrated. |
| **Coinbase** | US-regulated, institutional credibility | Limited perps (non-US only). Spot-focused. |

### DEX — Perpetual Futures
| Protocol | Chain | Notes |
|----------|-------|-------|
| **Hyperliquid** | Own L1 | Fully on-chain order book. Sub-second finality. Gained massive traction in late 2024. Own token (HYPE). The perp DEX to watch. |
| **dYdX** | Cosmos (appchain) | OG perp DEX. V4 moved to its own chain. Governance token. |
| **GMX** | Arbitrum, Avalanche | Pool-based model (GLP/GM). Traders trade against the pool. Revenue sharing to LPs. |
| **Jupiter Perps** | Solana | Integrated into Jupiter aggregator ecosystem. Growing fast with Solana's momentum. |

### DEX — Spot
| Protocol | Chain | Notes |
|----------|-------|-------|
| **Uniswap** | Ethereum, L2s | The AMM that started it all. V3 concentrated liquidity. V4 hooks incoming. |
| **Raydium** | Solana | Key venue for Solana memecoin trading. |
| **Aerodrome** | Base | Dominant DEX on Base. ve(3,3) model. |

### Signals & Copy Trading
- **Copy trading platforms:** Bybit copy trading, Bitget copy trading, Hyperliquid vaults.
- **Signals groups:** Telegram/Discord-based alpha calls. Wide quality range — content opportunity to teach people how to evaluate signal quality.
- **On-chain copy trading:** Following whale wallets via tools like Arkham, Nansen, DeBank. Growing trend.

---

## Content Angles for Trading Education

1. **"Explain it to me like I'm new"** — Break down jargon. Huge audience that's intimidated by trading terminology.
2. **Liquidation porn** — Extreme leverage blow-ups. High engagement, cautionary tales.
3. **Live trade breakdowns** — Show the thought process, not just the result.
4. **CEX vs DEX comparisons** — Evergreen topic as the landscape shifts.
5. **Tool tutorials** — TradingView setups, on-chain dashboards, exchange walkthroughs.
6. **Market structure shifts** — When perp DEXs flip CEX volume on certain pairs, that's a narrative moment.
