---
skill_id: 6c60de700d66
usage_count: 1
last_used: 2026-06-16
---
## RBAC — Roles and ServiceAccounts

### Principle of Least Privilege

**Two patterns depending on whether the app calls the Kubernetes API:**

#### Pattern A — App does NOT need the Kubernetes API (most apps)

Disable token automounting on the ServiceAccount. The Role/RoleBinding are not needed.

```yaml