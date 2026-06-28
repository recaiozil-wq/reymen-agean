---
name: ecc_python-testing_references_pytest-configuration
description: pytest Configuration
title: "Ecc Python Testing References Pytest Configuration"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | pytest Configuration |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## pytest Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=mypackage
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=mypackage",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## Pitfalls

### `ValueError: I/O operation on closed file` during test collection

**Cause:** Some modules (e.g. agent frameworks, plugin loaders, skill registries) write to `stdout`/`stderr` directly during import — they print banners, init logs, or plugin status. pytest's default stdout capture opens a temporary file to buffer this output. When the module's import changes or closes file descriptors (e.g. by replacing `sys.stdout`), the capture tmpfile can get out of sync, producing:

```
ValueError: I/O operation on closed file
  File ".../capture.py", line 591, in snap
    self.tmpfile.seek(0)
```

**Fix:** Add `addopts = -s` to `pytest.ini`:

```ini
[pytest]
addopts = -s
```

This disables stdout/stderr capture entirely. Trade-off: test output mixes with module print statements (noisy), but the tests run reliably. Only use this when modules irreparably break capture — not as a default for well-behaved projects.

**Alternative (better isolation):** Refactor tests to avoid importing the heavy module at module level. Move imports inside test functions. Use a conftest.py fixture with `autouse=True` to suppress stdout during import:

```python
# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(autouse=True)
def _suppress_stdout():
    """Suppress noisy module-import output during collection."""
    sys.stdout = io.StringIO()
    yield
    sys.stdout = sys.__stdout__
```

### `addopts` collisions when running from multiple project roots

If a `pytest.ini` with `addopts = -s` is in a parent directory, it can silently override child-project settings. Use `--override-ini` to bypass:

```bash
pytest --override-ini="addopts=" tests/
```
