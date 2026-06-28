---
skill_id: f38975008fe1
usage_count: 1
last_used: 2026-06-16
---
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