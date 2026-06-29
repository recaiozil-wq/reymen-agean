---
name: ecc_mle-workflow_references_iteration-compact
description: Iteration Compact
title: "Ecc Mle Workflow References Iteration Compact"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mle-workflow_references_iteration-compact.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Iteration Compact

Before touching model code, compress the work into one reviewable artifact. This should be short enough to fit in a PR description and precise enough that another engineer can challenge the tradeoffs.

```text
Goal:
Who cares:
Decision owner:
User or system action changed by the model:
Success metric:
Guardrail metrics:
Mistake budget:
Unacceptable mistakes:
Acceptable mistakes:
Assumptions:
Constraints:
Labels and data snapshot:
Baseline:
Candidate signals:
Threshold or config plan:
Eval slices:
Known risks:
Next experiment:
Rollback or fallback:
```

This compact is the MLE equivalent of a strong SWE design note. It keeps the team from optimizing a metric no one trusts, adding features that do not address the real error mode, or shipping complexity without a rollback.
