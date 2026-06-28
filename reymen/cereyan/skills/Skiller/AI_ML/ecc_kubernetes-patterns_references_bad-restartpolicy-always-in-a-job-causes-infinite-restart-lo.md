---
name: ecc_kubernetes-patterns_references_bad-restartpolicy-always-in-a-job-causes-infinite-restart-lo
description: "BAD: restartPolicy: Always in a Job (causes infinite restart loop)"
title: "Ecc Kubernetes Patterns References Bad Restartpolicy Always In A Job Causes Infinite Restart Lo"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_bad-restartpolicy-always-in-a-job-causes-infinite-restart-lo.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# BAD: restartPolicy: Always in a Job (causes infinite restart loop)
spec:
  restartPolicy: Always   # Use OnFailure or Never for Jobs
```

---
