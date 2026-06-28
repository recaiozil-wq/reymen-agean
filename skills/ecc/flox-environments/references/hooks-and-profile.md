---
skill_id: 9c0faa17d266
usage_count: 1
last_used: 2026-06-16
---
## Hooks and Profile

### Hooks — Non-Interactive Setup

Hooks run on every activation. Keep them fast and idempotent. Rule of thumb: **if it should happen automatically, put it in `[hook]`; if the user should be able to type it, put it in `[profile]`.**

```toml
[hook]
on-activate = """
  setup_database() {
    if [ ! -d "$FLOX_ENV_CACHE/pgdata" ]; then
      initdb -D "$FLOX_ENV_CACHE/pgdata" --no-locale --encoding=UTF8
    fi
  }
  setup_database
"""
```

### Profile — Interactive Shell Configuration

Profile code is available in the user's shell session.

```toml
[profile]
common = """
  dev() { npm run dev; }
  test() { npm run test -- "$@"; }
"""
```