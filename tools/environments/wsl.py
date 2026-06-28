"""
tools.environments.wsl — Windows Subsystem for Linux Ortamı

Komutları WSL içinde çalıştırır. wsl.exe CLI üzerinden erişir.
"""

import locale
import logging
import platform
import subprocess
from typing import Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)


class WSLEnvironment(BaseEnvironment):
    """WSL (Windows Subsystem for Linux) ortamı.

    wsl.exe komut satırı aracılığıyla Linux dağıtımında
    komut çalıştırır.

    Args:
        dagitim: WSL dağıtım adı (None = varsayılan)
    """

    def __init__(self, dagitim: Optional[str] = None):
        self.dagitim = dagitim
        self._wsl_bulundu = self._wsl_kontrol()

    @staticmethod
    def _wsl_kontrol() -> bool:
        """wsl.exe kullanılabilir mi?"""
        try:
            subprocess.run(
                ["wsl.exe", "--version"],
                capture_output=True, timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False

    def execute(self, komut: str, timeout: Optional[int] = None) -> dict:
        """WSL içinde komut çalıştırır.

        Args:
            komut: Çalıştırılacak komut.
            timeout: Maksimum bekleme süresi (saniye).

        Returns:
            dict: {"basarili": bool, "cikti": str, "hata": str, "donus_kodu": int}
        """
        if not self._wsl_bulundu:
            return {
                "basarili": False, "cikti": "", "hata": "wsl.exe bulunamadı",
                "donus_kodu": -1,
            }
        try:
            wsl_args = ["wsl.exe"]
            if self.dagitim:
                wsl_args += ["-d", self.dagitim]
            wsl_args += ["--"] + komut.split()

            sonuc = subprocess.run(
                wsl_args,
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
                "basarili": False, "cikti": "",
                "hata": f"WSL komutu zaman aşımı ({timeout}s)", "donus_kodu": -1,
            }
        except Exception as e:
            return {
                "basarili": False, "cikti": "", "hata": str(e), "donus_kodu": -1,
            }

    def ping(self) -> bool:
        """WSL'in kullanılabilir olup olmadığını kontrol eder."""
        if not self._wsl_bulundu:
            return False
        try:
            sonuc = subprocess.run(
                ["wsl.exe", "--list", "--quiet"],
                capture_output=True, text=True, timeout=10,
            )
            return sonuc.returncode == 0
        except Exception:
            return False

    def bilgi(self) -> dict:
        return {
            "tur": "wsl",
            "dagitim": self.dagitim or "(varsayilan)",
            "wsl_bulundu": self._wsl_bulundu,
            "aciklama": "WSL Linux ortamı",
        }


def run(komut: str, dagitim: Optional[str] = None, timeout: Optional[int] = None) -> dict:
    """Kısayol: WSLEnvironment().execute()"""
    return WSLEnvironment(dagitim=dagitim).execute(komut, timeout=timeout)


def ping() -> bool:
    """Kısayol: WSLEnvironment().ping()"""
    return WSLEnvironment().ping()
