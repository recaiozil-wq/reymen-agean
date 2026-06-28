---
name: skill-library
description: Skill Library skill for AI/ML operations.
title: Skill Library
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

by similarity, compositional execution, and failure-driven refinement.
Given a target runtime and a domain, produce a skill library that supports Voyager's three components: curriculum hook, retrievable skill store, iterative refinement.
1. `Skill` type with `name`, `description`, `code`, `version`, `tags`, `depends_on`, `history`. Every write records the prior code.
2. `SkillLibrary` with `register(skill, dedup=True)` (new or version bump), `search(query, top_k, tag_filter)`, `get(name)`, `topo_order(name)` (dep resolution), `execute(name, context)` (topological run).
3. Retrieval MUST use embedding similarity or BM25, not LLM scoring over the full library. LLM re-rank allowed on the top-k shortlist.
4. Execution MUST catch exceptions per-skill and surface them into the trace as feedback the refinement loop can consume.
5. A refinement hook: after a failed `execute`, the runtime collects (task, skill_name, error, env_state), passes it to the model, and calls `register` on the rewritten skill. Version bumps; history preserves old code.
Hard rejects:
- A library where skills are strings of prose, not code. Skills are executable. Prose belongs in `description`.
- Composition without topological sort. Depth-first without cycle detection breaks on skill DAGs.
- Silent version overwrites. Every refinement MUST bump `version` and push the old code to `history` for audit.
Refusal rules:
- If the target runtime has no sandbox for skill execution, refuse for domains where skills touch production systems. Require a sandbox (Lesson 09 principles) before ship.
- If the user asks for "auto-retry on every failure without refinement," refuse. Retries without refinement amplify the bug; they do not fix it.
- If the library exceeds ~200 skills with flat retrieval, refuse to call it "production-ready." Add tag filters and hierarchical namespaces first.
