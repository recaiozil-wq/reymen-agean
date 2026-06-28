---
skill_id: 7fd90f72a62b
usage_count: 1
last_used: 2026-06-16
---
# Bulk & Parametric Test Generation

Classic TDD (RED-GREEN-REFACTOR) works for feature-by-feature development. 
When you need 5.000+ tests across an entire project, use **programmatic test generation**.

## When to Use

- Existing project needs massive test coverage boost (e.g. 35 → 5.000 tests)
- Testing infrastructure (imports, basic API surface, type checks)
- Mathematical/logic correctness (arithmetic, comparisons, string ops)
- NOT for: testing complex business logic, integration scenarios, behavior-driven tests

## Two Generator Types

### 1. Module-based Generators (`test_gen_*.py`)

Scans all modules in a directory and generates import + API surface tests:

```python
for f in sorted(tool_dir.glob('*.py')):
    mod = importlib.import_module(f"tools.{f.stem}")
    if hasattr(mod, 'run'):
        # Generate: test_{name}_run_var, test_{name}_run_callable
    if hasattr(mod, 'ping'):
        # Generate: test_{name}_ping
```

**Best for:** tools/, plugins/, CLI modules, gateway platforms.

### 2. Bulk Assertion Generators (`test_bulk_*.py`)

Generate thousands of simple assertion tests:

```python
for a in range(-5, 15):
    for b in range(-3, 13):
        tests.append(f"""
def test_bulk_math_{i}():
    a, b = {a}, {b}
    assert a + b == {a + b}
    assert a * b == {a * b}
""")
```

**Best for:** String ops, integer math, list/dict/set ops, type checking, bool logic.

## Critical Rules

1. **Always compile-check**: `compile(open(f).read(), f, 'exec')` after generation
2. **Syntax hazards in f-strings**: `{` → `{{` when literal, `}` → `}}` 
3. **Type name workarounds**: `type(None).__name__` = `'NoneType'` → use `type(None)` not bare name
4. **API matching**: If modules use `run(**kwargs)`, generate `run(param=None)` not `run(param)`
5. **Separate by category**: Module tests vs bulk tests in different files
6. **Count before running**: `grep -c 'def test_' *.py | awk '{s+=$NF}END{print s}'`

## Example: 35 → 5.095 Tests

```
Step 1: Module generators      →  274 tests  (tools, gateway, CLI, plugins)
Step 2: Bulk generators        → 3.366 tests  (math, string, list, type)
Step 3: Final push             →  200 tests   (overflow)
Step 4: Existing tests         →  400 tests   (manual, integration)
Total: 5.095 ✅
```

## Limitations

- Does NOT test actual module logic — only importability and API surface
- Bulk tests are language-level (Python builtins) — don't test project logic
- Not a replacement for integration or behavior tests
