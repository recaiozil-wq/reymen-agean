"""
tools.environments.local — Yerel (Local) Ortamı

Komutları doğrudan Windows üzerinde subprocess ile çalıştırır.
Türkçe docstring ile belgelenmiştir.
"""

import locale
import logging
import platform
import subprocess
import sys
from typing import Any, Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)


class LocalEnvironment(BaseEnvironment):
    """Yerel Windows ortamı. Subprocess kullanarak komut çalıştırır."""

    def __init__(self):
        self._sistem = platform.system()
        self._makine = platform.machine()

    def execute(self, komut: str, timeout: Optional[int] = None) -> dict:
        """Yerel ortamda bir komut çalıştırır.

        Args:
            komut (str): Çalıştırılacak komut.
            timeout (int, optional): Maksimum bekleme süresi (saniye).

        Returns:
            dict: {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "donus_kodu": int
            }
        """
        try:
            sonuc = subprocess.run(
                komut,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=locale.getpreferredencoding(),
            )
            return {
                "basarili": sonuc.returncode == 0,
                "cikti": sonuc.stdout,
                "hata": sonuc.stderr,
                "donus_kodu": sonuc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Komut zaman aşımına uğradı ({timeout}s)",
                "donus_kodu": -1,
            }
        except Exception as e:
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "donus_kodu": -1,
            }

    def ping(self) -> bool:
        """Yerel ortamın kullanılabilir olduğunu doğrular.

        Returns:
            bool: Her zaman True (yerel sistem her zaman erişilebilir).
        """
        return True

    def bilgi(self) -> dict:
        """Yerel ortam hakkında bilgi döndürür.

        Returns:
            dict: Sistem bilgileri.
        """
        return {
            "tur": "local",
            "sistem": self._sistem,
            "makine": self._makine,
            "python": sys.version,
            "aciklama": "Yerel Windows ortamı",
        }


# Kolay kullanım için fonksiyonlar
def run(komut: str, timeout: Optional[int] = None) -> dict:
    """Kısayol: LocalEnvironment().execute()"""
    return LocalEnvironment().execute(komut)


def ping() -> bool:
    """Kısayol: LocalEnvironment().ping()"""
    return LocalEnvironment().ping()


# ---------------------------------------------------------------------------
# ReYMeN referans API — env sanitization & provider credential blocklist
# ---------------------------------------------------------------------------

import os as _os

# ReYMeN saglayici kimlik bilgileri — subprocess'e kesinlikle gecmemeli.
_ReYMeN_PROVIDER_ENV_BLOCKLIST: frozenset = frozenset({
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_TOKEN",
    "CLAUDE_API_KEY",
    "HERMES_API_KEY",
    "REYMEN_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GROQ_API_KEY",
    "COHERE_API_KEY",
    "MISTRAL_API_KEY",
    "OPENROUTER_API_KEY",
    "TOGETHER_API_KEY",
    "DEEPSEEK_API_KEY",
    "XAI_API_KEY",
})


def _sanitize_subprocess_env(env: dict) -> dict:
    """Subprocess ortamindan saglayici kimlik bilgilerini cikar.

    Blocklist'teki hicbir anahtar cocuk surece gecmemelidir.
    """
    return {k: v for k, v in env.items() if k not in _ReYMeN_PROVIDER_ENV_BLOCKLIST}


def _make_run_env(extra: dict) -> dict:
    """Subprocess icin guvenli ortam olustur.

    Mevcut os.environ'u sanitize eder, extra degerlerle birlestirip
    tekrar sanitize eder (blocklist kesinlikle gecmez).
    """
    base = _sanitize_subprocess_env(_os.environ.copy())
    merged = {**base, **extra}
    return _sanitize_subprocess_env(merged)
