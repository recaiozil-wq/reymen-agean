---
name: ecc_kubernetes-patterns_references_good-non-root-with-explicit-uid
description: "GOOD: Non-root with explicit UID"
title: "Ecc Kubernetes Patterns References Good Non Root With Explicit Uid"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_good-non-root-with-explicit-uid.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# GOOD: Non-root with explicit UID
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
