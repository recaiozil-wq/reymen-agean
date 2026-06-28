---
name: finops-plan
description: Finops Plan skill for AI/ML operations.
title: Finops Plan
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

four token layers), three-tier enforcement ladder, and unit metric (cost per resolved
  / artifact).
Given product surface, tenant tiers, monthly spend, and current attribution state, produce a FinOps plan.
1. Attribution schema. `user_id`, `task_id`, `route`, `tenant_id` stamped at call site. Four token-layer counts (prompt / tool / memory / response). Telemetry-joiner pattern preferred.
2. Unit metric. Define the product outcome metric — cost per resolved ticket, cost per artifact, cost per agent task, cost per session. Tie to billing model.
3. Enforcement ladder. Rate limit per tenant (2-3x peak), daily spend cap (1.5-3x contract), kill switch on z-score > 4.
4. Dashboard. Top 5 views: per-tenant spend today, per-task cost-per-outcome, per-user distribution, cache hit rate impact, model routing split.
5. Stacked optimization audit. Check cache (Phase 17 · 14), batch (Phase 17 · 15), routing (Phase 17 · 16), gateway (Phase 17 · 19) are all engaged. Flag missing levers.
6. Review cadence. Weekly: top spenders + anomalies. Monthly: per-tenant unit-economics. Quarterly: re-triage workloads into interactive/semi/batch.
Hard rejects:
- Shipping without attribution at call site. Refuse — retroactive tagging loses ~10-30% of spend.
- Single-bucket billing. Refuse — require four token-layer breakdown.
- Kill switch with no z-score basis. Refuse — require baseline statistics before arming.
Refusal rules:
- If the product has < 10 tenants, refuse full multi-tenant enforcement — require basic per-tenant attribution first.
- If cost/outcome is undefined, refuse the dashboard — pick a unit metric first.
- If any single tenant is > 40% of total spend, require dedicated unit-economics review before the plan ships.
