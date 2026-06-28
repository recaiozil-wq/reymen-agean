"""
tools.environments.modal — Modal Cloud Ortamı

Modal SDK ile bulut fonksiyonu çalıştırır.
Modal opsiyoneldir; kurulu değilse uyarı verir.
Türkçe docstring ile belgelenmiştir.
"""

import logging
from typing import Any, Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)

try:
    import modal
    HAS_MODAL = True
except ImportError:
    HAS_MODAL = False
    logger.warning("modal kurulu değil. Modal ortamı kullanılamaz.")


class ModalEnvironment(BaseEnvironment):
    """Modal cloud ortamı.

    Modal SDK ile bulut fonksiyonlarını çalıştırır.

    Args:
        fonksiyon_adi (str): Modal fonksiyon adı.
    """

    def __init__(self, fonksiyon_adi: str = "default"):
        self.fonksiyon_adi = fonksiyon_adi
        self._app = None

    def _get_app(self):
        """Modal uygulamasını oluşturur."""
        if self._app is not None:
            return self._app
        if not HAS_MODAL:
            raise RuntimeError("modal kurulu değil. pip install modal")
        self._app = modal.App(self.fonksiyon_adi)
        return self._app

    def execute(
        self,
        komut: str,
        fonksiyon_adi: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> dict:
        """Modal cloud'da bir fonksiyon/kod çalıştırır.

        Args:
            komut (str): Çalıştırılacak Python kodu veya shell komutu.
            fonksiyon_adi (str, optional): Fonksiyon adı (override).
            timeout (int, optional): Maksimum bekleme süresi.

        Returns:
            dict: {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "donus_kodu": int
            }
        """
        if fonksiyon_adi:
            self.fonksiyon_adi = fonksiyon_adi

        try:
            app = self._get_app()

            @app.function()
            def calistir(kod: str) -> str:
                import subprocess
                sonuc = subprocess.run(
                    kod, shell=False, capture_output=True, text=True, timeout=timeout or 60
                )
                return sonuc.stdout + ("\n" + sonuc.stderr if sonuc.stderr else "")

            with app.run():
                cikti = calistir.remote(komut)

            return {
                "basarili": True,
                "cikti": str(cikti),
                "hata": "",
                "donus_kodu": 0,
            }
        except Exception as e:
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "donus_kodu": -1,
            }

    def ping(self) -> bool:
        """Modal'ın kullanılabilir olup olmadığını kontrol eder.

        Returns:
            bool: Modal erişilebilir ise True.
        """
        if not HAS_MODAL:
            return False
        try:
            # Modal token kontrolü
            modal.config._lookup_token()
            return True
        except Exception:
            return False

    def bilgi(self) -> dict:
        """Modal ortamı hakkında bilgi döndürür.

        Returns:
            dict: Modal yapılandırma bilgileri.
        """
        return {
            "tur": "modal",
            "fonksiyon_adi": self.fonksiyon_adi,
            "modal_kurulu": HAS_MODAL,
            "aciklama": f"Modal cloud ortamı ({self.fonksiyon_adi})",
        }


# Kolay kullanım için fonksiyonlar
def run(komut: str, fonksiyon_adi: str = "default") -> dict:
    """Kısayol: ModalEnvironment().execute()"""
    return ModalEnvironment(fonksiyon_adi=fonksiyon_adi).execute(komut)


def ping() -> bool:
    """Kısayol: ModalEnvironment().ping()"""
    return ModalEnvironment().ping()
