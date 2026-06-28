---
name: ecc_kubernetes-patterns_references_reference-in-deployment-no-token-no-api-access
description: Reference in Deployment — no token, no API access
title: "Ecc Kubernetes Patterns References Reference In Deployment No Token No Api Access"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_reference-in-deployment-no-token-no-api-access.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Reference in Deployment — no token, no API access
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      automountServiceAccountToken: false   # Belt-and-suspenders: also set at pod level
```

#### Pattern B — App DOES need the Kubernetes API (operators, controllers, config watchers)

Enable the token and grant only the permissions actually required.

```yaml
