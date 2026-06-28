# -*- coding: utf-8 -*-
"""tests/test_http_client_limits.py — platform_httpx_limits birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from unittest.mock import patch

# Import httpx first to verify it's available
import httpx
from gateway.platforms._http_client_limits import platform_httpx_limits


class TestHttpClientLimits:
    def test_with_httpx(self):
        """With httpx installed, returns proper Limits."""
        result = platform_httpx_limits()
        assert result is not None
        assert result.keepalive_expiry == 2.0
        assert result.max_keepalive_connections == 10

    def test_env_overrides(self):
        with patch.dict("os.environ", {
            "HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY": "5.0",
            "HERMES_GATEWAY_HTTPX_MAX_KEEPALIVE": "20",
        }, clear=False):
            result = platform_httpx_limits()
            assert result is not None
            assert result.keepalive_expiry == 5.0
            assert result.max_keepalive_connections == 20

    def test_env_invalid_values_fallback(self):
        with patch.dict("os.environ", {
            "HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY": "invalid",
            "HERMES_GATEWAY_HTTPX_MAX_KEEPALIVE": "-5",
        }, clear=False):
            result = platform_httpx_limits()
            assert result is not None
            assert result.keepalive_expiry == 2.0
            assert result.max_keepalive_connections == 10

    def test_env_negative_values_fallback(self):
        with patch.dict("os.environ", {
            "HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY": "-1.0",
        }, clear=False):
            result = platform_httpx_limits()
            assert result is not None
            assert result.keepalive_expiry == 2.0

    def test_env_empty_values_fallback(self):
        with patch.dict("os.environ", {
            "HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY": "",
            "HERMES_GATEWAY_HTTPX_MAX_KEEPALIVE": "",
        }, clear=False):
            result = platform_httpx_limits()
            assert result is not None
            assert result.keepalive_expiry == 2.0
            assert result.max_keepalive_connections == 10
