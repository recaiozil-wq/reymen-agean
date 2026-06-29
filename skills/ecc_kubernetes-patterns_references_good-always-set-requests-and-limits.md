---
name: ecc_kubernetes-patterns_references_good-always-set-requests-and-limits
description: "GOOD: Always set requests and limits"
title: "Ecc Kubernetes Patterns References Good Always Set Requests And Limits"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_good-always-set-requests-and-limits.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# GOOD: Always set requests and limits
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
