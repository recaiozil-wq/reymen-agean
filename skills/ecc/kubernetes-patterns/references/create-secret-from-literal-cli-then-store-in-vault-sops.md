---
skill_id: 27efd44dd70f
usage_count: 1
last_used: 2026-06-16
---
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