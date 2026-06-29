---
name: ecc_kubernetes-patterns_references_bad-storing-plaintext-secrets-in-configmaps
description: "BAD: Storing plaintext secrets in ConfigMaps"
title: "Ecc Kubernetes Patterns References Bad Storing Plaintext Secrets In Configmaps"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_bad-storing-plaintext-secrets-in-configmaps.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# BAD: Storing plaintext secrets in ConfigMaps
apiVersion: v1
kind: ConfigMap
data:
  DB_PASSWORD: "mysecretpassword"   # NEVER — use Secret or external secrets manager
