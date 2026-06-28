---
skill_id: febd3955f22e
usage_count: 1
last_used: 2026-06-16
---
# --- Dry-run to validate YAML ---
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server   # Validates against live cluster
```

### Diagnosing Common Errors

```bash