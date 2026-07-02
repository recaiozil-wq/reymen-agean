# -*- coding: utf-8 -*-
"""test_cron_manager.py — CronManager birim testleri (yüzeyel geçiş)."""

import json
import uuid
from unittest.mock import patch, MagicMock

import pytest

from src.core.cron_manager import CronManager, CronJob


@pytest.fixture
def cron() -> CronManager:
    """Temiz CronManager örneği (dosya I/O'su devre dışı)."""
    with (
        patch("reymen.core.cron_manager._json_oku", return_value={}),
        patch("reymen.core.cron_manager._json_yaz"),
        patch("reymen.core.cron_manager._watchdog_log"),
    ):
        mgr = CronManager()
    return mgr


# ── Happy Path ──────────────────────────────────────────────────────────


class TestCronEkle:
    """CronJob ekleme işlemleri."""

    def test_ekle_basarili(self, cron: CronManager):
        """Yeni cron işi ekleme → başarılı."""
        sonuc = cron.ekle(
            ad="test_job",
            komut="echo merhaba",
            cron_ifade="0 */6 * * *",
            aciklama="Test cron",
        )
        assert sonuc["basarili"] is True
        assert "id" in sonuc
        assert len(sonuc["id"]) == 12  # uuid4[:12]

    def test_eklenen_is_listede_gorunur(self, cron: CronManager):
        """Eklenen iş liste() içinde döner."""
        cron.ekle(ad="liste_test", komut="ls", cron_ifade="* * * * *")
        isler = cron.liste()
        assert len(isler) == 1
        assert isler[0]["ad"] == "liste_test"
        assert isler[0]["cron"] == "* * * * *"


class TestCronSil:
    """CronJob silme işlemleri."""

    def test_sil_basarili(self, cron: CronManager):
        """Var olan işi silme → başarılı, listeden kaybolur."""
        sonuc = cron.ekle(ad="silinecek", komut="echo sil", cron_ifade="0 0 * * *")
        job_id = sonuc["id"]

        sil = cron.sil(job_id)
        assert sil["basarili"] is True
        assert len(cron.liste()) == 0

    def test_sil_olmayan_id(self, cron: CronManager):
        """Var olmayan job_id silme → hata döner."""
        sonuc = cron.sil("non_existent_id_123")
        assert sonuc["basarili"] is False
        assert "bulunamadi" in sonuc["hata"]


class TestCronListe:
    """CronJob listeleme işlemleri."""

    def test_liste_bos(self, cron: CronManager):
        """Hiç iş yokken liste boş döner."""
        assert cron.liste() == []

    def test_liste_aktif_filtre(self, cron: CronManager):
        """aktif_mi parametresine göre filtreleme."""
        cron.ekle(ad="aktif_is", komut="echo a", cron_ifade="* * * * *", aktif=True)
        cron.ekle(ad="pasif_is", komut="echo p", cron_ifade="* * * * *", aktif=False)

        aktif = cron.liste(aktif_mi=True)
        pasif = cron.liste(aktif_mi=False)
        assert len(aktif) == 1
        assert len(pasif) == 1
        assert aktif[0]["ad"] == "aktif_is"
        assert pasif[0]["ad"] == "pasif_is"


class TestCronHata:
    """Hata senaryoları."""

    def test_ekle_bos_ad_hata(self, cron: CronManager):
        """Boş ad ile ekleme → _cron_ekle tool'u hata döner,
        ancak CronManager.ekle() kendisi boş ada izin verir.
        Doğrudan _cron_ekle motor tool'una bakarız."""
        from reymen.core.cron_manager import _cron_ekle

        sonuc = json.loads(_cron_ekle(ad=""))
        assert "hata" in sonuc
        assert "adi zorunlu" in sonuc["hata"]
