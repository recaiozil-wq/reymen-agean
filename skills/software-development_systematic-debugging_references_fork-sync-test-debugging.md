---
name: software-development_systematic-debugging_references_fork-sync-test-debugging
description: Fork Sync — Test Debugging After Upstream Merge
title: "Software Development Systematic Debugging References Fork Sync Test Debugging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Fork Sync — Test Debugging After Upstream Merge |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Fork Sync — Test Debugging After Upstream Merge

## When to Use

After copying files from an upstream repo (Hermes) into a fork (ReYMeN), tests that previously passed now fail — or new files cause import errors.

## Step-by-Step Diagnostic

### Phase 1 — Import Check (fastest signal)

```bash
python -c "
for mod in ['agent.coding_context', 'agent.credits_tracker', 'agent.ssl_guard',
            'agent.turn_context', 'agent.turn_finalizer', 'agent.turn_retry_state']:
    try:
        __import__(mod)
        print(f'  OK {mod}')
    except Exception as e:
        print(f'  FAIL {mod}: {e}')
"
```

**Common failures:**
| Error | Fix |
|-------|-----|
| `ModuleNotFoundError` | Copy the missing dependency module too |
| `AttributeError` | Fork has older version — update it |
| `NameError` | Fork initializes globals differently |

### Phase 2 — Dead Code Detection

Handlers that ended up AFTER an unconditional `return`:

```python
def calistir(self, arac, params):
    sonuc = self._fallback_calistir(arac, params)
    return sonuc          # ← always returns
    # ALL CODE BELOW IS DEAD
    if arac == "GOREV_BITTI":   # never reached
```

**Fix:** Move dead handlers into `_fallback_calistir()`.

### Phase 3 — Registry Prefix Mismatch

Registry returns `[Hata]:` but caller checks `[Bilinmeyen arac]`:

```python
r = _REGISTRY.calistir("TEST", "")
print(r.startswith("[Bilinmeyen arac]"))  # False → treated as success!
```

**Fix:** Align registry prefix with caller's check.

### Phase 4 — Test Expectation Drift

| Failure | Fix |
|---------|-----|
| `assert 'X' in 'Y'` — message changed | Update test string |
| `TypeError: not subscriptable` — class vs dict | `result["key"]` → `result.key` |
| `ValueError: closed file` — pytest I/O | `addopts = -s` in `pytest.ini` |
| Timeout >30s — real I/O | Replace with lightweight assertion |

### Phase 5 — Verify

```bash
python -m pytest tests/test_core.py --tb=short -v
python -m pytest tests/ --ignore=tests/hermes_reference --tb=short
```

## Prevention

1. Map integration points first (modified files: motor.py, main.py, beyin.py)
2. Copy unchanged files separately (safe to overwrite)
3. Modified files = manual merge (never overwrite)
4. Batch import test all new files first
5. Check for dead code after merge
