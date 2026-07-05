"""ReYMeN tools.process_registry shim â€” ReYMeN process registry'sini yÃ¶nlendirir."""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ProcessRegistry:
    """ReYMeN ProcessRegistry â€” ReYMeN iÃ§in basit implementasyon."""

    def __init__(self):
        self._processes: Dict[str, Any] = {}

    def register(self, name: str, process: Any) -> None:
        self._processes[name] = process

    def unregister(self, name: str) -> None:
        self._processes.pop(name, None)

    def get(self, name: str) -> Any:
        return self._processes.get(name)


process_registry = ProcessRegistry()


def format_uptime_short(seconds: float) -> str:
    """ReYMeN format_uptime_short â€” ReYMeN iÃ§in basit."""
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    if h > 0:
        return f"{h}s {m}d"
    if m > 0:
        return f"{m}d {s}s"
    return f"{s}s"
