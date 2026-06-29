---
name: ecc_kubernetes-patterns_references_mount-configmap-as-a-file
description: Mount ConfigMap as a file
title: "Ecc Kubernetes Patterns References Mount Configmap As A File"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_mount-configmap-as-a-file.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Mount ConfigMap as a file
volumes:
  - name: config
    configMap:
      name: my-app-config
      items:
        - key: app.yaml
          path: app.yaml
volumeMounts:
  - name: config
    mountPath: /etc/app
    readOnly: true
```

### Secrets — Sensitive data

```bash
