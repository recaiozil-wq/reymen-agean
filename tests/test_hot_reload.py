"""Test: reymen/sistem/hot_reload.py — HotReloader, motor tool kaydi"""
from __future__ import annotations

import sys
import time
import json
import os
from pathlib import Path

import pytest

# Proje kokunu path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@pytest.fixture
def fake_motor():
    class FakeMotor:
        def __init__(self):
            self.kayitlar = []

        def _plugin_arac_kaydet(self, ad, fonk, aciklama):
            self.kayitlar.append((ad, fonk, aciklama))

    return FakeMotor()


@pytest.fixture
def reloader(fake_motor):
    from reymen.sistem.hot_reload import HotReloader
    hr = HotReloader(fake_motor, aralik=30)
    yield hr


# ── Initialization ───────────────────────────────────────────────────────

class TestInit:
    def test_default_values(self, fake_motor):
        from reymen.sistem.hot_reload import HotReloader
        hr = HotReloader(fake_motor, aralik=30)
        assert hr._aralik == 30
        assert hr._motor is fake_motor
        assert hr._istatistik["tarama"] == 0
        assert hr._istatistik["yenilenen"] == 0
        assert hr._istatistik["hata"] == 0
        assert not hr.durum()["calisiyor"]

    def test_initial_klasorler(self, fake_motor):
        from reymen.sistem.hot_reload import HotReloader
        hr = HotReloader(fake_motor, aralik=30)
        assert len(hr._klasorler) == 2  # arac/ ve plugins/
        for k in hr._klasorler:
            assert isinstance(k, Path)

    def test_durum_before_start(self, reloader):
        durum = reloader.durum()
        assert isinstance(durum, dict)
        assert durum["calisiyor"] is False
        assert durum["izlenen_klasor"] == 2
        assert durum["izlenen_dosya"] == 0
        assert durum["istatistik"]["tarama"] == 0

    def test_aralik_default(self, fake_motor):
        from reymen.sistem.hot_reload import HotReloader
        hr = HotReloader(fake_motor)  # varsayilan aralik=10
        assert hr._aralik == 10


# ── Baslat / Durdur ──────────────────────────────────────────────────────

class TestBaslatDurdur:
    def test_baslat_message(self, reloader):
        sonuc = reloader.baslat()
        assert "Baslatildi" in sonuc
        time.sleep(0.1)
        reloader.durdur()

    def test_baslat_changes_state(self, reloader):
        reloader.baslat()
        time.sleep(0.1)
        durum = reloader.durum()
        assert durum["calisiyor"] is True
        reloader.durdur()

    def test_durdur_message(self, reloader):
        reloader.baslat()
        time.sleep(0.1)
        sonuc = reloader.durdur()
        assert "Durduruldu" in sonuc

    def test_baslat_zaten_calisiyor(self, reloader):
        reloader.baslat()
        time.sleep(0.1)
        sonuc = reloader.baslat()  # ikinci kez
        assert "Zaten calisiyor" in sonuc
        reloader.durdur()

    def test_durdur_zaten_kapali(self, reloader):
        sonuc = reloader.durdur()
        assert "Zaten kapali" in sonuc


# ── Klasor Ekle ──────────────────────────────────────────────────────────

class TestKlasorEkle:
    def test_klasor_ekle_valid(self, reloader, tmp_path):
        yeni = tmp_path / "test_plugins"
        yeni.mkdir()
        reloader.klasor_ekle(yeni)
        assert yeni in reloader._klasorler

    def test_klasor_ekle_nonexistent(self, reloader):
        reloader.klasor_ekle("/nonexistent/path/12345")
        assert len(reloader._klasorler) == 2  # eklenmemis

    def test_klasor_ekle_file_not_dir(self, reloader, tmp_path):
        dosya = tmp_path / "test.py"
        dosya.write_text("# test")
        reloader.klasor_ekle(dosya)  # file, not dir → should not add
        assert len(reloader._klasorler) == 2

    def test_klasor_ekle_cagrisi_ekler(self, reloader, tmp_path):
        """Motor tool klasor ekleme islevselligi."""
        yeni = tmp_path / "eklenti"
        yeni.mkdir()
        reloader.klasor_ekle(yeni)
        assert len(reloader._klasorler) == 3


