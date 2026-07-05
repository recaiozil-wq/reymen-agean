"""ReYMeN tools.delegate_tool shim â€” gerçek implementasyon için delegate_task_tool'a yönlendirir."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_max_concurrent_children() -> int:
    """ReYMeN _get_max_concurrent_children â€” maksimum paralel alt ajan sayÄ±sÄ±."""
    return int(__import__("os").environ.get("DELEGATE_MAX_PARALEL", "5"))


def delegate_task(*args, **kwargs) -> Any:
    """ReYMeN delegate_task â€” reymen.tools.delegate_task_tool'a yönlendirir.

    Gerçek ThreadPoolExecutor tabanlÄ± implementasyon için
    reymen.tools.delegate_task_tool.delegate_task() kullanÄ±lÄ±r.
    """
    try:
        from reymen.tools.delegate_task_tool import delegate_task as _real_delegate

        return _real_delegate(*args, **kwargs)
    except ImportError as _e:
        logger.warning("delegate_task_tool yüklenemedi, stub kullanÄ±lÄ±yor: %s", _e)
        return []


def motor_kaydet(motor) -> None:
    """DELEGATE_TASK tool'unu motor'a kaydet.

    Gerçek tool kaydÄ± delegate_task_tool.py üzerinden yapÄ±lÄ±r.
    Bu fonksiyon sadece eski referanslar için tutulmaktadÄ±r.
    """
    try:
        from reymen.tools.delegate_task_tool import motor_kaydet as _real_kaydet

        _real_kaydet(motor)
    except ImportError as _e:
        logger.warning("delegate_task_tool yüklenemedi, tool kaydedilemedi: %s", _e)
