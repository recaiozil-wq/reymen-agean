---
skill_id: 9722f708fa79
usage_count: 1
last_used: 2026-06-16
---
# Multi-Module Integration Patterns

## The Pattern

A Python project that has 4+ independent modules (dashboard, telegram bot,
notion writer, LLM provider) needs:
1. A shared `.env` at the root level
2. A unified `start.py` orchestrator that launches all modules
3. Proper `__init__.py` in each module directory
4. An import chain from the main entry point to each module

## Three-Layer Integration Architecture (from ReYMeN)

### Layer 1 — Module Files (EXISTENCE)
All Python files exist, no syntax errors, can be imported individually.

### Layer 2 — Integration Wiring (CONNECTION) ← MOST COMMON FAILURE
Each module is imported by the files that need it:

```
Integration Point Map:
  motor.py calistir()     -> every tool module in tools/
  main.py                 -> iteration_budget, prompt_builder, trajectory,
                             conversation_compression, credential_pool
  beyin.py                -> credential_pool, prompt_caching, nous_rate_guard
  reyment.py              -> hermes_cli/* modules
  gateway_runner.py       -> gateway/platforms/*, session, mirror
  start.py                -> checkpoint_manager, tirith_security
```

### Layer 3 — Runtime Verification (VALIDATION)
All integrations verified by test_suite.py (30+ tests covering all layers).

## Registry Pattern (for Tool Systems)

Instead of hardcoded if/else chains, use a central registry:

```python
# tool_registry.py
class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._aliases = {
            "KOMUT_CALISTIR": "shell",
            "DOSYA_YAZ": "file_ops.yaz",
            # ...
        }

    def calistir(self, ad, *args):
        # 1. Direct tool lookup
        if ad in self._tools:
            return self._tools[ad](*args)

        # 2. Alias resolution (mod.func pattern)
        alias = self._aliases.get(ad, "")
        if alias:
            parts = alias.split(".")
            if len(parts) == 2:
                mod = import_module(f"tools.{parts[0]}")
                fonk = getattr(mod, parts[1])
                return fonk(*args)
            # Single-part alias -> mod.run()
            mod = import_module(f"tools.{alias}")
            return mod.run(*args)

        return f"[Hata]: Bilinmeyen arac '{ad}'."
```

### Why Registry Beats if/else
- New tools = new file + new alias line. No need to touch motor.py.
- Aliases bridge old names (KOMUT_CALISTIR) to new module functions.
- Graceful fallback: if registry fails, if/else chain still works.

## Credential Pool Pattern

Instead of reading .env directly in every module, centralize:

```python
class CredentialPool:
    def __init__(self):
        self._sources = [
            "env_file:.env",         # project env
            "env_file:hermes.env",    # system env (fallback)
            "wcm",                    # Windows Credential Manager
        ]

    def al(self, anahtar: str) -> str:
        for source in self._sources:
            value = self._source_oku(source, anahtar)
            if value and not value.startswith("***"):
                return value
        return ""
```

This ensures:
- API keys found somewhere even if project .env has *** placeholder
- Centralized logging of which source provided each key
- Easy addition of new sources (Bitwarden, 1Password, etc.)

## Integration Verification Flow

```
Step 1: Import chain test
  python -c "from main import X; from motor import Y; from beyin import Z"

Step 2: Registry tool test
  python -c "from tool_registry import ToolRegistry; r=ToolRegistry(); print(r.calistir('KOMUT_CALISTIR', 'echo test'))"

Step 3: Full test suite
  python test_suite.py

Step 4: Runtime test (if LLM available)
  python -c "from main import AIAgentOrchestrator; a=AIAgentOrchestrator(config={...}, max_tur=2)"
```

## Integration Checklist

- [ ] All module directories exist under the project root
- [ ] Each module has `__init__.py` (for explicit imports)
- [ ] Root `.env` contains ALL environment variables needed by ALL modules
- [ ] Sub-module `.env` files exist only as optional overrides
- [ ] `start.py` loads root `.env` before any sub-module imports
- [ ] Module-level `requirements.txt` files are aggregated into root
- [ ] Main entry point (main.py) can import all modules
- [ ] Gateway/service layer can launch sub-modules as subprocesses
- [ ] Registry pattern used instead of hardcoded if/else chains
- [ ] Credential pool used instead of direct .env reads
- [ ] Integration tests exist and pass (test_suite.py)
- [ ] ALL integration points verified: motor + main + beyin + CLI + gateway

## start.py Orchestrator Template

```python
import subprocess, sys, time
from pathlib import Path
from dotenv import load_dotenv

PROJE_KOK = Path(__file__).parent.resolve()
load_dotenv(PROJE_KOK / ".env", override=True)

class Servis:
    def __init__(self, ad, path, env=None):
        self.ad = ad
        self.path = path
        self.env = env or dict(os.environ)

    def baslat(self):
        self.process = subprocess.Popen(
            [sys.executable, str(self.path)],
            cwd=str(PROJE_KOK),
            env=self.env,
        )
```

## Common Issues

1. **Duplicate .env files** — Root .env has ALL vars, sub-module .env is local dev only.
2. **Import path confusion** — When a sub-module is run as subprocess, use `sys.path.insert(0, str(PROJE_KOK))`.
3. **Port conflicts** — Make ports configurable via .env.
4. **Shared data corruption** — Use SQLite or file locks instead of shared JSON.
5. **Files exist but NOT wired** — The most common failure. Files in tools/ don't do anything until motor.py imports them.
6. **Registry has tools but if/else has duplicates** — Keep registry as primary, if/else as fallback only. Never maintain both.
