# -*- coding: utf-8 -*-
"""Test: xai_http.py — xAI HTTP istemci (requests mock)."""

from unittest.mock import patch, MagicMock
from tools import xai_http
import requests as _real_requests


def test_run_modeller():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": [{"id": "grok-2"}, {"id": "grok-3"}]}
        mock_get.return_value = mock_resp
        with patch("tools.xai_http._XAI_API_KEY", "test_key"):
            sonuc = xai_http.run(islem="modeller")
            assert "grok-2" in sonuc


def test_run_modeller_api_error():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_get.return_value = mock_resp
        with patch("tools.xai_http._XAI_API_KEY", "test_key"):
            sonuc = xai_http.run(islem="modeller")
            assert "API hatası" in sonuc


def test_run_modeller_no_key():
    with patch("tools.xai_http._XAI_API_KEY", ""):
        sonuc = xai_http.run(islem="modeller")
        assert "bulunamadı" in sonuc


def test_run_bakiye():
    with patch("tools.xai_http._XAI_API_KEY", "test_key"):
        sonuc = xai_http.run(islem="bakiye")
        assert "Mevcut" in sonuc


def test_run_bakiye_no_key():
    with patch("tools.xai_http._XAI_API_KEY", ""):
        sonuc = xai_http.run(islem="bakiye")
        assert "Hata" in sonuc


def test_run_sorgula():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Merhaba!"}}],
            "usage": {"total_tokens": 10},
        }
        mock_post.return_value = mock_resp
        with patch("tools.xai_http._XAI_API_KEY", "test_key"):
            sonuc = xai_http.run(islem="sorgula", mesaj="Selam")
            assert "Merhaba" in sonuc


def test_run_sorgula_no_message():
    with patch("tools.xai_http._XAI_API_KEY", "test_key"):
        sonuc = xai_http.run(islem="sorgula")
        assert "Hata" in sonuc


def test_run_sorgula_no_key():
    with patch("tools.xai_http._XAI_API_KEY", ""):
        sonuc = xai_http.run(islem="sorgula", mesaj="test")
        assert "bulunamadı" in sonuc


def test_run_sorgula_list_messages():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Merhaba!"}}],
            "usage": {},
        }
        mock_post.return_value = mock_resp
        with patch("tools.xai_http._XAI_API_KEY", "test_key"):
            sonuc = xai_http.run(islem="sorgula", mesaj=[{"role": "user", "content": "test"}])
            assert "Merhaba" in sonuc


def test_run_invalid_islem():
    assert "Geçersiz" in xai_http.run(islem="gecersiz")


def test_resolve_xai_http_credentials():
    with patch("tools.xai_http.os.environ.get", return_value="test_key"):
        creds = xai_http.resolve_xai_http_credentials()
        assert creds is not None
        assert creds["api_key"] == "test_key"


def test_resolve_xai_http_credentials_none():
    with patch("tools.xai_http.os.environ.get", return_value=""):
        creds = xai_http.resolve_xai_http_credentials()
        assert creds is None


def test_has_xai_credentials():
    with patch("tools.xai_http.os.environ.get", return_value="key"):
        assert xai_http.has_xai_credentials() is True


def test_has_xai_credentials_false():
    with patch("tools.xai_http.os.environ.get", return_value=""):
        assert xai_http.has_xai_credentials() is False


def test_ReYMeN_xai_user_agent():
    ua = xai_http.ReYMeN_xai_user_agent()
    assert "ReYMeN" in ua
