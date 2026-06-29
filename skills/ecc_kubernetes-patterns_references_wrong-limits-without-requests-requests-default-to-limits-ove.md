---
name: ecc_kubernetes-patterns_references_wrong-limits-without-requests-requests-default-to-limits-ove
description: "WRONG: Limits without requests — requests default to limits, over-reserves capacity"
title: "Ecc Kubernetes Patterns References Wrong Limits Without Requests Requests Default To Limits Ove"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_wrong-limits-without-requests-requests-default-to-limits-ove.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# WRONG: Limits without requests — requests default to limits, over-reserves capacity
resources:
  limits:
    cpu: "2"
    memory: "1Gi"
