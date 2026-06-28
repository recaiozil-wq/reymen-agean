---
name: ecc_kubernetes-patterns_references_values-are-base64-encoded-not-encrypted-use-sealed-secrets-o
description: Values are base64-encoded (NOT encrypted — use Sealed Secrets or ESO for real encryption)
title: "Ecc Kubernetes Patterns References Values Are Base64 Encoded Not Encrypted Use Sealed Secrets O"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_values-are-base64-encoded-not-encrypted-use-sealed-secrets-o.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Values are base64-encoded (NOT encrypted — use Sealed Secrets or ESO for real encryption)
data:
  db-password: czNjcjN0  # base64 of 's3cr3t'
```

> **Important:** Raw Kubernetes Secrets are only base64-encoded, not encrypted at rest unless your cluster has encryption configured. Use [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) or [External Secrets Operator](https://external-secrets.io) for production.

---
