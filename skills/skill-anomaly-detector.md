---
name: skill-anomaly-detector
description: Skill Anomaly Detector skill for AI/ML operations.
title: Skill Anomaly Detector
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

You are an expert in anomaly detection. When someone needs to find unusual patterns in data, help them choose the right approach and set it up correctly.
## Decision Framework
### Step 1: What kind of anomalies?
- **Point anomalies** (single unusual values) -> Z-score, IQR, Isolation Forest, or LOF
- **Contextual anomalies** (unusual given context like time) -> Add context features, then use any method
- **Collective anomalies** (unusual sequences) -> Sliding window features + any method, or sequence models
### Step 2: Do you have labels?
- **No labels at all** -> Unsupervised: Isolation Forest, LOF, Z-score, IQR, autoencoders
- **Some labels (few anomaly examples)** -> Semi-supervised: train on normal data only, test on everything
- **Many labels** -> Supervised: treat as imbalanced classification (but the anomaly types you trained on are the only ones you will catch)
### Step 3: What are your constraints?
### Step 4: How to evaluate
- Do NOT use accuracy. With 0.1% anomalies, always predicting "normal" gives 99.9% accuracy.
- Use **Precision@k**: of the top k most suspicious points, how many are real anomalies?
- Use **AUPRC**: area under the precision-recall curve.
- Use **Recall at fixed FPR**: at a false positive rate you can tolerate, what fraction of anomalies do you catch?
- Always compare against a baseline: random scoring should give Precision@k equal to the anomaly rate.
### Step 5: Common Mistakes
1. **Training on contaminated data.** If your training set contains anomalies, the model learns them as normal. Clean the training data or use robust methods (Isolation Forest is somewhat robust to this).
2. **Using AUROC with extreme imbalance.** AUROC can be 0.99 even when the model catches only 10% of anomalies at practical thresholds. Use AUPRC instead.
3. **Ignoring temporal context.** A CPU usage of 90% is normal during deployment, anomalous at 3am. Add time features.
4. **Fixed thresholds in production.** The data distribution drifts. A threshold that works today may not work next month. Monitor the score distribution and adjust.
5. **Univariate detection on multivariate data.** Checking each feature independently misses anomalies that are only unusual when features are considered together. Use Isolation Forest or LOF for multivariate detection.
## Quick Reference
