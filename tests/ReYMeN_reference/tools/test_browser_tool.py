# -*- coding: utf-8 -*-
"""Test: browser_tool.py — Tarayıcı kontrol aracı."""

from unittest.mock import patch, MagicMock
from tools import browser_tool


def test_run_ac():
    sonuc = browser_tool.run(islem="ac")
    assert "açıldı" in sonuc


def test_run_kapat():
    sonuc = browser_tool.run(islem="kapat")
    assert "kapatıldı" in sonuc


def test_run_gezinti():
    sonuc = browser_tool.run(islem="gezinti", url="https://example.com")
    assert "yüklendi" in sonuc


def test_run_gezinti_no_url():
    sonuc = browser_tool.run(islem="gezinti")
    assert "Hata" in sonuc


def test_run_ekran_al():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b"dummy_image_data"
        mock_get.return_value = mock_resp
        sonuc = browser_tool.run(islem="ekran_al", url="https://example.com")
        assert "alındı" in sonuc


def test_run_ekran_al_no_url():
    sonuc = browser_tool.run(islem="ekran_al")
    assert "Hata" in sonuc


def test_run_js_calistir():
    sonuc = browser_tool.run(islem="js_calistir", js_kodu="console.log('test')")
    assert "OK" in sonuc


def test_run_js_calistir_no_kod():
    sonuc = browser_tool.run(islem="js_calistir")
    assert "Hata" in sonuc


def test_run_invalid_islem():
    sonuc = browser_tool.run(islem="gecersiz")
    assert "Hata" in sonuc


def test_cleanup_browser():
    """cleanup_browser should not raise."""
    browser_tool.cleanup_browser()


def test_discover_homebrew_node_dirs():
    dirs = browser_tool._discover_homebrew_node_dirs()
    assert dirs == []
