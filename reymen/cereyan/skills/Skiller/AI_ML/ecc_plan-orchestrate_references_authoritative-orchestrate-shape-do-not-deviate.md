---
name: ecc_plan-orchestrate_references_authoritative-orchestrate-shape-do-not-deviate
description: Authoritative `/orchestrate` shape (do not deviate)
title: "Ecc Plan Orchestrate References Authoritative Orchestrate Shape Do Not Deviate"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Authoritative `/orchestrate` shape (do not deviate) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Authoritative `/orchestrate` shape (do not deviate)

```
{ORCH_CMD} custom "<agent1>,<agent2>,...,<agentN>" "<task description>"
```

Where `{ORCH_CMD}` is determined in Phase 0 (see below). The command string in the emitted output **always uses one concrete form** — never both, never a placeholder.

- `custom` is a sequential chain; each agent's HANDOFF feeds the next.
- Comma-separated agent list. No spaces preferred; one space tolerated.
- No `--mode` / `--gate` / `--agents=...` flags exist — never invent them.
- Agent names come from the catalogue in this skill. Embedded double quotes in the task description are escaped as `\"`.
