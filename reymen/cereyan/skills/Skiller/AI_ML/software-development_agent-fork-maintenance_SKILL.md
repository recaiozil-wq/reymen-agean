---
name: software-development-agent-fork-maintenance
description: Maintain, audit and improve a forked AI agent project. Designed for the
  ReYMeN (Hermes Agent fork) pattern but generalizes to any fork.
title: Software Development Agent Fork Maintenance
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

fork of Hermes Agent). Covers: fork health audit, dead file cleanup, try/except
  fix, provider routing with circuit breaker, upstream sync setup, duplicate resolution,
  and structured reporting.'
# Agent Fork Maintenance

Maintain, audit and improve a forked AI agent project. Designed for the ReYMeN (Hermes Agent fork) pattern but generalizes to any fork.

## User Preferences (ReYMeN Fork)

- **Brand identity:** All "Hermes" references in ReYMeN's own code (comments, docstrings, file names, directory names, test paths) MUST be renamed to "ReYMeN". The upstream name belongs to the upstream project; the fork has its own brand.
- **Preserve unmodified:** Actual system paths (`~/AppData/Local/hermes/`, `C:\\Users\\...\\hermes\\`), env vars (`HERMES_HOME`, `HERMES_API_KEY`), installed package names (`hermes_cli`, `hermes-agent`), and upstream backup directories (`agent/`) stay as-is — they refer to upstream infrastructure, not the fork's brand.
- **Method:** See `references/branding-rename-pattern.md` for the systematic find-and-replace approach.

## Workflow

### Phase 1: Fork Health Audit

Run these checks to understand fork state:

```bash
# Python file count
ls *.py | wc -l

# Check for duplicate files between root and agent/ style subdirs
ls agent/*.py 2>/dev/null | xargs -n1 basename | while read f; do
  [ -f "$f" ] && echo "DUPLICATE: $f"
done
```

```python
# Silent except census
from pathlib import Path
proj = Path(".")

for py in proj.glob("*.py"):
    lines = py.read_text().split("\n")
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("except") and i < len(lines):
            if lines[i].strip() == "pass":
                print(f"SILENT {py.name}:{i} | {s}")
```

**Key metrics to report:**
| Metric | What It Tells |
|--------|---------------|
| Total `.py` files | Codebase size |
| Root vs agent/ duplicates | Fork cleanliness |
| Silent except blocks | Error handling quality |
| Protected files count | Upstream sync risk |
| Dead/temp files | Codebase hygiene |

### Phase 2: Dead File Cleanup

Identify and quarantine unnecessary files:

**Trash categories:**
- Log files: `*.log`, `bot_*.log`
- Temporary/test output: `_test_progress*.txt`, `_raporu.txt`
- Backup archives: `*.zip` in root
- Old Claude conversation dumps: `claude_*.txt`
- Generated reports: `*_RAPORU.md`, `*_ANALIZ_*.md`
- Duplicate/backup modules: `*_backup.py`, `*.py.bak`
- Setup scripts used once: `setup_*.py`, `set_*.py`

**Move pattern:**
```python
import shutil
from pathlib import Path

proje = Path(".")
hedef = Path.home() / "Desktop" / "PROJE_olu_dosyalar"
hedef.mkdir(parents=True, exist_ok=True)

dead = ["bot.log", "test_output.txt", ...]  # file list
for f in dead:
    src = proje / f
    if src.exists():
        shutil.move(str(src), str(hedef / f))
```

### Phase 3: Fix Silent Except Blocks

See `python-error-handling-audit` skill for the full pipeline.

Key points:
- Batch-fix with regex across ALL files at once
- `except X: as _var:` → `except X as _var:` (colon before as removal)
- `except: as _var:` → `except Exception as _var:` (bare except fix)
- Fix indentation of next line after except
- COMPILE-VERIFY every file after changes

### Phase 4: Duplicate Resolution

When root and `agent/` dir have the same files:

1. Check which ones ReYMeN-specific code actually imports from root
2. Remove root duplicates NOT imported by any ReYMeN file
3. Keep root versions for imports ReYMeN customizes
4. agent/ directory keeps the upstream originals

