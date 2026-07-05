"""ReYMeN tools.browser_tool shim â€” ReYMeN browser fonksiyonlarÄ±nÄ± ReYMeN browser_engine'e yÃ¶nlendirir."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _emergency_cleanup_all_sessions() -> None:
    """ReYMeN browser acil kapatma â€” ReYMeN browser_engine'e yÃ¶nlendirir."""
    try:
        from reymen.arac.browser_engine import BrowserEngine

        be = BrowserEngine()
        be.kapat()
        logger.info("Browser sessions cleaned up via ReYMeN browser_engine")
    except Exception as e:
        logger.warning("Browser cleanup failed: %s", e)


def cleanup_all_browsers() -> None:
    """TÃ¼m browser session'larÄ±nÄ± temizler."""
    _emergency_cleanup_all_sessions()


def cleanup_browser() -> None:
    """Aktif browser session'Ä±nÄ± temizler."""
    _emergency_cleanup_all_sessions()


def _stop_cdp_supervisor() -> None:
    """CDP supervisor'Ä± durdurur. ReYMeN'de kullanÄ±lmaz."""
    pass


def _ensure_cdp_supervisor(*args, **kwargs) -> None:
    """CDP supervisor'Ä± garanti eder. ReYMeN'de direkt Playwright kullanÄ±lÄ±r."""
    pass


def _get_browser_engine() -> Any:
    """ReYMeN browser engine referansÄ± â€” ReYMeN BrowserEngine dÃ¶ndÃ¼rÃ¼r."""
    try:
        from reymen.arac.browser_engine import BrowserEngine

        return BrowserEngine()
    except Exception as e:
        logger.warning("BrowserEngine not available: %s", e)
        return None


def _get_cloud_provider() -> Optional[str]:
    """ReYMeN cloud browser provider â€” ReYMeN'de local browser kullanÄ±lÄ±r."""
    return None


# ---------------------------------------------------------------------------
# Ana browser tool fonksiyonlarÄ±
# ---------------------------------------------------------------------------


def browser_navigate(url: str) -> str:
    """ReYMeN browser_navigate â€” ReYMeN browser_engine'e yÃ¶nlendirir."""
    import json

    try:
        from reymen.arac.browser_engine import BrowserEngine

        be = BrowserEngine()
        be.sayfa_ac(url)
        title = be.sayfa_basligi()
        return json.dumps({"success": True, "title": title, "url": url})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
