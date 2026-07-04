# -*- coding: utf-8 -*-
"""Test: browser.py — Tarayıcı otomasyon."""

from tools import browser


def test_ping():
    """ping bool döndürür."""
    sonuc = browser.ping()
    assert isinstance(sonuc, bool)


def test_sayfa_ac_no_url():
    """URL parametresi yoksa hata mesajı döndürür."""
    sonuc = browser.sayfa_ac("")
    assert "URL" in sonuc or "gerekli" in sonuc


def test_sayfa_ac_url_var():
    """URL verilirse fonksiyon çalışır."""
    sonuc = browser.sayfa_ac("https://example.com")
    assert sonuc is not None
    assert isinstance(sonuc, str)
