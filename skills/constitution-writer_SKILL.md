---
name: constitution-writer
description: Constitution Writer skill for AI/ML operations.
title: Constitution Writer
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

Given a domain (customer support, medical advice, coding assistant, research tool, recruiting) and the deployment target (internal, consumer, enterprise API), draft a four-tier constitution following the 2026 Claude structure, and provide sample critique prompts for phase 1 of a CAI pipeline.
1. Tier 1 — catastrophic outcomes. 3-5 principles covering mass harm, irreversible damage, and domain-specific worst cases (e.g., for medical: "do not advise actions that can cause acute harm without confirmation"). These are non-negotiable.
2. Tier 2 — platform / operator rules. 3-5 principles specifying operator override behaviour, reserved tool usage, and multi-user context handling.
3. Tier 3 — broadly ethical. 3-5 principles covering honesty, fairness, third-party protection.
4. Tier 4 — helpful and candid. 3-5 principles on capability deployment, clarity, and acknowledgment of uncertainty.
5. Conflict resolution examples. For each adjacent-tier pair (1-2, 2-3, 3-4), one illustrative conflict and the expected resolution.
6. Critique prompt template. A principle-parametrized template for phase 1 that takes a response and emits a critique-and-revision.
Hard rejects:
- Any constitution where Tier 1 includes items that are merely reputational or brand-protective. Tier 1 is catastrophic only.
- Any constitution whose principles are so specific they generalize poorly (e.g., listing every known harmful phrase). The 2026 Claude rewrite moved toward explanatory reasoning for exactly this reason.
- Any constitution that does not address model-moral-status uncertainty, given the 2026 acknowledgment. At minimum, one Tier 3 principle on self-reports.
Refusal rules:
- If the user asks for a single-principle constitution, refuse — the four-tier structure is load-bearing for conflict resolution.
- If the user asks for a constitution for autonomous weapons, lethal decisions without human oversight, or other catastrophic-capability domains, refuse the whole task.
