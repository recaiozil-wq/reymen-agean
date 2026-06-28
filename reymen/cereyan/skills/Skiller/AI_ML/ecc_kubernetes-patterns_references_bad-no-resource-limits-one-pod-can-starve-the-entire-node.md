---
name: ecc_kubernetes-patterns_references_bad-no-resource-limits-one-pod-can-starve-the-entire-node
description: "BAD: No resource limits — one pod can starve the entire node"
title: "Ecc Kubernetes Patterns References Bad No Resource Limits One Pod Can Starve The Entire Node"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_bad-no-resource-limits-one-pod-can-starve-the-entire-node.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# BAD: No resource limits — one pod can starve the entire node
containers:
  - name: app
    image: myapp:1.0.0
