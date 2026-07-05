"""ReYMeN tools.interrupt shim (override) â€” ReYMeN interrupt yÃ¶netimini ReYMeN'e yÃ¶nlendirir."""

from __future__ import annotations

import logging
import os
import threading

logger = logging.getLogger(__name__)

_thread_local = threading.local()
_DEBUG_INTERRUPT = bool(os.getenv("REYMEN_DEBUG_INTERRUPT", os.getenv("HERMES_DEBUG_INTERRUPT")))


def is_interrupted() -> bool:
    """ReYMeN'de interrupt mekanizmasÄ± yok â€” her zaman False."""
    return False


def set_interrupt(thread_id: int) -> None:
    logger.debug("set_interrupt(%d) â€” ReYMeN stub", thread_id)


def clear_interrupt() -> None:
    logger.debug("clear_interrupt â€” ReYMeN stub")
