---
skill_id: 44f5e7566d99
usage_count: 1
last_used: 2026-06-16
---
# GOOD — skip if already installed
[hook]
on-activate = """
  if [ ! -f "$FLOX_ENV_CACHE/.deps_installed" ]; then
    uv pip install -r requirements.txt --quiet
    touch "$FLOX_ENV_CACHE/.deps_installed"
  fi
"""
```

### Putting User Commands in Hooks

```toml