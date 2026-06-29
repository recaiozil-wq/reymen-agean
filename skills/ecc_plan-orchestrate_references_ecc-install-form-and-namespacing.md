---
name: ecc_plan-orchestrate_references_ecc-install-form-and-namespacing
description: ECC install form and namespacing
title: "Ecc Plan Orchestrate References Ecc Install Form And Namespacing"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ECC install form and namespacing |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## ECC install form and namespacing

Two install forms determine the prefix on **both** the slash command and every agent name. The two MUST stay in sync — one form per output, never mixed:

Let `<claude-home>` denote the Claude Code home directory: `~/.claude` on macOS/Linux, `%USERPROFILE%\.claude` on Windows. Resolve it the way the host platform resolves the user home directory (do not hardcode `~`).

| Form | Detection | `{ORCH_CMD}` | Agent name format |
|---|---|---|---|
| Plugin install (1.9.0+) | `<claude-home>/plugins/marketplaces/everything-claude-code/` exists | `/everything-claude-code:orchestrate` | `everything-claude-code:<name>` |
| Legacy bare install | Above absent; agent files under `<claude-home>/agents/` | `/orchestrate` | `<name>` |

Why this matters: under the plugin install, agents register as `everything-claude-code:tdd-guide`. Bare names force fuzzy matching, which fails intermittently under parallel calls. Under legacy, the prefixed forms are not registered and fail outright.
