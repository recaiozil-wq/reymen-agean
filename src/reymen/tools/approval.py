"""ReYMeN tools.approval shim â€” ReYMeN onay mekanizmasÄ±nÄ± ReYMeN'e yÃ¶nlendirir."""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

_approval_callback: Optional[Callable] = None


def set_approval_callback(callback: Optional[Callable]) -> None:
    global _approval_callback
    _approval_callback = callback


def request_approval(
    action: str,
    details: str = "",
    timeout: float = 30.0,
) -> bool:
    """ReYMeN request_approval â€” ReYMeN'de varsayÄ±lan olarak onaylar."""
    if _approval_callback:
        try:
            return bool(_approval_callback(action, details))
        except Exception as e:
            logger.warning("Approval callback failed: %s", e)
    return True  # VarsayÄ±lan: onayla


def request_approval_async(
    action: str,
    details: str = "",
    timeout: float = 30.0,
) -> bool:
    return request_approval(action, details, timeout)
