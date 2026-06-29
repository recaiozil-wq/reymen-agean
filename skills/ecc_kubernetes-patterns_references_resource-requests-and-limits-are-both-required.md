---
name: ecc_kubernetes-patterns_references_resource-requests-and-limits-are-both-required
description: Resource requests AND limits are both required
title: "Ecc Kubernetes Patterns References Resource Requests And Limits Are Both Required"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_resource-requests-and-limits-are-both-required.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Resource requests AND limits are both required
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
