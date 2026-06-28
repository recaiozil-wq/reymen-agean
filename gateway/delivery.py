# -*- coding: utf-8 -*-
"""gateway/delivery.py — Mesaj Teslimat Motoru.

Mesaj kuyruğu, yeniden deneme, teslimat durumu takibi.
"""

import json
import os
import threading
import time
import uuid
from typing import Any, Callable, Optional
import logging
logger = logging.getLogger(__name__)


class DeliveryItem:
    """Teslimat öğesi — kuyruktaki bir mesajı temsil eder."""

    def __init__(self, platform: str, hedef: str, mesaj: str,
                 meta: Optional[dict] = None):
        self.id = uuid.uuid4().hex[:12]
        self.platform = platform
        self.hedef = hedef
        self.mesaj = mesaj
        self.meta = meta or {}
        self.olusturma = time.time()
        self.son_deneme = 0.0
        self.deneme_sayisi = 0
        self.durum = "beklemede"  # beklemede | gonderiliyor | basarili | basarisiz
        self.son_hata = ""


class DeliveryEngine:
    """Mesaj teslimat motoru — kuyruk, yeniden deneme, durum takibi."""

    def __init__(self, max_deneme: int = 3, bekleme_suresi: float = 2.0):
        self._max_deneme = max_deneme
        self._bekleme_suresi = bekleme_suresi
        self._kuyruk: list[DeliveryItem] = []
        self._gecmis: list[DeliveryItem] = []
        self._kilit = threading.Lock()
        self._gonderici: Optional[Callable] = None
        self._calisiyor = False
        self._thread: Optional[threading.Thread] = None

    # ── Kuyruk Yönetimi ───────────────────────────────────────────────

    def kuyruk_ekle(self, platform: str, hedef: str, mesaj: str,
                    meta: Optional[dict] = None) -> str:
        """Mesajı teslimat kuyruğuna ekle.

        Args:
            platform: Hedef platform
            hedef: Hedef kanal/kullanıcı
            mesaj: Mesaj içeriği
            meta: Ek metadata

        Returns:
            Teslimat ID'si
        """
        item = DeliveryItem(platform, hedef, mesaj, meta)
        with self._kilit:
            self._kuyruk.append(item)
        return item.id

    def kuyruk_uzunlugu(self) -> int:
        """Kuyruktaki bekleyen mesaj sayısı."""
        with self._kilit:
            return len(self._kuyruk)

    def kuyruk_temizle(self):
        """Kuyruğu tamamen temizle."""
        with self._kilit:
            self._kuyruk.clear()

    # ── Gönderici Bağlama ──────────────────────────────────────────────

    def gonderici_bagla(self, fn: Callable[[str, str, str, dict], str]):
        """Mesaj gönderme fonksiyonunu bağla.

        Args:
            fn: (platform, hedef, mesaj, meta) -> str
        """
        self._gonderici = fn

    # ── Teslimat Döngüsü ──────────────────────────────────────────────

    def baslat(self):
        """Teslimat motorunu arka planda başlat."""
        if self._calisiyor:
            return
        self._calisiyor = True
        self._thread = threading.Thread(target=self._don, daemon=True)
        self._thread.start()

    def durdur(self):
        """Teslimat motorunu durdur."""
        self._calisiyor = False

    def _don(self):
        """Ana teslimat döngüsü."""
        while self._calisiyor:
            try:
                self._bir_sonraki_gonder()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
            time.sleep(0.5)

    def _bir_sonraki_gonder(self):
        """Kuyruktaki bir sonraki mesajı göndermeyi dene."""
        item: Optional[DeliveryItem] = None
        with self._kilit:
            for i, it in enumerate(self._kuyruk):
                if it.durum == "beklemede":
                    item = it
                    item.durum = "gonderiliyor"
                    item.son_deneme = time.time()
                    item.deneme_sayisi += 1
                    del self._kuyruk[i]
                    break

        if not item:
            return

        try:
            if self._gonderici:
                sonuc = self._gonderici(item.platform, item.hedef, item.mesaj, item.meta)
                item.durum = "basarili"
            else:
                item.durum = "basarili"
                sonuc = "[Delivery]: Gönderici bağlı değil (simülasyon)"
        except Exception as e:
            item.son_hata = str(e)
            if item.deneme_sayisi < self._max_deneme:
                item.durum = "beklemede"
                time.sleep(self._bekleme_suresi * item.deneme_sayisi)
                with self._kilit:
                    self._kuyruk.append(item)
                return
            else:
                item.durum = "basarisiz"

        with self._kilit:
            self._gecmis.append(item)

    # ── Durum ve İstatistik ────────────────────────────────────────────

    def teslimat_durumu(self, item_id: str) -> Optional[dict]:
        """Bir teslimatın durumunu döndür."""
        with self._kilit:
            for item in self._kuyruk:
                if item.id == item_id:
                    return self._item_dict(item)
            for item in self._gecmis:
                if item.id == item_id:
                    return self._item_dict(item)
        return None

    def istatistik(self) -> dict:
        """Teslimat istatistikleri."""
        with self._kilit:
            toplam = len(self._gecmis)
            basarili = sum(1 for i in self._gecmis if i.durum == "basarili")
            basarisiz = sum(1 for i in self._gecmis if i.durum == "basarisiz")
            return {
                "bekleyen": len(self._kuyruk),
                "tamamlanan": toplam,
                "basarili": basarili,
                "basarisiz": basarisiz,
                "max_deneme": self._max_deneme,
            }

    @staticmethod
    def _item_dict(item: DeliveryItem) -> dict:
        return {
            "id": item.id,
            "platform": item.platform,
            "hedef": item.hedef,
            "durum": item.durum,
            "deneme": item.deneme_sayisi,
            "son_hata": item.son_hata,
        }

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "delivery",
            "durum": "hazir",
            "calisiyor": self._calisiyor,
            **self.istatistik(),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Kuyruğa mesaj ekle ve hemen dön."""
        platform = kwargs.get("platform", "default")
        item_id = self.kuyruk_ekle(platform, hedef, mesaj)
        return f"[Delivery]: Kuyruğa eklendi (ID: {item_id})"


# Global instance
motor = DeliveryEngine()


class DeliveryRouter:
    """Mesaj yonlendirici — platform adapterlerine mesaj dagitir.

    Minimal stub: gateway/run.py'nin import zincirini kirabilmek icin
    gereken minimum arayuzu saglar.
    """

    def __init__(self, config: Any):
        self.config = config
        self.adapters: dict = {}


if __name__ == "__main__":
    de = DeliveryEngine()
    de.baslat()
    id1 = de.kuyruk_ekle("telegram", "user1", "Merhaba!")
    id2 = de.kuyruk_ekle("whatsapp", "user2", "Selam!")
    print(f"Kuyruk: {de.kuyruk_uzunlugu()}")
    time.sleep(1)
    de.durdur()
    print(de.istatistik())
