---
name: ecc_kubernetes-patterns_references_poddisruptionbudget-pdb
description: PodDisruptionBudget (PDB)
title: "Ecc Kubernetes Patterns References Poddisruptionbudget Pdb"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_poddisruptionbudget-pdb.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## PodDisruptionBudget (PDB)

Prevent too many pods going down during node drains or rolling updates:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: my-namespace
spec:
  minAvailable: 2           # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```
