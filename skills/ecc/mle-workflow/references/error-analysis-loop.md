---
skill_id: 374ff3f78512
usage_count: 1
last_used: 2026-06-16
---
## Error Analysis Loop

After each baseline, training run, threshold change, or config change:

1. Split mistakes into false positives, false negatives, abstentions, low-confidence cases, and system failures.
2. Cluster errors by shared traits: language, entity type, source, time, geography, device, sparsity, recency, feature freshness, label source, or model version.
3. Separate model mistakes from data bugs, label ambiguity, product ambiguity, instrumentation gaps, and serving mismatches.
4. Trace each major cluster to one of four moves: better labels, better features, better threshold/config, or better product fallback.
5. Preserve every important mistake as a regression test, eval slice, dashboard panel, or runbook entry.
6. Write the next iteration as a falsifiable experiment, not a vague "improve model" task.

The strongest MLE loop is not train -> metric -> ship. It is mistake -> cluster -> hypothesis -> experiment -> evidence -> simpler system.