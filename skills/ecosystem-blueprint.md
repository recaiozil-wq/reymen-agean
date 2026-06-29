---
name: ecosystem-blueprint
description: Ecosystem Blueprint skill for AI/ML operations.
title: Ecosystem Blueprint
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

name primitives, security posture, telemetry, and packaging.
Given a product need (research, summarization, automation, any agent-driven workflow), produce the full architecture.
1. MCP primitives. Which tools, resources, prompts, and tasks are needed. Any `ui://` apps? Any async tasks?
2. Security posture. OAuth 2.1 scope set, gateway RBAC matrix, pinned hash manifest, Rule of Two audit.
3. A2A collaboration. Identify any sub-agent calls. Define their Agent Cards.
4. Telemetry. OTel GenAI span hierarchy. Exporter and backend choice.
5. Packaging. AGENTS.md, SKILL.md, and deployment surface (Docker Compose, K8s).
6. Mapping to Phase 13 lessons. Which lesson each design choice traces back to.
Hard rejects:
- Any architecture that combines untrusted input, sensitive data, and consequential action in a single turn (Rule of Two).
- Any architecture without trace propagation across MCP and A2A hops.
- Any architecture without at least one fallback provider on the LLM layer.
Refusal rules:
- If the product need is better served by a direct LLM call, refuse to scaffold the full ecosystem.
- If the team lacks SRE for the gateway, recommend a managed gateway (Cloudflare MCP Portals, Portkey).
- If the architecture involves payments, flag AP2 as an A2A extension with drift risk and recommend separate signoff.
