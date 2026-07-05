"""ReYMeN tools.macro shim â€” ReYMeN macro fonksiyonlarÄ±nÄ± yönlendirir."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def oynat(makro_adi: str, **kwargs) -> str:
    """ReYMeN macro.oynat â€” ReYMeN'de makro çalÄ±ÅŸtÄ±rma."""
    logger.info("Macro '%s' called with %d args (ReYMeN stub)", makro_adi, len(kwargs))
    return f"[MAKRO] {makro_adi} çalÄ±ÅŸtÄ±rÄ±ldÄ± (stub)"
