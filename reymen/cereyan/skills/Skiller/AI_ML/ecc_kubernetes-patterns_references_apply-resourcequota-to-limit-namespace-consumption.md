---
name: ecc_kubernetes-patterns_references_apply-resourcequota-to-limit-namespace-consumption
description: Apply ResourceQuota to limit namespace consumption
title: "Ecc Kubernetes Patterns References Apply Resourcequota To Limit Namespace Consumption"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_apply-resourcequota-to-limit-namespace-consumption.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Apply ResourceQuota to limit namespace consumption
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: my-namespace-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 8Gi
    pods: "20"
EOF
```

---
