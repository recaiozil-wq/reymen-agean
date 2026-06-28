---
skill_id: e7e29fa064d0
usage_count: 1
last_used: 2026-06-16
---
# BAD: ClusterAdmin for application service accounts
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
roleRef:
  kind: ClusterRole
  name: cluster-admin    # Grants god-mode to your app