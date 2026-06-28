# -*- coding: utf-8 -*-
"""gateway/response_filters.py — Yanıt Filtreleri.

Otomatik yanıt kuralları, spam filtresi, içerik denetimi.
"""

import re
import threading
import time
from typing import Any, Callable, Optional


class ResponseFilter:
    """Tek bir filtre kuralı."""

    def __init__(self, ad: str, desen: str, yanit: str,
                   aktif: bool = True, platform: Optional[str] = None):
        self.ad = ad
        self.desen = desen
        self._regex = re.compile(desen, re.IGNORECASE)
        self.yanit = yanit
        self.aktif = aktif
        self.platform = platform
        self.tetiklenme = 0
        self.son_tetiklenme = 0.0

    def esles(self, mesaj: str) -> bool:
        """Mesaj filtreye uyuyor mu?"""
        return bool(self._regex.search(mesaj))

    def tetikle(self) -> str:
        """Filtreyi tetikle, yanıt metnini döndür."""
        self.tetiklenme += 1
        self.son_tetiklenme = time.time()
        return self.yanit

    def __repr__(self) -> str:
        return f"<Filter '{self.ad}': /{self.desen}/ -> {self.yanit[:30]}>"


class SpamKontrol:
    """Spam kontrolü — rate limit ve tekrar mesaj denetimi."""

    def __init__(self, esik: int = 5, pencere: float = 10.0):
        self._esik = esik  # max mesaj sayısı
        self._pencere = pencere  # saniye cinsinden zaman penceresi
        self._kayit: dict[str, list[float]] = {}
        self._kilit = threading.Lock()

    def kontrol(self, gonderen: str) -> bool:
        """Spam kontrolü. True = spam (engellendi)."""
        with self._kilit:
            simdi = time.time()
            if gonderen not in self._kayit:
                self._kayit[gonderen] = [simdi]
                return False

            zamanlar = self._kayit[gonderen]
            # Pencere dışındakileri temizle
            zamanlar[:] = [t for t in zamanlar if simdi - t < self._pencere]
            zamanlar.append(simdi)

            if len(zamanlar) > self._esik:
                return True
            return False

    def sifirla(self, gonderen: Optional[str] = None):
        """Spam kaydını sıfırla."""
        with self._kilit:
            if gonderen:
                self._kayit.pop(gonderen, None)
            else:
                self._kayit.clear()


class IcerikDenetim:
    """İçerik denetimi — yasaklı kelime ve desen kontrolü."""

    def __init__(self):
        self._yasakli_kelimeler: list[str] = []
        self._yasakli_regex: list[re.Pattern] = []
        self._izin_verilenler: list[str] = []

    def kelime_ekle(self, kelime: str):
        """Yasaklı kelime ekle."""
        self._yasakli_kelimeler.append(kelime.lower())

    def regex_ekle(self, desen: str):
        """Yasaklı regex deseni ekle."""
        self._yasakli_regex.append(re.compile(desen, re.IGNORECASE))

    def izin_ekle(self, gonderen: str):
        """Göndereni izin listesine ekle."""
        self._izin_verilenler.append(gonderen.lower())

    def denetle(self, mesaj: str, gonderen: Optional[str] = None) -> Optional[str]:
        """Mesajı denetle. Sorun varsa hata mesajı, yoksa None.

        Args:
            mesaj: Denetlenecek mesaj
            gonderen: Gönderen ID'si (izin listesi için)

        Returns:
            Sorun varsa açıklama, yoksa None
        """
        # İzin listesi kontrolü
        if gonderen and gonderen.lower() in self._izin_verilenler:
            return None

        mesaj_lower = mesaj.lower()

        # Yasaklı kelime kontrolü
        for kelime in self._yasakli_kelimeler:
            if kelime in mesaj_lower:
                return f"Yasaklı kelime: '{kelime}'"

        # Regex kontrolü
        for regex in self._yasakli_regex:
            if regex.search(mesaj):
                return f"Yasaklı desen: '{regex.pattern}'"

        return None


