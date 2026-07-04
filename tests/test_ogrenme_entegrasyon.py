# -*- coding: utf-8 -*-
"""tests/test_ogrenme_entegrasyon.py — Ogrenme sistemi entegrasyon testleri.

Sistem butunlugunu dogrular:
  - Konusma kaydedilip FTS5 ile bulunabiliyor mu?
  - SteeringLoop + GelismisHafiza ayri DB'lerde bagimsiz mi?
  - Veri tutarliligi: ayni session birden fazla sisteme yazilsa bile tutarli mi?
  - Tam ogrenme turu: kaydet -> ara -> konu_cikar -> beceri

Calistirma: python -m pytest tests/test_ogrenme_entegrasyon.py -v
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from hafiza_genislet import GelismisHafiza
from steering_loop import SteeringLoop, Katman4Kanca
from closed_learning_loop import ClosedLearningLoop


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def ortam(tmp_path):
    """Birbirinden izole tum ogrenme sistemi bilesenleri."""
    hafiza = GelismisHafiza(db_yolu=str(tmp_path / "hafiza.db"))
    hafiza.initialize(session_id="entegrasyon_ses_01")

    steering = SteeringLoop(db_path=str(tmp_path / "steering.db"))

    loop = ClosedLearningLoop(
        db_yolu=str(tmp_path / "skills.db"),
        skills_dir=str(tmp_path / "skills"),
        auto_index=False,
    )
    yield {"hafiza": hafiza, "steering": steering, "loop": loop, "tmp": tmp_path}
    try:
        loop.kapat()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# 1. KONUSMA AKISI
# ══════════════════════════════════════════════════════════════════════════════


class TestKonusmaAkisi:
    def test_konusma_kaydedilip_fts5_ile_bulunur(self, ortam):
        hg = ortam["hafiza"]
        hg.kaydet(
            "Python lambda fonksiyonlari nasil kullanilir?",
            koleksiyon="konusmalar",
            anahtar="python_lambda",
        )
        hg.kaydet("Lambda tek satirlik anonim fonksiyondur", koleksiyon="konusmalar")
        sonuclar = hg.ara("lambda")
        assert len(sonuclar) >= 1
        assert any("lambda" in s["icerik"].lower() for s in sonuclar)

    def test_session_ara_konusmada_bulur(self, ortam):
        hg = ortam["hafiza"]
        hg.kaydet("FTS5 full_text_search entegrasyon_testi", koleksiyon="konusmalar")
        sonuclar = hg.session_ara("full_text_search")
        assert len(sonuclar) > 0

    def test_konu_cikar_anlamli_kelime(self, ortam):
        hg = ortam["hafiza"]
        hg.kaydet(
            "SQLite veritabani indeksleme performans optimizasyon",
            koleksiyon="konusmalar",
        )
        hg.kaydet(
            "SQLite FTS5 indeksleme hizi artirma yontemi", koleksiyon="konusmalar"
        )
        konular = hg.konu_cikar("entegrasyon_ses_01", limit=5)
        assert len(konular) >= 1
        # En az bir anlamli teknik kelime bekleniyor
        tum_metin = " ".join(konular).lower()
        assert any(
            kw in tum_metin
            for kw in ["sqlite", "indeks", "fts", "veritaban", "performans"]
        )


# ══════════════════════════════════════════════════════════════════════════════
# 2. STEERING + HAFIZA BIRLIKTE
# ══════════════════════════════════════════════════════════════════════════════


class TestSteeringHafizaBirlikte:
    def test_steering_ve_hafiza_bagimsiz_db(self, ortam):
        hg = ortam["hafiza"]
        sl = ortam["steering"]

        hg.kaydet("Hafiza sistemi kaydi", koleksiyon="konusmalar")
        sl.hafiza_kaydet("task_entg", "adim", "Steering sistemi kaydi")

        # Her sistem kendi DB'sini kullaniyor — cakisma yok
        hg_sonuc = hg.ara("Hafiza")
        sl_sonuc = sl.hafiza_ara("Steering")
        assert len(hg_sonuc) >= 1
        assert len(sl_sonuc) >= 1

    def test_steering_kanca_hafizayi_etkilemez(self, ortam):
        hg = ortam["hafiza"]
        sl = ortam["steering"]

        hg.kaydet("Onemli konusma verisi", koleksiyon="konusmalar")
        # Steering bloke olursa hafiza etkilenmemeli
        for _ in range(Katman4Kanca.MAKS_ART_ARDA + 2):
            sl.kanca_denetle("task_bloke", "DOSYA_OKU")

        # Hafiza hala calisiyor
        sonuclar = hg.ara("Onemli")
        assert len(sonuclar) >= 1

    def test_gozlem_ve_hafiza_paralel(self, ortam):
        hg = ortam["hafiza"]
        sl = ortam["steering"]

        hg.kaydet("Paralel test icerigi", koleksiyon="konusmalar")
        sl.gozlem_kaydet(
            "task_paralel",
            1.5,
            cevap="cevap",
            basarili=True,
            girdi_token=100,
            cikti_token=200,
        )

        hg_durum = hg.durum()
        sl_durum = sl.durum()
        assert hg_durum["toplam_kayit"] >= 1
        assert sl_durum["katman5_gozlem"]["toplam_cagri"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. OGRENME DONGUSU TAM TUR
# ══════════════════════════════════════════════════════════════════════════════


class TestOgrenmeDogusuTamTur:
    def test_tam_ogrenme_turu(self, ortam):
        """Kullanici sorar -> hafizaya kaydet -> ara -> konu_cikar -> beceri kristallestir."""
        hg = ortam["hafiza"]
        loop = ortam["loop"]

        # 1. Konusmayi kaydet
        soru = "Python context manager nasil yazilir?"
        cevap = "Context manager __enter__ ve __exit__ metodlari ile yazilir"
        hg.kaydet(soru, koleksiyon="konusmalar", anahtar="context_manager")
        hg.kaydet(cevap, koleksiyon="konusmalar", anahtar="context_manager_cevap")

        # 2. Ara ve bul
        sonuclar = hg.ara("context manager")
        assert len(sonuclar) >= 1

        # 3. Konu cikar
        konular = hg.konu_cikar("entegrasyon_ses_01", limit=5)
        assert isinstance(konular, list)

        # 4. Beceri kristallestir — str dondurmeli (dosya yolu)
        dosya_yolu = loop.beceri_kristallestir(
            "python_context_manager",
            "Python context manager kullanimi",
            "1. __enter__ ile baslat\n2. __exit__ ile temizle\n3. with bloku kullan",
        )
        assert isinstance(dosya_yolu, str)

    def test_beceri_arama_ile_bulunur(self, ortam):
        loop = ortam["loop"]
        loop.beceri_kristallestir(
            "decorator_deseni",
            "Python decorator tasarim deseni",
            "1. Fonksiyon al\n2. Sarici olustur\n3. Dondurun",
        )
        sonuclar = loop.ilgili_becerileri_cagir("decorator")
        assert isinstance(sonuclar, str)
        assert "decorator" in sonuclar.lower() or "eslesen" in sonuclar.lower()

    def test_tekrar_kristallestirme_gunceller(self, ortam):
        loop = ortam["loop"]
        loop.beceri_kristallestir("tekrar_test", "Ilk baslik", "Ilk icerik")
        ilk = loop.ilgili_becerileri_cagir("tekrar_test")
        assert isinstance(ilk, str)

        loop.beceri_kristallestir(
            "tekrar_test", "Guncellenmis baslik", "Guncellenmis icerik"
        )
        guncellenmis = loop.ilgili_becerileri_cagir("tekrar_test")
        assert isinstance(guncellenmis, str)


# ══════════════════════════════════════════════════════════════════════════════
# 4. VERI TUTARLILIGI
# ══════════════════════════════════════════════════════════════════════════════


class TestVeriTutarliligi:
    def test_hafiza_kendi_db_tutarli(self, ortam):
        hg = ortam["hafiza"]
        n = 15
        for i in range(n):
            hg.kaydet(f"Tutarlilik testi kayit {i}", koleksiyon="konusmalar")
        assert hg.durum()["toplam_kayit"] == n

    def test_steering_kendi_db_tutarli(self, ortam):
        sl = ortam["steering"]
        for i in range(10):
            sl.hafiza_kaydet(f"task_{i}", "adim", f"Icerik {i}")
        d = sl.durum()
        assert d["katman1_hafiza"]["toplam_kayit"] == 10

    def test_cakisma_yok_farkli_db(self, ortam):
        hg = ortam["hafiza"]
        sl = ortam["steering"]

        hg.kaydet("HAFIZA_OZEL_VERI", koleksiyon="konusmalar")
        sl.hafiza_kaydet("task_01", "adim", "STEERING_OZEL_VERI")

        # Her sistem sadece kendi verisini gormeli
        hg_sonuc = hg.ara("STEERING_OZEL_VERI")
        sl_sonuc = sl.hafiza_ara("HAFIZA_OZEL_VERI")
        # Farkli DB'lerde oldugu icin birbirini gorememeli
        assert len(hg_sonuc) == 0
        assert len(sl_sonuc) == 0

    def test_session_izolasyonu(self, ortam):
        hg = ortam["hafiza"]
        hg.kaydet("Session A icerigi", koleksiyon="konusmalar")

        hg.initialize(session_id="entegrasyon_ses_02")
        hg.kaydet("Session B icerigi", koleksiyon="konusmalar")

        # A aradiginda B gelmemeli
        a_sonuc = hg.ara("Session A", session_id="entegrasyon_ses_01")
        b_sonuc = hg.ara("Session B", session_id="entegrasyon_ses_01")
        for s in a_sonuc:
            assert s["session_id"] == "entegrasyon_ses_01"
        assert len(b_sonuc) == 0
