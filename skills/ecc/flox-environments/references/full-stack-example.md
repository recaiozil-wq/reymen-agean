---
skill_id: c61844387b01
usage_count: 1
last_used: 2026-06-16
---
## Full-Stack Example

A complete environment for a Python API with PostgreSQL:

```toml
[install]
python.pkg-path = "python311"
uv.pkg-path = "uv"
postgresql.pkg-path = "postgresql_16"
redis.pkg-path = "redis"
jq.pkg-path = "jq"
curl.pkg-path = "curl"

[vars]
UV_CACHE_DIR = "$FLOX_ENV_CACHE/uv-cache"
DATABASE_URL = "postgres://localhost:5432/myapp"
REDIS_URL = "redis://localhost:6379"

[hook]
on-activate = """
  if [ ! -d "$FLOX_ENV_CACHE/pgdata" ]; then
    initdb -D "$FLOX_ENV_CACHE/pgdata" --no-locale --encoding=UTF8
  fi

  venv="$FLOX_ENV_CACHE/venv"
  if [ ! -d "$venv" ]; then
    uv venv "$venv" --python python3
  fi
  if [ -f "$venv/bin/activate" ]; then
    source "$venv/bin/activate"
  fi

  if [ -f requirements.txt ] && [ ! -f "$FLOX_ENV_CACHE/.deps_installed" ]; then
    uv pip install --python "$venv/bin/python" -r requirements.txt --quiet
    touch "$FLOX_ENV_CACHE/.deps_installed"
  fi
"""

[profile]
common = """
  serve() { uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; }
  migrate() { alembic upgrade head; }
"""

[services]
postgres.command = "postgres -D $FLOX_ENV_CACHE/pgdata -k $FLOX_ENV_CACHE"
redis.command = "redis-server --port 6379 --daemonize no"

[options]
systems = ["x86_64-linux", "aarch64-linux", "x86_64-darwin", "aarch64-darwin"]
```

Activate with services: `flox activate --start-services`