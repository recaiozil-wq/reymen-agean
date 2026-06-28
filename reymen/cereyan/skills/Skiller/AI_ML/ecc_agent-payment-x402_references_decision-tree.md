---
name: ecc_agent-payment-x402_references_decision-tree
description: Decision Tree
title: "Ecc Agent Payment X402 References Decision Tree"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Decision Tree |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Decision Tree

Choose the integration path based on whether your agent is buying access to a paid API or charging others for one:

| Need | Recommended path |
|------|------------------|
| Agent pays a 402-gated API on Base or another agentwallet-supported chain | Use `agentwallet-sdk` as an MCP payment server with strict spending policy |
| Agent pays a 402-gated API on X Layer | Use OKX Agent Payments Protocol from `okx/onchainos-skills`; `okx-x402-payment` is a deprecated legacy alias |
| TypeScript API charges agents | Use OKX Payments TypeScript seller SDK docs for Express, Hono, Fastify, or Next.js |
| Go API charges agents | Use OKX Payments Go seller SDK docs for Gin, Echo, or `net/http` |
| Rust API charges agents | Use OKX Payments Rust seller SDK docs for Axum |
| Java API charges agents | Use OKX Payments Java seller SDK docs for Spring Boot 2/3, Java EE, or Jakarta |
| Python API charges agents | Check the current OKX Payments repository before implementation; a Python seller guide may not be available |
