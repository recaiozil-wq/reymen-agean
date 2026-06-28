---
skill_id: 5aae0b5d4961
usage_count: 1
last_used: 2026-06-16
---
## Red-Green-Refactor Cycle

### RED — Write Failing Test

Write one minimal test showing what should happen.

**Good test:**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'

    result = retry_operation(operation)

    assert result == 'success'
    assert attempts == 3
```
Clear name, tests real behavior, one thing.

**Bad test:**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # What about retry count? Timing?
```
Vague name, tests mock not real code.

**Requirements:**
- One behavior per test
- Clear descriptive name ("and" in name? Split it)
- Real code, not mocks (unless truly unavoidable)
- Name describes behavior, not implementation

### Verify RED — Watch It Fail

**MANDATORY. Never skip.**

```bash