---
skill_id: 400c370b96a4
usage_count: 1
last_used: 2026-06-16
---
# tmp_path is cleaned up automatically by pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{outcome.get_result().when}", outcome.get_result())
```

### Tier 2 — Windows Job Object (optional: process-lifetime containment)

Attach the process to a Job Object so it is **automatically terminated** when
the test fixture's job handle is GC'd. Also prevents the app from spawning
child processes that escape fixture cleanup.

> **Scope of isolation:** Job Objects do NOT virtualize filesystem access or
> block network traffic. File-write and network isolation require AppContainer,
> Windows Firewall rules, or Tier 3 (Windows Sandbox). Use Tier 2 only for
> process-lifetime and child-process containment.

Requires no extra dependencies.

```python
import ctypes, ctypes.wintypes as wt

def restrict_process(pid: int):
    """
    Attach the process to a Job Object that prevents it from:
    - spawning processes outside the job (LIMIT_KILL_ON_JOB_CLOSE)
    Does NOT block network — use Windows Firewall rules for that.
    """
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000