**Check imports:**
```python
reyimen_files = [f for f in proj.iterdir() if f.suffix == ".py" and not (agent_dir / f.name).exists()]
for f in reyimen_files:
    for dup in duplicates:
        if dup.replace(".py", "") in f.read_text():
            print(f"USED: {dup}")
```

### Phase 5: Provider Routing with Circuit Breaker

Add intelligent provider failover to a `beyin.py`-style LLM router:

**Components:**
1. `provider_router.py` — Circuit breaker + health check + scoring
2. Integration into `Beyin.dusun()` — Skip blacklisted providers, report success/failure

**Circuit breaker config:**
```python
_BREAKER_HATA_LIMITI = 2       # Errors before blacklist
_BREAKER_BEKLEME_SN = 120      # Seconds in blacklist
_PING_TIMEOUT_SN = 5           # Health check timeout
```

**Scoring (local first):**
```python
_LOCAL_PROVIDERS = {"lmstudio", "ollama"}  # Highest priority
_KARMA_PROVIDERS = {"groq", "gemini"}      # Medium priority
# API providers = lowest priority
```

**Integration points in Beyin.dusun():**
1. Filter out blacklisted providers: `[a for a in chain if router.aktif_mi(a.provider)]`
2. Sort by score: `chain = router.sirala(chain)`
3. On success: `router.basari_bildir(provider)`
4. On failure: `router.hata_bildir(provider)` — auto-blacklists after 2 failures

**CLI command: `/routing`** shows all provider health status.

### Phase 6: Upstream Git Sync

Set up proper fork update flow:

1. Add upstream remote:
```bash
git remote add upstream https://github.com/ORIGINAL_REPO/ORIGINAL_PROJECT.git
```

2. Update only the `agent/` subdirectory:
```bash
git fetch upstream main
git checkout upstream/main -- agent/
```

3. Protect custom files (never overwrite):
```bash
for f in main.py beyin.py motor.py hata_cozucu.py tor_otomasyonu.py; do
    git checkout HEAD -- "$f" 2>/dev/null || true
done
```

**`.ReYMeN_sync.sh` script:**
- `--sync` → fetch upstream, update agent/, protect ReYMeN files
- `--diff` → show agent/ changes
- `--reset` → force-reset agent/ from upstream (with confirmation)
- Default → show status

### Phase 7: Reporting

Always close with a summary table:

```markdown
| # | Değişiklik | Detay |
|:-:|-----------|-------|
| 🗑️ | N duplicate cleaned | Path to quarantine |
| 🔧 | M files fixed | What was fixed |
| 📁 | New module added | Path and purpose |
```

### Phase 8: Test File Organization

After cleanup, consolidate scattered test files into a proper `tests/` directory.

#### 8a. Inventory & Move

1. **Inventory:** Find all `test_*.py` files in root:
```bash
ls test_*.py 2>/dev/null
```

2. **Check existing `tests/` structure:**
```bash
ls tests/*.py 2>/dev/null | head -5
find tests/ -type d | head -10
```

3. **Categorize and move:**
   - Core module tests → `tests/test_<modul>.py`
   - Tool tests → `tests/tools/test_<tool>.py`
   - Gateway tests → `tests/gateway/test_<platform>.py`
   - Windows automation tests → `tests/windows/test_<ozellik>.py`

4. **Move command:**
```python
import shutil
from pathlib import Path

proje = Path(".")
hedef = proje / "tests" / "<category>"
hedef.mkdir(parents=True, exist_ok=True)

for f in proje.glob("test_*.py"):
    if (hedef / f.name).exists():
        print(f"⚠️  {f.name} already in tests/<category>/, skipping")
    else:
        shutil.move(str(f), str(hedef / f.name))
        print(f"✅ {f.name} → tests/<category>/")
```

5. **Verify after move:**
```bash
ls test_*.py 2>/dev/null | wc -l     # Expected: 0 (all moved)
ls tests/<category>/*.py 2>/dev/null | wc -l  # Expected: N
```

6. **Clean up `__pycache__` in root:**
```python
import shutil
from pathlib import Path
pycache = Path(".") / "__pycache__"
if pycache.exists():
    shutil.rmtree(pycache)
```

