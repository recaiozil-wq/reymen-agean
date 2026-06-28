---
name: lm-eval-harness
description: Lm Eval Harness skill for AI/ML operations.
title: Lm Eval Harness
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

metrics, swappable adapter, and leaderboard JSON output.
## When to use
Compare two models, two checkpoints, or two prompt templates against a fixed set of tasks. Anything that ships and that you need to monitor over time.
## Task spec
One JSONL line per example:
```json
{"id": "ex-001", "prompt": "...", "targets": ["..."], "metric": "exact_match", "extras": {}}
```
All examples in a file share a metric. The file name is the task name.
## Metrics
All metrics return float in [0.0, 1.0]. Task score is the mean.
## Adapter
```python
class Adapter(Protocol):
    def generate(self, prompts: list[str]) -> list[str]: ...
```
The adapter is the only model-specific code.
## Leaderboard JSON
Schema string, timestamp, per-task scores and latency, overall mean. Include per-example records when comparing runs so prediction-level regressions are visible.
## Failure modes
- Metric returns outside [0, 1]: overall score becomes uninterpretable.
- Mixed metrics in one task file: assertion fires; keep one metric per file.
- code_exec without restricted namespace: arbitrary code execution.
- No schema string: format evolution breaks downstream dashboards.
