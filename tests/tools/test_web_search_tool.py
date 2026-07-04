# -*- coding: utf-8 -*-
"""Test: web_search_tool.py — DuckDuckGo web arama (urllib mock)."""

from unittest.mock import patch, MagicMock
from tools import web_search_tool


@patch("tools.web_search_tool.urllib.request.urlopen")
def test_run_duckduckgo_abstract(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = (
        b'{"AbstractText": "Test sonucu", "AbstractURL": "https://example.com"}'
    )
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    sonuc = web_search_tool.run(sorgu="test")
    assert "Test sonucu" in sonuc
    assert "Kaynak" in sonuc


@patch("tools.web_search_tool.urllib.request.urlopen")
def test_run_duckduckgo_related(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"AbstractText": "", "RelatedTopics": [{"Text": "Ilgili konu", "FirstURL": "https://example.com"}]}'
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    sonuc = web_search_tool.run(sorgu="test")
    assert "Ilgili konu" in sonuc


@patch("tools.web_search_tool.urllib.request.urlopen")
def test_run_duckduckgo_nested(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"AbstractText": "", "RelatedTopics": [{"Name": "Kategori", "Topics": [{"Text": "Alt konu"}]}]}'
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    sonuc = web_search_tool.run(sorgu="test")
    assert "Alt konu" in sonuc


@patch("tools.web_search_tool.urllib.request.urlopen")
def test_run_duckduckgo_empty(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"AbstractText": "", "RelatedTopics": []}'
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    sonuc = web_search_tool.run(sorgu="test")
    assert "Bulunamadi" in sonuc


def test_run_no_query():
    sonuc = web_search_tool.run(sorgu="")
    assert "Hata" in sonuc


def test_run_unknown_source():
    sonuc = web_search_tool.run(sorgu="test", kaynak="google")
    assert "Hata" in sonuc


@patch(
    "tools.web_search_tool.urllib.request.urlopen", side_effect=Exception("Ağ hatası")
)
def test_run_exception(mock_urlopen):
    sonuc = web_search_tool.run(sorgu="test")
    assert "Hata" in sonuc


def test_motor_kaydet():
    motor = MagicMock()
    web_search_tool.motor_kaydet(motor)
    motor._plugin_arac_kaydet.assert_called_once()