#### 8b. Fix Namespace `__path__` Conflicts

When `tests/tools/` (or any test subdir) has an `__init__.py` that redirects the package namespace via `__path__`, **pytest cannot collect local test files** in that directory — Python resolves the module through the redirected path, not the actual filesystem.

**Symptoms:** `ModuleNotFoundError: No module named 'tests.tools.test_<name>'` despite the file existing.

**Root cause:** A single-element `__path__` like:
```python
# tests/tools/__init__.py — BROKEN for local test files
from pathlib import Path as _Path
__path__ = [str(_Path(__file__).parent.parent / "ReYMeN_reference" / "tools")]
```
This replaces the module path entirely, so Python never sees the `tests/tools/` directory on disk.

**Fix:** Include BOTH paths (local first for priority, upstream second):
```python
# tests/tools/__init__.py — WORKS for both sets
from pathlib import Path as _Path
__path__ = [
    str(_Path(__file__).parent),                       # Local (fork) tests first
    str(_Path(__file__).parent.parent / "ReYMeN_reference" / "tools"),  # Upstream tests second
]
```

After this fix, pytest discovers both local AND upstream reference tests. Run to verify:
```bash
python -m pytest tests/tools/ -q --tb=short | tail -10
```

#### 8c. Handle Fork-Specific Test Failures

After consolidation, ReYMeN test files that were COPIED from upstream may fail because the fork's tool API differs from upstream:

| Failure Pattern | Cause | Fix |
|----------------|-------|-----|
| `run()` accepts different command names | Fork uses Turkish cmd names, test expects English (or vice versa) | Add alias dict to the tool module, OR update test to match actual API |
| `AttributeError: module has no attribute 'X'` | Test references upstream internal functions the fork removed/renamed | Either restore the function, remove the test, or move it to `tests/ReYMeN_reference/` |
| `ModuleNotFoundError: numpy` | Test depends on a package not in the fork's venv | Install dep or skip test |
| 20+ unexpected failures | Likely the namespace `__path__` is pulling tests from the wrong source | Apply fix from Phase 8b, then triage remaining failures by category |

**Turkish API alias pattern** — When the fork's tools use English commands but tests expect Turkish (or vice versa), add a lightweight alias dict at the top of the `run()` function (see `references/turkish-api-aliases.md` for the full pattern with placement rules and edge cases):

```python
def run(islem: str = "", **kwargs) -> str:
    # Türkçe → İngilizce alias mapping
    _alias = {
        "ac": "navigate",
        "kapat": "back",
        "tikla": "click",
        "yaz": "type",
        "kaydir": "scroll",
        "goruntu": "snapshot",
        "gorsel": "vision",
        "durum": "status",
    }
    islem = _alias.get(islem, islem)
    # ... rest of the function uses English command names
```

**Triage strategy for remaining failures:**
1. Tests that test the upstream API → move to `tests/ReYMeN_reference/<category>/`
2. Tests that test ReYMeN API but expect wrong behavior → fix the test
3. Tests that test ReYMeN API correctly but tool is missing a feature → add the feature to the tool
4. Tests with missing dependencies → install dep, add to requirements, or skip with `@pytest.mark.skipif`

**Reference:** See `references/test-organization-patterns.md` for detailed category mapping.

### Phase 9: Windows Automation Event Bus Integration

Connect disparate Windows automation modules (error watchdog, Tor automation, target finder, crash reporter) through a central event system.

**Core components:**

1. `windows_events.py` — Thread-safe event bus (singleton):
   - `WindowsEventBus.dinle(tip, fonk)` — Register a listener
   - `WindowsEventBus.yayinla(tip, veri)` — Fire an event
   - `WindowsEventBus.son_olaylar(n)` — Last N events for debugging
   - Built-in event types: `OLAY_HATA`, `OLAY_NISAN`, `OLAY_TOR_HATA`, `OLAY_COKUS`, `OLAY_TOR_BASARILI`, `OLAY_COZUM_UYGULANDI`

