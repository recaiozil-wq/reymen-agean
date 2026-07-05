"""ReYMeN tools.delegate_tool shim â€” gerÃ§ek implementasyon iÃ§in delegate_task_tool'a yÃ¶nlendirir."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_max_concurrent_children() -> int:
    """ReYMeN _get_max_concurrent_children â€” maksimum paralel alt ajan sayÄ±sÄ±."""
    return int(__import__("os").environ.get("DELEGATE_MAX_PARALEL", "5"))


def delegate_task(*args, **kwargs) -> Any:
    """ReYMeN delegate_task â€” reymen.tools.delegate_task_tool'a yÃ¶nlendirir.

    GerÃ§ek ThreadPoolExecutor tabanlÄ± implementasyon iÃ§in
    reymen.tools.delegate_task_tool.delegate_task() kullanÄ±lÄ±r.
    """
    try:
        from reymen.tools.delegate_task_tool import delegate_task as _real_delegate

        return _real_delegate(*args, **kwargs)
    except ImportError as _e:
        logger.warning("delegate_task_tool yÃ¼klenemedi, stub kullanÄ±lÄ±yor: %s", _e)
        return []


def motor_kaydet(motor) -> None:
    """DELEGATE_TASK tool'unu motor'a kaydet.

    GerÃ§ek tool kaydÄ± delegate_task_tool.py Ã¼zerinden yapÄ±lÄ±r.
    Bu fonksiyon sadece eski referanslar iÃ§in tutulmaktadÄ±r.
    """
    try:
        from reymen.tools.delegate_task_tool import motor_kaydet as _real_kaydet

        _real_kaydet(motor)
    except ImportError as _e:
        logger.warning("delegate_task_tool yÃ¼klenemedi, tool kaydedilemedi: %s", _e)
