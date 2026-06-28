# -*- coding: utf-8 -*-
"""gateway/hooks.py — Gateway Hook Sistemi.

Olay bazlı hook'lar: mesaj_geldi, mesaj_gitti, hata_olustu.
"""

import threading
import time
from typing import Any, Callable, Optional


class Hooks:
    """Gateway hook sistemi — olay bazlı callback yönetimi."""

    OLAYLAR = {
        "mesaj_geldi": "Bir platformdan mesaj alındığında tetiklenir",
        "mesaj_gitti": "Bir platforma mesaj gönderildiğinde tetiklenir",
        "hata_olustu": "Bir işlem sırasında hata oluştuğunda tetiklenir",
        "platform_baglandi": "Bir platform bağlantı kurduğunda tetiklenir",
        "platform_koptu": "Bir platform bağlantısı kesildiğinde tetiklenir",
        "baslangic": "Gateway başladığında tetiklenir",
        "kapanis": "Gateway kapanırken tetiklenir",
    }

    def __init__(self):
        self._hooklar: dict[str, list[dict]] = {olay: [] for olay in self.OLAYLAR}
        self._kilit = threading.Lock()

    # ── Hook Kaydı ─────────────────────────────────────────────────────

    def kaydet(self, olay: str, callback: Callable,
               ad: Optional[str] = None, sira: int = 0) -> bool:
        """Bir olaya hook kaydet.

        Args:
            olay: Olay adı (mesaj_geldi, mesaj_gitti, hata_olustu, ...)
            callback: Tetiklenecek fonksiyon
            ad: Opsiyonel hook adı
            sira: Çalışma sırası (düşük önce çalışır)

        Returns:
            Başarılı mı
        """
        if olay not in self.OLAYLAR:
            return False
        with self._kilit:
            self._hooklar[olay].append({
                "ad": ad or f"hook_{len(self._hooklar[olay])}",
                "callback": callback,
                "sira": sira,
                "kayit_zamani": time.time(),
            })
            self._hooklar[olay].sort(key=lambda h: h["sira"])
        return True

    def sil(self, olay: str, ad: str) -> bool:
        """Bir hook'u kaldır."""
        with self._kilit:
            if olay not in self._hooklar:
                return False
            onceki = len(self._hooklar[olay])
            self._hooklar[olay] = [
                h for h in self._hooklar[olay] if h["ad"] != ad
            ]
            return len(self._hooklar[olay]) < onceki

    def temizle(self, olay: Optional[str] = None):
        """Hook'ları temizle. Olay belirtilmezse tümünü temizle."""
        with self._kilit:
            if olay:
                self._hooklar[olay] = []
            else:
                for o in self.OLAYLAR:
                    self._hooklar[o] = []

    def listele(self, olay: Optional[str] = None) -> dict:
        """Kayıtlı hook'ları listele."""
        with self._kilit:
            if olay:
                return {
                    olay: [
                        {"ad": h["ad"], "sira": h["sira"]}
                        for h in self._hooklar.get(olay, [])
                    ]
                }
            return {
                o: [{"ad": h["ad"], "sira": h["sira"]} for h in hooklar]
                for o, hooklar in self._hooklar.items()
            }

    # ── Hook Tetikleme ─────────────────────────────────────────────────

    def tetikle(self, olay: str, *args, **kwargs) -> list[Any]:
        """Bir olaydaki tüm hook'ları tetikle.

        Args:
            olay: Olay adı
            *args: Callback'lere iletilecek argümanlar
            **kwargs: Callback'lere iletilecek keyword argümanlar

        Returns:
            Hook sonuçları listesi
        """
        sonuclar = []
        with self._kilit:
            hooklar = list(self._hooklar.get(olay, []))

        for hook in hooklar:
            try:
                sonuc = hook["callback"](*args, **kwargs)
                sonuclar.append({"hook": hook["ad"], "sonuc": sonuc})
            except Exception as e:
                sonuclar.append({
                    "hook": hook["ad"],
                    "hata": str(e),
                })
                # Hata hook'unu da tetikle (sonsuz döngü önle)
                if olay != "hata_olustu":
                    self.tetikle("hata_olustu", olay=olay, hook=hook["ad"], hata=str(e))
        return sonuclar

    # ── Kolaylık Metodları ─────────────────────────────────────────────

    def mesaj_geldi(self, mesaj: str, platform: str, meta: Optional[dict] = None):
        """mesaj_geldi olayını tetikle (kolaylık)."""
        return self.tetikle("mesaj_geldi", mesaj=mesaj, platform=platform, meta=meta or {})

    def mesaj_gitti(self, mesaj: str, platform: str, hedef: str,
                    durum: str = "basarili"):
        """mesaj_gitti olayını tetikle (kolaylık)."""
        return self.tetikle(
            "mesaj_gitti", mesaj=mesaj, platform=platform,
            hedef=hedef, durum=durum,
        )

    def hata_olustu(self, kaynak: str, hata: str, detay: Optional[dict] = None):
        """hata_olustu olayını tetikle (kolaylık)."""
        return self.tetikle(
            "hata_olustu", kaynak=kaynak, hata=hata, detay=detay or {},
        )

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "hooks",
            "durum": "hazir",
            "olay_sayisi": len(self.OLAYLAR),
            "toplam_hook": sum(len(v) for v in self._hooklar.values()),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Hook üzerinden mesaj gönder (hook tetikler gibi)."""
        sonuc = self.tetikle("mesaj_gitti", mesaj=mesaj, platform=hedef)
        return f"[Hooks]: {len(sonuc)} hook tetiklendi."


# Global instance
hooklar = Hooks()


if __name__ == "__main__":
    h = Hooks()

    @h.kaydet("mesaj_geldi", ad="logger")
    def _log(mesaj, platform, meta):
        print(f"[{platform}] {mesaj[:50]}...")

    # Alternatif kayıt
    h.kaydet("mesaj_geldi", lambda mesaj, platform, meta: print(f"Geldi: {mesaj}"),
             ad="printci", sira=10)

    h.mesaj_geldi("Merhaba dünya!", "telegram")
    print(h.listele())
    print(h.ping())
