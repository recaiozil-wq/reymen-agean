---
name: software-development_fork-project-audit_references_test-suite-api-adaptation
description: Test Suite API Adaptation
title: "Software Development Fork Project Audit References Test Suite Api Adaptation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test Suite API Adaptation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Test Suite API Adaptation

When a fork/derived project replaces root modules with `agent/` versions (from upstream), the test suite will break because the simplified fork API differs from the full upstream API.

## Workflow

### Phase 1: Import Path Fix

Change `from module import Class` → `from agent.module import Class`:

```bash
# Find all failing imports
python test_suite.py 2>&1 | grep "No module named"
# → iteration_budget, prompt_builder, trajectory, etc.

# Fix each one (17 files common for Hermes→Reymen)
for mod in iteration_budget prompt_builder trajectory; do
  sed -i "s/from $mod import/from agent.$mod import/g" test_suite.py
done
```

### Phase 2: API Signature Discovery

Simplified fork APIs and full upstream APIs are NEVER the same. Discover actual signatures:

```python
import inspect
from agent.iteration_budget import IterationBudget
print(inspect.signature(IterationBudget.__init__))
# → (self, max_total: int)  NOT (self, max_tur: int)
```

Common pattern differences (Hermes → Reymen):

| Reymen (old) | Hermes (new) | Change |
|---|---|---|
| `IterationBudget(max_tur=N)` | `IterationBudget(max_total=N)` | Keyword rename |
| `b.analiz_et()` | `b.consume()` + `b.remaining` (property) | Method rename, property |
| `b.devam_etmeli_mi()` | `b.remaining > 0` | Replace method |
| `tam_temizle(text)` | `redact_sensitive_text(text)` | Function rename |
| `model_listele()` | `get_model_context_length(name)` | Different API entirely |
| `skill_sayisi()` | `get_skills_dir()` + `parse_frontmatter()` | Different API entirely |
| `CredentialPool()` | `CredentialPool(provider, entries)` | Required args |

### Phase 3: Mock Agent for Upstream Functions

Some upstream functions require an `agent` object with specific attributes:

```python
class MockAgent:
    session_id = "test"
    conversation_id = "test"
    model = "test-model"
    provider = None
```

Add attributes one at a time as the runtime reveals new requirements.

### Phase 4: Property vs Method Check

Upstream modules may use properties instead of methods:

```python
# Old (method call):
b.remaining()  # → TypeError: 'int' is not callable
b.used()       # → TypeError: 'int' is not callable

# New (property access):
b.remaining    # → int
b.used         # → int
```

Detect with:
```python
members = [(k, type(v).__name__) for k, v in inspect.getmembers(obj) if not k.startswith('_')]
```

### Phase 5: Incremental Test

Run after EVERY few fixes — don't batch all 20 and debug at once:

```bash
python test_suite.py 2>&1 | grep -E "^(  OK|  FAIL|Sonuc)"
# Track: 15/35 → 21/35 → 26/35 → 31/35
```

## Common Failure Patterns

| Error | Cause | Fix |
|---|---|---|
| `No module named 'X'` | Import path wrong | `from agent.X import Y` |
| `__init__() got unexpected keyword arg` | Parameter renamed | Check `inspect.signature()` |
| `takes N positional but M given` | Wrong arg count | Check signature |
| `'int' object is not callable` | Property, not method | Remove `()` |
| `'NoneType' object has no attribute` | Missing mock attr | Add to MockAgent |
| Empty error string | Shell/exec timeout | Check command path or timeout |

## Expected Progress Curve

Starting from a fresh upstream copy:

| Iteration | Passing | Strategy |
|---|---|---|
| 1 (import fix) | 15/35 | Fix paths only |
| 2 (signature fix) | 21/35 | Fix obvious API diffs |
| 3 (property fix) | 26/35 | Fix property/method mixup |
| 4 (mock + remaining) | 31/35 | Fix complex APIs |
| 5 (deep bugs) | 32-35/35 | Fix execution-level issues |
