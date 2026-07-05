# -*- coding: utf-8 -*-
"""iteration_budget.py â€” ReYMeN thread-safe iterasyon butcesi.

ReYMeN Agent IterationBudget pattern'i ile ayni.
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

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # GERIYE UYUMLULUK â€” eski API
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

    def tur_bitir(
        self, basarili: bool = True, sonuc: str = "", hata_tipi: str = ""
    ) -> bool:
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
        """Gorev karmasikligini analiz et (1-5).

        Kategori bazli hesaplama:
          1 = selamlasma/sosyal/basit soru
          2 = tek kategorili basit islem
          3 = iki kategorili veya cok adimli islem
          4 = 3+ kategori veya toplu gorev (swarm esigi)
          5 = toplu + islem (swarm)
        """
        hedef = gorev.lower().strip()

        # â”€â”€ 0. Selamlasma/sosyal/basit soru â†’ direkt 1 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        _selam = any(
            k in hedef
            for k in [
                "merhaba",
                "selam",
                "naber",
                "nasÄ±lsÄ±n",
                "nasilsin",
                "iyi misin",
                "teÅŸekkÃ¼r",
                "tesekkur",
                "saÄŸol",
                "sagol",
                "gÃ¼naydÄ±n",
                "gunaydin",
                "iyi gÃ¼nler",
                "iyi gunler",
                "iyi akÅŸamlar",
                "iyi aksamlar",
                "iyi geceler",
                "ne yapÄ±yorsun",
                "ne yapiyorsun",
                "napÄ±yorsun",
                "napiyorsun",
                "kolay gelsin",
                "hayÄ±rlÄ±",
                "hayirli",
            ]
        )
        # Eger sadece selam kelimeleri varsa (ek istek yoksa)
        if _selam:
            # Icinde ek islem kelimesi yoksa direkt 1
            _ek_islem = any(
                k in hedef
                for k in [
                    "yap",
                    "ara",
                    "oku",
                    "yaz",
                    "sil",
                    "bul",
                    "calistir",
                    "Ã§alÄ±ÅŸtÄ±r",
                    "indir",
                    "yukle",
                    "yÃ¼kle",
                    "kur",
                    "gÃ¶nder",
                    "gonder",
                    "tara",
                    "kontrol",
                    "dÃ¼zelt",
                    "duzelt",
                    "temizle",
                    "dÃ¼zenle",
                    "duzenle",
                    "raporla",
                    "analiz",
                    "incele",
                    "gÃ¼ncelle",
                    "guncelle",
                    "aÃ§",
                    "ac",
                    "kapat",
                    "kes",
                    "koÅŸtur",
                    "kostur",
                ]
            )
            if not _ek_islem:
                return {"karmasiklik": 1}

        # â”€â”€ 1. Toplu gorev tespiti â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        _toplu = any(
            k in hedef
            for k in [
                "hepsini",
                "hepsin",
                "hepsi",
                "tÃ¼mÃ¼nÃ¼",
                "tÃ¼mÃ¼",
                "tÃ¼m",
                "tumu",
                "tumunu",
                "bÃ¼tÃ¼n",
                "butun",
                "toplu",
            ]
        )
        _islem = any(
            k in hedef
            for k in [
                "kontrol",
                "gider",
                "dÃ¼zelt",
                "duzelt",
                "onar",
                "temizle",
                "tara",
                "dÃ¼zenle",
                "duzenle",
                "yap",
                "calistir",
                "Ã§alÄ±ÅŸtÄ±r",
                "incele",
                "dÃ¶nÃ¼ÅŸtÃ¼r",
                "donustur",
                "gÃ¼ncelle",
                "guncelle",
            ]
        )
        if _toplu and _islem:
            return {"karmasiklik": 5}
        if _toplu:
            return {"karmasiklik": 4}

        # â”€â”€ 2. Cok adimli gorev tespiti (baglac + virgul) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        _cok_adim_baglac = any(
            k in hedef
            for k in [
                "ve",
                "sonra",
                "ardindan",
                "ardÄ±ndan",
                "daha sonra",
                "once",
                "Ã¶nce",
                "daha Ã¶nce",
                "daha once",
            ]
        )
        _cok_adim_virgul = hedef.count(",") >= 2
        _cok_adim = _cok_adim_baglac or _cok_adim_virgul

        # â”€â”€ 3. Kategori bazinda keyword sayisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # Her kategoriden ilk keyword sayilir, ayni kategoriden
        # birden fazla keyword extra puan vermez
        kategoriler = {
            "dosya_islem": ["dosya", "klasÃ¶r", "klasor", "dizin", "belge", "uzanti"],
            "web_islem": [
                "web",
                "internet",
                "url",
                "site",
                "sayfa",
                "link",
                "indir",
                "yukle",
                "yÃ¼kle",
                "gÃ¶nder",
                "gonder",
            ],
            "kod_islem": [
                "kod",
                "python",
                "script",
                "calistir",
                "Ã§alÄ±ÅŸtÄ±r",
                "analiz",
                "derle",
                "debug",
                "test",
            ],
            "sistem_islem": [
                "sistem",
                "komut",
                "terminal",
                "powershell",
                "servis",
                "port",
                "aÄŸ",
                "ag",
                "islem",
                "iÅŸlem",
                "proses",
                "durdur",
            ],
            "arama_islem": [
                "ara",
                "bul",
                "tara",
                "sorgula",
                "keÅŸfet",
                "kesfet",
                "listele",
                "getir",
            ],
            "yazma_islem": [
                "yaz",
                "oluÅŸtur",
                "olustur",
                "kaydet",
                "ekle",
                "gÃ¼ncelle",
                "guncelle",
                "sil",
                "dÃ¼zenle",
                "duzenle",
                "temizle",
                "dÃ¶nÃ¼ÅŸtÃ¼r",
                "donustur",
                "dÃ¼zelt",
                "duzelt",
                "onar",
            ],
            "guvenlik": [
                "gÃ¼venlik",
                "guvenlik",
                "ÅŸifre",
                "sifre",
                "izin",
                "yetki",
                "eriÅŸim",
                "erisim",
            ],
            "github_islem": [
                "git",
                "github",
                "repo",
                "commit",
                "push",
                "pull",
                "clone",
                "branch",
                "merge",
            ],
        }

        # Ekstra puan veren kelimeler (kategori disi kapsam artirici)
        _ekstra_kelimeler = [
            "raporla",
            "Ã¶zet",
            "ozet",
            "karÅŸÄ±laÅŸtÄ±r",
            "karsilastir",
            "birleÅŸtir",
            "birlestir",
            "gÃ¶rsel",
            "gorsel",
            "grafik",
        ]

        # Kac farkli kategori bulundu
        _bulunan_kategori = 0
        for kategori, kw_list in kategoriler.items():
            if any(kw in hedef for kw in kw_list):
                _bulunan_kategori += 1

        # â”€â”€ 4. Skor hesaplama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        skor = _bulunan_kategori
        if _cok_adim:
            skor += 1

        # Ek keyword sayisi (kategori disi ekstra)
        _ek_kelimeler = [
            "raporla",
            "Ã¶zet",
            "ozet",
            "karÅŸÄ±laÅŸtÄ±r",
            "karsilastir",
            "donÃ¼ÅŸtÃ¼r",
            "donustur",
            "birleÅŸtir",
            "birlestir",
        ]
        for k in _ek_kelimeler:
            if k in hedef:
                # Sadece yeni kategori eklemediysek bonus
                if not any(kw in hedef for kw in kategoriler.get("yazma_islem", [])):
                    skor += 1
                    break

        return {"karmasiklik": max(1, min(skor, 5))}
