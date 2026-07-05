"""ReYMeN tools.tirith_security shim â€” ReYMeN Tirith gÃ¼venlik kontrollerini yÃ¶nlendirir."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def ensure_installed() -> bool:
    """ReYMeN ensure_installed â€” ReYMeN'de Tirith kullanÄ±lmaz."""
    return True


def is_platform_supported() -> bool:
    """ReYMeN is_platform_supported â€” ReYMeN'de her platform desteklenir."""
    return True
