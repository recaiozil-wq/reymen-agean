"""test_motor.py — Motor (araç çözümleyici) mock testleri.

Motor sinifinin tool kaydetme, yonlendirme ve hata yonetimi
mekanizmalarini unittest.mock ile test eder.
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest


# ── Yardimci: Motor ornegi olustur (init'teki plugin yuklemeyi atla) ─────────

@pytest.fixture
def motor_instance():
    """Motor ornegi olustur, _plugin_moduller_yukle'yi devre disi birak.

    Motor.__init__() icinde _plugin_moduller_yukle() cagrilir ve bu da
    460+ modulu import etmeye calisir. Bu fixture sadece o metodu pas gecer.
    """
    with patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle", return_value=None):
        from reymen.cereyan.motor import Motor
        motor = Motor()
        return motor


# ── _plugin_arac_kaydet Testleri ─────────────────────────────────────────────

class TestPluginAracKaydet:
    """Motor._plugin_arac_kaydet() — arac kaydetme mekanizmasi."""

    def test_registry_yoksa_hata_vermez(self):
        """_REGISTRY None iken _plugin_arac_kaydet hata vermemeli."""
        with patch("reymen.cereyan.motor._REGISTRY", None):
            with patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle"):
                from reymen.cereyan.motor import Motor
                motor = Motor()
                motor._plugin_arac_kaydet("TEST_ARAC", lambda: "test", "Test araci")

    def test_registry_var_kaydeder(self):
        """_REGISTRY varsa kaydet() cagrilmali."""
        mock_registry = MagicMock()
        mock_registry._tools = {}
        broker_patches = [
            patch("reymen.cereyan.motor._REGISTRY", mock_registry),
            patch("reymen.cereyan.motor._BROKER_MEVCUT", False),
            patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle"),
        ]
        for p in broker_patches:
            p.start()
        try:
            from reymen.cereyan.motor import Motor
            motor = Motor()
            fonk = lambda: "sonuc"
            motor._plugin_arac_kaydet("TEST", fonk)
            mock_registry.kaydet.assert_called_once_with("TEST", fonk)
        finally:
            for p in broker_patches:
                p.stop()

    def test_kaydet_farkli_isimler(self):
        """Farkli arac isimleri ayri ayri kaydedilebilmeli."""
        mock_registry = MagicMock()
        mock_registry._tools = {}
        broker_patches = [
            patch("reymen.cereyan.motor._REGISTRY", mock_registry),
            patch("reymen.cereyan.motor._BROKER_MEVCUT", False),
            patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle"),
        ]
        for p in broker_patches:
            p.start()
        try:
            from reymen.cereyan.motor import Motor
            motor = Motor()
            motor._plugin_arac_kaydet("ARAC_A", lambda: "1")
            motor._plugin_arac_kaydet("ARAC_B", lambda: "2")
            assert mock_registry.kaydet.call_count == 2
        finally:
            for p in broker_patches:
                p.stop()


# ── calistir_fc Testleri ─────────────────────────────────────────────────────

class TestCalistirFC:
    """Motor.calistir_fc() — FC args dict'ini calistir()'a kopruler."""

    def test_calistir_fc_bos_args(self, motor_instance):
        """calistir_fc() args=None ise calistir'a bos string gitmeli."""
        with patch.object(motor_instance, "calistir", return_value="OK") as mock_calistir:
            sonuc = motor_instance.calistir_fc("TEST", {})
            mock_calistir.assert_called_once_with("TEST", "")
            assert sonuc == "OK"

    def test_calistir_fc_tek_param(self, motor_instance):
        """Tek parametreli args dogru formata donusuyor mu?"""
        with patch.object(motor_instance, "calistir", return_value="OK") as mock_calistir:
            motor_instance.calistir_fc("TEST", {"dosya": "test.py"})
            args_str = mock_calistir.call_args[0][1]
            assert "test.py" in args_str

    def test_calistir_fc_coklu_param(self, motor_instance):
        """Coklu parametreli args sıralı string'e donusuyor mu?"""
        with patch.object(motor_instance, "calistir", return_value="OK") as mock_calistir:
            motor_instance.calistir_fc("TEST", {"x": "1", "y": "2"})
            args_str = mock_calistir.call_args[0][1]
            assert "1" in args_str
            assert "2" in args_str

    def test_calistir_fc_ozel_karakter_escape(self, motor_instance):
        """Ozel karakterler (tirnak, ters slash) escape ediliyor mu?"""
        with patch.object(motor_instance, "calistir", return_value="OK") as mock_calistir:
            motor_instance.calistir_fc("TEST", {"metin": 'deger"icinde"tirnak'})
            args_str = mock_calistir.call_args[0][1]
            assert '\\"' in args_str


# ── Motor Baslatma Testleri ──────────────────────────────────────────────────

class TestMotorBaslatma:
    """Motor() kurulumu — try/except importlar mock'lanmis."""

    def test_motor_baslatma_minimal(self):
        """Tum opsiyonel bagimliliklar kapaliyken Motor() hata vermemeli."""
        patchers = [
            patch("reymen.cereyan.motor.TerminalBackendDispatcher", None),
            patch("reymen.cereyan.motor._REGISTRY", None),
            patch("reymen.cereyan.motor._PLUGIN_MGR", None),
            patch("reymen.cereyan.motor._PROFILE_MGR", None),
            patch("reymen.cereyan.motor._COMPRESSOR", None),
            patch("reymen.cereyan.motor._CACHE", None),
            patch("reymen.cereyan.motor._BROKER_MEVCUT", False),
            patch("reymen.cereyan.motor._CUA_MEVCUT", False),
            patch("reymen.cereyan.motor._ORCHESTRATOR_MEVCUT", False),
            patch("reymen.cereyan.motor._OGRENME_MEVCUT", False),
            patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle"),
        ]
        for p in patchers:
            p.start()
        try:
            from reymen.cereyan.motor import Motor
            motor = Motor()
            assert motor.terminal is None
            assert motor.hafiza is None
        finally:
            for p in patchers:
                p.stop()

    def test_motor_config_parametresi(self):
        """Motor(config) parametresi dogru saklaniyor mu?"""
        with patch("reymen.cereyan.motor.Motor._plugin_moduller_yukle"):
            from reymen.cereyan.motor import Motor
            test_config = {"test_key": "test_val"}
            motor = Motor(config=test_config)
            assert motor.config["test_key"] == "test_val"


# ── Motor Durum / Yardimci Testleri ─────────────────────────────────────────

class TestMotorYardimci:
    """Motor yardimci metodlari ve durum."""

    def test_hook_kaydet_hooks_yoksa_hata_vermez(self, motor_instance):
        """_hooks=None iken hook_kaydet() hata vermemeli."""
        motor_instance._hooks = None
        try:
            motor_instance.hook_kaydet("TEST", lambda: None)
        except Exception as e:
            pytest.fail(f"hook_kaydet hata firlatti: {e}")

    def test_broker_durum_broker_yoksa(self, motor_instance):
        """Broker yokken broker_durum() dict donuyor mu?"""
        motor_instance._broker = None
        durum = motor_instance.broker_durum()
        assert isinstance(durum, dict)
        assert "running" in durum
        assert durum["running"] is False

    def test_ekstra_izin_araclar_bos(self, motor_instance):
        """ekstra_izin_araclar set ile basliyor mu?"""
        assert isinstance(motor_instance.ekstra_izin_araclar, set)
        assert len(motor_instance.ekstra_izin_araclar) == 0
