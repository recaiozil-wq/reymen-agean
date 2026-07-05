"""ReYMeN tools.skill_usage shim â€” ReYMeN skill kullanÄ±m takibini yÃ¶nlendirir."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def bump_use(skill_name: str, by: int = 1) -> None:
    """ReYMeN bump_use â€” ReYMeN'de skill kullanÄ±m sayacÄ±."""
    logger.debug("Skill '%s' usage bumped by %d (ReYMeN stub)", skill_name, by)
