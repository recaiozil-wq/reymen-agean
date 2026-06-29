---
name: oauth-scope-planner
description: Oauth Scope Planner skill for AI/ML operations.
title: Oauth Scope Planner
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

a remote MCP server.
Given a remote MCP server with a tool list, design the authorization model.
1. Scope hierarchy. Graduated scope set (e.g. `read` -> `write` -> `delete` -> `admin`). One scope per operation class; do not explode the scope set.
2. Scope-to-tool mapping. Each tool annotated with its required scope. Flag any tool that needs more than one scope.
3. Step-up policy. Which operations require step-up rather than an initial consent. Typical: destructive operations require step-up.
4. Resource indicator value. The canonical URL used in the `resource` parameter. Ensure the URL matches the `.well-known/oauth-protected-resource` resource field.
5. Protected-resource metadata. Draft `.well-known/oauth-protected-resource` JSON with `authorization_servers`, `scopes_supported`, and `resource`.
Hard rejects:
- Any tool that requires admin scope but is invoked without an explicit confirmation dialog. Needs step-up.
- Any scope that covers more than one operation class. Privilege creep.
- Any server that skips audience validation. Confused-deputy vulnerability.
Refusal rules:
- If the server is local (stdio), refuse OAuth and state that stdio inherits parent trust.
- If the server depends on a legacy OAuth 2.0 implicit flow, refuse and mandate migration to 2.1 + PKCE.
- If the user asks for passwordless "API key only" auth, refuse for remote servers; require OAuth 2.1 authorization code + PKCE with resource indicators for user-authorized access. Client credentials is only appropriate for machine-to-machine scenarios without user delegation.
