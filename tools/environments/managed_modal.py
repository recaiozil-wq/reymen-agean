"""
Yönetilen Modal ortam eklentisi.

Modal üzerinde yönetilen (managed) bulut ortamları.
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ManagedModalEnvironment:
    """Modal yönetilen ortam yöneticisi."""

    def __init__(self, app_adı: str = "ReYMeN-managed", token_id: Optional[str] = None, token_secret: Optional[str] = None):
        self.app_adı = app_adı
        self.token_id = token_id
        self.token_secret = token_secret
        self._app = None

    def _modal_app(self):
        """Modal uygulamasını al (geç yükleme)."""
        if self._app is not None:
            return self._app
        try:
            import modal

            modal.config.token_id = self.token_id or "not-set"
            modal.config.token_secret = self.token_secret or "not-set"
            self._app = modal.App(self.app_adı)
            return self._app
        except ImportError:
            logger.warning("Modal kütüphanesi yüklü değil")
            return None

    def _async_run(self, fn, *args, **kwargs):
        """Modal async fonksiyonunu çalıştırır."""
        try:
            # Modal async çalıştırma
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fn(*args, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            logger.error("Modal async çalıştırma hatası: %s", e)
            return None

    def fonksiyon_calistir(self, kod: str) -> dict[str, Any]:
        """Modal üzerinde bir fonksiyon çalıştırır.

        Args:
            kod: Çalıştırılacak Python kodu (fonksiyon tanımı).

        Returns:
            Çalıştırma sonucu.
        """
        try:
            import modal

            app = self._modal_app()
            if not app:
                return {"durum": "hata", "hata": "Modal başlatılamadı"}

            # Dinamik Modal fonksiyonu
            @app.function()
            def calistir():
                exec(kod, globals())
                return "kod çalıştırıldı"

            sonuc = calistir.remote()
            return {"durum": "basarili", "sonuc": str(sonuc)}
        except ImportError:
            return {"durum": "hata", "hata": "modal kütüphanesi gerekli: pip install modal"}
        except Exception as e:
            logger.error("Modal fonksiyon hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def sekronize_et(self, dosya_yolu: str) -> dict[str, Any]:
        """Bir dosyayı Modal ortamına senkronize eder.

        Args:
            dosya_yolu: Senkronize edilecek dosya yolu.

        Returns:
            İşlem sonucu.
        """
        try:
            import modal

            app = self._modal_app()
            if not app:
                return {"durum": "hata", "hata": "Modal başlatılamadı"}

            with open(dosya_yolu) as f:
                icerik = f.read()

            @app.function()
            def yaz_ve_calistir():
                with open(dosya_yolu.split("/")[-1], "w") as f:
                    f.write(icerik)
                return f"{dosya_yolu} senkronize edildi"

            sonuc = yaz_ve_calistir.remote()
            return {"durum": "basarili", "mesaj": str(sonuc)}
        except Exception as e:
            logger.error("Modal senkronizasyon hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        try:
            import modal
            return json.dumps({
                "durum": "hazir",
                "app": self.app_adı,
                "modal_versiyon": modal.__version__,
            }, indent=2, ensure_ascii=False)
        except ImportError:
            return json.dumps({
                "durum": "modal_yok",
                "mesaj": "Modal kütüphanesi yüklü değil. pip install modal",
            }, indent=2, ensure_ascii=False)
