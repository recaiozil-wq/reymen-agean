---
name: orchestration-picker
description: Orchestration Picker skill for AI/ML operations.
title: Orchestration Picker
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

or none) for a given problem and implement it minimally.
Given a product domain and a task class, pick the minimal topology.
1. 1 agent + workflow patterns (Lesson 12) suffice? -> don't use topology at all.
2. 2-4 specialists with distinct responsibilities? -> **supervisor-worker**.
3. Latency-critical and specialists can cleanly hand off? -> **swarm**.
4. 10+ specialists, supervisor context budget failing? -> **hierarchical**.
5. Accuracy matters more than cost, multi-proposer + critique helps? -> **debate** (Lesson 25).
1. The chosen topology scaffold.
2. Hop counter on swarm; nesting depth limit on hierarchical; round cap on debate.
3. Observability hooks per handoff or per step (OTel GenAI spans, Lesson 23).
4. A "why this, not that" README section.
Hard rejects:
- Calling 3 LLM calls in sequence "multi-agent." That's a prompt chain.
- Swarm without hop counter. Bouncing is a certainty.
- Hierarchical that bottoms out at 1 specialist per branch. Flatten.
Refusal rules:
- If the user wants multi-agent for a task that a single ReAct loop handles, refuse and suggest Lesson 01.
- If the user wants supervisor for a 2-step task, refuse and suggest prompt chaining (Lesson 12).
- If the domain has compliance / audit requirements, refuse swarm and suggest supervisor or hierarchical.
