---
name: ecc_kubernetes-patterns_references_serviceaccount-with-token-disabled-safest-default
description: ServiceAccount with token disabled — safest default
title: "Ecc Kubernetes Patterns References Serviceaccount With Token Disabled Safest Default"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_serviceaccount-with-token-disabled-safest-default.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# ServiceAccount with token disabled — safest default
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: false   # No K8s API token injected into pods
```

```yaml