2. `windows_entegrasyon.py` — Wiring layer:
   - `windows_entegrasyonu_baslat()` → Connects all modules via event bus
   - Graceful degradation: missing modules silently skipped (try/except)

**Connection map:**
```
tor_otomasyonu.py ──tor_hata──→ hata_cozucu.py (auto-fix)
tor_otomasyonu.py ──tor_basarili──→ akilli_yonlendirici.py (log)
araclar_nisan.py  ──nisan──→ tor_otomasyonu.py (navigate)
hata_cozucu.py    ──cozum_uygulandi──→ motor.py (log)
motor.py          ──hata──→ cokus_raporlayici.py (3+ errors → crash report)
```

**Integration in main.py (AIAgentOrchestrator):**
```python
self.windows_entegrasyon = None
if self.motor:
    try:
        from windows_entegrasyon import windows_entegrasyonu_baslat
        bus = windows_entegrasyonu_baslat()
        if bus:
            self.windows_entegrasyon = bus
    except Exception as e:
        _modul_uyar("Windows Entegrasyon", e)
```

**Usage pattern for any module:**
```python
from windows_events import event_bus_al, OLAY_TOR_HATA

bus = event_bus_al()
bus.yayinla(OLAY_TOR_HATA, {"mesaj": "Timeout", "kaynak": "tor"})
# hata_cozucu automatically receives and attempts fix
```

**Reference:** See `references/windows-event-bus.md` for full architecture.

### Phase 10: Branding Rename (Hermes → ReYMeN)

After the fork has diverged significantly from upstream, rename all brand references. This is both a user preference and a hygiene measure.

**Scope decision (always ask the user):**
- All "hermes" in the fork's own code (comments, docstrings, string literals)
- All file/directory names with "hermes"
- All test path references
- **NOT** actual system paths (`~/AppData/Local/hermes/`), env vars (`HERMES_HOME`), installed packages (`hermes_cli`), or upstream backup dirs (`agent/`)

**Rename order (safe top-down):**

