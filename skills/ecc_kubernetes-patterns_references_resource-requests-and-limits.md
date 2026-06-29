---
name: ecc_kubernetes-patterns_references_resource-requests-and-limits
description: Resource Requests and Limits
title: "Ecc Kubernetes Patterns References Resource Requests And Limits"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_resource-requests-and-limits.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Resource Requests and Limits

```yaml
resources:
  requests:       # Scheduler uses this to place the pod
    cpu: "100m"   # 100 millicores = 0.1 CPU
    memory: "128Mi"
  limits:         # Container is killed/throttled above this
    cpu: "500m"
    memory: "256Mi"
```

**Rules of thumb:**

| Workload Type | CPU Request | Memory Request | Notes |
|---------------|-------------|----------------|-------|
| Web API | 100–250m | 128–256Mi | Set limits 2-4x requests |
| Worker/consumer | 250–500m | 256–512Mi | Memory limit = request for predictability |
| JVM app | 500m–1 | 512Mi–2Gi | Allow headroom above `-Xmx` for JVM overhead |
| Sidecar | 10–50m | 32–64Mi | Keep minimal |

```yaml
