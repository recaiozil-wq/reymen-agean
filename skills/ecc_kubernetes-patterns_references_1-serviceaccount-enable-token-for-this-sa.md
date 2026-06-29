---
name: ecc_kubernetes-patterns_references_1-serviceaccount-enable-token-for-this-sa
description: 1.
title: "Ecc Kubernetes Patterns References 1 Serviceaccount Enable Token For This Sa"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_1-serviceaccount-enable-token-for-this-sa.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 1. ServiceAccount — enable token for this SA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: true    # Token required: app calls K8s API
```

```yaml
