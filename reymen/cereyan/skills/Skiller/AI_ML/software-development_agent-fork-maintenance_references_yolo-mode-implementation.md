---
name: software-development_agent-fork-maintenance_references_yolo-mode-implementation
description: YOLO Mode (Dangerous Mode) Implementation
title: "Software Development Agent Fork Maintenance References Yolo Mode Implementation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | YOLO Mode (Dangerous Mode) Implementation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# YOLO Mode (Dangerous Mode) Implementation

The fork's equivalent of Claude Code's `dangerous` flag — bypasses dangerous command approval prompts. In Hermes Agent this is called **YOLO mode**.

## Tirith Security Interaction (Critical)

**YOLO mode does NOT disable Tirith.** This is the single most important architectural difference from Claude Code's `dangerous` flag — and the most common misunderstanding.

### Two-Layer Model

```
┌──────────────────────────────────────────────────┐
│                   YOLO Mode                      │
│  (approvals.mode: off)                          │
│  Skips "are you sure?" prompts                  │
│  ──────────── but ────────────                  │
│  Tirith is still ACTIVE below                   │
├──────────────────────────────────────────────────┤
│              Tirith Security Engine              │
│  (security.tirith_enabled: true)                │
│  Policy-based command blocking:                 │
│  • rm -rf /, dd, mkfs → BLOCKED                │
│  • curl to known-malicious domains → BLOCKED    │
│  • Path traversal attempts → BLOCKED            │
│  • Prompt injection patterns → FLAGGED          │
└──────────────────────────────────────────────────┘
```

### Configuration States

| Config | Terminal Prompts | Command Blocking | Use Case |
|--------|-----------------|------------------|----------|
| Default (both on) | Asks | Blocks | Safe mode |
| YOLO only | ✅ Skipped | Still blocks | Development — wants speed but keeps guardrails |
| Full dangerous | ✅ Skipped | ✅ Bypassed | Emergency admin, trusted automation |

### How User Requests It

Users typically mention "YOLO mode" and may not know about Tirith. Common phrases:
- *"YOLO var mı?"* → They want approval prompt bypass. Tell them about YOLO.
- *"Tirith'i aç"* → In ReYMeN jargon, this means **disable Tirith** (`tirith_enabled: false`)
- *"Tam yetki"* → They want both YOLO + Tirith disabled

**When the user says "Tirith'i aç" (Tirithi ac):** This is ReYMeN-specific jargon meaning "disable/bypass the Tirith security." The parenthetical in conversation was: *"(approvals.mode: off + security.tirith_enabled: false ile tam yetki)"* — confirming that "Tirith açmak" in this context = tirith_enabled: false.

### Implementation: Disabling Tirith

**Via config.yaml:**
```yaml
security:
  tirith_enabled: false
```

**Via CLI (if implemented):**
```bash
reymen config set security.tirith_enabled false
```

### What YOLO + Tirith Disabled Still Protects

| Protection | Status | Why |
|-----------|--------|-----|
| 🔴 Secret redaction | Still active | API keys/tokens are redacted from output — this is in the display layer, not the policy layer |
| 🔴 Tool loop protection | Still active | Prevents infinite tool call loops regardless of security mode |
| 🟡 Website blocklist | Active by default | Separate config: `security.website_blocklist: [domains]` |

### Gateway Warning

When `approvals.mode: manual` (not `off`) is combined with `tirith_enabled: false` and no `auxiliary.approval`, the gateway logs a warning:

```
Gateway approvals.mode=manual with no automated risk assessor
(security.tirith_enabled is false and auxiliary.approval is unset):
dangerous commands and execute_code scripts will BLOCK until
a human approves them in chat.
```

**Fix:** Use `approvals.mode: off` (not `manual`) for unattended dangerous mode.

### Code References

- Gateway check: `gateway/run.py:1944-1956`
- Tirith class: `reymen/guvenlik/tirith_security.py`
- Config parsing: `reymen/sistem/cli.py:4871-4876`


## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `_YOLO_MODE_FROZEN` | `tools/approval.py` | Frozen at process start from env var — cannot be flipped mid-session by prompt injection |
| `_session_yolo` (set) | `tools/approval.py` | Per-session YOLO toggle — survives session transfers |
| `/yolo` command | `cli.py:_toggle_yolo()` | CLI toggle for current session |
| `--yolo` flag | `cli.py:main(yolo=True)` | Process-start flag via `fire.Fire(main)` auto-arg parsing |
| `⚠ YOLO` status bar | `cli.py` | Visual indicator in status bar when active |
| `approvals.mode: off` config | `~/.ReYMeN/config.yaml` | Persistent YOLO via config file |

