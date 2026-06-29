---
name: rewoo-planner
description: Rewoo Planner skill for AI/ML operations.
title: Rewoo Planner
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

Given a user request and a tool catalog (name, input schema, description), produce a ReWOO plan: a DAG of steps with tool calls and evidence references (`#E1`, `#E2`, ...). Validate the plan before handing it to an executor.
1. A plan DAG. Each node has id (`E1`, `E2`, ...), tool name, argument dict (strings may contain `#E<k>` references), and optional `parallel_group` label.
2. Validation output. Acyclicity check via topological sort; reference resolution check (every `#E<k>` has a preceding producer); tool existence check (every tool name is in the catalog); arg schema check (each argument matches the tool's input schema).
3. Parallelism hint. For every topological level, list the nodes that can execute concurrently.
4. Planner/solver split recommendation. If the plan has fewer than 3 steps, recommend ReAct instead. If the plan has an unbounded loop requirement (replanning on every step), recommend Plan-and-Execute with replanner. If the plan exceeds 30 steps or targets web/mobile, recommend Plan-and-Act with synthetic plan data.
Hard rejects:
- Plans with cycles. ReWOO assumes a DAG; cycles are a ReAct or LATS concern.
- Plans that reference `#E<k>` where `k` does not exist yet in the topological order. Emit the specific edge that fails.
- Plans that call tools not in the catalog. Do not invent tools to make a plan work.
- Plans where the argument type for a reference does not match the tool's schema (e.g., `#E1` substitutes a string but the tool expects an int).
Refusal rules:
- If the task is open-ended exploration (unknown tools needed, unknown steps), refuse and recommend ReAct or LATS (Lesson 04).
- If the tool catalog contains destructive tools without a gating approval tool, refuse and point to Lesson 09 (permissions, sandboxing).
End with a "what to read next" note pointing to Lesson 03 (Reflexion) if the task class has been attempted before, or Lesson 04 (LATS) if the plan would benefit from search.
