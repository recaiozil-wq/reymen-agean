"""
ReYMeN tools.terminal_tool â€” Terminal komut yoneticisi.

SSH, Daytona ve local subprocess ortamlari ile entegre shell komutu
calistirma. Ortam secimi otomatik (env var) veya manuel (ortam parametresi)
yapilabilir.

Ortam Secimi (oncelik sirasi):
  1. `ortam` parametresi ile manuel secim (local/ssh/daytona)
  2. SSH_HOST env var varsa -> SSH
  3. DAYTONA_API_KEY env var varsa -> Daytona
  4. Hicbiri yoksa -> local
"""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict, Optional

from .environments.local import LocalEnvironment
from .environments.ssh import SSHEnvironment
from .environments.daytona import DaytonaEnvironment

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ReYMeN uyumluluk arayuzleri (degismeden kalir)
# ---------------------------------------------------------------------------

_sudo_password_callback: Optional[Callable] = None
_approval_callback: Optional[Callable] = None


def set_sudo_password_callback(callback: Optional[Callable]) -> None:
    global _sudo_password_callback
    _sudo_password_callback = callback


def set_approval_callback(callback: Optional[Callable]) -> None:
    global _approval_callback
    _approval_callback = callback


def cleanup_all_environments() -> None:
    """ReYMeN cleanup_all_environments â€” ReYMeN'de no-op."""
    logger.debug("cleanup_all_environments: ReYMeN stub")


def cleanup_vm() -> None:
    """ReYMeN cleanup_vm â€” ReYMeN'de no-op."""
    logger.debug("cleanup_vm: ReYMeN stub")


# ---------------------------------------------------------------------------
# Ortam Secimi
# ---------------------------------------------------------------------------


def _ortam_bul(ortam: Optional[str] = None) -> str:
    """
    Kullanilacak ortam turunu belirler.

    Args:
        ortam: Acikca belirtilmis ortam (local/ssh/daytona).
               None ise env var'larina gore otomatik secim yapar.

    Returns:
        "local", "ssh" veya "daytona"
    """
    if ortam and ortam.lower() in ("local", "ssh", "daytona"):
        return ortam.lower()

    # Otomatik tespit
    if os.environ.get("SSH_HOST", "").strip():
        return "ssh"
    if os.environ.get("DAYTONA_API_KEY", "").strip():
        return "daytona"
    return "local"


# ---------------------------------------------------------------------------
# Ana Calistirma Fonksiyonu
# ---------------------------------------------------------------------------


async def calistir(
    komut: str,
    ortam: Optional[str] = None,
    *,
    timeout: Optional[int] = None,
    workdir: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Shell komutunu uygun ortamda calistirir.

    Args:
        komut: Calistirilacak shell komutu.
        ortam: Hedef ortam (local/ssh/daytona).
               None -> env var'larindan otomatik tespit.
        timeout: Zamani asimi (saniye). None -> ortam varsayilani.
        workdir: Calisma dizini (hedef ortam icinde).
        **kwargs: Ortama ozel ek parametreler (opsiyonel).

    Returns:
        {
            "basarili": bool,
            "cikti": str,
            "hata": str,
            "exit_code": int,
            "ortam": "local" | "ssh" | "daytona",
            ... (ortama ozel ek alanlar)
        }

    Ornek:
        >>> sonuc = await calistir("ls -la")
        >>> print(sonuc["cikti"])

        >>> sonuc = await calistir(
        ...     "python test.py",
        ...     ortam="ssh",
        ...     workdir="/home/proje",
        ...     timeout=120,
        ... )
        >>> print(sonuc["basarili"])

        >>> sonuc = await calistir(
        ...     "npm run build",
        ...     ortam="daytona",
        ... )
        >>> print(sonuc.get("sandbox_id", ""))
    """
    secilen_ortam = _ortam_bul(ortam)
    logger.debug(
        "[terminal_tool] calistir: ortam=%s komut=%s", secilen_ortam, komut[:80]
    )

    if secilen_ortam == "ssh":
        env = SSHEnvironment(**kwargs)
        if not env.hazir:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "SSH ortami hazir degil. SSH_HOST ayarlandigindan emin olun.",
                "exit_code": -1,
                "ortam": "ssh",
            }
        return await env.calistir(komut, timeout=timeout, workdir=workdir)

    elif secilen_ortam == "daytona":
        env = DaytonaEnvironment(**kwargs)
        if not env.hazir:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "Daytona ortami hazir degil. DAYTONA_API_KEY ayarlandigindan emin olun.",
                "exit_code": -1,
                "ortam": "daytona",
            }
        return await env.calistir(komut, timeout=timeout, workdir=workdir)

    else:
        # local (varsayilan)
        env = LocalEnvironment(**kwargs)
        return await env.calistir(komut, timeout=timeout, workdir=workdir)
