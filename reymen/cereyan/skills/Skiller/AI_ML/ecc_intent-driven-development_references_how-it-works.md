---
name: ecc_intent-driven-development_references_how-it-works
description: How It Works
title: "Ecc Intent Driven Development References How It Works"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | How It Works |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## How It Works

1. **Inspect context first** — reads the repository, docs, schemas, and test infrastructure for technical facts before asking any question, while treating product/business constraints as something only the user or a product artifact can supply
2. **Choose depth** — selects Quick Capture (3-7 criteria, low/moderate risk) or Full Acceptance Brief (security, data, migration, cross-system changes) based on the risk profile
3. **Ask minimally** — only asks questions whose answers cannot be inferred and that materially change scope or behavior
4. **Write observable criteria** — each AC-NNN describes a starting condition, trigger, expected outcome, prohibited side effect, verification method, and priority; no vague words like "correctly" or "securely" without evidence
5. **Proceed or hand off** — for clear requests with no blocking risks, records criteria and continues; for risky changes, presents blockers and waits for confirmation
6. **Handle revision** — if an AC fails mid-implementation due to architectural constraints, marks it `[revised]`, updates scope or verification method, increments the revision number, and re-presents only the changed criteria
