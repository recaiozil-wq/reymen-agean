---
name: ecc_windows-desktop-e2e_references_after-proc-subprocess-popen-job-restrict_process-proc-pid
description: "After proc = subprocess.Popen(...):  job = restrict_process(proc.pid)"
title: "Ecc Windows Desktop E2E References After Proc Subprocess Popen Job Restrict Process Proc Pid"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | After proc = subprocess.Popen(...):  job = restrict_process(proc.pid) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# After proc = subprocess.Popen(...):  job = restrict_process(proc.pid)
```

### Tier 3 — Windows Sandbox (CI full-OS isolation)

When you need a clean Windows image per run (no leftover registry keys, no
shared GPU state, true isolation), run the **entire test suite** inside
[Windows Sandbox](https://learn.microsoft.com/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-overview).

**Requirement:** Windows 10/11 Pro or Enterprise, Virtualization enabled.

Create `e2e-sandbox.wsb` in your project root:

```xml
<Configuration>
  <MappedFolders>
    <!-- App binary (read-only) -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\build\Release</HostFolder>
      <SandboxFolder>C:\app</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <!-- Test suite (read-write for artifacts) -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\e2e_test</HostFolder>
      <SandboxFolder>C:\e2e_test</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <!--
      Windows Sandbox starts with no Python. Install it silently first,
      then install deps and run tests. Artifacts are written back to the
      host via the MappedFolder above.
    -->
    <Command>powershell -Command "
      winget install --id Python.Python.3.11 --silent --accept-package-agreements;
      $env:PATH += ';' + $env:LOCALAPPDATA + '\Programs\Python\Python311\Scripts';
      cd C:\e2e_test;
      pip install -r requirements.txt;
      pytest tests\ -v
    "</Command>
  </LogonCommand>
</Configuration>
```

Launch: `WindowsSandbox.exe e2e-sandbox.wsb`

> pywinauto and the app both run **inside** the sandbox (same session required).
> Artifacts are written back to the host via the mapped folder.

### Tier comparison

| Tier | Isolation | Setup cost | Works on CI | Use when |
|------|-----------|-----------|-------------|----------|
| 1 — `tmp_path` env redirect | Filesystem | Zero | Always | Default for all tests |
| 2 — Job Object | Process tree | Low | Always | Prevent child-process escape |
| 3 — Windows Sandbox | Full OS | Medium | Needs Pro/Enterprise image | Nightly clean-room runs |

### Prevent hanging tests

Add `pytest-timeout` to cap any single test. In `pytest.ini` set `timeout = 60` and `timeout_method = thread`. Note: `thread` method cannot kill Qt app subprocesses on Windows — add `atexit.register(lambda: [p.kill() for p in psutil.Process().children(recursive=True)])` in `conftest.py` to reap orphans.
