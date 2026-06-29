---
name: ecc_mle-workflow_references_review-checklist
description: Review Checklist
title: "Ecc Mle Workflow References Review Checklist"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mle-workflow_references_review-checklist.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Review Checklist

- [ ] Prediction contract is explicit and testable
- [ ] Data contract defines entity grain, label timing, feature timing, and snapshot/version
- [ ] Leakage risks were checked against prediction-time availability
- [ ] Training is reproducible from code, config, data version, and seed
- [ ] Metrics compare against baseline and current production model
- [ ] Slice metrics and guardrails are included for high-risk cohorts
- [ ] Promotion gates are automated and fail closed
- [ ] Training and serving transformations are shared or equivalence-tested
- [ ] Model artifact carries version, config, dataset reference, and preprocessing
- [ ] Serving path validates inputs and has timeout, fallback, and rollback behavior
- [ ] Monitoring covers system health, feature drift, prediction drift, and delayed labels
- [ ] Sensitive data is excluded from artifacts, logs, prompts, and examples
