# -*- coding: utf-8 -*-
"""kancalar.py icin pytest testleri."""

import sys
import time
sys.path.insert(0, ".")

from kancalar import KancaMotoru, kanca_motoru, ENGELLENEN_ARACLAR


class TestKancaMotoru:
    """KancaMotoru birim testleri."""

    def setup_method(self):
        self.km = KancaMotoru()

    def test_normal_eylem_ihlal_yok(self):
        """Normal bir eylem kural ihlali uretmemeli."""
        hata = self.km.denetle("t001", "DOSYA_OKU")
        assert hata is None

    def test_art_arda_bloke(self):
        """4 kere ayni eylem → bloke."""
        for i in range(5):
            hata = self.km.denetle("t002", "WEB_ARA")
        assert hata is not None

    def test_yasakli_arac_bloke(self):
        """ALT_AJAN_GOREVLENDIR yasakli araç → hemen bloke."""
        hata = self.km.denetle("t003", "ALT_AJAN_GOREVLENDIR")
        assert hata is not None
        assert "yasakl" in hata.lower()

    def test_bloke_cozme(self):
        """Bloke edilmis task cozulebilmeli."""
        for i in range(5):
            self.km.denetle("t004", "DOSYA_OKU")
        assert self.km.bloke_coz("t004")
        durum = self.km.task_durum("t004")
        assert not durum["bloke"]

    def test_derinlik_uyarisi(self):
        """Derinlik > 3 uyarisi."""
        hata = self.km.denetle("t005", "DOSYA_OKU", derinlik=5)
        assert hata is not None
        assert "Derinlik" in hata

    def test_eylem_limiti(self):
        """30+ eylem → bloke."""
        for i in range(35):
            hata = self.km.denetle("t006", "DOSYA_OKU", maks_eylem=30)
        assert hata is not None

    def test_hizli_dongu(self):
        """0.5s altında iki eylem → hizli dongu uyarisi."""
        hata = self.km.denetle("t007", "DOSYA_OKU", min_aralik=0.5)
        assert hata is None  # İlk eylem
        hata = self.km.denetle("t007", "DOSYA_OKU", min_aralik=0.5)
        assert hata is not None  # Çok hızlı

    def test_task_temizle(self):
        """Task temizleme calismali."""
        self.km.denetle("t008", "DOSYA_OKU")
        self.km.task_temizle("t008")
        durum = self.km.task_durum("t008")
        assert not durum["bloke"]

    def test_istatistik(self):
        """Istatistik dondurmeli."""
        self.km.denetle("t009", "DOSYA_OKU")
        istat = self.km.istatistik()
        assert "aktif_task" in istat
        assert "blokeli_task" in istat

    def test_farkli_task_ayri_sayac(self):
        """Farkli task'lar ayri sayaclara sahip olmali."""
        self.km.denetle("t010", "WEB_ARA")
        self.km.denetle("t010", "WEB_ARA")
        self.km.denetle("t010", "WEB_ARA")
        hata = self.km.denetle("t011", "DOSYA_OKU")
        assert hata is None  # t011 etkilenmemeli

    def test_engellenen_araclar_seti(self):
        """ENGELLENEN_ARACLAR frozenset olmali."""
        assert "ALT_AJAN_GOREVLENDIR" in ENGELLENEN_ARACLAR
        assert isinstance(ENGELLENEN_ARACLAR, frozenset)
