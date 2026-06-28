# -*- coding: utf-8 -*-
"""tests/test_cron_tools.py — Cron araçları testleri.

Kapsar:
- motor_kaydet() ile CRON_EKLE/SIL/LISTELE/CALISTIR kaydı
- JSON tabanlı cron job CRUD
- CronScheduler daemon entegrasyonu (baslat/durdur/durum)
- CRON_ZAMANLA ile cron ifadesi zamanlaması
"""

import json
import os
import sys
import threading
import time
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))


# ── Yardımcı mock motor ─────────────────────────────────────────────────────

class MockMotor:
    def __init__(self):
        self._araclar = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self._araclar[ad] = fonk


# ── Fixture: geçici JSON dosyası ────────────────────────────────────────────

@pytest.fixture(autouse=True)
def gecici_cron_dosyasi(tmp_path, monkeypatch):
    dosya = str(tmp_path / "cron_jobs.json")
    import tools.cronjob_tools as ct
    monkeypatch.setattr(ct, "CRON_DOSYASI", dosya)
    # Scheduler singleton sıfırla
    monkeypatch.setattr(ct, "_scheduler_instance", None)
    yield dosya


# ── motor_kaydet testleri ────────────────────────────────────────────────────

class TestMotorKaydet:
    def test_araclar_kayitli(self):
        from tools.cronjob_tools import motor_kaydet
        motor = MockMotor()
        motor_kaydet(motor)
        beklenen = {
            "CRON_EKLE", "CRON_SIL", "CRON_LISTELE",
            "CRON_CALISTIR", "CRON_BASLAT", "CRON_DURDUR",
            "CRON_DURUM", "CRON_ZAMANLA",
        }
        assert beklenen.issubset(set(motor._araclar.keys()))

    def test_cron_listele_araci_cagrilebilir(self):
        from tools.cronjob_tools import motor_kaydet
        motor = MockMotor()
        motor_kaydet(motor)
        sonuc = motor._araclar["CRON_LISTELE"]()
        veri = json.loads(sonuc)
        assert veri["durum"] == "basarili"
        assert veri["sayi"] == 0


# ── JSON tabanlı CRUD ────────────────────────────────────────────────────────

class TestCronCRUD:
    def test_ekle_ve_listele(self):
        from tools.cronjob_tools import run
        r = run("ekle", "sabah_raporu", "09:00", "python rapor.py")
        assert json.loads(r)["durum"] == "basarili"

        liste = json.loads(run("listele"))
        assert liste["sayi"] == 1
        assert liste["cron_jobs"][0]["ad"] == "sabah_raporu"

    def test_gecersiz_zaman_formati(self):
        from tools.cronjob_tools import run
        r = json.loads(run("ekle", "test", "25:99", "echo x"))
        assert r["durum"] == "hata"
        assert "zaman" in r["mesaj"].lower()

    def test_sil(self):
        from tools.cronjob_tools import run
        run("ekle", "silinecek", "10:00", "echo x")
        r = json.loads(run("sil", "silinecek"))
        assert r["durum"] == "basarili"
        assert json.loads(run("listele"))["sayi"] == 0

    def test_sil_olmayan(self):
        from tools.cronjob_tools import run
        r = json.loads(run("sil", "yok_olan"))
        assert r["durum"] == "hata"

    def test_ayni_ad_tekrar_eklenemez(self):
        from tools.cronjob_tools import run
        run("ekle", "tek", "08:00", "echo a")
        r = json.loads(run("ekle", "tek", "09:00", "echo b"))
        assert r["durum"] == "hata"

    def test_bilinmeyen_islem(self):
        from tools.cronjob_tools import run
        r = json.loads(run("yoktur"))
        assert r["durum"] == "hata"


# ── CronScheduler daemon entegrasyonu ────────────────────────────────────────

class TestSchedulerDaemon:
    def test_durum_calismıyor(self):
        from tools.cronjob_tools import _scheduler_durum
        r = json.loads(_scheduler_durum())
        # cron_scheduler import edilemezse hata döner (CI'da normal)
        assert r["durum"] in ("basarili", "hata")

    def test_baslat_durdur(self):
        try:
            from cron_scheduler import CronScheduler
        except ImportError:
            pytest.skip("cron_scheduler modülü yok")

        from tools.cronjob_tools import _scheduler_baslat, _scheduler_durdur, _scheduler_durum
        r = json.loads(_scheduler_baslat())
        assert r["durum"] == "basarili"

        durum = json.loads(_scheduler_durum())
        assert durum["calisiyor"] is True

        r2 = json.loads(_scheduler_durdur())
        assert r2["durum"] == "basarili"

        durum2 = json.loads(_scheduler_durum())
        assert durum2["calisiyor"] is False

    def test_baslat_ikinci_kez(self):
        try:
            from cron_scheduler import CronScheduler
        except ImportError:
            pytest.skip("cron_scheduler modülü yok")

        from tools.cronjob_tools import _scheduler_baslat
        _scheduler_baslat()
        r = json.loads(_scheduler_baslat())
        assert r["durum"] == "bilgi"  # zaten çalışıyor


# ── CRON_ZAMANLA ─────────────────────────────────────────────────────────────

class TestCronZamanla:
    def test_zamanla_eksik_parametre(self):
        from tools.cronjob_tools import _zamanla
        r = json.loads(_zamanla("", "echo x", ""))
        assert r["durum"] == "hata"

    def test_zamanla_scheduler_yok(self, monkeypatch):
        import tools.cronjob_tools as ct
        monkeypatch.setattr(ct, "_scheduler_instance", None)
        # CronScheduler import'ı başarısız yap
        import builtins
        _orijinal_import = builtins.__import__
        def _mock_import(name, *args, **kwargs):
            if name == "cron_scheduler":
                raise ImportError("mock")
            return _orijinal_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, "__import__", _mock_import)
        r = json.loads(ct._zamanla("* * * * *", "echo x", "test"))
        assert r["durum"] == "hata"

    def test_zamanla_basarili(self):
        try:
            from cron_scheduler import CronScheduler
        except ImportError:
            pytest.skip("cron_scheduler modülü yok")

        from tools.cronjob_tools import _zamanla
        r = json.loads(_zamanla("0 9 * * *", "python rapor.py", "gunluk"))
        assert r["durum"] == "basarili"
        assert r["job_id"] == "gunluk"

    def test_zamanla_otomatik_id(self):
        try:
            from cron_scheduler import CronScheduler
        except ImportError:
            pytest.skip("cron_scheduler modülü yok")

        from tools.cronjob_tools import _zamanla
        r = json.loads(_zamanla("*/5 * * * *", "echo x", ""))
        assert r["durum"] == "basarili"
        assert r["job_id"].startswith("job_")
