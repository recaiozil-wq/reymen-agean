---
skill_id: 9ca04c035132
usage_count: 1
last_used: 2026-06-16
---
# Teammates just run:
git clone <repo> && cd <repo> && flox activate
```

For reusable base environments across projects, push to FloxHub:

```bash
flox push                         # Push environment to FloxHub
flox activate -r owner/env-name   # Activate remote environment anywhere
```

Compose environments with `[include]`:

```toml
[include]
base.floxhub = "myorg/python-base"

[install]