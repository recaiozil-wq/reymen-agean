---
name: ecc_kubernetes-patterns_references_increase-memory-limits-check-for-memory-leaks
description: Increase memory limits, check for memory leaks
title: "Ecc Kubernetes Patterns References Increase Memory Limits Check For Memory Leaks"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_increase-memory-limits-check-for-memory-leaks.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Increase memory limits, check for memory leaks
kubectl describe pod <pod-name> -n my-namespace | grep -A5 "Last State"
```

---
