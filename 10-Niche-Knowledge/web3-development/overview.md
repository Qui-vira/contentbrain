# Web3 Development — Overview

> Reference doc for writing accurate Web3 dev content. Practical, not academic.

---

## What Is Web3 Development?

Building applications where core logic runs on blockchains (smart contracts) rather than centralized servers. Users interact through wallets, own their data/assets, and transactions are settled on public ledgers. The "backend" is a smart contract; the "frontend" is a dApp (decentralized app) connecting to it via RPC.

**Key mental model for content:** Web2 = read/write. Web3 = read/write/own.

---

## EVM Chains (The Big Players)

All share the Ethereum Virtual Machine standard — same Solidity code deploys across them.

| Chain | Type | Key Trait | Content Angle |
|-------|------|-----------|---------------|
| **Ethereum** | L1 | Security anchor, highest fees | "The settlement layer." Gold standard for trust. |
| **Arbitrum** | L2 (Optimistic) | Largest L2 by TVL, Arbitrum Orbit for appchains | DeFi powerhouse, dev-friendly ecosystem |
| **Optimism** | L2 (Optimistic) | OP Stack (powers Base, Zora, etc.), retroactive public goods funding | "The Superchain" thesis — network of L2s |
| **Base** | L2 (Optimistic) | Coinbase-backed, massive consumer onboarding | Normie-friendly L2, onchain social/commerce |
| **Polygon** | L2 / Sidechain | Polygon CDK for custom chains, zkEVM live | Enterprise partnerships, gaming, NFTs |

**For content:** Compare these chains on speed, cost, ecosystem size, and developer experience — not just "which is best."

---

## Smart Contracts — The Basics

- Self-executing code deployed on-chain. Once deployed, it runs exactly as written — no one can change it (unless it's upgradeable by design).
- Written primarily in **Solidity** (90%+ of EVM contracts) or **Vyper**.
- Key concepts: gas fees, state variables, events, modifiers, inheritance, interfaces.
- Common patterns: ERC-20 (tokens), ERC-721 (NFTs), ERC-1155 (multi-token), proxy/upgradeable patterns.

**For content:** Smart contracts are the "why" behind trustless systems. They replace middlemen with math.

---

## Current State of the Ecosystem (2024–2025)

- **L2 dominance:** Activity has migrated heavily to L2s. Ethereum L1 is becoming a settlement/security layer.
- **Modular thesis winning:** Execution, data availability, consensus, and settlement are being unbundled across specialized layers.
- **Account abstraction gaining traction:** Wallets are getting smarter (social recovery, gas sponsorship, session keys).
- **Onchain AI:** AI agents interacting with smart contracts — autonomous trading, content, governance.
- **Real-world assets (RWAs):** Tokenized treasuries, real estate, and credit on-chain. BlackRock's BUIDL fund crossed $500M+.
- **Developer tooling matured significantly:** Foundry overtaking Hardhat for serious devs. Viem/Wagmi replacing ethers.js.

---

## Developer Tooling Landscape

| Category | Tools | Notes |
|----------|-------|-------|
| **Frameworks** | Hardhat, Foundry, Truffle (deprecated) | Foundry is the new standard for speed and testing |
| **Frontend libs** | Viem, Wagmi, ethers.js, web3.js | Viem/Wagmi = modern stack. ethers.js still widely used |
| **Wallets** | MetaMask, Rabby, Rainbow, Coinbase Wallet | MetaMask still dominant but Rabby gaining fast |
| **Block explorers** | Etherscan, Blockscout, Routescan | Etherscan is the "Google" of on-chain data |
| **Testing** | Foundry (Forge), Hardhat tests, Tenderly | Foundry's fuzz testing is a game-changer |
| **Deployment** | Hardhat Ignition, Foundry scripts, Thirdweb | Thirdweb for no-code/low-code deploys |

---

## Key Infrastructure

### RPCs (Remote Procedure Calls)
How dApps talk to blockchains. Every wallet call, every transaction — goes through an RPC.
- **Providers:** Alchemy, Infura, QuickNode, Chainstack, public RPCs
- **Content angle:** RPCs are the internet pipes of Web3. When they go down, dApps go dark.

### Indexers
Query on-chain data efficiently (blockchain nodes are bad at complex queries).
- **The Graph** — decentralized indexing, uses subgraphs
- **Goldsky, Envio, Subsquid** — faster alternatives gaining share
- **Content angle:** "Without indexers, building a dApp is like searching Google one page at a time."

### Oracles
Bring off-chain data (prices, weather, sports scores) on-chain.
- **Chainlink** — dominant player, price feeds power most of DeFi
- **Pyth** — fast, Solana-native but expanding to EVM
- **RedStone, API3** — newer challengers
- **Content angle:** "Smart contracts are blind without oracles. They can't see the real world."

---

## Quick Stats (for content credibility)

- Ethereum: ~$400B+ market cap, 500K+ validators
- L2s combined: processing 10-50x more transactions than Ethereum L1
- Solidity: most-used smart contract language, 30K+ monthly active developers (Electric Capital report)
- Total crypto developers: ~25,000 monthly active (down from peak, but quality up)

---

*Last updated: 2025-03*
