---
name: software-development_agent-fork-maintenance_references_gateway-upstream-restoration
description: Gateway Upstream Function Restoration
title: "Software Development Agent Fork Maintenance References Gateway Upstream Restoration"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Gateway Upstream Function Restoration |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Gateway Upstream Function Restoration

When a fork (e.g. ReYMeN) replaces upstream Hermes gateway files with custom versions, certain functions/constants may go missing silently. These surface as import errors in downstream modules like `stream_consumer.py`.

> **Branding note:** This fork has been renamed from "Hermes" to "ReYMeN". Directory names in code examples below use the old `hermes_reference` only when referring to the upstream reference tests directory — the fork's actual directory is `ReYMeN_reference`. Update paths accordingly in practice.

## Common Missing Items

| Missing Symbol | Required By | File to Fix | Implementation |
|----------------|-------------|-------------|----------------|
| `_custom_unit_to_cp` | `gateway/stream_consumer.py` | `gateway/platforms/base.py` | Proportionally maps safe_limit to character position (handles token/byte vs char length mismatch) |
| `MEDIA_TAG_CLEANUP_RE` | `gateway/stream_consumer.py` | `gateway/platforms/base.py` | Regex to strip `MEDIA:` tags with known-extension paths from streamed text |
| `DEFAULT_STREAMING_EDIT_INTERVAL` | `gateway/stream_consumer.py` | `gateway/config.py` | Module-level constant `float = 0.4` |
| `DEFAULT_STREAMING_BUFFER_THRESHOLD` | `gateway/stream_consumer.py` | `gateway/config.py` | Module-level constant `int = 60` |
| `DEFAULT_STREAMING_CURSOR` | `gateway/stream_consumer.py` | `gateway/config.py` | Module-level constant `str = "▊"` |

## Detect Missing Imports

Run this to surface ALL missing gateway imports at once:

```python
suspects = [
    "gateway",
    "gateway.stream_consumer",
    "gateway.stream_dispatch",
    "gateway.config",
]
for mod in suspects:
    try:
        __import__(mod, fromlist=[''])
        print(f"  ✅ {mod}")
    except ImportError as e:
        print(f"  ❌ {mod}: {e}")
```

## Restoration Pattern

### 1. Module-level constants → `gateway/config.py`

Add after the stdlib imports, before the first class:

```python
# ── Streaming sabitleri ──────────────────────────────────────────────────────
DEFAULT_STREAMING_EDIT_INTERVAL: float = 0.4
DEFAULT_STREAMING_BUFFER_THRESHOLD: int = 60
DEFAULT_STREAMING_CURSOR: str = "▊"
```

Also add matching keys to `VARSAYILAN_YAPI` dict for runtime access:

```python
VARSAYILAN_YAPI = {
    "STREAMING_EDIT_INTERVAL": 0.4,
    "STREAMING_BUFFER_THRESHOLD": 60,
    "STREAMING_CURSOR": "▊",
    "genel": {
        ...
    },
}
```

### 2. Regex + helper function → `gateway/platforms/base.py`

Add at the end of `base.py` (after existing functions, before any file-except-return patterns to avoid duplicate-match issues):

```python
import re as _re
from typing import Callable as _Callable

MEDIA_TAG_CLEANUP_RE: _re.Pattern = _re.compile(
    r'\[.*?\]\s*\(MEDIA:[^)]+\.(?:png|jpg|jpeg|gif|webp|mp4|ogg|mp3|wav|pdf|txt|json|yaml|yml|md|py|js|ts|sh|bat|ps1)\)',
    _re.IGNORECASE,
)

def _custom_unit_to_cp(
    accumulated: str,
    safe_limit: int,
    len_fn: _Callable[[str], int],
) -> int:
    """Estimate character position equivalent to safe_limit when len_fn
    differs from len() (e.g., token-based length)."""
    total = len_fn(accumulated)
    if total <= safe_limit:
        return len(accumulated)
    ratio = safe_limit / total
    return max(int(len(accumulated) * ratio), safe_limit)
```

> **Watch out:** If `base.py` has multiple `except Exception: return ""` blocks near the end, a `replace_all` patch may duplicate the function in several places. Always pin the old_string to a unique surrounding context (e.g. include the function's docstring or the preceding function name).

## Verification

```python
from gateway.stream_consumer import GatewayStreamConsumer, StreamConsumerConfig
from gateway.stream_dispatch import GatewayEventDispatcher
from gateway.platforms.base import _custom_unit_to_cp, MEDIA_TAG_CLEANUP_RE
from gateway.config import (
    DEFAULT_STREAMING_EDIT_INTERVAL,
    DEFAULT_STREAMING_BUFFER_THRESHOLD,
    DEFAULT_STREAMING_CURSOR,
)
print("✅ All gateway upstream restorations working")
```

## Why This Happens

When a fork replaces files like `gateway/platforms/base.py` with custom versions, upstream additions (especially helper functions and constants added in later upstream commits) are lost. The functions are real Hermes upstream code that `stream_consumer.py` (which was kept from upstream) depends on. The fork's custom `base.py` just never had them.
