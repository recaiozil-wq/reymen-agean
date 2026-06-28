---
name: ecc_kubernetes-patterns_references_port-forward-for-local-debugging
description: --- Port-forward for local debugging ---
title: "Ecc Kubernetes Patterns References Port Forward For Local Debugging"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_port-forward-for-local-debugging.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Port-forward for local debugging ---
kubectl port-forward pod/<pod-name> 8080:8080 -n my-namespace
kubectl port-forward svc/my-app 8080:80 -n my-namespace