1. **Directories first** — rename dirs, then fix references (otherwise the moved dir can't be found):
   ```bash
   mv tests/hermes_reference tests/ReYMeN_reference
   mv reymen/hermes reymen/ReYMeN_mirror
   mv tools/hermes_ajan.py tools/reymen_ajan.py
   mv .hermes_sync.sh .ReYMeN_sync.sh
   mv hermes-full-backup ReYMeN-full-backup
   ```

2. **Code path references** — update all string/file-path references to the renamed dirs:
   ```python
   # Strategic find-and-replace in the fork's own code
   replacements = {
       "hermes_reference": "ReYMeN_reference",
       ".hermes_sync.sh": ".ReYMeN_sync.sh",
       "hermes-full-backup": "ReYMeN-full-backup",
       "tools/hermes_ajan": "tools/reymen_ajan",
   }
   ```

3. **Comment/docstring "Hermes" → "ReYMeN"** — only in the fork's own code:
   - Replace word-boundary `\bHermes\b` with `ReYMeN` in comments and docstrings
   - Replace word-boundary `\bhermes\b` with `reymen` in comments and docstrings
   - **Skip** lines containing `OpenHermes`, `hermite`, `AppData`, `Local/hermes`, `hermes_projesi`

4. **Function/variable names** — rename internal functions that use "hermes" prefix:
   ```python
   def hermes_memory_buda → def reymen_memory_buda
   hermes_bot → reymen_bot
   _HERMES_CORE_TOOLS → _REYMEN_CORE_TOOLS
   ```

5. **Test `__init__.py` files** — update all `__path__` redirects:
   ```python
   # In tests/<subdir>/__init__.py
   __path__ = [
       str(_Path(__file__).parent),                       # Local tests first
       str(_Path(__file__).parent.parent / "ReYMeN_reference" / "<subdir>"),  # Reference tests
   ]
   ```

**Verification:**
```bash
# 1. Count remaining "hermes" references
grep -r "hermes" --include="*.py" reymen/ tools/ gateway/ tests/ \
  | grep -vi "appdata\|local/hermes\|hermes_home\|openhermes\|hermite\|hermes_projesi\|hermes_cli" \
  | wc -l

# 2. Tests pass
python -m pytest tests/tools/ -q --tb=short -s 2>&1 | grep -E "passed|failed|error"

# 3. Symmetry check (after directory renames)
ls *.py 2>/dev/null | wc -l  # expected: N shims (no real files)
```

**Pitfall: Directory shadows module shim.** If a `telegram_bot/` directory exists alongside `telegram_bot.py` (shim), Python loads the directory, ignoring the shim. Fix: integrate the shim's re-exports into the directory's `__init__.py`, or remove the directory's __init__.py if the dir was created by mistake.

**Reference:** See `references/branding-rename-pattern.md` for detailed batch scripts and edge cases.

### Phase 11: Session History Extraction

After significant fork work (renaming, consolidation, gateway fixes), extract all past agent conversations from the Hermes session database into the ReYMeN project for archival and knowledge base.

**Why:** (1) Session DBs may be cleaned/archived in the future, (2) markdown copies are human-readable and searchable, (3) the fork's own code should own its conversation history, not depend on the upstream's session store.

**Method:** Extract from `state.db` (SQLite) per profile — `sessions` table joined with `messages` table. Save to `reymen/gecmis_konusmalar/<profil>_<session_id>_<title>.md`.

**Coverage:** Check ALL Hermes profiles in `~/AppData/Local/hermes/profiles/*/state.db`. Each profile may hold sessions from different agent instances.

**Output format:** Per-session markdown with metadata table + emoji-prefixed message sections + embedded tool call JSON.

**Reference:** See `references/session-history-extraction.md` for complete script and output format.

### Phase 12: Large-Scale Import Resolution

Systematically fix hundreds of unresolved import errors across a forked project's test suite.

**Trigger:** After a fork divergence or upstream sync, tests/ has 100+ `ModuleNotFoundError` failures.

**Workflow:**

1. **SCAN** — Get the baseline:
   ```python
   # Walk all test files, extract unique top-level modules, try __import__
   imports = set()
   for root, dirs, files in os.walk('tests'):
       for f in files:
           if not f.endswith('.py'): continue
           with open(os.path.join(root, f)) as fh:
               for line in fh:
                   s = line.strip()
                   if s.startswith('import '):
                       imports.add(s.split()[1].split('.')[0].split(',')[0])
                   elif s.startswith('from ') and ' import ' in s:
                       imports.add(s.split()[1].split('.')[0])
   failed = {m: str(e) for m in sorted(imports) if not __import__(m) is None}
   except Exception as e:
       # handle per-module
   ```

2. **CATEGORIZE** failures into 5 buckets:

   | Bucket | Example | Fix |
   |--------|---------|-----|
   | External pip packages | `botocore`, `numpy`, `tiktoken`, `tomli`, `watchdog`, `qrcode`, `lark-oapi`, `mautrix` | `pip install <pkg>` (check first with `python -c "import <pkg>"`) |
   | Unix-only (Windows) | `curses`→`_curses`, `pty`→`termios`, `pwd` | Add stub to `tests/conftest.py` |
   | Fork-specific modules | `anayasa_denetcisi`, `reymen_agent`, `sistem_talimati`, `reymen_skill_cli`, `ReYMeN_tools` | Create the module at project root with the exports tests expect |
   | Internal modules (subdir) | `auxiliary_client`→`agent/`, `memory_tool`→`tools/`, `voice_mixer`→`plugins/platforms/discord/` | Create root-level SHIM: `from agent.auxiliary_client import *` |
   | Parsing artifacts | `or`, `it`, `side`, `path`, `nonexistent_module` | Skip (not real imports — parser splitting `import os, sys` or matching inside docstrings) |

3. **FIX AT ROOT CAUSE** (descending order of impact):

   a) **conftest.py** — Add Unix stubs + path extensions once:
      ```python
      # tests/conftest.py
      import types
      for _unix_mod in ('termios', 'curses', 'pwd'):
          if _unix_mod not in sys.modules:
              try: __import__(_unix_mod)
              except ImportError:
                  sys.modules[_unix_mod] = types.ModuleType(_unix_mod)

      # Subdirs for shim modules
      for _sub in ['agent', 'tools', 'plugins', 'plugins/platforms/discord',
                   'optional-skills/productivity/memento-flashcards/scripts']:
          _p = str(PROJECT_ROOT / _sub)
          if _p not in sys.path: sys.path.insert(0, _p)
      ```

   b) **Root-level SHIM files** — one-liner per internal module:
      ```python
      # auxiliary_client.py  (at project root)
      from agent.auxiliary_client import *  # noqa: F401, F403
      ```

   c) **pip install** — batch the remaining:
      ```bash
      python -m pip install botocore numpy qrcode tiktoken tomli watchdog
      ```

