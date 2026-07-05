"""ReYMeN â€” Otonom gÃ¶rev Ã§Ã¶zÃ¼cÃ¼ Ã§ekirdeÄŸi.

Bu paket, gÃ¶rev 7 kapsamÄ±ndaki 7 dÃ¼ÅŸÃ¼k Ã¶ncelikli Ã¶zelliÄŸi barÄ±ndÄ±rÄ±r:

- ``cost_tracker``      : API harcama takibi + log
- ``platform_adapter``  : WSL/Kali adapter + path Ã§evirici
- ``tui``               : Rich ile status bar, spinner, progress
- ``self_improve``      : Kalite metrikleri + otomatik iyileÅŸtirme
- ``kanban``            : Kart, kolon, Ã¶ncelik, deadline
- ``video_tools``       : yt-dlp + ffmpeg wrapper
- ``a2a``               : Basit agent mesajlaÅŸma (A2A prototip)
- ``problem_solver``    : AjanÄ±n sorun Ã§Ã¶zme doÄŸasÄ± (retry, fallback, Ã¶ÄŸrenme)
- ``learning_loop``     : Kendi kendine Ã¶ÄŸrenen Ã§Ã¶zÃ¼m bulma dÃ¶ngÃ¼sÃ¼

Her modÃ¼l kendi baÅŸÄ±na Ã§alÄ±ÅŸabilir ve opsiyonel baÄŸÄ±mlÄ±lÄ±klarÄ±n yokluÄŸunda
graceful fallback yapar.
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

__version__ = "0.9.0"

# tools.xxx â†’ reymen.tools.xxx import hook'u (ReYMeN baÄŸÄ±msÄ±zlÄ±k)
try:
    from reymen.tools import _importer  # noqa: F401 â€” otomatik hook kurar
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

__all__ = [
    "__version__",
    "cost_tracker",
    "platform_adapter",
    "tui",
    "self_improve",
    "kanban",
    "video_tools",
    "a2a",
    "problem_solver",
    "learning_loop",
]
