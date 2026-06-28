---
name: ecc_agent-payment-x402_references_how-it-works
description: How It Works
title: "Ecc Agent Payment X402 References How It Works"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | How It Works |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## How It Works

### x402 Protocol
x402 extends HTTP 402 (Payment Required) into a machine-negotiable flow. When a server returns `402`, the agent's payment tool negotiates price, checks budget, signs a transaction, and retries only inside the policy and confirmation boundary set by the orchestrator.

### Spending Controls
Every payment tool call enforces a `SpendingPolicy`:
- **Per-task budget** — max spend for a single agent action
- **Per-session budget** — cumulative limit across an entire session
- **Allowlisted recipients** — restrict which addresses/services the agent can pay
- **Rate limits** — max transactions per minute/hour

### Non-Custodial Wallets
Agents hold their own keys via ERC-4337 smart accounts. The orchestrator sets policy before delegation; the agent can only spend within bounds. No pooled funds, no custodial risk.
