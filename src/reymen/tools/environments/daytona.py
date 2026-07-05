"""
ReYMeN tools.environments.daytona â€” Daytona cloud sandbox environment.

Daytona (https://daytona.io) ile cloud'da izole sandbox ortami olusturur
ve komut calistirir. Python SDK (pip install daytona) ile calisir.

Yapilandirma (ortam degiskenleri):
  - DAYTONA_API_KEY â€” Daytona API anahtari (zorunlu)
  - DAYTONA_TARGET  â€” Hedef bolge (opsiyonel, varsayilan: "us")
  - DAYTONA_TIMEOUT â€” Komut zamani asimi saniye (opsiyonel, varsayilan: 60)

Kullanim:
    env = DaytonaEnvironment()
    sonuc = await env.calistir("python script.py")
    print(sonuc["cikti"])
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    from daytona import Daytona, DaytonaConfig
    from daytona.models import ExecuteResponse

    DAYTONA_AVAILABLE = True
except ImportError:
    DAYTONA_AVAILABLE = False
    Daytona = Any  # type: ignore[assignment]
    DaytonaConfig = Any  # type: ignore[assignment]
    ExecuteResponse = Any  # type: ignore[assignment]


def check_daytona_requirements() -> bool:
    """Check if daytona SDK is available, attempt lazy install if not."""
    global DAYTONA_AVAILABLE, Daytona, DaytonaConfig, ExecuteResponse
    if DAYTONA_AVAILABLE:
        return True
    try:
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "daytona", "-q"],
            timeout=30,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False
    try:
        from daytona import Daytona as _D, DaytonaConfig as _DC
        from daytona.models import ExecuteResponse as _ER

        Daytona = _D
        DaytonaConfig = _DC
        ExecuteResponse = _ER
        DAYTONA_AVAILABLE = True
        return True
    except ImportError:
        return False


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[Daytona] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Daytona Environment
# ---------------------------------------------------------------------------


class DaytonaEnvironment:
    """
    Daytona cloud sandbox environment.

    Her `calistir()` cagrisinda yeni bir sandbox olusturur, komutu calistirir
    ve sandbox'i temizler. Bu sayede her calistirma izole ve guvenlidir.

    Dayaniklilik:
    - API key yoksa hata firlatir
    - SDK kurulu degilse lazy install dener
    - Sandbox olusturulamazsa hata firlatir
    - Komut zamani asarsa TimeoutError firlatir
    - Sandbox temizleme hatalari loglanir, gizlenmez
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        target: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Args:
            api_key: Daytona API anahtari. None ise DAYTONA_API_KEY env'den okur.
            target: Hedef bolge (us/eu/asia vs.). None ise DAYTONA_TARGET env'den okur.
            timeout: Varsayilan komut zamani asimi (saniye).
        """
        self._api_key: str = api_key or _env("DAYTONA_API_KEY", "")
        self._target: str = target or _env("DAYTONA_TARGET", "us")
        self._timeout: int = int(_env("DAYTONA_TIMEOUT", str(timeout)))
        self._client: Optional[Daytona] = None
        self._sandbox: Any = None  # daytona.Sandbox

    # â”€â”€ Bagimlilik Kontrolu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @property
    def hazir(self) -> bool:
        """Daytona ortaminin kullanima hazir olup olmadigini kontrol eder."""
        if not DAYTONA_AVAILABLE:
            return False
        if not self._api_key:
            logger.warning("[Daytona] DAYTONA_API_KEY ayarlanmamis.")
            return False
        return True

    # â”€â”€ Istemci Yonetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _get_client(self) -> Daytona:
        """Daytona istemcisini olusturur (lazy init)."""
        if self._client is None:
            config = DaytonaConfig(api_key=self._api_key, target=self._target)
            self._client = Daytona(config)
        return self._client

    async def _create_sandbox(self):
        """Yeni bir Daytona sandbox'i olusturur."""
        client = self._get_client()
        self._sandbox = await asyncio.to_thread(client.create)
        logger.info(
            "[Daytona] Sandbox olusturuldu: %s",
            getattr(self._sandbox, "id", "?"),
        )

    async def _delete_sandbox(self):
        """Sandbox'i guvenli sekilde temizler."""
        if self._sandbox is None:
            return
        try:
            await asyncio.to_thread(self._sandbox.delete)
            logger.info("[Daytona] Sandbox temizlendi.")
        except Exception as e:
            logger.warning("[Daytona] Sandbox temizleme hatasi: %s", e)
        finally:
            self._sandbox = None

    # â”€â”€ Komut Calistirma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def calistir(
        self,
        komut: str,
        *,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Daytona sandbox'inda komut calistirir.

        Args:
            komut: Calistirilacak shell komutu.
            timeout: Zamani asimi (saniye). None ise varsayilan kullanilir.
            workdir: Calisma dizini (sandbox icinde).

        Returns:
            {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "exit_code": int,
                "sandbox_id": str,
            }
        """
        # On kosullar
        if not DAYTONA_AVAILABLE:
            if not check_daytona_requirements():
                return {
                    "basarili": False,
                    "cikti": "",
                    "hata": "daytona SDK kurulu degil. pip install daytona",
                    "exit_code": -1,
                    "sandbox_id": "",
                }

        if not self._api_key:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "DAYTONA_API_KEY eksik. Daytona Dashboard'dan API key alin.",
                "exit_code": -1,
                "sandbox_id": "",
            }

        sandbox_id = ""
        try:
            # Sandbox olustur
            await self._create_sandbox()
            sandbox_id = str(getattr(self._sandbox, "id", ""))

            # workdir ayarla
            if workdir and self._sandbox:
                try:
                    await asyncio.to_thread(
                        self._sandbox.fs.create_folder,
                        f"/workspace/{workdir.lstrip('/')}",
                    )
                    komut = f"cd /workspace/{workdir.lstrip('/')} && {komut}"
                except Exception:
                    pass  # workdir basarisiz olursa normal calistir

            # Komutu calistir
            actual_timeout = timeout or self._timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(self._sandbox.process.code_run, komut),
                timeout=actual_timeout,
            )

            # Yaniti isle
            exit_code = getattr(response, "exit_code", -1)
            result_text = getattr(response, "result", "") or ""
            error_text = getattr(response, "error", "") or ""

            return {
                "basarili": exit_code == 0,
                "cikti": result_text,
                "hata": error_text,
                "exit_code": exit_code,
                "sandbox_id": sandbox_id,
            }

        except asyncio.TimeoutError:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Komut zaman asimi ({timeout or self._timeout}s)",
                "exit_code": -1,
                "sandbox_id": sandbox_id,
            }

        except Exception as e:
            logger.error("[Daytona] Komut calistirma hatasi: %s", e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "exit_code": -1,
                "sandbox_id": sandbox_id,
            }

        finally:
            # Sandbox'i temizle
            await self._delete_sandbox()

    # â”€â”€ Bilgi Metodlari â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def __repr__(self) -> str:
        return (
            f"DaytonaEnvironment(target={self._target}, "
            f"timeout={self._timeout}s, "
            f"hazir={self.hazir})"
        )

    def __str__(self) -> str:
        durum = "hazir" if self.hazir else "hazir degil"
        return f"Daytona [target={self._target}, {durum}]"
