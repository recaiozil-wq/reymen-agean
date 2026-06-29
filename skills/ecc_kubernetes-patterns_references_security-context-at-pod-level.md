---
name: ecc_kubernetes-patterns_references_security-context-at-pod-level
description: Security context at pod level
title: "Ecc Kubernetes Patterns References Security Context At Pod Level"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_security-context-at-pod-level.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Security context at pod level
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
