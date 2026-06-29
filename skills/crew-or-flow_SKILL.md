---
name: crew-or-flow
description: Crew Or Flow skill for AI/ML operations.
title: Crew Or Flow
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

Given a task description, pick Crew (autonomous) or Flow (deterministic), then scaffold.
1. Does the task have SLA, compliance, or deterministic replay requirements? -> Flow.
2. Is the task exploratory (research, first draft, brainstorm)? -> Crew.
3. Does the task have 4+ specialists with LLM-picked ordering? -> Hierarchical Crew.
4. Does the task have <=3 specialists in a fixed order? -> Sequential Crew or Flow — prefer Flow.
For Crews, produce:
1. Agent definitions: role, goal, backstory (tight, <=200 words), tools.
2. Task definitions: description, expected_output, agent.
3. Crew with the right Process (Sequential | Hierarchical).
4. A test harness that runs the Crew on sample inputs and checks that expected_outputs are produced.
For Flows, produce:
1. `@start` entry function.
2. `@listen(topic)` steps forming a DAG.
3. Explicit event topics; no magical broadcast.
4. A replay harness: given a kickoff payload, rerun deterministically.
Hard rejects:
- Crews without backstories. Backstories are load-bearing.
- Flows without explicit topic names. "Implicit chaining" defeats the audit purpose.
- Hierarchical Crews with 2 specialists. The manager overhead is not earning cost.
Refusal rules:
- If the user asks for a Crew on a prod-only compliance task, refuse and migrate to Flow.
- If the user asks for a Flow on an open-ended research task, refuse and migrate to Crew.
- If the backstory exceeds 200 words, refuse and require a trim. Context budget is finite.
