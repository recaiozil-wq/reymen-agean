---
name: ecc_kubernetes-patterns_references_dry-run-to-validate-yaml
description: --- Dry-run to validate YAML ---
title: "Ecc Kubernetes Patterns References Dry Run To Validate Yaml"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_dry-run-to-validate-yaml.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# --- Dry-run to validate YAML ---
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server   # Validates against live cluster
```

### Diagnosing Common Errors

```bash
