---
name: ecc_kubernetes-patterns_references_crashloopbackoff-container-keeps-crashing
description: "CrashLoopBackOff: container keeps crashing"
title: "Ecc Kubernetes Patterns References Crashloopbackoff Container Keeps Crashing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_crashloopbackoff-container-keeps-crashing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# CrashLoopBackOff: container keeps crashing
kubectl logs <pod-name> --previous -n my-namespace  # Check crash logs
kubectl describe pod <pod-name> -n my-namespace     # Check exit code & OOMKilled
