---
skill_id: e53193d0c0a4
usage_count: 1
last_used: 2026-06-16
---
## Best Practices Checklist

### Security
- [ ] Container runs as non-root (`runAsNonRoot: true`, `runAsUser` set)
- [ ] `readOnlyRootFilesystem: true` with `emptyDir` for writable paths
- [ ] `allowPrivilegeEscalation: false`
- [ ] All capabilities dropped (`capabilities.drop: [ALL]`)
- [ ] Dedicated ServiceAccount per app, not `default`
- [ ] `automountServiceAccountToken: false` unless needed
- [ ] RBAC follows least privilege (use `Role`, not `ClusterRole` unless needed)
- [ ] Secrets managed via Sealed Secrets or External Secrets Operator

### Reliability
- [ ] All 3 probe types configured (startup + liveness + readiness)
- [ ] Resource requests AND limits set on every container
- [ ] `minReplicas: 2+` for any production workload
- [ ] PodDisruptionBudget defined for stateful or critical services
- [ ] `RollingUpdate` strategy with `maxUnavailable: 0`
- [ ] HPA configured for variable-load services

### Observability
- [ ] App exposes `/health` (liveness) and `/ready` (readiness) endpoints
- [ ] Structured JSON logging (no PII in logs)
- [ ] Resource labels: `app`, `version`, `environment`

---