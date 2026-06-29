---
name: ecc_kubernetes-patterns_references_2-role-grant-only-what-the-app-needs-namespace-scoped
description: 2.
title: "Ecc Kubernetes Patterns References 2 Role Grant Only What The App Needs Namespace Scoped"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_2-role-grant-only-what-the-app-needs-namespace-scoped.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 2. Role — grant only what the app needs (namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]    # Read-only, specific resource
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secrets"]  # Restrict to specific secret by name
    verbs: ["get"]
```

```yaml
