---
name: ecc_kubernetes-patterns_references_rbac-roles-and-serviceaccounts
description: RBAC — Roles and ServiceAccounts
title: "Ecc Kubernetes Patterns References Rbac Roles And Serviceaccounts"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_rbac-roles-and-serviceaccounts.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## RBAC — Roles and ServiceAccounts

### Principle of Least Privilege

**Two patterns depending on whether the app calls the Kubernetes API:**

#### Pattern A — App does NOT need the Kubernetes API (most apps)

Disable token automounting on the ServiceAccount. The Role/RoleBinding are not needed.

```yaml
