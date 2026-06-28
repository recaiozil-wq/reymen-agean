---
name: ecc_kubernetes-patterns_references_if-the-app-takes-60s-to-start-set-a-startupprobe-instead
description: If the app takes 60s to start, set a startupProbe instead
title: "Ecc Kubernetes Patterns References If The App Takes 60S To Start Set A Startupprobe Instead"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_if-the-app-takes-60s-to-start-set-a-startupprobe-instead.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# If the app takes 60s to start, set a startupProbe instead
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 60   # BAD: Arbitrary wait, race condition
```

---
