"""
tools.environments.singularity — Singularity/Apptainer Konteyner Ortamı

Singularity/Apptainer ile HPC ortamında komut çalıştırır.
Singularity/Apptainer opsiyoneldir; kurulu değilse uyarı verir.
Türkçe docstring ile belgelenmiştir.
"""

import logging
import subprocess
import shutil
from typing import Any, Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)


class SingularityEnvironment(BaseEnvironment):
    """Singularity/Apptainer konteyner ortamı.

    HPC sistemlerinde Singularity veya Apptainer ile
    konteyner içinde komut çalıştırır.

    Args:
        imaj_yolu (str): .sif imaj dosyasının yolu.
    """

    def __init__(self, imaj_yolu: str = ""):
        self.imaj_yolu = imaj_yolu
        self._binary = self._bul_binary()

    def _bul_binary(self) -> Optional[str]:
        """Sistemde singularity veya apptainer binary'sini bulur."""
        for b in ["apptainer", "singularity"]:
            yol = shutil.which(b)
            if yol:
                logger.info(f"Singularity binary bulundu: {yol}")
                return yol
        logger.warning("singularity veya apptainer bulunamadı.")
        return None

    def execute(
        self,
        komut: str,
        imaj_yolu: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> dict:
        """Singularity konteyner içinde komut çalıştırır.

        Args:
            komut (str): Çalıştırılacak komut.
            imaj_yolu (str, optional): .sif imaj yolu (override).
            timeout (int, optional): Maksimum bekleme süresi.

        Returns:
            dict: {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "donus_kodu": int
            }
        """
        if imaj_yolu:
            self.imaj_yolu = imaj_yolu
        if not self._binary:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "singularity/apptainer bulunamadı.",
                "donus_kodu": -1,
            }
        if not self.imaj_yolu:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "İmaj yolu belirtilmedi.",
                "donus_kodu": -1,
            }

        try:
            singularity_komut = [
                self._binary, "exec",
                self.imaj_yolu,
                "sh", "-c", komut,
            ]
            sonuc = subprocess.run(
                singularity_komut,
                capture_output=True,
                text=True,
                timeout=timeout,
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
                "hata": f"Zaman aşımı ({timeout}s)",
                "donus_kodu": -1,
            }
        except FileNotFoundError:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"{self._binary} çalıştırılamadı.",
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
        """Singularity/Apptainer'ın kullanılabilir olduğunu kontrol eder.

        Returns:
            bool: Binary mevcut ve çalışabiliyorsa True.
        """
        if not self._binary:
            return False
        try:
            sonuc = subprocess.run(
                [self._binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return sonuc.returncode == 0
        except Exception:
            return False

    def bilgi(self) -> dict:
        """Singularity ortamı hakkında bilgi döndürür.

        Returns:
            dict: Singularity yapılandırma bilgileri.
        """
        surum = ""
        if self._binary:
            try:
                sonuc = subprocess.run(
                    [self._binary, "--version"],
                    capture_output=True, text=True, timeout=5,
                )
                surum = sonuc.stdout.strip()
            except Exception:
                surum = "bilinmiyor"
        return {
            "tur": "singularity",
            "binary": self._binary,
            "surum": surum,
            "imaj_yolu": self.imaj_yolu,
            "aciklama": f"Singularity/Apptainer HPC ortamı ({surum})",
        }


# --- ReYMeN uyumlu yardımcı fonksiyonlar ---

def _get_scratch_dir():
    """Geçici çalışma dizini döndür — ReYMeN uyumluluğu."""
    import os, pathlib
    scratch = os.environ.get("SCRATCH") or os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(scratch)


def _get_apptainer_cache_dir():
    """Apptainer cache dizini — ReYMeN uyumluluğu."""
    import pathlib
    return _get_scratch_dir() / "apptainer-cache"

# --- ReYMeN uyumlu yardımcı fonksiyonlar sonu ---


# Kolay kullanım için fonksiyonlar
def run(komut: str, imaj_yolu: str = "") -> dict:
    """Kısayol: SingularityEnvironment().execute()"""
    return SingularityEnvironment(imaj_yolu=imaj_yolu).execute(komut)


def ping() -> bool:
    """Kısayol: SingularityEnvironment().ping()"""
    return SingularityEnvironment().ping()
