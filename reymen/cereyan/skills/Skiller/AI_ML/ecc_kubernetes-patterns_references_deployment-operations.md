---
name: ecc_kubernetes-patterns_references_deployment-operations
description: --- Deployment operations ---
title: "Ecc Kubernetes Patterns References Deployment Operations"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_deployment-operations.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Deployment operations ---
kubectl rollout status deployment/my-app -n my-namespace
kubectl rollout history deployment/my-app -n my-namespace
kubectl rollout undo deployment/my-app -n my-namespace      # Rollback
kubectl rollout undo deployment/my-app --to-revision=2 -n my-namespace
