"""ReYMeN tools.skills_tool shim â€” ReYMeN skill fonksiyonlarÄ±nÄ± ReYMeN'e yönlendirir."""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

_secret_capture_callback: Optional[Callable] = None


def set_secret_capture_callback(callback: Optional[Callable]) -> None:
    global _secret_capture_callback
    _secret_capture_callback = callback


def skill_view(name: str) -> str:
    """ReYMeN skill_view â€” ReYMeN skill_view tool'una yönlendirir."""
    import json

    try:
        from reymen.arac.skill_utils import skill_goruntule

        return json.dumps({"success": True, "content": skill_goruntule(name)})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
