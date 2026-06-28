---
skill_id: c44780f03901
usage_count: 1
last_used: 2026-06-16
---
# .env → Config Wiring Patterns

## The Problem

Many Python projects have a hardcoded `CONFIG` dict at the top of `main.py`. Environment variables from `.env` are never read, so API keys set in `.env` have no effect.

## The Fix: _env_anahtar() Helper

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env FIRST
DOT_ENV = Path(__file__).parent / ".env"
if DOT_ENV.exists():
    load_dotenv(DOT_ENV, override=True)

def _env_anahtar(anahtar, varsayilan=""):
    """Read env var from os.environ, ignore masked (***) values.
    Use startswith() not == because *** might have trailing text."""
    deger = os.environ.get(anahtar, "").strip()
    if not deger or deger.startswith("***") or deger == "...":
        return varsayilan
    return deger
```

## Usage in CONFIG

Replace hardcoded values:

```python
# BEFORE (hardcoded, broken):
CONFIG = {
    "default_model": "llava-v1.6-mistral-7b",
    "providers": {
        "deepseek": {"api_key": ""},  # always empty
    },
}

# AFTER (reads from .env):
CONFIG = {
    "default_model": _env_anahtar("ReYMeN_DEFAULT_MODEL", "llava-v1.6-mistral-7b"),
    "providers": {
        "deepseek": {
            "api_key": _env_anahtar("DEEPSEEK_API_KEY"),
        },
    },
    "fallback_model": {
        "api_key": _env_anahtar("DEEPSEEK_API_KEY"),
    } if _env_anahtar("DEEPSEEK_API_KEY") else None,  # None if key missing
}
```

## Key Details

- **`***` detection** — Users often share `.env` files with `***` as placeholder. The helper must treat these as empty.
- **Fallback with `None`** — If a fallback provider has no API key, set the whole fallback block to `None` rather than keeping a broken entry.
- **`dotenv` import safety** — If `dotenv` isn't installed, `load_dotenv()` fails silently. Pre-install via `pip install python-dotenv` or handle the ImportError.
- **`override=True`** — Ensures .env values override any pre-existing environment variables (e.g. from system env or parent process).
- **os.environ vs reading file directly** — Always use `os.environ` after `load_dotenv()`, not direct file reads. This allows environment injection from Docker, CI, or parent processes.

## Multi-Module Projects

When a project has sub-modules with their own `.env` files (e.g. `llm_provider/.env`, `telegram_bot/.env`):

1. The **root `.env`** should contain ALL variables
2. Sub-module `.env` files are optional overrides
3. `start.py` or the main entry point should load the root `.env` before any sub-module imports

```python
# In start.py or main.py:
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV = Path(__file__).parent / ".env"
if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV, override=True)
```