## Enabling Methods

```bash
# 1. CLI flag (one-shot)
reymen --yolo

# 2. Config (permanent)
# In ~/.ReYMeN/config.yaml:
approvals:
  mode: yolo        # or "off", "dangerous"

# 3. Environment variable
export REYMEN_YOLO_MODE=1

# 4. Runtime toggle (inside CLI)
/yolo
```

## How It Works

### Process-Start Flow

1. `cli.py:main(yolo=True)` receives the `--yolo` flag
2. Sets `os.environ["REYMEN_YOLO_MODE"] = "1"` BEFORE any tool imports
3. When `tools/approval.py` is imported, `_YOLO_MODE_FROZEN` reads the env var:
   ```python
   _YOLO_MODE_FROZEN: bool = os.environ.get("REYMEN_YOLO_MODE", "").strip() in ("1", "true", "yes", "on")
   ```
4. This value is **frozen** — prompt-injected skills cannot flip it mid-session

### Config-Based Flow

```python
# In cli.py:main(), after --yolo flag check:
if not os.environ.get("REYMEN_YOLO_MODE"):
    _cfg = load_config()
    _approvals = _cfg.get("approvals", {}) or {}
    if _approvals.get("mode") in ("off", "yolo", "dangerous"):
        os.environ["REYMEN_YOLO_MODE"] = "1"
```

### Runtime Toggle Flow

The `/yolo` command uses `enable_session_yolo(session_key)` / `disable_session_yolo(session_key)` to control YOLO on a per-session basis. This is **not** frozen — it's user-intended interactive control.

### YOLO State Check (Priority)

```python
def is_session_yolo_active(self) -> bool:
    # 1. Frozen env var (highest priority)
    if _YOLO_MODE_FROZEN:
        return True
    # 2. Session toggle
    return is_session_yolo_enabled(session_key)
```

## Session Transfer

When a session is forked (e.g. `/branch` or auto-compression rotates the session id), YOLO state is transferred:

```python
def _transfer_session_yolo(self, old_id, new_id):
    if is_session_yolo_enabled(old_id):
        enable_session_yolo(new_id)
        disable_session_yolo(old_id)
```

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Frozen env var at import time | Prevents prompt-injected skills from enabling YOLO mid-session |
| Separate session-key store | Allows `/yolo ON` / `/yolo OFF` per interactive session without affecting other agents |
| Two-tier priority (frozen > toggle) | `--yolo` flag and config are non-bypassable; `/yolo` gives interactive control but can't override admin intent |
| `fire.Fire` auto-arg | The `--yolo` CLI flag is auto-generated from the `main(yolo: bool = False)` function parameter — no manual argparse needed |

## Code Implementation

### `tools/approval.py` additions:

```python
import os as _os
import threading as _threading

_session_yolo: set = set()
_yolo_lock = _threading.Lock()
_YOLO_ENV_VAR = "REYMEN_YOLO_MODE"

# Frozen at import time — cannot be changed mid-session
_YOLO_MODE_FROZEN: bool = _os.environ.get(_YOLO_ENV_VAR, "").strip() in ("1", "true", "yes", "on")

def enable_session_yolo(session_key: str) -> None:
    with _yolo_lock:
        _session_yolo.add(session_key)

def disable_session_yolo(session_key: str) -> None:
    with _yolo_lock:
        _session_yolo.discard(session_key)

def is_session_yolo_enabled(session_key: str) -> bool:
    with _yolo_lock:
        return session_key in _session_yolo
```

### `cli.py` additions:

```python
# In main() function signature:
def main(
    ...
    yolo: bool = False,  # ← new
):

# In main() function body:
    if yolo:
        os.environ["REYMEN_YOLO_MODE"] = "1"
    
    # Also check config
    if not os.environ.get("REYMEN_YOLO_MODE"):
        from ReYMeN_cli.config import load_config
        _cfg = load_config()
        if _cfg.get("approvals", {}).get("mode") in ("off", "yolo", "dangerous"):
            os.environ["REYMEN_YOLO_MODE"] = "1"
```

## Security Notes

- YOLO mode does **NOT** disable secret redaction — API keys still get hidden
- Only skips the approval prompt for dangerous commands (`rm -rf`, system commands, etc.)
- Frozen env var prevents mid-session override from injected prompts
- Per-session toggle resets on CLI restart (unless `--yolo` flag or config is used)
- Process-start methods (`--yolo` flag, env var, config) survive all session operations
