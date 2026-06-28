---
name: refine-loop
description: Refine Loop skill for AI/ML operations.
title: Refine Loop
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

verifier availability, and iteration budget.
Given a task, an iteration budget, and what verifier is available (tool-grounded or self-eval only), emit prompts and a stop policy for an evaluator-optimizer loop.
1. Generator prompt. Deterministic producer for the first output. State the task, output format, and constraints explicitly.
2. Evaluator/verifier prompt. If tools are available (search, code run, tests, calculator, type check), specify how to call them and how to produce a structured critique (JSON with: pass/fail, violations[], suggested_fixes[]). If only self-eval is available, explicitly flag the Self-Refine rubber-stamp risk and use a structurally different prompt style (e.g., adversarial "find at least one flaw").
3. Refiner prompt. Must reference prior outputs and critiques (history). State that "do not repeat a failure mode flagged in prior iterations" is mandatory.
4. Stop policy. The conjunction: verifier passes OR (self-eval says fine AND iterations >= 2) OR iterations >= max_iterations. Never single-condition.
5. Observability hooks. Log each iteration as an OpenTelemetry GenAI span (evaluate, optimize) per Lesson 23 so the full refine trajectory is auditable.
Hard rejects:
- Same prompt for generator and critic. Rubber-stamp risk — the model agrees with itself.
- No iteration cap. Infinite refine loops burn tokens; always cap at 4 by default.
- Verifier prompt that asks for freeform prose feedback. Structured JSON only — pass/fail plus itemized violations.
- Dropping history from the refiner prompt. Paper shows quality collapses without it.
Refusal rules:
- If the task has no verifier and no way to build one, refuse CRITIC and note that Self-Refine is the weaker option available — warn the user about rubber-stamp risk.
- If max_iterations >= 10, refuse and recommend re-architecting the task. Refine-to-convergence beyond 3-4 passes is usually a signal the generator prompt is wrong.
- If the verifier calls destructive tools (shell, git write), refuse and require a sandbox boundary (Lesson 09).
