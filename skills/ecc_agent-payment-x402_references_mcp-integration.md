---
name: ecc_agent-payment-x402_references_mcp-integration
description: MCP Integration
title: "Ecc Agent Payment X402 References Mcp Integration"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | MCP Integration |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## MCP Integration

The payment layer exposes standard MCP tools that slot into any Claude Code or agent harness setup.

> **Security note**: Always pin the package version. This tool manages private keys — unpinned `npx` installs introduce supply-chain risk.

### Option A: agentwallet-sdk (Base / multi-chain)

```json
{
  "mcpServers": {
    "agentpay": {
      "command": "npx",
      "args": ["agentwallet-sdk@6.0.0"]
    }
  }
}
```

### Available Tools (agent-callable)

| Tool | Purpose |
|------|---------|
| `get_balance` | Check agent wallet balance |
| `send_payment` | Send payment to address or ENS |
| `check_spending` | Query remaining budget |
| `list_transactions` | Audit trail of all payments |

> **Note**: Spending policy is set by the **orchestrator** before delegating to the agent — not by the agent itself. This prevents agents from escalating their own spending limits. Configure policy via `set_policy` in your orchestration layer or pre-task hook, never as an agent-callable tool.

### Option B: OKX Agent Payments Protocol (X Layer)

Use this path for X Layer x402, Multi-Party Payment (MPP), session payment, charge, and A2A charge flows.

For buyer-side agent flows:

1. Install or reference the current `okx/onchainos-skills` repository.
2. Use `skills/okx-agent-payments-protocol/SKILL.md` as the dispatcher.
3. Treat `skills/okx-x402-payment/SKILL.md` as a deprecated compatibility alias, not as the canonical skill.
4. Require explicit user confirmation before wallet status checks or payment actions. Do not hide payment execution behind a generic tool call.

For seller-side API flows, fetch the latest language-specific guide before generating code:

| Runtime | Current guide |
|---------|---------------|
| TypeScript | `https://raw.githubusercontent.com/okx/payments/main/typescript/SELLER.md` |
| Go | `https://raw.githubusercontent.com/okx/payments/main/go/x402/SELLER.md` |
| Rust | `https://raw.githubusercontent.com/okx/payments/main/rust/x402/SELLER.md` |
| Java | `https://raw.githubusercontent.com/okx/payments/main/java/SELLER.md` |

Do not copy examples from older docs without checking the current OKX repository. Current OKX guidance uses `okx-agent-payments-protocol` as the dispatcher, and Java seller docs are now available.
