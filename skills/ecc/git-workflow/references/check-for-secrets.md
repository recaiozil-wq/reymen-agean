---
skill_id: c08edf781c7a
usage_count: 1
last_used: 2026-06-16
---
# Check for secrets
if git diff --cached | grep -E '(password|api_key|secret)'; then
    echo "Possible secret detected. Commit aborted."
    exit 1
fi
```

### Pre-Push Hook

```bash
#!/bin/bash