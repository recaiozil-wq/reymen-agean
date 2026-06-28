# -*- coding: utf-8 -*-
"""tests/test_circuit_breaker.py — CircuitBreaker kapsamlı test."""

import time
from unittest.mock import patch

import pytest

# import yolunu ayarla
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reymen.sistem.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestCircuitBreakerInit:
    """Başlangıç durumu."""

    def test_baslangic_durumu_closed(self):
        cb = CircuitBreaker()
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_baslangic_hata_sifir(self):
        cb = CircuitBreaker()
        assert cb.ardisik_hata == 0

    def test_baslangic_son_acilma_sifir(self):
        cb = CircuitBreaker()
        assert cb.son_acilma == 0.0

    def test_esik_degeri(self):
        assert CircuitBreaker.ESIK == 5

    def test_bekleme_suresi(self):
        assert CircuitBreaker.BEKLEME_SURESI == 30


class TestDenetle:
    """denetle() — circuit open kontrolü."""

    def test_closed_durumunda_none(self):
        cb = CircuitBreaker()
        assert cb.denetle() is None

    def test_half_open_durumunda_none(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        assert cb.denetle() is None

    def test_open_ici_kalan_mesaj(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.OPEN
        cb.son_acilma = time.time()
        mesaj = cb.denetle()
        assert mesaj is not None
        assert "CIRCUIT_BREAKER" in mesaj
        assert "kaldi" in mesaj

    def test_open_bekleme_gecmis_otomatik_half_open(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.OPEN
        cb.son_acilma = time.time() - 31  # 31sn once → bekleme geçti
        mesaj = cb.denetle()
        assert mesaj is None
        assert cb.durum == CircuitBreakerState.HALF_OPEN

    def test_open_kalan_saniye_hesap(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.OPEN
        cb.son_acilma = time.time() - 5  # 5sn once → 25sn kalan
        mesaj = cb.denetle()
        assert "25s" in mesaj or "24s" in mesaj  # timing tolerance


class TestHataKaydet:
    """hata_kaydet() — esik asimi."""

    def test_tek_hata_none(self):
        cb = CircuitBreaker()
        assert cb.hata_kaydet() is None
        assert cb.ardisik_hata == 1

    def test_4_hata_hala_none(self):
        cb = CircuitBreaker()
        for _ in range(4):
            assert cb.hata_kaydet() is None
        assert cb.ardisik_hata == 4
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_5_hata_open_mesaj(self):
        cb = CircuitBreaker()
        for _ in range(5):
            mesaj = cb.hata_kaydet()
        assert mesaj is not None
        assert "CIRCUIT_BREAKER" in mesaj
        assert "circuit open" in mesaj
        assert "5" in mesaj  # hata sayisi
        assert cb.durum == CircuitBreakerState.OPEN
        assert cb.son_acilma > 0

    def test_6_hata_hala_open(self):
        cb = CircuitBreaker()
        for _ in range(6):
            cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN
        assert cb.ardisik_hata == 6

    def test_basarisizlik_sayaci_artar(self):
        cb = CircuitBreaker()
        cb.hata_kaydet()
        cb.hata_kaydet()
        assert cb.ardisik_hata == 2


class TestBasariKaydet:
    """basari_kaydet() — sayac reset ve durum degisimi."""

    def test_closed_hata_sifirlanir(self):
        cb = CircuitBreaker()
        cb.ardisik_hata = 3
        cb.basari_kaydet()
        assert cb.ardisik_hata == 0

    def test_half_open_closed_gecis(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        cb.ardisik_hata = 2
        cb.basari_kaydet()
        assert cb.durum == CircuitBreakerState.CLOSED
        assert cb.ardisik_hata == 0

    def test_open_durumunda_basari_sayac_sifirlanir(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.OPEN
        cb.ardisik_hata = 5
        cb.basari_kaydet()
        assert cb.ardisik_hata == 0
        # OPEN durumundan basari → durum degismez (sadece sayac sifirlanir)
        assert cb.durum == CircuitBreakerState.OPEN


class TestSifirla:
    """sifirla() — tam reset."""

    def test_tam_sifirla(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.OPEN
        cb.ardisik_hata = 10
        cb.son_acilma = 999.0
        cb.sifirla()
        assert cb.durum == CircuitBreakerState.CLOSED
        assert cb.ardisik_hata == 0
        assert cb.son_acilma == 0.0

    def test_sifirla_sonra_denetle_none(self):
        cb = CircuitBreaker()
        cb.hata_kaydet()
        cb.hata_kaydet()
        cb.sifirla()
        assert cb.denetle() is None


class TestDurumBilgisi:
    """durum_bilgisi() — dict dondurme."""

    def test_durum_bilgisi_format(self):
        cb = CircuitBreaker()
        bilgi = cb.durum_bilgisi()
        assert isinstance(bilgi, dict)
        assert "durum" in bilgi
        assert "ardisik_hata" in bilgi
        assert "son_acilma" in bilgi

    def test_durum_bilgisi_degerleri(self):
        cb = CircuitBreaker()
        bilgi = cb.durum_bilgisi()
        assert bilgi["durum"] == "closed"
        assert bilgi["ardisik_hata"] == 0
        assert bilgi["son_acilma"] == 0.0

    def test_durum_bilgisi_acikken(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        bilgi = cb.durum_bilgisi()
        assert bilgi["durum"] == "open"
        assert bilgi["ardisik_hata"] == 5
        assert bilgi["son_acilma"] > 0


class TestFullCycle:
    """Tam yaşam döngüsü: CLOSED → OPEN → HALF_OPEN → CLOSED."""

    def test_tam_dongu(self):
        cb = CircuitBreaker()

        # 1. CLOSED → 4 hata → CLOSED
        for _ in range(4):
            assert cb.hata_kaydet() is None
        assert cb.durum == CircuitBreakerState.CLOSED

        # 2. 5. hata → OPEN
        mesaj = cb.hata_kaydet()
        assert mesaj is not None
        assert cb.durum == CircuitBreakerState.OPEN

        # 3. OPEN → denetle → bloklu
        assert cb.denetle() is not None

        # 4. Bekleme süresi geçti → HALF_OPEN
        cb.son_acilma = time.time() - 31
        assert cb.denetle() is None
        assert cb.durum == CircuitBreakerState.HALF_OPEN

        # 5. HALF_OPEN → basari → CLOSED
        cb.basari_kaydet()
        assert cb.durum == CircuitBreakerState.CLOSED
        assert cb.ardisik_hata == 0

    def test_yarim_acikta_basarisizlik(self):
        """HALF_OPEN'da 5 hata → geri OPEN."""
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        cb.son_acilma = time.time()

        # HALF_OPEN'da 4 hata → hala HALF_OPEN (sayac=4, < ESIK)
        for _ in range(4):
            assert cb.hata_kaydet() is None
        assert cb.durum == CircuitBreakerState.HALF_OPEN

        # 5. hata → OPEN'a düşer
        mesaj = cb.hata_kaydet()
        assert mesaj is not None
        assert cb.durum == CircuitBreakerState.OPEN

    def test_dongu_tekrarlanabilir(self):
        """Tam döngü birden fazla kez çalıştırılabilir."""
        for _ in range(3):
            cb = CircuitBreaker()
            for _ in range(5):
                cb.hata_kaydet()
            assert cb.durum == CircuitBreakerState.OPEN
            cb.son_acilma = time.time() - 31
            cb.denetle()
            assert cb.durum == CircuitBreakerState.HALF_OPEN
            cb.basari_kaydet()
            assert cb.durum == CircuitBreakerState.CLOSED


class TestConstants:
    """Sabir degerler."""

    def test_esik_5(self):
        assert CircuitBreaker.ESIK == 5

    def test_bekleme_30(self):
        assert CircuitBreaker.BEKLEME_SURESI == 30

    def test_state_values(self):
        assert CircuitBreakerState.CLOSED == "closed"
        assert CircuitBreakerState.OPEN == "open"
        assert CircuitBreakerState.HALF_OPEN == "half_open"
