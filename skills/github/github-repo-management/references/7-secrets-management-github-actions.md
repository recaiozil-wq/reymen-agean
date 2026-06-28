---
skill_id: 793e6b710d9c
usage_count: 1
last_used: 2026-06-16
---
## 7. Secrets Management (GitHub Actions)

**With gh:**

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

**With curl:**

Secrets require encryption with the repo's public key — more involved via API:

```bash