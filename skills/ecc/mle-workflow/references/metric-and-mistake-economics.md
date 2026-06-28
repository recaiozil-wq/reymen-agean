---
skill_id: 8862065883d8
usage_count: 1
last_used: 2026-06-16
---
## Metric and Mistake Economics

Choose metrics from failure costs, not habit:

- Use a confusion matrix early so the team can discuss concrete false positives and false negatives instead of abstract accuracy.
- Favor precision when the cost of an incorrect positive decision dominates.
- Favor recall when the cost of a missed positive dominates.
- Use F1 only when the precision/recall tradeoff is genuinely balanced and explainable.
- Use AUC or ranking metrics when ordering quality matters more than a single threshold.
- Track latency, throughput, memory, and cost as first-class metrics because they shape feasible model complexity.
- Compare against a baseline and the current production model before celebrating an offline gain.
- Treat real-world feedback signals as delayed labels with bias, lag, and coverage gaps; do not treat them as ground truth without analysis.

Every metric choice should state which mistake it makes cheaper, which mistake it makes more likely, and who absorbs that cost.