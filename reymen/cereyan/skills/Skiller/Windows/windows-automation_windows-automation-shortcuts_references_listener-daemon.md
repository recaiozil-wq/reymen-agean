
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Windows Automation Shortcuts_References_Listener Daemon |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Hermes Listener Daemon Architecture

## Overview

`hermes_listener.py` is a Python background daemon that captures global keyboard
shortcuts using the `keyboard` library and dispatches them to Python functions —
either directly (via imports or inline code) or via subprocess/powershell fallback.

It is the Python-native alternative to the AutoHotkey (`windows-shortcuts.ahk`)
approach. Both can run side-by-side without conflict.

## Why This Pattern

| AHK | Python Daemon |
|-----|--------------|
| External exe, separate ecosystem | Tamamen Python |
| subprocess → python script | Direct import or inline |
| No structured logging | Log to file + stdout |
| No PID/debugging | --status, --stop, --list |
| Hard to extend dynamically | Easy to add/modify handlers |

## Architecture

```
[keyboard library]           ← user presses Ctrl+Alt+M
       ↓
  global hook (SetWindowsHookEx)
       ↓
  keyboard.add_hotkey('ctrl+alt+m', handler)
       ↓
  handler function
       ↓
  ┌─── Direct (import)    — hermesmouse.get_pos()
  ├─── Inline PowerShell  — screenshot via PS
  └─── Subprocess         — python other_script.py
       ↓
  logging to:
  ├─── stdout (Hermes panel)
  └─── ~/.hermes/logs/listener.log
```

## Key Design Decisions

### 1. Direct import over subprocess

Where possible, Python modules are imported directly so the listener's process
calls functions in-memory. No shell overhead, no PATH issues, instant response.

Currently imported directly:
- `hermesmouse.py` (ctypes mouse/keyboard)

Inline (no subprocess):
- `.env` file reading/masking
- System status queries

Subprocess (necessary):
- PowerShell screenshots (must run in separate process)
- Ollama, Kali SSH, Tor Browser (external programs)
- Other Python scripts (not designed as importable modules)

### 2. PID File for Single Instance

```python
PID_FILE = "~/.hermes/listener.pid"

def is_running():
    pid = read_pid()
    os.kill(pid, 0)  # signal 0 = existence check
```

Prevents duplicate instances. `--stop` reads the PID and sends SIGTERM.

### 3. Signal Handling

```python
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

Cleans up PID file and unhooks all keyboard hooks on shutdown.

### 4. Hybrid Command Dispatch

Each hotkey handler chooses the right dispatch method:

| Method | Use When |
|--------|----------|
| `hm.get_pos()` | Fare konumu — 1ms, zero overhead |
| `_run_powershell(ps_script)` | Screenshot, window focus — Windows API |
| `subprocess.Popen(...)` | Ollama, Tor — long-running external process |
| `_run_python(script.py)` | Kali scripts — imported modules don't exist yet |

## Hotkey Map

All registered via `keyboard.add_hotkey()`:

| Hotkey | Function | Dispatch | Response Time |
|--------|----------|----------|---------------|
| `Ctrl+Alt+M` | Fare konumu | Direct (ctypes) | <10ms |
| `Ctrl+Alt+S` | Ekran görüntüsü | PowerShell inline | ~500ms |
| `Ctrl+Alt+V` | Vision analiz | PS + Ollama | ~3s |
| `Ctrl+Alt+O` | Ollama başlat | Popen | ~100ms |
| `Ctrl+Alt+Q` | Ollama (alt) | Popen | ~100ms |
| `Ctrl+Alt+K` | Kali SSH | SSH via PS | ~2s |
| `Ctrl+Alt+H` | Kali help | Subprocess | ~1s |
| `Ctrl+Alt+W` | Kali WiFi | Subprocess | ~1s |
| `Ctrl+Alt+T` | Web terminal | Subprocess | ~1s |
| `Ctrl+Alt+A` | VS Code focus | PowerShell | ~500ms |
| `Ctrl+Alt+B` | Tor Browser | Popen | ~100ms |
| `Ctrl+Alt+I` | CLI installer | Subprocess | ~1s |
| `Ctrl+Alt+R` | Hafıza temizliği | Subprocess | ~2s |
| `Ctrl+Alt+N` | .env kuralları | Direct (Python) | <10ms |

## Files

| File | Purpose |
|------|---------|
| `C:\Users\marko\hermes_listener.py` | Main daemon (the pattern itself) |
| `C:\Users\marko\hermes_listener.bat` | CLI wrapper: start/stop/status/list |
| `C:\Users\marko\hermes_listener.vbs` | Silent launch (no console window) |
| `C:\Users\marko\hermes_listener_install.bat` | Task Scheduler registration |

## Adding a New Hotkey

Two easy steps:

1. Write a handler function:
```python
def on_my_action():
    log.info("My action triggered")
    # your code here
    print(">>> [HERMES] My action ran")
```

2. Add to HOTKEYS list:
```python
HOTKEYS = [
    ...
    ("ctrl+alt+z", on_my_action, "My action description"),
]
```

No restart needed if the process is running — just `--stop` then start again.

## Platform Caveats

- **Admin required**: `keyboard` library uses `SetWindowsHookEx` which needs
  admin on Windows. Task Scheduler with `rl highest` handles this.
- **No PYWH**: `pythonw.exe` works but the `keyboard` library's internal message
  pump may not function correctly without a console. Use the VBS wrapper instead.
- **No concurrent dispatch**: `keyboard` library's callbacks are sequential.
  A slow handler blocks subsequent hotkeys. Keep handlers fast; push slow work
  to subprocess/Popen.
