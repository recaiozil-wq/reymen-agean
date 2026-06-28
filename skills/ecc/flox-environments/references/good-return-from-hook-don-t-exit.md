---
skill_id: 439cb68627ee
usage_count: 1
last_used: 2026-06-16
---
# GOOD — return from hook, don't exit
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config — run setup first"
    return 1
  fi
"""
```

### Storing Secrets in Manifest

```toml