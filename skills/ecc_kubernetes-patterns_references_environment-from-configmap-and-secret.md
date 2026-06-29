---
name: ecc_kubernetes-patterns_references_environment-from-configmap-and-secret
description: Environment from ConfigMap and Secret
title: "Ecc Kubernetes Patterns References Environment From Configmap And Secret"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_environment-from-configmap-and-secret.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Environment from ConfigMap and Secret
          envFrom:
            - configMapRef:
                name: my-app-config
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: db-password
