---
name: ecc_kubernetes-patterns_references_pod-status-and-logs
description: --- Pod status and logs ---
title: "Ecc Kubernetes Patterns References Pod Status And Logs"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_pod-status-and-logs.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Pod status and logs ---
kubectl get pods -n my-namespace
kubectl get pods -n my-namespace -o wide          # Show node assignment
kubectl describe pod <pod-name> -n my-namespace   # Events and state details
kubectl logs <pod-name> -n my-namespace           # Current logs
kubectl logs <pod-name> -n my-namespace --previous  # Logs from crashed container
kubectl logs <pod-name> -n my-namespace -c <container>  # Multi-container pod
