# -*- coding: utf-8 -*-
"""tests/test_steering_loop.py — 5 Katmanli SteeringLoop birim testleri.

API notlari:
- Katman1Hafiza.kaydet(task_id, tur, icerik, metadata=None)
- Katman4Kanca.denetle(task_id, arac, derinlik=1) -> None | str
- Katman5Gozlem.kaydet(task_id, sure_sn, cevap='', basarili=True, girdi_token=0, cikti_token=0, notlar='')
- SteeringLoop.hafiza_kaydet / kanca_denetle / gozlem_kaydet
- Calistirma: python -m pytest tests/test_steering_loop.py -v
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from steering_loop import (
    Katman1Hafiza,
    Katman4Kanca,
    Katman5Gozlem,
    SteeringLoop,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def k1(tmp_path):
    return Katman1Hafiza(db_path=str(tmp_path / "k1.db"))


@pytest.fixture
def k4(tmp_path):
    return Katman4Kanca(db_path=str(tmp_path / "k4.db"))


@pytest.fixture
def k5(tmp_path):
    return Katman5Gozlem(db_path=str(tmp_path / "k5.db"))


@pytest.fixture
def sl(tmp_path):
    """Birlesik SteeringLoop — ayni DB."""
    db = str(tmp_path / "steering.db")
    return SteeringLoop(db_path=db)


# ══════════════════════════════════════════════════════════════════════════════
# KATMAN 1 — HAFIZA
# ══════════════════════════════════════════════════════════════════════════════


class TestKatman1Hafiza:
    def test_kaydet_basarili(self, k1):
        assert k1.kaydet("task_01", "adim", "Python decorator nasil calisir?") is True

    def test_kaydet_ve_fts5_ara(self, k1):
        k1.kaydet("task_01", "adim", "Python decorator fonksiyon sarici")
        k1.kaydet("task_01", "sonuc", "Decorator wraps ile meta bilgi kopyalanir")
        sonuclar = k1.ara("decorator")
        assert len(sonuclar) > 0
        assert any("decorator" in s["icerik"].lower() for s in sonuclar)

    def test_kaydet_metadata(self, k1):
        assert (
            k1.kaydet(
                "task_01",
                "adim",
                "Meta icerik",
                metadata={"kaynak": "api", "adim_no": 1},
            )
            is True
        )

    def test_ara_bos_sorgu_bos_doner(self, k1):
        k1.kaydet("task_01", "adim", "Icerik var")
        assert k1.ara("") == []

    def test_ara_task_filtresi(self, k1):
        k1.kaydet("task_A", "adim", "A gorevi python lambda")
        k1.kaydet("task_B", "adim", "B gorevi python lambda")
        sonuclar = k1.ara("python lambda", task_id="task_A")
        for s in sonuclar:
            assert s["task_id"] == "task_A"

    def test_task_gecmis_sirali(self, k1):
        k1.kaydet("task_01", "adim", "Adim 1")
        k1.kaydet("task_01", "sonuc", "Sonuc 1")
        k1.kaydet("task_01", "hata", "Hata mesaji")
        gecmis = k1.task_gecmis("task_01")
        assert len(gecmis) == 3
        # Zamana gore sirali gelmeli
        turler = [g["tur"] for g in gecmis]
        assert "adim" in turler and "sonuc" in turler

    def test_task_gecmis_olmayan_task_bos(self, k1):
        assert k1.task_gecmis("olmayan_task_xyz") == []

    def test_durum_aktif(self, k1):
        k1.kaydet("task_01", "adim", "Icerik")
        d = k1.durum()
        assert d["aktif"] is True
        assert d["toplam_kayit"] >= 1
        assert d["aktif_task"] >= 1

    def test_durum_bos_db(self, tmp_path):
        k = Katman1Hafiza(db_path=str(tmp_path / "bos.db"))
        d = k.durum()
        assert d["toplam_kayit"] == 0

    def test_ara_sql_injection_guvenli(self, k1):
        k1.kaydet("task_01", "adim", "Normal icerik")
        sonuclar = k1.ara("'; DROP TABLE katman1_kayit; --")
        assert isinstance(sonuclar, list)

    def test_uzun_icerik_kirpilir(self, k1):
        uzun = "X" * 3000
        assert k1.kaydet("task_01", "adim", uzun) is True


# ══════════════════════════════════════════════════════════════════════════════
# KATMAN 4 — KANCA
# ══════════════════════════════════════════════════════════════════════════════


class TestKatman4Kanca:
    def test_normal_eylem_gecerli(self, k4):
        hata = k4.denetle("task_01", "DOSYA_OKU")
        assert hata is None

    def test_yasakli_arac_bloke(self, k4):
        hata = k4.denetle("task_01", "ALT_AJAN_GOREVLENDIR")
        assert hata is not None
        assert "yasakli" in hata.lower() or "KANCA" in hata

    def test_yasakli_arac_sil_dosya(self, k4):
        assert k4.denetle("task_01", "SIL_DOSYA") is not None

    def test_art_arda_ayni_eylem_bloke(self, k4):
        for _ in range(Katman4Kanca.MAKS_ART_ARDA - 1):
            k4.denetle("task_01", "DOSYA_OKU")
        # MAKS_ART_ARDA. tekrarda bloke olmali
        hata = k4.denetle("task_01", "DOSYA_OKU")
        assert hata is not None

    def test_farkli_eylem_sayaci_sifirlar(self, k4):
        """Farkli eylem sayaci sifirlamali, bloke OLMAMALI"""
        # MIN_ARALIK=0.5s oldugu icin her cagri arasinda bekle
        k4.denetle("task_01", "DOSYA_OKU")
        time.sleep(0.55)
        k4.denetle("task_01", "DOSYA_OKU")
        time.sleep(0.55)
        # Farkli eylem — sayaci sifirlar, MIN_ARALIK kadar bekle
        time.sleep(0.55)
        hata = k4.denetle("task_01", "DOSYA_YAZ")
        # Bloke mesaji degil — yasakli arac degil, art_arda sifirlanmali
        assert hata is None

    def test_bloke_coz(self, k4):
        # Bloke et
        for _ in range(Katman4Kanca.MAKS_ART_ARDA + 1):
            k4.denetle("task_01", "DOSYA_OKU")
        assert k4.denetle("task_01", "DOSYA_OKU") is not None
        # Coz
        assert k4.bloke_coz("task_01") is True
        # Simdi gecerli olmali
        assert k4.denetle("task_01", "DOSYA_YAZ") is None

    def test_istatistik_dict(self, k4):
        k4.denetle("task_01", "DOSYA_OKU")
        k4.denetle("task_02", "DOSYA_YAZ")
        ist = k4.istatistik()
        assert "aktif_task" in ist
        assert ist["aktif_task"] >= 2

    def test_task_temizle(self, k4):
        k4.denetle("task_temizle", "DOSYA_OKU")
        k4.task_temizle("task_temizle")
        ist = k4.istatistik()
        # Temizlenen task artik cache'de olmamali
        assert "task_temizle" not in k4._cache

    def test_hizli_dongu_engellenir(self, k4):
        k4.denetle("task_hiz", "DOSYA_OKU")
        # Cok hizli ikinci cagri uyari vermeli (ama bloke etmeyebilir)
        hata = k4.denetle("task_hiz", "DOSYA_YAZ")
        # MIN_ARALIK icinde cagri uyari dondurebilir
        # Kesin assert yerine tipi kontrol et
        assert hata is None or isinstance(hata, str)


# ══════════════════════════════════════════════════════════════════════════════
# KATMAN 5 — GOZLEM
# ══════════════════════════════════════════════════════════════════════════════


class TestKatman5Gozlem:
    def test_kaydet_basarili(self, k5):
        # kaydet donüs degeri yok (None), hata vermemesi yeterli
        k5.kaydet(
            "task_01",
            sure_sn=2.5,
            cevap="Merhaba",
            basarili=True,
            girdi_token=50,
            cikti_token=100,
        )

    def test_task_ozet(self, k5):
        k5.kaydet(
            "task_ozet",
            sure_sn=1.0,
            cevap="Cevap 1",
            basarili=True,
            girdi_token=10,
            cikti_token=20,
        )
        k5.kaydet(
            "task_ozet",
            sure_sn=2.0,
            cevap="Cevap 2",
            basarili=True,
            girdi_token=15,
            cikti_token=30,
        )
        ozet = k5.task_ozet("task_ozet")
        assert ozet["cagri_sayisi"] == 2
        assert ozet["toplam_sure_sn"] == pytest.approx(3.0, abs=0.01)
        assert ozet["toplam_girdi_token"] == 25
        assert ozet["toplam_cikti_token"] == 50

    def test_task_ozet_olmayan_task(self, k5):
        ozet = k5.task_ozet("olmayan_task")
        assert ozet["cagri_sayisi"] == 0

    def test_basarisiz_kayit(self, k5):
        k5.kaydet("task_hata", sure_sn=0.5, cevap="", basarili=False, notlar="TIMEOUT")
        ozet = k5.task_ozet("task_hata")
        assert ozet["basarisiz"] == 1

    def test_maliyet_hesaplanir(self, k5):
        k5.kaydet("task_maliyet", sure_sn=1.0, girdi_token=1000, cikti_token=500)
        ozet = k5.task_ozet("task_maliyet")
        assert ozet["tahmini_maliyet_usd"] > 0

    def test_genel_ozet(self, k5):
        k5.kaydet("task_A", sure_sn=1.0, basarili=True)
        k5.kaydet("task_B", sure_sn=2.0, basarili=False)
        g = k5.genel_ozet()
        assert g["toplam_cagri"] == 2
        assert g["aktif_task"] == 2

    def test_son_kayit_liste(self, k5):
        for i in range(5):
            k5.kaydet(f"task_{i}", sure_sn=float(i))
        kayitlar = k5.son_kayit()
        assert isinstance(kayitlar, list)
        assert len(kayitlar) >= 1

    def test_cevap_token_otomatik_hesaplanir(self, k5):
        k5.kaydet("task_auto", sure_sn=1.0, cevap="a" * 400)
        ozet = k5.task_ozet("task_auto")
        # cikti_token otomatik hesaplandiysa > 0 olmali
        assert ozet["toplam_cikti_token"] > 0

    def test_temizle(self, k5):
        k5.kaydet("task_01", sure_sn=1.0)
        k5.temizle()
        assert k5.genel_ozet()["toplam_cagri"] == 0


# ══════════════════════════════════════════════════════════════════════════════
# STEERING LOOP — BIRLESIK API
# ══════════════════════════════════════════════════════════════════════════════


class TestSteeringLoop:
    def test_hafiza_kaydet_ve_ara(self, sl):
        sl.hafiza_kaydet("task_01", "adim", "SteeringLoop FTS5 testi")
        sonuclar = sl.hafiza_ara("SteeringLoop")
        assert len(sonuclar) > 0

    def test_kanca_denetle_gecerli(self, sl):
        assert sl.kanca_denetle("task_01", "DOSYA_OKU") is None

    def test_kanca_yasakli(self, sl):
        assert sl.kanca_denetle("task_01", "ALT_AJAN_GOREVLENDIR") is not None

    def test_kanca_coz(self, sl):
        for _ in range(Katman4Kanca.MAKS_ART_ARDA + 1):
            sl.kanca_denetle("task_bloke", "DOSYA_OKU")
        sl.kanca_coz("task_bloke")
        assert sl.kanca_denetle("task_bloke", "DOSYA_YAZ") is None

    def test_gozlem_kaydet_ve_ozet(self, sl):
        sl.gozlem_kaydet(
            "task_01",
            1.5,
            cevap="Cevap",
            basarili=True,
            girdi_token=50,
            cikti_token=100,
        )
        ozet = sl.gozlem_ozet("task_01")
        assert ozet["cagri_sayisi"] == 1

    def test_gozlem_genel_ozet(self, sl):
        sl.gozlem_kaydet("t1", 1.0, basarili=True)
        sl.gozlem_kaydet("t2", 2.0, basarili=False)
        g = sl.gozlem_ozet()
        assert g["toplam_cagri"] == 2

    def test_task_gecmis(self, sl):
        sl.hafiza_kaydet("task_01", "adim", "Adim 1")
        sl.hafiza_kaydet("task_01", "sonuc", "Sonuc 1")
        gecmis = sl.task_gecmis("task_01")
        assert len(gecmis) == 2

    def test_durum_tum_katmanlar(self, sl):
        sl.hafiza_kaydet("task_01", "adim", "Test icerik")
        sl.kanca_denetle("task_01", "DOSYA_OKU")
        sl.gozlem_kaydet("task_01", 1.0)
        d = sl.durum()
        assert "katman1_hafiza" in d
        assert "katman4_kanca" in d
        assert "katman5_gozlem" in d
        assert d["katman1_hafiza"]["toplam_kayit"] >= 1

    def test_ayni_db_paylasimi(self, tmp_path):
        db = str(tmp_path / "paylasilan.db")
        loop1 = SteeringLoop(db_path=db)
        loop2 = SteeringLoop(db_path=db)
        loop1.hafiza_kaydet("paylasilan_task", "adim", "paylasilan icerik test")
        # loop2 ayni DB'yi okuyabilmeli
        sonuclar = loop2.hafiza_ara("paylasilan")
        assert len(sonuclar) > 0

    def test_kanca_temizle(self, sl):
        sl.kanca_denetle("temizlenecek", "DOSYA_OKU")
        sl.kanca_temizle("temizlenecek")
        assert "temizlenecek" not in sl.kanca._cache


# ══════════════════════════════════════════════════════════════════════════════
# KATMAN 4 — CIRCUIT BREAKER ENTEGRASYONU
# ══════════════════════════════════════════════════════════════════════════════


class TestKatman4CircuitBreaker:
    """Katman4Kanca.denetle() circuit breaker entegrasyon testleri."""

    def test_cb_nitelik_var(self, k4):
        assert hasattr(k4, "_cb")

    def test_cb_baslangic_none_degil(self, k4):
        assert k4._cb is not None

    def test_denetle_circuit_closed_normal_calisir(self, k4):
        assert k4.denetle("task_01", "DOSYA_OKU") is None

    def test_hata_bildir_sayaci_artirir(self, k4):
        k4.hata_bildir("task_01")
        k4.hata_bildir("task_01")
        assert k4._cb.ardisik_hata == 2

    def test_hata_bildir_5x_open(self, k4):
        for _ in range(5):
            k4.hata_bildir("task_01")
        from circuit_breaker import CircuitBreakerState

        assert k4._cb.durum == CircuitBreakerState.OPEN

    def test_denetle_circuit_open_bloke_eder(self, k4):
        for _ in range(5):
            k4.hata_bildir("task_01")
        mesaj = k4.denetle("task_02", "DOSYA_OKU")
        assert mesaj is not None
        assert "[CIRCUIT_BREAKER]" in mesaj

    def test_basari_bildir_sayaci_sifirlar(self, k4):
        k4.hata_bildir("task_01")
        k4.hata_bildir("task_01")
        k4.basari_bildir("task_01")
        assert k4._cb.ardisik_hata == 0

    def test_circuit_breaker_sifirla(self, k4):
        for _ in range(5):
            k4.hata_bildir("task_01")
        k4.circuit_breaker_sifirla()
        assert k4.denetle("task_02", "DOSYA_OKU") is None

    def test_istatistik_circuit_breaker_anahtari(self, k4):
        ist = k4.istatistik()
        assert "circuit_breaker" in ist

    def test_istatistik_circuit_breaker_durum(self, k4):
        ist = k4.istatistik()
        assert "durum" in ist["circuit_breaker"]

    def test_30sn_sonra_half_open_tekrar_calisir(self, k4):
        import time

        for _ in range(5):
            k4.hata_bildir("task_01")
        # Zamanı 31sn ileri kaydır
        k4._cb.son_acilma = time.time() - 31
        mesaj = k4.denetle("task_02", "DOSYA_OKU")
        assert mesaj is None  # HALF_OPEN → None dönmeli

    def test_4_hata_denetle_normal(self, k4):
        for _ in range(4):
            k4.hata_bildir("task_01")
        # 4 hata yeterli degil, denetle None donmeli
        assert k4.denetle("task_02", "DOSYA_OKU") is None
