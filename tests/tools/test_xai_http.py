# -*- coding: utf-8 -*-
"""Test: xai_http.py — xAI HTTP istemci."""

from unittest.mock import patch, MagicMock
from tools import xai_http


def test_has_xai_credentials_with_key():
    """XAI_API_KEY varsa True döndürür."""
    with patch.dict("os.environ", {"XAI_API_KEY": "test_key_123"}):
        assert xai_http.has_xai_credentials() is True


def test_has_xai_credentials_no_key():
    """XAI_API_KEY yoksa False döndürür."""
    with patch.dict("os.environ", {"XAI_API_KEY": ""}, clear=False):
        with patch("os.getenv", return_value=""):
            assert xai_http.has_xai_credentials() is False


def test_get_env_value_from_env():
    """os.environ'dan değer okur."""
    with patch.dict("os.environ", {"TEST_XAI_VAR": "hello"}):
        result = xai_http.get_env_value("TEST_XAI_VAR")
        assert result == "hello"


def test_get_env_value_default():
    """Olmayan değişken için default döndürür."""
    result = xai_http.get_env_value("NONEXISTENT_VAR_XYZ", default="fallback")
    assert result == "fallback"


def test_hermes_xai_user_agent():
    """User-Agent string'i ReYMeN içermeli."""
    ua = xai_http.hermes_xai_user_agent()
    assert "ReYMeN" in ua


def test_resolve_xai_http_credentials_with_key():
    """XAI_API_KEY varsa Authorization header döndürür."""
    with patch.dict("os.environ", {"XAI_API_KEY": "sk-test-key"}):
        creds = xai_http.resolve_xai_http_credentials()
        assert isinstance(creds, dict)
        assert "Authorization" in creds
        assert "sk-test-key" in creds["Authorization"]


def test_resolve_xai_http_credentials_no_key():
    """XAI_API_KEY yoksa boş dict döndürür."""
    with patch.object(xai_http, "get_env_value", return_value=""):
        creds = xai_http.resolve_xai_http_credentials()
        assert creds == {}


def test_module_has_expected_names():
    """Modül beklenen isimleri içermeli."""
    assert hasattr(xai_http, "has_xai_credentials")
    assert hasattr(xai_http, "get_env_value")
    assert hasattr(xai_http, "hermes_xai_user_agent")
    assert hasattr(xai_http, "resolve_xai_http_credentials")
