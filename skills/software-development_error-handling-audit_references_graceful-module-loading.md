---
name: software-development_error-handling-audit_references_graceful-module-loading
description: Graceful Module Loading Pattern
title: "Software Development Error Handling Audit References Graceful Module Loading"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Graceful Module Loading Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Graceful Module Loading Pattern

## Problem

A large agent project has optional modules (gateway, telegram_bot, dashboard, etc.) that may or may not be installed. You want the agent to start even if some are missing, but you don't want to silently hide errors.

## Anti-Pattern — Silent Failure

```python
try:
    import telegram_bot
    _TELEGRAM_BOT = telegram_bot
except Exception:
    _TELEGRAM_BOT = None   # ❌ Hata sessizce yutuluyor
```

Problems:
- Never know WHY the import failed
- "Telegram support" is claimed but broken
- Impossible to debug

## Correct Pattern — Logged Degradation

```python
try:
    import telegram_bot
    _TELEGRAM_BOT = telegram_bot
except ImportError as e:
    _modul_uyar("telegram_bot", f"kütüphane eksik: {e}")
    _TELEGRAM_BOT = None
except Exception as e:
    _modul_uyar("telegram_bot", e, "hata")
    _TELEGRAM_BOT = None
```

## Helper Function

```python
def _modul_uyar(modul, hata, seviye="uyari"):
    """Module loading warning — visible but non-fatal."""
    if seviye == "hata":
        print(f"  \033[91m[Hata]\033[0m {modul}: {hata}")
    else:
        print(f"  \033[93m[Uyarı]\033[0m {modul}: {hata}")
```

## Usage in main.py Pattern

```python
# ── OPSIYONEL MODULLER ──────────────────────────
try:
    from iteration_budget import IterationBudget
except ImportError:
    _modul_uyar("iteration_budget", "kütüphane eksik")
    IterationBudget = None

try:
    import gateway
    _GATEWAY = gateway
except Exception as e:
    _modul_uyar("gateway", e, "hata")
    _GATEWAY = None

# ── FAZ 6 Modulleri ─────────────────────────────
try:
    from beceri_kutuphanesi import BeceriKutuphanesi as _BeceriKutuphanesi
except ImportError as e:
    _modul_uyar("beceri_kutuphanesi", e)
    _BeceriKutuphanesi = None
```

## Checking at Runtime

```python
class AIAgentOrchestrator:
    def __init__(self):
        self.gateway = _GATEWAY
        self.telegram = _TELEGRAM_BOT
    
    def gateway_health(self) -> str:
        """Gateway durumunu kontrol et."""
        parts = []
        if self.gateway: parts.append(f"✅ gateway")
        else: parts.append("❌ gateway (yüklü değil)")
        if self.telegram: parts.append(f"✅ telegram")
        else: parts.append("❌ telegram (yüklü değil)")
        return " | ".join(parts)
```

## Distinction from Circuit Breaker

This pattern is for **static import-time availability** (is the library installed?). The circuit breaker pattern in `provider_router.py` handles **runtime failures** (API is down, rate limited, auth expired). Both patterns complement each other.
