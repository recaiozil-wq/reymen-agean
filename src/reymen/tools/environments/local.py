"""
ReYMeN tools.environments.local — Local subprocess environment.

Yerel makinede shell komutlari calistirir. Python standard kutuphanesi
ile calisir — harici bagimlilik gerektirmez.

Kullanim:
    env = LocalEnvironment()
    sonuc = await env.calistir("ls -la")
    print(sonuc["cikti"])
"""
from __future__ import annotations

import asyncio
import functools
import logging
import subprocess
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Local Environment
# ---------------------------------------------------------------------------


class LocalEnvironment:
    """
    Yerel subprocess ortami.

    `subprocess.run()` ile shell komutlari calistirir. Hem senkron
    (sync_run) hem de asenkron (calistir) kullanim destekler.
    """

    def __init__(self, timeout: int = 60):
        """
        Args:
            timeout: Varsayilan komut zamani asimi (saniye).
        """
        self._timeout: int = timeout

    # ── Durum ─────────────────────────────────────────────────────────

    @property
    def hazir(self) -> bool:
        """Yerel ortam her zaman hazirdir."""
        return True

    # ── Senkron Calistirma ────────────────────────────────────────────

    def sync_run(
        self,
        komut: str,
        *,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Shell komutunu senkron olarak calistirir.

        Args:
            komut: Calistirilacak shell komutu.
            timeout: Zamani asimi (saniye). None ise varsayilan kullanilir.
            workdir: Calisma dizini.

        Returns:
            {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "exit_code": int,
                "ortam": "local",
            }
        """
        actual_timeout = timeout if timeout is not None else self._timeout

        try:
            result = subprocess.run(
                komut,
                shell=True,
                capture_output=True,
                text=True,
                timeout=actual_timeout,
                cwd=workdir,
            )

            return {
                "basarili": result.returncode == 0,
                "cikti": result.stdout or "",
                "hata": result.stderr or "",
                "exit_code": result.returncode,
                "ortam": "local",
            }

        except subprocess.TimeoutExpired:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Komut zaman asimi ({actual_timeout}s)",
                "exit_code": -1,
                "ortam": "local",
            }

        except FileNotFoundError as e:
            logger.error("[Local] Komut bulunamadi: %s", e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Komut bulunamadi: {e}",
                "exit_code": -1,
                "ortam": "local",
            }

        except OSError as e:
            logger.error("[Local] Sistem hatasi: %s", e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "exit_code": -1,
                "ortam": "local",
            }

        except Exception as e:
            logger.error("[Local] Beklenmeyen hata: %s", e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "exit_code": -1,
                "ortam": "local",
            }

    # ── Asenkron Calistirma ───────────────────────────────────────────

    async def calistir(
        self,
        komut: str,
        *,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Shell komutunu asenkron olarak calistirir.

        Asagidaki durumlari thread havuzuna havale eder:
        - subprocess.run() cagrisi
        - cwd, timeout gibi ayarlar

        Args:
            komut: Calistirilacak shell komutu.
            timeout: Zamani asimi (saniye). None ise varsayilan kullanilir.
            workdir: Calisma dizini.

        Returns:
            {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "exit_code": int,
                "ortam": "local",
            }
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self.sync_run,
            komut,
        ) | {"timeout": timeout, "workdir": workdir}

    # ── Bilgi Metodlari ──────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"LocalEnvironment(timeout={self._timeout}s)"

    def __str__(self) -> str:
        return "Local [her zaman hazir]"
