"""
ReYMeN tools.environments.ssh â€” SSH remote environment.

SSH uzerinden uzak sunucuda komut calistirir.
Hem parola hem de SSH key authentication destekler.

Yapilandirma (ortam degiskenleri):
  - SSH_HOST       â€” Sunucu adresi (zorunlu)
  - SSH_PORT       â€” Port (varsayilan: 22)
  - SSH_USER       â€” Kullanici adi (varsayilan: root)
  - SSH_PASSWORD   â€” Parola (opsiyonel, key yoksa zorunlu)
  - SSH_KEY_PATH   â€” SSH private key yolu (opsiyonel)
  - SSH_TIMEOUT    â€” Komut zamani asimi saniye (varsayilan: 60)

Kullanim:
    env = SSHEnvironment()
    sonuc = await env.calistir("ls -la")
    print(sonuc["cikti"])
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    import asyncssh

    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    asyncssh = Any  # type: ignore[assignment]


def check_ssh_requirements() -> bool:
    """Check if asyncssh is available, attempt lazy install if not."""
    global SSH_AVAILABLE, asyncssh
    if SSH_AVAILABLE:
        return True
    try:
        import subprocess
        import sys

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "asyncssh", "-q"],
            timeout=30,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False
    try:
        import asyncssh as _A

        asyncssh = _A
        SSH_AVAILABLE = True
        return True
    except ImportError:
        return False


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# ---------------------------------------------------------------------------
# SSH Environment
# ---------------------------------------------------------------------------


class SSHEnvironment:
    """
    SSH remote environment.

    Uzak sunucuda shell komutlari calistirir. Her `calistir()` cagrisi
    yeni bir SSH baglantisi acar, komutu calistirir ve baglantiyi kapatir.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 22,
        user: str = "root",
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Args:
            host: Sunucu adresi. None ise SSH_HOST env'den okur.
            port: SSH portu. None ise SSH_PORT env'den okur.
            user: Kullanici adi. None ise SSH_USER env'den okur.
            password: Parola. None ise SSH_PASSWORD env'den okur.
            key_path: SSH private key yolu. None ise SSH_KEY_PATH env'den okur.
            timeout: Komut zamani asimi (saniye).
        """
        self._host: str = host or _env("SSH_HOST", "")
        self._port: int = port or int(_env("SSH_PORT", "22"))
        self._user: str = user or _env("SSH_USER", "root")
        self._password: Optional[str] = password or _env("SSH_PASSWORD", "") or None
        self._key_path: Optional[str] = key_path or _env("SSH_KEY_PATH", "") or None
        self._timeout: int = timeout or int(_env("SSH_TIMEOUT", "60"))

    # â”€â”€ Bagimlilik Kontrolu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @property
    def hazir(self) -> bool:
        """SSH ortaminin kullanima hazir olup olmadigini kontrol eder."""
        if not SSH_AVAILABLE:
            return False
        if not self._host:
            logger.warning("[SSH] SSH_HOST ayarlanmamis.")
            return False
        return True

    # â”€â”€ Baglanti Yardimcisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _baglanti_kwargs(self) -> dict:
        """asyncssh.connect() icin kwargs hazirlar."""
        kwargs: dict = {
            "host": self._host,
            "port": self._port,
            "username": self._user,
            "known_hosts": None,  # host key kontrolu yapma
        }

        if self._password:
            kwargs["password"] = self._password
        elif self._key_path:
            kwargs["client_keys"] = [self._key_path]

        return kwargs

    # â”€â”€ Komut Calistirma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def calistir(
        self,
        komut: str,
        *,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        SSH uzerinden uzak sunucuda komut calistirir.

        Args:
            komut: Calistirilacak shell komutu.
            timeout: Zamani asimi (saniye). None ise varsayilan kullanilir.
            workdir: Calisma dizini (sunucu icinde).

        Returns:
            {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "exit_code": int,
                "host": str,
            }
        """
        # On kosullar
        if not SSH_AVAILABLE:
            if not check_ssh_requirements():
                return {
                    "basarili": False,
                    "cikti": "",
                    "hata": "asyncssh kurulu degil. pip install asyncssh",
                    "exit_code": -1,
                    "host": self._host,
                }

        if not self._host:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "SSH_HOST eksik. Hedef sunucu adresini belirtin.",
                "exit_code": -1,
                "host": "",
            }

        actual_timeout = timeout or self._timeout

        try:
            # SSH baglantisi ac
            kwargs = self._baglanti_kwargs()
            async with asyncssh.connect(**kwargs) as conn:  # type: ignore[arg-type]
                # workdir varsa cd ile birlestir
                calistir_komut = komut
                if workdir:
                    calistir_komut = f"cd {workdir} && {komut}"

                # Komutu calistir
                result = await asyncio.wait_for(
                    conn.run(calistir_komut),
                    timeout=actual_timeout,
                )

                exit_code = result.returncode or -1
                stdout = result.stdout or ""
                stderr = result.stderr or ""

                return {
                    "basarili": exit_code == 0,
                    "cikti": stdout,
                    "hata": stderr,
                    "exit_code": exit_code,
                    "host": f"{self._user}@{self._host}:{self._port}",
                }

        except asyncio.TimeoutError:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Komut ({actual_timeout}s) veya baglanti zaman asimi",
                "exit_code": -1,
                "host": f"{self._user}@{self._host}:{self._port}",
            }

        except asyncssh.DisconnectError as e:
            logger.error("[SSH] Baglanti hatasi (%s:%d): %s", self._host, self._port, e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"SSH baglanti hatasi: {e}",
                "exit_code": -1,
                "host": f"{self._user}@{self._host}:{self._port}",
            }

        except asyncssh.PermissionDeniedError:
            logger.error(
                "[SSH] Kimlik dogrulama hatasi (%s@%s)", self._user, self._host
            )
            return {
                "basarili": False,
                "cikti": "",
                "hata": "SSH kimlik dogrulama hatasi. Kullanici/parola/key kontrol edin.",
                "exit_code": -1,
                "host": f"{self._user}@{self._host}:{self._port}",
            }

        except OSError as e:
            logger.error("[SSH] Baglanti hatasi (%s:%d): %s", self._host, self._port, e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Sunucuya erisilemiyor: {e}",
                "exit_code": -1,
                "host": f"{self._user}@{self._host}:{self._port}",
            }

        except Exception as e:
            logger.error("[SSH] Beklenmeyen hata: %s", e)
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "exit_code": -1,
                "host": f"{self._user}@{self._host}:{self._port}",
            }

    # â”€â”€ Bilgi Metodlari â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def __repr__(self) -> str:
        return (
            f"SSHEnvironment(host={self._host}:{self._port}, "
            f"user={self._user}, "
            f"hazir={self.hazir})"
        )

    def __str__(self) -> str:
        durum = "hazir" if self.hazir else "hazir degil"
        return f"SSH [{self._user}@{self._host}:{self._port}, {durum}]"
