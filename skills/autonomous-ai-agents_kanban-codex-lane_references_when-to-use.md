---
name: autonomous-ai-agents_kanban-codex-lane_references_when-to-use
description: When to Use
title: "Autonomous Ai Agents Kanban Codex Lane References When To Use"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | When to Use |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## When to Use

Use the Codex lane when all of these are true:

- The Kanban task is a coding, refactor, documentation, test, or mechanical migration task with clear acceptance criteria.
- A bounded diff can be evaluated by Hermes in one run.
- The repo can be copied or checked out in an isolated git worktree/branch.
- Hermes can run the relevant tests itself after Codex exits.
- The prompt can state all safety constraints and files that must not change.

Do not use the Codex lane when any of these are true:

- The task requires human judgment that is not already captured in the Kanban body.
- The worker lacks repo access, Codex auth, or time to reconcile the result.
- The change touches secrets, credential stores, private user data, or production order-entry systems.
- A small direct edit is faster and safer than spawning another agent.
- The task is research-only and should produce a written handoff rather than a diff.
- The worker would be tempted to mark Done based only on Codex self-report.
