---
name: ecc_kubernetes-patterns_references_inspect-events-cluster-wide-issues
description: --- Inspect events (cluster-wide issues) ---
title: "Ecc Kubernetes Patterns References Inspect Events Cluster Wide Issues"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_inspect-events-cluster-wide-issues.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Inspect events (cluster-wide issues) ---
kubectl get events -n my-namespace --sort-by='.lastTimestamp'
