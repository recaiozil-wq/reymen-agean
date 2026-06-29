---
name: ecc_kubernetes-patterns_references_execute-into-a-running-container
description: --- Execute into a running container ---
title: "Ecc Kubernetes Patterns References Execute Into A Running Container"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_execute-into-a-running-container.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Execute into a running container ---
kubectl exec -it <pod-name> -n my-namespace -- sh
kubectl exec -it <pod-name> -n my-namespace -- bash
