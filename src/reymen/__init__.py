"""ReYMeN â€” Otonom görev çözücü çekirdeÄŸi.

Bu paket, görev 7 kapsamÄ±ndaki 7 düÅŸük öncelikli özelliÄŸi barÄ±ndÄ±rÄ±r:

- ``cost_tracker``      : API harcama takibi + log
- ``platform_adapter``  : WSL/Kali adapter + path çevirici
- ``tui``               : Rich ile status bar, spinner, progress
- ``self_improve``      : Kalite metrikleri + otomatik iyileÅŸtirme
- ``kanban``            : Kart, kolon, öncelik, deadline
- ``video_tools``       : yt-dlp + ffmpeg wrapper
- ``a2a``               : Basit agent mesajlaÅŸma (A2A prototip)
- ``problem_solver``    : AjanÄ±n sorun çözme doÄŸasÄ± (retry, fallback, öÄŸrenme)
- ``learning_loop``     : Kendi kendine öÄŸrenen çözüm bulma döngüsü

Her modül kendi baÅŸÄ±na çalÄ±ÅŸabilir ve opsiyonel baÄŸÄ±mlÄ±lÄ±klarÄ±n yokluÄŸunda
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
