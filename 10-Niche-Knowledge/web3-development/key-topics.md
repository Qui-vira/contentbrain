# Web3 Development — Key Topics

> Quick-reference descriptions for each major Web3 dev topic. Use these to write accurate, authoritative posts.

---

## Languages

### Solidity
The dominant smart contract language for all EVM chains. C-like syntax, purpose-built for Ethereum. ~90% of deployed contracts are Solidity. If you're talking about smart contract development, you're almost always talking about Solidity. Content-wise, it's the "JavaScript of Web3" — the first language every blockchain dev learns.

### Vyper
Python-like smart contract language designed for simplicity and security. Intentionally limits features (no inheritance, no operator overloading) to reduce attack surface. Used by Curve Finance and other security-conscious protocols. Good content angle: "Less code, fewer bugs — Vyper trades flexibility for safety."

### Move Language Ecosystem
Originally built by Meta (for Diem), now powers Aptos and Sui blockchains. Resource-oriented programming — assets can't be copied or accidentally destroyed at the language level. Non-EVM, so it's a different developer ecosystem entirely. Content angle: Move is what you'd design if you built a smart contract language from scratch today, knowing everything Solidity got wrong.

---

## Development Frameworks

### Hardhat
The most widely-used Ethereum development environment. JavaScript/TypeScript-based. Great plugin ecosystem, console.log in Solidity (huge for debugging), and Hardhat Network for local testing. Still the go-to for teams that prefer JS tooling. Losing ground to Foundry for new projects but massive installed base.

### Foundry
Rust-based toolkit that's become the standard for serious Solidity devs. Blazing fast compilation and testing. Write tests in Solidity (not JS), built-in fuzz testing, gas snapshots, and `cast` for command-line chain interaction. Content angle: "Foundry is what Hardhat wants to be when it grows up." Adoption accelerated hard in 2024.

---

## Security & Optimization

### Smart Contract Auditing
Third-party review of contract code before deployment. Critical because bugs in deployed contracts can mean millions lost (and they have — repeatedly). Major firms: Trail of Bits, OpenZeppelin, Cyfrin, Spearbit. Audit contests (Code4rena, Sherlock, Immunefi) let independent auditors compete to find bugs. Content gold: every major hack is an auditing story.

### Gas Optimization
Reducing the computational cost of smart contract execution. Lower gas = cheaper transactions for users. Techniques: storage packing, using `calldata` over `memory`, minimizing SSTOREs, assembly/Yul for hot paths. Foundry's gas snapshots make this measurable. Content angle: gas optimization is the performance engineering of Web3 — it directly affects user cost.

---

## Account Abstraction (ERC-4337)

Turns wallets from simple key pairs into programmable smart contract accounts. Enables: social recovery (lose your key, recover via friends/email), gas sponsorship (apps pay gas for users), session keys (approve a game to act on your behalf for 1 hour), batched transactions (approve + swap in one click). This is the UX unlock that makes crypto usable for normal people. Huge content topic — "the end of seed phrases."

---

## Layer 2 Scaling

### Rollups (General Concept)
Execute transactions off Ethereum L1, post compressed data back. L1 inherits security from Ethereum. Two types: Optimistic and ZK. This is how Ethereum scales without sacrificing decentralization.

### Optimistic Rollups
Assume transactions are valid, allow a challenge period (~7 days) for fraud proofs. Used by Arbitrum, Optimism, Base. Simpler to build, EVM-equivalent. Tradeoff: withdrawal delays due to challenge period. Dominant rollup type by TVL and usage today.

### ZK Rollups
Use zero-knowledge proofs to mathematically prove transaction validity. No challenge period — withdrawals are faster. Used by zkSync, Scroll, Polygon zkEVM, Linea, StarkNet. Harder to build but theoretically superior long-term. Content angle: "ZK is the endgame, optimistic is the bridge to get there."

---

## Cross-Chain Bridges

Move assets and data between blockchains. Historically the most-hacked category in crypto ($2B+ lost across bridge exploits). Types: lock-and-mint, burn-and-mint, liquidity networks. Major bridges: LayerZero (messaging), Wormhole, Across, Stargate. Security models vary wildly. Content angle: bridges are crypto's weakest link — and the most necessary infrastructure.

---

## Intent-Based Architectures

Users express *what* they want (swap token A for token B at best price) rather than *how* (which DEX, which route, which chain). Solvers compete to fulfill intents optimally. UniswapX, Across, CowSwap use this model. Abstracts away chain complexity. Content angle: "Intents turn crypto from manual transmission to automatic."

---

## Key EIPs Worth Knowing

| EIP | What It Does | Why It Matters |
|-----|-------------|----------------|
| **EIP-1559** | Base fee + priority tip fee model | Made gas predictable, introduced ETH burning |
| **EIP-4337** | Account abstraction (see above) | Smart wallets without protocol changes |
| **EIP-4844** | Proto-danksharding / blobs | Slashed L2 fees 10-100x. Shipped March 2024 |
| **EIP-7702** | EOAs can temporarily act as smart accounts | Bridges gap between regular wallets and smart wallets |
| **EIP-7251** | Max effective validator balance raised to 2048 ETH | Validator consolidation, reduces network overhead |

**For content:** EIPs are Ethereum's "patch notes." Each one is a content opportunity — explain what changed and who benefits.

---

*Last updated: 2025-03*
