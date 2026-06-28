# -*- coding: utf-8 -*-
"""gateway/status.py — Gateway Durum Raporu.

Tüm platformların bağlantı durumu, mesaj istatistikleri, hata sayıları.
"""

import threading
import time
from typing import Any, Optional


class PlatformStatus:
    """Tek bir platformun durum kaydı."""

    def __init__(self, platform: str):
        self.platform = platform
        self.bagli = False
        self.son_baglanti = 0.0
        self.son_kopma = 0.0
        self.giden_mesaj = 0
        self.gelen_mesaj = 0
        self.hata_sayisi = 0
        self.son_hata = ""
        self.son_hata_zamani = 0.0
        self.baslangic_zamani = time.time()

    def gonder_basarili(self):
        """Başarılı gönderim kaydet."""
        self.giden_mesaj += 1

    def gonder_basarisiz(self, hata: str = ""):
        """Başarısız gönderim kaydet."""
        self.hata_sayisi += 1
        self.son_hata = hata
        self.son_hata_zamani = time.time()

    def mesaj_alindi(self):
        """Gelen mesaj kaydet."""
        self.gelen_mesaj += 1

    def baglandi(self):
        """Bağlantı kuruldu kaydet."""
        self.bagli = True
        self.son_baglanti = time.time()

    def koptu(self, hata: str = ""):
        """Bağlantı koptu kaydet."""
        self.bagli = False
        self.son_kopma = time.time()
        if hata:
            self.hata_sayisi += 1
            self.son_hata = hata
            self.son_hata_zamani = time.time()

    def ozet(self) -> dict:
        """Platform durum özeti."""
        return {
            "platform": self.platform,
            "bagli": self.bagli,
            "son_baglanti": round(self.son_baglanti, 2) if self.son_baglanti else None,
            "son_kopma": round(self.son_kopma, 2) if self.son_kopma else None,
            "giden_mesaj": self.giden_mesaj,
            "gelen_mesaj": self.gelen_mesaj,
            "toplam_mesaj": self.giden_mesaj + self.gelen_mesaj,
            "hata_sayisi": self.hata_sayisi,
            "son_hata": self.son_hata,
            "calisma_suresi": round(time.time() - self.baslangic_zamani),
        }


class GatewayStatus:
    """Gateway durum raporu — tüm platformların durumunu toplar."""

    def __init__(self):
        self._platformlar: dict[str, PlatformStatus] = {}
        self._kilit = threading.Lock()
        self._baslangic = time.time()
        self._genel_hata = 0
        self._genel_giden = 0
        self._genel_gelen = 0

    # ── Platform Yönetimi ─────────────────────────────────────────────

    def platform_ekle(self, platform: str) -> PlatformStatus:
        """Yeni platform durum kaydı ekle."""
        with self._kilit:
            if platform not in self._platformlar:
                self._platformlar[platform] = PlatformStatus(platform)
            return self._platformlar[platform]

    def platform_al(self, platform: str) -> Optional[PlatformStatus]:
        """Platform durum kaydını al."""
        with self._kilit:
            return self._platformlar.get(platform)

    def platform_sil(self, platform: str) -> bool:
        """Platform durum kaydını sil."""
        with self._kilit:
            return bool(self._platformlar.pop(platform, None))

    # ── Olay Kaydı ────────────────────────────────────────────────────

    def gonder_basarili(self, platform: str):
        """Başarılı mesaj gönderimi kaydet."""
        ps = self.platform_ekle(platform)
        ps.gonder_basarili()
        with self._kilit:
            self._genel_giden += 1

    def gonder_basarisiz(self, platform: str, hata: str = ""):
        """Başarısız mesaj gönderimi kaydet."""
        ps = self.platform_ekle(platform)
        ps.gonder_basarisiz(hata)
        with self._kilit:
            self._genel_hata += 1

    def mesaj_alindi(self, platform: str):
        """Mesaj alındı kaydet."""
        ps = self.platform_ekle(platform)
        ps.mesaj_alindi()
        with self._kilit:
            self._genel_gelen += 1

    def platform_baglandi(self, platform: str):
        """Platform bağlandı kaydet."""
        ps = self.platform_ekle(platform)
        ps.baglandi()

    def platform_koptu(self, platform: str, hata: str = ""):
        """Platform bağlantısı koptu kaydet."""
        ps = self.platform_ekle(platform)
        ps.koptu(hata)

    # ── Rapor ─────────────────────────────────────────────────────────

    def platform_raporu(self, platform: str) -> Optional[dict]:
        """Tek bir platformun durum raporu."""
        ps = self.platform_al(platform)
        if not ps:
            return None
        return ps.ozet()

    def genel_rapor(self) -> dict:
        """Tüm gateway'in durum raporu."""
        with self._kilit:
            platform_ozetleri = {
                p: ps.ozet() for p, ps in self._platformlar.items()
            }
            bagli_sayisi = sum(1 for ps in self._platformlar.values() if ps.bagli)
            toplam_hata = sum(ps.hata_sayisi for ps in self._platformlar.values())

            return {
                "calisma_suresi": round(time.time() - self._baslangic),
                "platform_sayisi": len(self._platformlar),
                "bagli_platform": bagli_sayisi,
                "genel_giden": self._genel_giden,
                "genel_gelen": self._genel_gelen,
                "genel_toplam": self._genel_giden + self._genel_gelen,
                "genel_hata": self._genel_hata,
                "toplam_platform_hata": toplam_hata,
                "platformlar": platform_ozetleri,
            }

    def platform_listesi(self) -> list[dict]:
        """Platformların özet listesi."""
        with self._kilit:
            return [
                {
                    "platform": ps.platform,
                    "bagli": ps.bagli,
                    "giden": ps.giden_mesaj,
                    "gelen": ps.gelen_mesaj,
                    "hata": ps.hata_sayisi,
                }
                for ps in self._platformlar.values()
            ]

    def sifirla(self):
        """Tüm istatistikleri sıfırla."""
        with self._kilit:
            self._platformlar.clear()
            self._genel_hata = 0
            self._genel_giden = 0
            self._genel_gelen = 0
            self._baslangic = time.time()

    # ── Ortak Gateway Metodları ───────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü — genel raporun özetini döndür."""
        return {
            "modul": "status",
            "durum": "hazir",
            "platform_sayisi": len(self._platformlar),
            "bagli_platform": sum(1 for ps in self._platformlar.values() if ps.bagli),
            "toplam_mesaj": self._genel_giden + self._genel_gelen,
            "toplam_hata": self._genel_hata,
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Durum mesajı gönder (platform adına bir olay kaydeder)."""
        self.mesaj_alindi(hedef)
        return f"[Status]: {hedef} için mesaj alındı olarak kaydedildi."


# Global instance
durum = GatewayStatus()


if __name__ == "__main__":
    gs = GatewayStatus()
    gs.platform_baglandi("telegram")
    gs.gonder_basarili("telegram")
    gs.gonder_basarili("telegram")
    gs.mesaj_alindi("telegram")
    gs.gonder_basarisiz("whatsapp", "Bağlantı zaman aşımı")
    gs.platform_baglandi("whatsapp")

    import json
    print(json.dumps(gs.genel_rapor(), indent=2, ensure_ascii=False))
    print("---")
    print(gs.ping())