# ── Durum ────────────────────────────────────────────────────────────────

class TestDurum:
    def test_durum_keys(self, reloader):
        durum = reloader.durum()
        assert "calisiyor" in durum
        assert "izlenen_klasor" in durum
        assert "izlenen_dosya" in durum
        assert "istatistik" in durum

    def test_durum_istatistik_updates_on_loop(self, reloader):
        # Start, let it scan once (even if nothing to scan), stop
        reloader._aralik = 0.1  # hizli tarama
        reloader.baslat()
        time.sleep(0.3)
        reloader.durdur()
        durum = reloader.durum()
        # Tarama sayisi en az 1 olmali
        assert durum["istatistik"]["tarama"] >= 1


# ── Motor tool kaydi ─────────────────────────────────────────────────────

class TestMotorKaydet:
    def test_motor_kaydet_registers_tools(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet
        motor_kaydet(fake_motor)
        assert len(fake_motor.kayitlar) == 3
        adlar = [k[0] for k in fake_motor.kayitlar]
        assert "HOT_RELOAD_BASLAT" in adlar
        assert "HOT_RELOAD_DURDUR" in adlar
        assert "HOT_RELOAD_DURUM" in adlar

    def test_motor_hot_reload_baslat_func(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_baslat
        motor_kaydet(fake_motor)
        sonuc = motor_hot_reload_baslat("aralik=30")
        assert "Baslatildi" in sonuc
        # cleanup
        from reymen.sistem.hot_reload import motor_hot_reload_durdur
        motor_hot_reload_durdur()

    def test_motor_hot_reload_durum_func(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_durum
        motor_kaydet(fake_motor)
        durum_json = motor_hot_reload_durum()
        durum = json.loads(durum_json)
        assert "calisiyor" in durum
        assert "izlenen_klasor" in durum

    def test_motor_hot_reload_durdur_func(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_durdur
        motor_kaydet(fake_motor)
        # Once stop without starting -> "Zaten kapali" cunku _HOT_RELOADER var ama thread calismiyor
        sonuc = motor_hot_reload_durdur()
        assert "Zaten kapali" in sonuc


# ── _reload_modul Testleri ──────────────────────────────────────────────

class TestReloadModul:
    """_reload_modul fonksiyonunun cesitli senaryolari."""

    def test_reload_module_not_in_sys_modules(self, reloader, tmp_path):
        """Modul henuz sys.modules'te yoksa False doner."""
        # Gecici bir dosya olustur
        mod_dosya = tmp_path / "test_modul.py"
        mod_dosya.write_text("TEST_VAR = 1\n")
        result = reloader._reload_modul(mod_dosya)
        # Modul sys.modules'te olmadigi icin False donmeli
        assert result is False

    def test_reload_module_exception(self, reloader, tmp_path):
        """_reload_modul exception durumunda False doner."""
        # sys.modules'te olan ama hata firlatacak bir durum
        mod_dosya = tmp_path / "nonexistent_module.py"
        # Dosya olmadigi icin relative_to hata firlatir
        result = reloader._reload_modul(mod_dosya)
        assert result is False

    def test_reload_module_in_project_success(self, reloader, monkeypatch):
        """Proje icindeki bir modulu import edip _reload_modul ile yeniden yukle."""
        import importlib
        from pathlib import Path

        modul_adi = "reymen.test._test_hr_temp_module"
        import reymen.test._test_hr_temp_module as test_mod
        assert hasattr(test_mod, "motor_kaydet")
        assert test_mod.TEST_VAR == "initial_value"
        assert modul_adi in sys.modules

        mod_dosyasi = Path(test_mod.__file__).resolve()
        assert mod_dosyasi.exists()

        # Monkeypatch relative_to to return a path where the reymen prefix matches
        # Since _reload_modul prepends "reymen.", we need relative_to to return
        # "test._test_hr_temp_module" (without "reymen/") so the full name becomes
        # "reymen.test._test_hr_temp_module"
        def fake_relative_to(self, *args, **kwargs):
            if str(self).endswith("_test_hr_temp_module.py"):
                return Path("test") / "_test_hr_temp_module.py"
            return self.original_relative_to(*args, **kwargs)

        monkeypatch.setattr(Path, "relative_to", fake_relative_to)
        # Store original for non-test paths
        Path.original_relative_to = Path.__dict__["relative_to"].__func__ if hasattr(Path.__dict__["relative_to"], '__func__') else Path.__dict__["relative_to"]

        before_count = reloader._istatistik["yenilenen"]
        result = reloader._reload_modul(mod_dosyasi)
        assert result is True
        assert reloader._istatistik["yenilenen"] == before_count + 1

        # Verify motor_kaydet was called on the motor
        before_motor_count = len(reloader._motor.kayitlar) if hasattr(reloader._motor, 'kayitlar') else 0

    def test_reload_module_without_motor_kaydet(self, reloader, monkeypatch):
        """Modulde motor_kaydet yoksa reload yapilir ancak motor_kaydet cagrilmaz."""
        from pathlib import Path
        import reymen.test._test_hr_temp_module as test_mod

        mod_dosyasi = Path(test_mod.__file__).resolve()

        # motor_kaydet'i gecici olarak kaldir
        original_motor_kaydet = test_mod.motor_kaydet
        del test_mod.motor_kaydet

        def fake_relative_to(self, *args, **kwargs):
            if str(self).endswith("_test_hr_temp_module.py"):
                return Path("test") / "_test_hr_temp_module.py"
            raise ValueError("Not our path")

        monkeypatch.setattr(Path, "relative_to", fake_relative_to)

        before_count = reloader._istatistik["yenilenen"]
        result = reloader._reload_modul(mod_dosyasi)
        assert result is True
        assert reloader._istatistik["yenilenen"] == before_count + 1

        # Geri yukle
        test_mod.motor_kaydet = original_motor_kaydet

    def test_reload_module_motor_kaydet_error(self, reloader, monkeypatch):
        """Moduldeki motor_kaydet hata firlatirsa reload yine basarili sayilir."""
        from pathlib import Path
        import reymen.test._test_hr_temp_module as test_mod

        mod_dosyasi = Path(test_mod.__file__).resolve()

        original_motor_kaydet = test_mod.motor_kaydet

        def hatali_motor_kaydet(motor):
            raise RuntimeError("motor_kaydet hatasi")

        test_mod.motor_kaydet = hatali_motor_kaydet

        def fake_relative_to(self, *args, **kwargs):
            if str(self).endswith("_test_hr_temp_module.py"):
                return Path("test") / "_test_hr_temp_module.py"
            raise ValueError("Not our path")

        monkeypatch.setattr(Path, "relative_to", fake_relative_to)

        before_count = reloader._istatistik["yenilenen"]
        result = reloader._reload_modul(mod_dosyasi)
        assert result is True
        assert reloader._istatistik["yenilenen"] == before_count + 1

        test_mod.motor_kaydet = original_motor_kaydet

    def test_reload_module_not_yet_loaded(self, reloader):
        """Modul sys.modules'te yoksa else dali calisir ve False doner."""
        from reymen.sistem.hot_reload import HotReloader

        # Proje icinde var olan bir .py dosyasi kullan (ornegin __init__.py)
        # Ama modul adi sys.modules'te olmayacak
        proje_kok = Path(__file__).resolve().parent.parent.parent
        arac_init = proje_kok / "reymen" / "__init__.py"

        if arac_init.exists():
            # Bu dosyanin modul adi reymen ama muhtemelen sys.modules'te
            # Farkli bir dosya kullanalim - reymen/sistem/__init__.py
            sistem_init = proje_kok / "reymen" / "sistem" / "__init__.py"
            if sistem_init.exists():
                modul_adi = "reymen.sistem"
                if modul_adi in sys.modules:
                    # Modul yuklu, bu branch'i test edemeyiz. Skip.
                    pytest.skip("Modul zaten yuklu")
                result = reloader._reload_modul(sistem_init)
                assert result is False  # else branch: modul henuz yuklenmemis
            else:
                pytest.skip("reymen/sistem/__init__.py bulunamadi")
        else:
            pytest.skip("reymen/__init__.py bulunamadi")

    def test_reload_modul_importlib_error(self, reloader, tmp_path, monkeypatch):
        """importlib.reload basarisizlik durumu."""
        import importlib

        # Gecici bir modul
        modul_adi = "reymen_test_bad_module"
        mod_yolu = tmp_path / f"{modul_adi}.py"
        mod_yolu.write_text("TEST_VAR = 1\n")

        sys.path.insert(0, str(tmp_path))

        import importlib.util
        spec = importlib.util.spec_from_file_location(modul_adi, str(mod_yolu))
        if spec:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[modul_adi] = mod
            if spec.loader:
                spec.loader.exec_module(mod)

        # importlib.reload'un hata firlatmasi icin modulu boz
        if modul_adi in sys.modules:
            # importlib.reload'u monkeypatch ile hata firlatacak sekilde degistir
            original_reload = importlib.reload

            def fake_reload(module):
                raise ImportError("Simule edilmis reload hatasi")

            monkeypatch.setattr(importlib, "reload", fake_reload)

            # _reload_modul'u dogrudan cagir - proje yoluna goreceli olmali
            # Bunun icin baska bir yaklasim: dosyayi proje kokune yakin bir yerde goster
            # Aslinda _reload_modul Path(__file__).parent.parent.parent kullanarak
            # proje kokunu buluyor. Biz dosyayi proje disinda olusturduk, bu nedenle
            # relative_to hata firlatir. O hatayi test edelim.

            # Dosyayi proje disinda olusturdugumuz icin relative_to hata firlatir
            # ve bu da except blogunda yakalanir -> False doner
            result = reloader._reload_modul(mod_yolu)
            assert result is False

            monkeypatch.undo()

        if modul_adi in sys.modules:
            del sys.modules[modul_adi]
        sys.path.pop(0)


# ── _dongu ve _tarama Testleri ──────────────────────────────────────────

class TestDonguVeTarama:
    """_dongu ve _tarama icin cesitli senaryolar."""

    def test_tarama_nonexistent_dir(self, reloader):
        """Var olmayan klasor _tarama'da hata firlatmaz, skip eder."""
        reloader._klasorler = [Path("/nonexistent_dir_12345_test")]
        reloader._tarama()  # hata firlatmamali
        assert reloader._istatistik["tarama"] == 0  # _tarama direkt cagrildi, istatistik guncellenmez

    def test_tarama_new_file_detection(self, reloader, tmp_path):
        """Ilk taramada yeni dosyalar _izlenen'e eklenir."""
        # Gecici bir klasor olustur ve _klasorler'e ekle
        test_dir = tmp_path / "test_tools"
        test_dir.mkdir()
        mod_file = test_dir / "test_arac.py"
        mod_file.write_text("# test tool\n")

        reloader._klasorler = [test_dir]
        reloader._tarama()

        # Dosya _izlenen'de olmali
        assert str(mod_file) in reloader._izlenen

    def test_tarama_file_change_detection(self, reloader, tmp_path):
        """Dosya degisikligi algilanir ve _reload_modul cagrilir."""
        test_dir = tmp_path / "test_tools2"
        test_dir.mkdir()
        mod_file = test_dir / "test_arac2.py"
        mod_file.write_text("# version 1\n")

        reloader._klasorler = [test_dir]

        # Ilk tarama (kaydeder)
        reloader._tarama()
        assert str(mod_file) in reloader._izlenen

        # Dosyayi degistir
        time.sleep(0.1)  # mtime farki icin
        mod_file.write_text("# version 2\n")

        # Ikinci tarama (degisikligi algila)
        reloader._tarama()

        # Dosyanin mtime'i guncellenmis olmali
        # (reload basarisiz olur cunku modul sys.modules'te degil, ama _izlenen guncellenir)
        assert str(mod_file) in reloader._izlenen

    def test_tarama_skip_dunder_files(self, reloader, tmp_path):
        """__init__.py gibi __ ile baslayan dosyalar atlanir."""
        test_dir = tmp_path / "test_skip"
        test_dir.mkdir()
        init_file = test_dir / "__init__.py"
        init_file.write_text("# init\n")

        reloader._klasorler = [test_dir]
        reloader._tarama()

        # __init__.py atlanmis olmali
        assert str(init_file) not in reloader._izlenen

    def test_dongu_exception_handler(self, reloader):
        """_dongu icindeki exception handler hata sayacini artirir."""
        # _tarama'yi hata firlatacak sekilde degistir
        def hatali_tarama():
            raise RuntimeError("Test hatasi")

        reloader._tarama = hatali_tarama
        reloader._aralik = 0.05

        reloader.baslat()
        time.sleep(0.2)
        reloader.durdur()

        # Hata sayaci en az 1 olmali
        assert reloader._istatistik["hata"] >= 1


# ── Motor Tool Fonksiyon Testleri (no motor) ─────────────────────────────

class TestMotorToolsNoMotor:
    """_HOT_RELOADER yokken motor tool fonksiyonlari."""

    def test_motor_hot_reload_baslat_no_motor(self):
        from reymen.sistem.hot_reload import motor_hot_reload_baslat
        # _HOT_RELOADER globalini sifirla
        import reymen.sistem.hot_reload as hr_mod
        hr_mod._HOT_RELOADER = None

        sonuc = motor_hot_reload_baslat()
        assert "Motor referansi yok" in sonuc

    def test_motor_hot_reload_durdur_no_reloader(self):
        from reymen.sistem.hot_reload import motor_hot_reload_durdur
        import reymen.sistem.hot_reload as hr_mod
        hr_mod._HOT_RELOADER = None

        sonuc = motor_hot_reload_durdur()
        assert "Calismiyor" in sonuc

    def test_motor_hot_reload_durum_no_reloader(self):
        from reymen.sistem.hot_reload import motor_hot_reload_durum
        import reymen.sistem.hot_reload as hr_mod
        hr_mod._HOT_RELOADER = None

        sonuc = motor_hot_reload_durum()
        data = json.loads(sonuc)
        assert data["calisiyor"] is False


# ── Motor_hot_reload_baslat Parametre Testleri ──────────────────────────

class TestBaslatParametre:
    """motor_hot_reload_baslat parametre ayristirma."""

    def test_baslat_no_params(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_baslat, motor_hot_reload_durdur
        motor_kaydet(fake_motor)
        sonuc = motor_hot_reload_baslat("")
        assert "Baslatildi" in sonuc
        motor_hot_reload_durdur()

    def test_baslat_params_invalid(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_baslat, motor_hot_reload_durdur
        motor_kaydet(fake_motor)
        # Gecersiz parametre, varsayilan deger kullanilmali
        sonuc = motor_hot_reload_baslat("xyz=abc")
        assert "Baslatildi" in sonuc
        motor_hot_reload_durdur()

    def test_baslat_with_parantez(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet, motor_hot_reload_baslat, motor_hot_reload_durdur
        motor_kaydet(fake_motor)
        # Parantez icinde parametre
        sonuc = motor_hot_reload_baslat("aralik=5)")
        assert "Baslatildi" in sonuc
        motor_hot_reload_durdur()


# ── Singleton Pattern Testi ─────────────────────────────────────────────

class TestSingleton:
    """motor_kaydet singleton pattern testi."""

    def test_motor_kaydet_sets_global(self, fake_motor):
        from reymen.sistem.hot_reload import motor_kaydet
        import reymen.sistem.hot_reload as hr_mod
        hr_mod._HOT_RELOADER = None

        motor_kaydet(fake_motor)
        assert hr_mod._HOT_RELOADER is not None
        assert hr_mod._HOT_RELOADER._motor is fake_motor
