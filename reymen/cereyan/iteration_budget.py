# -*- coding: utf-8 -*-
"""iteration_budget.py — ReYMeN thread-safe iterasyon butcesi.

Hermes Agent IterationBudget pattern'i ile ayni.
Her ajan (ana veya alt) kendi butcesine sahiptir.
Thread-safe consume/refund sayaci.

Kullanim:
    budget = IterationBudget(max_total=90)
    if budget.consume():
        # islem yap
        pass
    budget.refund()  # execute_code gibi durumlarda iade
"""

import threading


class IterationBudget:
    """Thread-safe iterasyon sayaci.

    Her ajan kendi butcesine sahip olur.
    Ana ajan: max_iterations (varsayilan 90)
    Alt ajan: delegation.max_iterations (varsayilan 50)

    Geriye uyumluluk: max_tur parametresi de calisir (max_total ile ayni).
    """

    def __init__(self, max_total: int = None, max_tur: int = None):
        # max_tur eski API uyumlulugu
        if max_total is None and max_tur is not None:
            max_total = max_tur
        if max_total is None:
            max_total = 90
        self.max_total = max_total
        self._used = 0
        self._lock = threading.Lock()

    def consume(self) -> bool:
        """Bir iterasyon harca. True: izin var, False: butce doldu."""
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True

    def refund(self) -> None:
        """Bir iterasyonu iade et (ornek: execute_code icin)."""
        with self._lock:
            if self._used > 0:
                self._used -= 1

    @property
    def used(self) -> int:
        with self._lock:
            return self._used

    @property
    def remaining(self) -> int:
        with self._lock:
            return max(0, self.max_total - self._used)

    def reset(self) -> None:
        """Butceyi sifirla."""
        with self._lock:
            self._used = 0

    def __repr__(self) -> str:
        return f"IterationBudget({self.used}/{self.max_total})"

    # ══════════════════════════════════════════════════════════════════
    # GERIYE UYUMLULUK — eski API
    # ══════════════════════════════════════════════════════════════════

    @property
    def tur(self) -> int:
        """Eski API: tur sayisi = used ile ayni."""
        return self._used

    @property
    def max_tur(self) -> int:
        """Eski API alias: max_total ile ayni."""
        return self.max_total

    def tur_basla(self) -> None:
        """Eski API: consume ile ayni."""
        self.consume()

    def tur_bitir(self, basarili: bool = True, sonuc: str = "",
                  hata_tipi: str = "") -> bool:
        """Eski API: tur sonu kontrolu. True = devam et, False = dur."""
        return self.remaining > 0

    def devam_etmeli_mi(self) -> bool:
        """Eski API: kalan butce var mi?"""
        return self.remaining > 0

    def durum_raporu(self) -> str:
        """Eski API: butce durumunu okunabilir string olarak dondur."""
        return f"Tur {self._used}/{self.max_total} (kalan: {self.remaining})"

    def gorev_tamamla(self) -> None:
        """Eski API: reset ile ayni."""
        self.reset()

    # Takma adlar
    gorev_tamami = gorev_tamamla

    def eylem_kaydet(self, eylem: str) -> None:
        """Eski API: eylem logla (no-op)."""
        pass

    def ozet_dict(self) -> dict:
        """Eski API: dict'e cevir."""
        return {"tur": self._used, "max_tur": self.max_total}

    def analiz_et(self, gorev: str) -> dict:
        """Eski API: gorev karmasikligini analiz et.

        Heuristic: bulk/toplu gorevlere karmasiklik=5 ver, digerleri keyword sayisi.
        """
        hedef = gorev.lower()

        # Toplu görev tespiti: "hepsini", "tüm", "bütün" + eylem → karmaşıklık=5
        _toplu = any(k in hedef for k in [
            "hepsini", "hepsin", "hepsını", "hepsi",
            "tümünü", "tümü", "tüm", "tumu", "tumunu",
            "bütün", "butun", "toplu",
            "tum ", "tum\t",  # "tum " (tam kelime)
        ]) or hedef.startswith("tum ")
        _islem = any(k in hedef for k in [
            "kontrol", "gider", "düzelt", "duzelt", "onar", "temizle",
            "tara", "düzenle", "duzenle", "yap", "calistir", "incele",
        ])
        if _toplu and _islem:
            return {"karmasiklik": 5}
        if _toplu:
            return {"karmasiklik": 4}

        # Çok adımlı karmaşık görevler
        _cok_adim = any(k in hedef for k in [
            "ve", "sonra", "ardindan", "ardından", "daha sonra", "once", "önce",
        ])
        anahtarlar = [
            "dosya", "web", "kod", "calistir", "ara", "yaz", "oku",
            "sil", "guncelle", "indir", "yukle", "kur", "tara",
        ]
        sayac = sum(1 for k in anahtarlar if k in hedef)
        if _cok_adim:
            sayac += 1
        return {"karmasiklik": max(1, min(sayac, 5))}
