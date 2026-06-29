---
name: ecc_kubernetes-patterns_references_horizontal-pod-autoscaler-hpa
description: Horizontal Pod Autoscaler (HPA)
title: "Ecc Kubernetes Patterns References Horizontal Pod Autoscaler Hpa"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_horizontal-pod-autoscaler-hpa.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: my-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2      # Always at least 2 for HA
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # Scale up when avg CPU > 70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

> HPA requires `resources.requests` to be set on all containers — it calculates utilization as `current / request`.
