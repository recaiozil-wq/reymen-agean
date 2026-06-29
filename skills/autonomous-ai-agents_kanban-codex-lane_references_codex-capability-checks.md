---
name: autonomous-ai-agents_kanban-codex-lane_references_codex-capability-checks
description: Codex Capability Checks
title: "Autonomous Ai Agents Kanban Codex Lane References Codex Capability Checks"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Codex Capability Checks |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Codex Capability Checks

Run these before spawning Codex. Missing Codex is a normal reason to skip the lane, not a task blocker if Hermes can do the task directly.

```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

If `/goal` support is required, enable or launch with the feature flag only after checking availability:

```bash
codex features enable goals || true
codex --enable goals --version
```

Authentication can be via `OPENAI_API_KEY` or the Codex CLI OAuth state (often `~/.codex/auth.json`). Do not print token files. A missing `OPENAI_API_KEY` is not proof that auth is unavailable.
