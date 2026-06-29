---
name: ecc_kubernetes-patterns_references_configmaps-and-secrets
description: ConfigMaps and Secrets
title: "Ecc Kubernetes Patterns References Configmaps And Secrets"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_configmaps-and-secrets.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## ConfigMaps and Secrets

### ConfigMap — Non-sensitive configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: my-namespace
data:
  LOG_LEVEL: "info"
  APP_ENV: "production"
  MAX_CONNECTIONS: "100"
