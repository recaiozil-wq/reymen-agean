---
name: software-development_reymen-hermes-sync_references_batch-test-runner
description: Batch Test Runner — 1,500+ Test Parallel Execution
title: "Software Development Reymen Hermes Sync References Batch Test Runner"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Batch Test Runner — 1,500+ Test Parallel Execution |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Batch Test Runner — 1,500+ Test Parallel Execution

## Problem

Reymen has 1,500+ test files spanning multiple categories:
- `tests/` (27 standalone Reymen tests)
- `tests/hermes_reference/` (1,400+ pytest tests)
- `skills/*/tests/` (17 skill tests)
- Root test files (test_suite.py, test_learning_loop.py, etc.)

Running them all serially is impractical (~12+ hours).

## Solution: Parallel Batch Runner

Run test files in batches of 10 using `ThreadPoolExecutor`. Each test gets its own subprocess with a timeout. Standalone tests run via `python test.py`, pytest-style tests run via `python -m pytest test.py -q`.

### Key Design

```
BATCH_SIZE = 10
ThreadPoolExecutor(max_workers=BATCH_SIZE)
Each file: subprocess.run(timeout=30)
```

### Standalone vs Pytest Detection

```python
icerik = tf.read_text(encoding='utf-8')
if 'if __name__' in icerik:
    # Standalone — run with `python test.py`
    r = subprocess.run([sys.executable, str(tf)], ...)
else:
    # Pytest — run with `python -m pytest test.py -q`
    r = subprocess.run([sys.executable, '-m', 'pytest', str(tf), '-q', '--tb=line'], ...)
```

### Progress Tracking

Write output to a file for real-time monitoring instead of relying on stdout (which buffers on Windows):

```python
_OUT_FILE = open('_test_progress.txt', 'w', encoding='utf-8')
def log(msg):
    print(msg)
    _OUT_FILE.write(msg + '\n')
    _OUT_FILE.flush()
```

### Time Estimates

- 1,563 test files × 30s timeout × 10 workers → ~78 minutes worst case
- Most failing tests return in <2s (ImportError at module level)
- Real runtime: 20–40 minutes

### Result Categories

| Code | Meaning |
|------|---------|
| ✅ OK | Test passed (exit code 0) |
| ❌ FAIL | Test failed (non-zero exit or import error) |
| ⏰ TIMEOUT | Test exceeded 30s timeout |

## Pitfalls

1. **Stdout buffering on Windows** — Background process stdout is fully buffered and unreadable until the process ends. Always redirect to a file.
2. **PyTest collection errors** — ImportError at module level prevents pytest from running any tests in that file. These errors show in stderr, not stdout.
3. **`-x` flag** — Never use `-x` (stop on first failure) for batch runs. Let all files finish.
4. **Hermes reference tests** — Most require Hermes's full environment and fail in Reymen. File-level pass rate is ~15–20%.
5. **Hersona tests** — `test_attributes.py` and `test_cli.py` tend to timeout (30s+). Consider running them separately with a longer timeout.
