---
name: ecc_kubernetes-patterns_references_bad-clusteradmin-for-application-service-accounts
description: "BAD: ClusterAdmin for application service accounts"
title: "Ecc Kubernetes Patterns References Bad Clusteradmin For Application Service Accounts"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_bad-clusteradmin-for-application-service-accounts.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# BAD: ClusterAdmin for application service accounts
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
roleRef:
  kind: ClusterRole
  name: cluster-admin    # Grants god-mode to your app
