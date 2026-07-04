# -*- coding: utf-8 -*-
"""Test: openrouter_client.py — OpenRouter API istemci (requests mock)."""

from unittest.mock import patch, MagicMock
from tools import openrouter_client


def test_run_modeller():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"id": "openai/gpt-4o"}, {"id": "openai/gpt-4o-mini"}]
        }
        mock_get.return_value = mock_resp
        with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
            sonuc = openrouter_client.run(islem="modeller")
            assert "gpt-4o" in sonuc


def test_run_modeller_api_error():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_get.return_value = mock_resp
        with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
            sonuc = openrouter_client.run(islem="modeller")
            assert "API hatası" in sonuc


def test_run_modeller_no_key():
    with patch("tools.openrouter_client._OPENROUTER_API_KEY", ""):
        sonuc = openrouter_client.run(islem="modeller")
        assert "bulunamadı" in sonuc


def test_run_token():
    with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
        sonuc = openrouter_client.run(islem="token")
        assert "Mevcut" in sonuc


def test_run_token_no_key():
    with patch("tools.openrouter_client._OPENROUTER_API_KEY", ""):
        sonuc = openrouter_client.run(islem="token")
        assert "Bulunamadı" in sonuc


def test_run_sorgula_no_message():
    with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
        sonuc = openrouter_client.run(islem="sorgula", model="openai/gpt-4o")
        assert "Hata" in sonuc


def test_run_sorgula_no_key():
    with patch("tools.openrouter_client._OPENROUTER_API_KEY", ""):
        sonuc = openrouter_client.run(
            islem="sorgula", mesaj="test", model="openai/gpt-4o"
        )
        assert "bulunamadı" in sonuc


def test_run_sorgula_success():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Merhaba!"}}],
            "usage": {"total_tokens": 10},
        }
        mock_post.return_value = mock_resp
        with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
            sonuc = openrouter_client.run(
                islem="sorgula", mesaj="Selam", model="openai/gpt-4o"
            )
            assert "Merhaba" in sonuc


def test_run_sorgula_list_messages():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "OK"}}],
            "usage": {},
        }
        mock_post.return_value = mock_resp
        with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
            sonuc = openrouter_client.run(
                islem="sorgula",
                mesaj=[{"role": "user", "content": "test"}],
                model="openai/gpt-4o",
            )
            assert "OK" in sonuc


def test_run_sorgula_default_model():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "OK"}}],
            "usage": {},
        }
        mock_post.return_value = mock_resp
        with patch("tools.openrouter_client._OPENROUTER_API_KEY", "test_key"):
            sonuc = openrouter_client.run(islem="sorgula", mesaj="test")
            assert "OK" in sonuc


def test_run_invalid_islem():
    sonuc = openrouter_client.run(islem="gecersiz")
    assert "Geçersiz" in sonuc
