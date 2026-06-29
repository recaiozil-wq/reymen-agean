---
name: ai-sre-plan
description: Ai Sre Plan skill for AI/ML operations.
title: Ai Sre Plan
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

structured runbooks, adversarial evaluation, narrow auto-remediation, and predictive-detection
  posture.
Given team size, incident volume, observability maturity, and risk tolerance, produce an AI SRE plan.
1. Architecture. Multi-agent: supervisor + log agent + metric agent + runbook agent + human gate. Match specialized agents to existing data sources (Datadog, Grafana, Loki, Confluence).
2. Runbook transformation. Move from unstructured Confluence to structured markdown with symptom / hypothesis / verify / act sections. Version in git.
3. Product choice. Datadog Bits AI, Azure SRE Agent, NeuBird Hawkeye, Incident.io Autopilot, or DIY.
4. Auto-remediation scope. Narrow safe set (restart pod, revert deploy, scale within bounds). Explicit deny list (topology, code, IAM, database). Policy as code.
5. Adversarial evaluation. Specify two-model agreement gate for auto-remediation. Disagreement escalates.
6. Predictive-detection posture. If considering (MIT 89% result), name the actuation policy — pager, pre-drain, auto-scale — otherwise it's just a dashboard.
Hard rejects:
- Auto-remediation without human gate on broad changes. Refuse — name the safe set explicitly.
- Unstructured runbooks as the knowledge base. Refuse — require structured, versioned markdown.
- "Set it and forget it" framing. Refuse — explicitly scope what is and isn't autonomous.
Refusal rules:
- If incident volume is <10/month, refuse full AI SRE rollout — cost exceeds benefit. Recommend structured runbooks only.
- If team observability is immature (logs unsearchable, metrics sparse), refuse — AI SRE amplifies bad data.
- If the team proposes "predictive detection → auto-remediation" as first feature, refuse — walk through the actuation-policy question first.
