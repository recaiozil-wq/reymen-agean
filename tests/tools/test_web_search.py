# -*- coding: utf-8 -*-
"""Test: web_search.py — Web arama aracı (requests mock)."""

from unittest.mock import patch, MagicMock
from tools import web_search


@patch("tools.web_search.requests.get")
def test_ara_url(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html><body>Merhaba Dünya</body></html>"
    mock_get.return_value = mock_resp
    sonuc = web_search.ara("https://example.com")
    assert "Merhaba" in sonuc
    assert "karakter" in sonuc


@patch("tools.web_search.requests.get")
def test_ara_search_query(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<p>sonuç</p>"
    mock_get.return_value = mock_resp
    sonuc = web_search.ara("test sorgu")
    assert "karakter" in sonuc


@patch("tools.web_search.requests.get")
def test_ara_non_200(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp
    sonuc = web_search.ara("https://example.com")
    assert "HTTP" in sonuc


@patch("tools.web_search.requests.get", side_effect=Exception("Bağlantı hatası"))
def test_ara_exception(mock_get):
    sonuc = web_search.ara("https://example.com")
    assert "Hata" in sonuc


def test_ara_no_query():
    sonuc = web_search.ara("")
    assert "gerekli" in sonuc
