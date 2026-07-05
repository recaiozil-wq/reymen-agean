"""ReYMeN tools.achievements shim â€” ReYMeN baÅŸarÄ±mlarÄ±nÄ± yönlendirir."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _listeye_ekle(*args, **kwargs) -> None:
    """ReYMeN _listeye_ekle â€” ReYMeN'de no-op."""
    pass


def check_achievements(*args, **kwargs) -> Any:
    """ReYMeN check_achievements â€” ReYMeN'de no-op."""
    return []


def rozet_listele(*args, **kwargs) -> str:
    """ReYMeN rozet_listele â€” ReYMeN'de no-op."""
    return "Rozetler (ReYMeN stub)"
