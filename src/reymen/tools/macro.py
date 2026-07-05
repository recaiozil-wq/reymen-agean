"""ReYMeN tools.macro shim â€” ReYMeN macro fonksiyonlarÄ±nÄ± yÃ¶nlendirir."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def oynat(makro_adi: str, **kwargs) -> str:
    """ReYMeN macro.oynat â€” ReYMeN'de makro Ã§alÄ±ÅŸtÄ±rma."""
    logger.info("Macro '%s' called with %d args (ReYMeN stub)", makro_adi, len(kwargs))
    return f"[MAKRO] {makro_adi} Ã§alÄ±ÅŸtÄ±rÄ±ldÄ± (stub)"
