---
name: ecc_mle-workflow_references_data-and-feature-hypotheses
description: Data and Feature Hypotheses
title: "Ecc Mle Workflow References Data And Feature Hypotheses"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mle-workflow_references_data-and-feature-hypotheses.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Data and Feature Hypotheses

Features should come from a theory of separation:

- Text, categorical fields, numeric histories, graph relationships, recency, frequency, and aggregates are candidate signal families, not automatic features.
- For every feature family, state why it should separate outcomes and how it could leak future information.
- For noisy labels, consider adjudication, label confidence, soft targets, or confidence weighting.
- For class imbalance, compare weighted loss, resampling, threshold movement, and calibrated decision rules.
- For missing values, decide whether absence is informative, imputable, or a reason to abstain.
- For outliers, decide whether to clip, bucket, investigate, or preserve them as rare but important signal.
- For correlated features, check whether they are redundant, unstable, or proxies for unavailable future state.

Do not add model complexity until error analysis shows that the baseline is failing for a reason additional signal or capacity can plausibly fix.
