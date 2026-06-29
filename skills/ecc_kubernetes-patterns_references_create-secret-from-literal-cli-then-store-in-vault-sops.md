---
name: ecc_kubernetes-patterns_references_create-secret-from-literal-cli-then-store-in-vault-sops
description: Create secret from literal (CLI, then store in Vault/SOPS)
title: "Ecc Kubernetes Patterns References Create Secret From Literal Cli Then Store In Vault Sops"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_create-secret-from-literal-cli-then-store-in-vault-sops.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Create secret from literal (CLI, then store in Vault/SOPS)
kubectl create secret generic my-app-secrets \
  --from-literal=db-password='s3cr3t' \
  --namespace=my-namespace \
  --dry-run=client -o yaml | kubectl apply -f -
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
  namespace: my-namespace
type: Opaque
