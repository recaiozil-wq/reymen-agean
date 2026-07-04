# -*- coding: utf-8 -*-
"""tests/test_cron_tools.py — CronManager tool fonksiyonlari testleri.

Kapsar:
- motor_kaydet() ile CRON_EKLE/SIL/LISTELE kaydi
- _cron_ekle / _cron_liste / _cron_sil JSON tabanli CRUD
"""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# -- Yardimci mock motor ---------------------------------------------------


class MockMotor:
    def __init__(self):
        self._araclar = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self._araclar[ad] = fonk


# -- Fixture: crontools modulunu dogru adresten al ---------------------------


@pytest.fixture(autouse=True)
def temiz_cron_manager():
    """Her test oncesi CronManager singleton'ini sifirla ve dosya I/O'sunu devre disi birak."""
    from unittest.mock import patch
    from src.core import cron_manager as cm

    # Singleton sifirla
    cm._cron_yonetici = None

    with (
        patch.object(cm, "_json_oku", return_value={}),
        patch.object(cm, "_json_yaz"),
        patch.object(cm, "_watchdog_log"),
    ):
        yield cm


# -- motor_kaydet testleri ---------------------------------------------------


class TestMotorKaydet:
    def test_araclar_kayitli(self):
        from src.core.cron_manager import motor_kaydet

        motor = MockMotor()
        motor_kaydet(motor)
        beklenen = {"CRON_LISTE", "CRON_EKLE", "CRON_SIL"}
        assert beklenen.issubset(set(motor._araclar.keys()))

    def test_cron_listele_araci_cagrilebilir(self):
        from src.core.cron_manager import motor_kaydet

        motor = MockMotor()
        motor_kaydet(motor)
        sonuc = motor._araclar["CRON_LISTE"]()
        # Bos listede "hic" veya "[]" donmeli
        assert "hic" in sonuc.lower() or "[]" in sonuc


# -- JSON tabanli CRUD --------------------------------------------------------


class TestCronCRUD:
    def test_ekle_ve_listele(self):
        from src.core.cron_manager import _cron_ekle, _cron_liste

        r = json.loads(_cron_ekle(ad="sabah_raporu", komut="python rapor.py", cron_ifade="0 9 * * *"))
        assert r["basarili"] is True

        liste = json.loads(_cron_liste())
        assert len(liste) == 1
        assert liste[0]["ad"] == "sabah_raporu"

    def test_sil(self):
        from src.core.cron_manager import _cron_ekle, _cron_liste, _cron_sil

        r = json.loads(_cron_ekle(ad="silinecek", komut="echo x", cron_ifade="0 10 * * *"))
        job_id = r["id"]
        s = json.loads(_cron_sil(job_id=job_id))
        assert s["basarili"] is True

        liste_raw = _cron_liste()
        if liste_raw.startswith("["):
            liste = json.loads(liste_raw)
            assert len(liste) == 0
        else:
            assert "hic" in liste_raw.lower()

    def test_sil_olmayan(self):
        from src.core.cron_manager import _cron_sil

        r = json.loads(_cron_sil(job_id="yok_olan"))
        assert r["basarili"] is False

    def test_bos_ad_hata(self):
        from src.core.cron_manager import _cron_ekle

        r = json.loads(_cron_ekle(ad=""))
        assert "hata" in r
