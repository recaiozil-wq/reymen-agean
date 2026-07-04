# -*- coding: utf-8 -*-
"""Test: macro.py — Makro oynatma aracı (stub)."""

from tools import macro


def test_oynat_returns_string():
    """oynat her zaman string döndürür."""
    sonuc = macro.oynat("test_macro")
    assert isinstance(sonuc, str)


def test_oynat_contains_name():
    """oynat makro adını içerir."""
    sonuc = macro.oynat("benim_makrom")
    assert "benim_makrom" in sonuc


def test_oynat_empty_name():
    """Boş isimle de çalışır (stub)."""
    sonuc = macro.oynat("")
    assert isinstance(sonuc, str)
    assert "[MAKRO]" in sonuc


def test_oynat_stub_message():
    """Stub mesajı döndürür."""
    sonuc = macro.oynat("herhangi_bir_sey")
    assert "çalıştırıldı" in sonuc or "stub" in sonuc


def test_module_has_expected_names():
    """Modül beklenen isimleri içermeli."""
    assert hasattr(macro, "oynat")
    assert hasattr(macro, "logger")
