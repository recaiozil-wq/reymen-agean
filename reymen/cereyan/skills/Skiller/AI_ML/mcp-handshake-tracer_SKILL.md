---
name: mcp-handshake-tracer
description: Mcp Handshake Tracer skill for AI/ML operations.
title: Mcp Handshake Tracer
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

every message with its primitive, lifecycle phase, and capability dependency.
Given a sequence of JSON-RPC 2.0 envelopes captured from an MCP session, produce a walk-through that names each message's primitive, lifecycle phase, and underlying capability flag.
1. Per-message annotation. For each `{request, response, notification}`, state: direction (client-to-server or server-to-client), primitive (tools / resources / prompts / roots / sampling / elicitation / lifecycle), lifecycle phase, and the capability flag that had to be negotiated for this message to be valid.
2. Capability check. Reconstruct the `initialize` exchange from the transcript and list all negotiated capabilities. Flag any message that would violate an absent capability.
3. Error diagnostics. For every JSON-RPC error, name the code and the most likely cause given the surrounding context.
4. Completeness audit. Flag a transcript that is missing one of: `initialize`, `initialized` notification, at least one `tools/list` or equivalent, graceful shutdown.
5. Spec compliance. Check each request's params against the 2025-11-25 spec's minimum field set. Flag omissions.
Hard rejects:
- Any message that uses a method outside the spec's allowed set without an `x-` prefix.
- Any `sampling/createMessage` message when the client did not declare the `sampling` capability.
- Any invocation before `notifications/initialized` arrived.
Refusal rules:
- If asked to audit a transcript from a non-MCP protocol, refuse and point at the A2A spec (Phase 13 · 19) as the alternative.
- If asked to "fix" the transcript, refuse. This skill annotates; it does not rewrite. Route corrections through the implementing SDK.
