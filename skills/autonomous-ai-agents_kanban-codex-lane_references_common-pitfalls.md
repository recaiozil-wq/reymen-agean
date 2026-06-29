---
name: autonomous-ai-agents_kanban-codex-lane_references_common-pitfalls
description: Common Pitfalls
title: "Autonomous Ai Agents Kanban Codex Lane References Common Pitfalls"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Common Pitfalls |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Common Pitfalls

1. Treating Codex self-report as verification. Always inspect the diff and rerun tests from Hermes.
2. Running Codex in the user's dirty main checkout. Always isolate in a worktree/branch.
3. Letting Codex own Kanban. Codex may summarize progress, but Hermes writes board state.
4. Forgetting PMB safety invariants in the prompt. Missing safety text is a lane setup failure.
5. Using `/goal` for quick edits. Prefer `codex exec` unless durable multi-step continuation is needed.
6. Killing a stuck lane without recording why. `rejected_reason` must explain the decision.
7. Accepting broad unrelated cleanup because tests pass. Reject or cherry-pick only the scoped changes.
