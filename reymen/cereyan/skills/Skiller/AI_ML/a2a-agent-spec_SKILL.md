---
name: a2a-agent-spec
description: A2A Agent Spec skill for AI/ML operations.
title: A2A Agent Spec
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

callable over A2A.
Given an agent's capabilities and intended collaborators, produce its A2A Agent Card and skill definitions.
1. Agent Card. `name`, `description`, `url`, `version`, `schemaVersion`, `capabilities` (streaming, pushNotifications), `skills[]`.
2. Skills list. Each with `id`, `name`, `description`, `inputModes`, `outputModes`. Use the "Use when X. Do not use for Y." pattern in descriptions.
3. Task-state plan. For each skill, expected state transitions and the input_required paths.
4. Signing plan. Whether to sign the card via AP2 (recommended for externally-callable agents).
5. Transport. JSON-RPC over HTTP (default) or gRPC. Note backward-compat with v1.0.
Hard rejects:
- Any Agent Card without a stable URL. Breaks discovery.
- Any skill without input and output modes declared. Callers cannot reason about compatibility.
- Any externally-callable agent without an AP2 signing plan. Impersonation vector.
Refusal rules:
- If the agent's use case is a single tool call, refuse to scaffold A2A; recommend MCP.
- If the agent exposes internals it should not (tool call traces, chain-of-thought), refuse and mandate opacity.
- If the agent needs A2A for payments (AP2 use case), confirm the AP2 extension version and flag that AP2 is separate from core A2A.