4. **VERIFY** — Re-run the scan, confirm failed count drops to 0. If a few remain, check:
   - Is it a runtime-only module? (`hermes_tools` only exists inside Hermes agent runtime — `ReYMeN_tools` wrapper can't import it standalone. Expected, skip.)
   - Is it a false positive from parsing? (Show in string literals, type hints, or `sys.modules` mock setup.)

5. **RACE CONCURRENT JOBS** — For 200+ errors, delegate in batches of 3:
   ```python
   delegate_task(tasks=[
       {"goal": "Fix category A", "context": "...", "toolsets": ["terminal", "file"]},
       {"goal": "Fix category B", ...},
       {"goal": "Fix category C", ...},
   ])
   ```
   Each sub-agent handles ~60-80 imports per 45-second iteration. Repeat until all categories resolved.

**Pitfalls:**
- `hermes_tools` is Hermes runtime-only — `ReYMeN_tools` cannot resolve standalone. Tests that import it directly will fail outside Hermes; they only work inside the agent sandbox.
- Parsing artifacts (`or`, `it`, `side`) come from `import os, sys, time, re, pathlib` splitting and from `from pathlib import Path` partials. Skip them.
- `main` module triggers setuptools entry point — exclude from `__import__` test loops.
- Verifying 200+ imports takes 30-60s; use fast line-based parsing (no `ast.parse` per file) and batch all try/except.

### Phase 13: YOLO / Dangerous Mode Implementation

Implement the fork's equivalent

**Pre-requisite check:** Does the CLI already have a `/yolo` command? Search for it before implementing:

```bash
grep -n "yolo\|_toggle_yolo" reymen/sistem/cli.py | head -5
```

The fork may already have the CLI `/yolo` toggle (from a prior upstream merge) but lack the underlying `tools/approval.py` functions (`_YOLO_MODE_FROZEN`, `enable_session_yolo`, etc.) and CLI `--yolo` flag.

**Implementation checklist:**

1. **`tools/approval.py`** — Add `_YOLO_MODE_FROZEN`, `_session_yolo` set, `enable_session_yolo()`, `disable_session_yolo()`, `is_session_yolo_enabled()`, `yolo_ac()`, `yolo_kapat()`. The frozen flag reads from `REYMEN_YOLO_MODE` env var at import time (not runtime), preventing prompt-injected skills from flipping it mid-session.

2. **`cli.py:main()`** — Add `yolo: bool = False` parameter. `fire.Fire` auto-generates the `--yolo` CLI flag from this. Set `os.environ["REYMEN_YOLO_MODE"] = "1"` if flag is present, before any tool imports happen.

3. **Config support** — After the `--yolo` flag check, also read `approvals.mode` from config. If it's `"off"`, `"yolo"`, or `"dangerous"`, set `REYMEN_YOLO_MODE=1`.

4. **Verify:**
```bash
python3 -c "
from tools.approval import _YOLO_MODE_FROZEN, enable_session_yolo, is_session_yolo_enabled
enable_session_yolo('test')
assert is_session_yolo_enabled('test') == True
print('✅ YOLO mode fully operational')
"
```

**Architecture notes:**
- Two-tier priority: frozen env var (process-start) > session toggle (runtime `/yolo`)
- Session transfer: YOLO state follows session on `/branch` or auto-compression
- Env var is frozen at import time — cannot be overridden mid-session
- `--yolo` flag, config, and env var survive all session operations
- `/yolo` runtime toggle resets on restart (doesn't modify env/config)

#### Critical: YOLO ≠ Full Dangerous Mode (Tirith Interaction)

⚠️ **YOLO mode only removes terminal approval prompts. It does NOT disable the Tirith security policy engine.** This is the key difference from Claude Code's `dangerous` flag.

**Two-layer security model:**

| Layer | What it does | How to disable |
|-------|-------------|----------------|
| YOLO (approvals) | Skips "are you sure?" prompts for `rm -rf`, system commands | `--yolo` flag, `/yolo` toggle, `approvals.mode: off` config |
| Tirith (security engine) | Blocks dangerous commands via policy rules (regardless of YOLO state) | `security.tirith_enabled: false` in config |

```
Claude dangerous:    onay kaldırır         ❌ güvenlik katmanı yok
Hermes YOLO:         onay kaldırır         ✅ Tirith çalışır (güvenlik duvarı)
Hermes FULL:         onay kaldırır         ❌ Tirith devre dışı
```

**To get full dangerous mode (Claude equivalent + more):**
```yaml
# config.yaml
approvals:
  mode: off           # Terminal onayını kaldır
security:
  tirith_enabled: false   # Güvenlik politikasını devre dışı bırak
```

**Even with both off, the following still protect:**
- **Secret redaction** — API keys, tokens, passwords are still redacted from output
- **Tool loop protection** — prevents infinite tool call loops
- **Website blocklist** — blocks known malicious domains

**Pitfall:** Setting `approvals.mode: manual` with `tirith_enabled: false` and no `auxiliary.approval` produces a warning from the gateway — dangerous commands will BLOCK until a human approves them in chat. Use `mode: off` (not `mode: manual`) for truly unattended operation.

**Reference:** See `references/yolo-mode-implementation.md` for full architecture, code, and security notes (includes Tirith interaction details).

## Pitfalls

- **Memory config in wrong section** — `memory_char_limit` under `general:` has NO effect on MemoryStore. Must be under the `memory:` section:
  ```yaml
  # ✅ Dogru: memory: anahtari altinda
  memory:
    memory_char_limit: 50000
    user_char_limit: 25000

  # ❌ Yanlis: general altinda — MemoryStore bunu okumaz
  general:
    memory_char_limit: 50000  # islevsiz
  ```
  Default fallback is 2200 chars. See `self-improvement-loop` skill's `references/memory-config-pitfalls.md` for details.
- **Tests fail with `ModuleNotFoundError` after consolidation** — Check `tests/<category>/__init__.py`. If it has a `__path__` namespace redirect, it blocks discovery of local test files. Fix by including the local dir first in the `__path__` list.
- **20+ unexpected test failures after moving test files** — If `tests/` subdirectories use namespace `__path__` redirects, pytest actually finds the UPSTREAM test files through the redirect, not the local ones. Compare the test count: pre-move vs post-move. If post-move shows way more tests than expected, the namespace is pulling from two sources — good for coverage but expect some API mismatches.
- **Don't fix all silent excepts blindly** — some optional imports intentionally use `try/except pass`. Add a comment instead.
- **`git pull` on a fork with protected files always risks conflict** — use `git checkout upstream/main -- dir/` pattern instead.
- **Verify syntax after EVERY batch change** — 1 syntax error = project won't start.
- **Provider health check can fail on auth-required endpoints** — 401/403 on `/v1/models` means API is alive but auth differs. Treat 401 as "API reachable".
- **Missing upstream gateway functions** — fork's custom `base.py`/`config.py` may lack Hermes streaming constants and helper functions. See `references/gateway-upstream-restoration.md` for recovery pattern.
- **Remove duplicates one file at a time** — ensure nothing breaks after each removal.
- **Profile-specific skills may collide with project skills** — when project dir is in the Hermes search path. Load by full path to disambiguate.
- **Gateway cannot be restarted from inside the gateway process** — `hermes gateway restart` detects it's inside the gateway's process tree (SIGTERM propagation check) and blocks with "cannot restart or stop the gateway from inside the gateway process". Even `DETACHED_PROCESS` / `Start-Job` are blocked. Must run from a physically separate shell (new PowerShell window). Workaround: directly kill the gateway PID via `taskkill /F` then start fresh from this session's terminal.