class ResponseFilters:
    """Yanıt filtreleri yöneticisi."""

    def __init__(self):
        self._filtreler: list[ResponseFilter] = []
        self._kilit = threading.Lock()
        self.spam = SpamKontrol()
        self.icerik = IcerikDenetim()

    # ── Filtre Yönetimi ────────────────────────────────────────────────

    def filtre_ekle(self, ad: str, desen: str, yanit: str,
                    aktif: bool = True, platform: Optional[str] = None) -> bool:
        """Yeni bir otomatik yanıt filtresi ekle.

        Args:
            ad: Filtre adı (benzersiz)
            desen: Regex deseni
            yanit: Yanıt metni
            aktif: Aktif mi
            platform: Opsiyonel platform kısıtlaması

        Returns:
            Başarılı mı
        """
        with self._kilit:
            # Aynı ada sahip filtre var mı kontrol et
            for f in self._filtreler:
                if f.ad == ad:
                    return False
            try:
                filtre = ResponseFilter(ad, desen, yanit, aktif, platform)
                self._filtreler.append(filtre)
                return True
            except re.error:
                return False

    def filtre_sil(self, ad: str) -> bool:
        """Filtre sil."""
        with self._kilit:
            onceki = len(self._filtreler)
            self._filtreler = [f for f in self._filtreler if f.ad != ad]
            return len(self._filtreler) < onceki

    def filtre_aktif(self, ad: str, aktif: bool) -> bool:
        """Filtreyi aktif/pasif yap."""
        with self._kilit:
            for f in self._filtreler:
                if f.ad == ad:
                    f.aktif = aktif
                    return True
            return False

    def filtre_listele(self) -> list[dict]:
        """Tüm filtreleri listele."""
        with self._kilit:
            return [
                {
                    "ad": f.ad,
                    "desen": f.desen,
                    "yanit": f.yanit[:60],
                    "aktif": f.aktif,
                    "platform": f.platform,
                    "tetiklenme": f.tetiklenme,
                }
                for f in self._filtreler
            ]

    # ── Filtre Uygulama ───────────────────────────────────────────────

    def isle(self, mesaj: str, platform: str,
             gonderen: Optional[str] = None) -> Optional[str]:
        """Mesaja filtreleri uygula. Eşleşen ilk yanıtı döndür.

        Args:
            mesaj: Gelen mesaj
            platform: Platform adı
            gonderen: Gönderen ID'si

        Returns:
            Otomatik yanıt varsa metni, yoksa None
        """
        # Spam kontrolü
        if gonderen and self.spam.kontrol(gonderen):
            return "[Spam]: Çok fazla mesaj gönderdiniz."

        # İçerik denetimi
        sorun = self.icerik.denetle(mesaj, gonderen)
        if sorun:
            return f"[Icerik]: {sorun}"

        # Otomatik yanıt filtreleri
        with self._kilit:
            for f in self._filtreler:
                if not f.aktif:
                    continue
                if f.platform and f.platform != platform:
                    continue
                if f.esles(mesaj):
                    return f.tetikle()

        return None

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "response_filters",
            "durum": "hazir",
            "filtre_sayisi": len(self._filtreler),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Mesajı filtrelerden geçir ve sonucu döndür."""
        sonuc = self.isle(mesaj, hedef)
        if sonuc:
            return f"[Filtre]: {sonuc}"
        return f"[Filtre]: {hedef} için eşleşme yok."


# Global instance
filtreler = ResponseFilters()


if __name__ == "__main__":
    rf = ResponseFilters()
    rf.filtre_ekle("merhaba", r"merhaba|selam|slm", "Merhaba! Size nasıl yardımcı olabilirim?")
    rf.filtre_ekle("yardim", r"yardım|help", "/yardim ile komutları görebilirsiniz.")

    print(rf.isle("merhaba", "telegram"))
    print(rf.isle("yardım", "whatsapp"))
    print(rf.isle("nasılsın", "telegram"))  # Eşleşme yok
    print(rf.filtre_listele())
    print(rf.ping())
