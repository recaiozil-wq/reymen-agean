---
name: ecc_kubernetes-patterns_references_3-bind-role-to-serviceaccount
description: 3.
title: "Ecc Kubernetes Patterns References 3 Bind Role To Serviceaccount"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_3-bind-role-to-serviceaccount.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 3. Bind Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: my-namespace
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: my-namespace
roleRef:
  kind: Role
  apiGroup: rbac.authorization.k8s.io
  name: my-app-role
```

```yaml
