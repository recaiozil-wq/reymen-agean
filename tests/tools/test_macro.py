# -*- coding: utf-8 -*-
"""Test: macro.py — Makro oynatma aracı."""

from unittest.mock import patch, MagicMock
from tools import macro


def test_oynat_no_name():
    sonuc = macro.oynat("")
    assert "gerekli" in sonuc


def test_oynat_not_found():
    with patch("pathlib.Path.exists", return_value=False):
        sonuc = macro.oynat("nonexistent_macro")
        assert "bulunamadi" in sonuc


def test_ping_no_folder():
    with patch("pathlib.Path.exists", return_value=False):
        assert macro.ping() is False


@patch("tools.macro.MAKRO_KLASOR")
def test_oynat_import_error(mock_klasor):
    """Makro dosyası var ama import edilemezse hata döner."""
    mock_klasor.__truediv__.return_value.exists.return_value = True
    with patch("importlib.util.spec_from_file_location", return_value=None):
        sonuc = macro.oynat("test_macro")
        assert "yuklenemedi" in sonuc or "Hata" in sonuc


@patch("tools.macro.MAKRO_KLASOR")
def test_oynat_no_adimlar(mock_klasor):
    """Makro var ama ADIMLAR yoksa hata döner."""
    mock_klasor.__truediv__.return_value.exists.return_value = True
    mock_spec = MagicMock()
    mock_spec.loader = MagicMock()
    mock_mod = MagicMock()
    mock_mod.ADIMLAR = None
    del mock_mod.ADIMLAR  # make hasattr return False
    mock_spec.loader.exec_module.return_value = None
    with patch("importlib.util.spec_from_file_location", return_value=mock_spec):
        with patch("importlib.util.module_from_spec", return_value=mock_mod):
            sonuc = macro.oynat("test_macro")
            assert "ADIMLAR" in sonuc or "bulunamadi" in sonuc


@patch("tools.macro.MAKRO_KLASOR")
def test_oynat_success(mock_klasor):
    """Başarılı makro oynatma."""
    mock_klasor.__truediv__.return_value.exists.return_value = True
    mock_klasor.glob.return_value = []
    mock_spec = MagicMock()
    mock_spec.loader = MagicMock()
    mock_mod = MagicMock()
    mock_mod.ADIMLAR = [{"eylem": "print", "parametre": "test"}]
    mock_spec.loader.exec_module.return_value = None
    with patch("importlib.util.spec_from_file_location", return_value=mock_spec):
        with patch("importlib.util.module_from_spec", return_value=mock_mod):
            with patch("motor.Motor") as MockMotor:
                motor_instance = MagicMock()
                motor_instance.calistir.return_value = "OK"
                MockMotor.return_value = motor_instance
                sonuc = macro.oynat("test_macro")
                assert "Oynatildi" in sonuc or "Makro" in sonuc
