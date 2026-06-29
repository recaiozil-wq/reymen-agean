---
name: ecc_kubernetes-patterns_references_clusterip-default-internal-only
description: ClusterIP (default) — internal-only
title: "Ecc Kubernetes Patterns References Clusterip Default Internal Only"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_clusterip-default-internal-only.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# ClusterIP (default) — internal-only
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: my-namespace
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  type: ClusterIP
```

```yaml
