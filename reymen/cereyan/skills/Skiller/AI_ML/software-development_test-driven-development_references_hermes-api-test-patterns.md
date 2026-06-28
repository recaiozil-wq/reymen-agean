---
name: software-development_test-driven-development_references_hermes-api-test-patterns
description: Hermes API Test Patterns
title: "Software Development Test Driven Development References Hermes Api Test Patterns"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes API Test Patterns |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes API Test Patterns

## 1. MagicMock for Complex Agent Mocks

When a Hermes function (e.g. `compress_context`) accesses many agent attributes
(`_emit_status`, `_memory_manager`, `context_compressor`, `_build_system_prompt`, etc.),
**do NOT** define a custom MockAgent class — use `MagicMock` instead.

```python
from unittest.mock import MagicMock

agent = MagicMock()
agent.session_id = "test"
agent.model = "test-model"
agent.provider = None
# Only override what the assertion needs
agent.context_compressor.compress.return_value = (messages, "summary")
```

### Why
- `MockAgent` class needs whack-a-mole fixes for every new attribute access
- `MagicMock` creates any attribute on access — no AttributeError
- Less code, more robust

### When NOT to use
- When the test validates real type behavior (use a real object or `spec=RealClass`)
- When only 1-2 simple attributes are needed (bare MockAgent is fine)

## 2. Keyword Argument for **kwargs Signatures

When calling functions with `**kwargs` in the signature, pass optional params
as keyword args, NOT positional:

```python
# WRONG — positional arg bypass:
t.calistir(komut, timeout)
# → TypeError: takes 2 positional args but 3 given

# RIGHT — keyword arg:
t.calistir(komut, timeout=timeout)
```

### Pattern
If you see `**kwargs` in the target signature, ALL extra params must be keyword.

## 3. Hermes API Return Types

Key Hermes functions that differ from older API expectations:

| Function | Returns | Old Expectation |
|----------|---------|-----------------|
| `build_preloaded_skills_prompt({})` | `tuple[str, list, list]` | `str` |
| `compress_context(agent, ...)` | `tuple[messages, system_prompt]` | `tuple[list, str]` |
| `IterationBudget(max_total=N)` | Has `.remaining` (int) and `.used` (int) properties | Methods |

## 4. Batch Test Runner for Reymen Projects

When running many standalone test files (not pytest), use a batch runner:

```python
for fn in sorted(Path("tests").glob("test_*.py")):
    r = subprocess.run([sys.executable, str(fn)], timeout=120, ...)
    if r.returncode == 0: passed.append(fn.name)
    else: failed.append((fn.name, r.stderr[-200:]))
```

Key: collect ALL results first, report one summary table at the end.
