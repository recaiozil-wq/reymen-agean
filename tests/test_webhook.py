# -*- coding: utf-8 -*-
"""gateway/platforms/webhook.py testleri."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestWebhookModuleFunctions:
    def test_baslat_durdur(self):
        from gateway.platforms.webhook import baslat, durdur

        assert baslat() is None
        assert durdur() is None

    def test_mesaj_gonder_invalid_url(self):
        from gateway.platforms.webhook import mesaj_gonder

        result = mesaj_gonder("not-a-url", "test")
        assert "URL" in result

    def test_mesaj_gonder_http_error(self):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.text = "Server Error"
            mock_post.return_value = mock_resp

            from gateway.platforms.webhook import mesaj_gonder

            result = mesaj_gonder("http://example.com/hook", "test")
            assert "500" in result

    def test_mesaj_gonder_success(self):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp

            from gateway.platforms.webhook import mesaj_gonder

            result = mesaj_gonder("http://example.com/hook", "test")
            assert "Gonderildi" in result

    def test_mesaj_gonder_timeout(self):
        with patch(
            "requests.post", side_effect=__import__("requests").Timeout("timeout")
        ):
            from gateway.platforms.webhook import mesaj_gonder

            result = mesaj_gonder("http://example.com/hook", "test")
            assert "Zaman asimi" in result

    def test_mesaj_gonder_exception(self):
        with patch("requests.post", side_effect=Exception("baglanti hatasi")):
            from gateway.platforms.webhook import mesaj_gonder

            result = mesaj_gonder("http://example.com/hook", "test")
            assert "Hata" in result


class TestWebhookAdapter:
    def test_adapter_init_no_config(self):
        from gateway.platforms.webhook import WebhookAdapter

        adapter = WebhookAdapter()
        assert adapter.platform == "webhook"
        assert adapter._port > 0
        assert adapter._mesaj_isleyici is None

    def test_adapter_init_with_config(self):
        config = MagicMock()
        config.extra = {"port": 9999, "secret": "s3cret", "enabled": True}

        with patch(
            "os.environ.get",
            lambda k, d=None: "" if k.startswith("WEBHOOK_") else (d or ""),
        ):
            from gateway.platforms.webhook import WebhookAdapter

            adapter = WebhookAdapter(config=config)
            assert adapter._port == 9999
            assert adapter._secret == "s3cret"
            assert adapter._enabled is True

    def test_adapter_aktif_false_when_not_started(self):
        from gateway.platforms.webhook import WebhookAdapter

        adapter = WebhookAdapter()
        assert adapter.aktif is False

    def test_adapter_mesaj_isleyici_kaydet(self):
        from gateway.platforms.webhook import WebhookAdapter

        adapter = WebhookAdapter()
        fn = lambda m: None
        adapter.mesaj_isleyici_kaydet(fn)
        assert adapter._mesaj_isleyici is fn

    def test_adapter_baslat_disabled(self):
        with patch(
            "os.environ.get",
            lambda k, d=None: {
                "WEBHOOK_ENABLED": "false",
                "WEBHOOK_PORT": "8644",
                "WEBHOOK_SECRET": "",
            }.get(k, d or ""),
        ):
            from gateway.platforms.webhook import WebhookAdapter

            adapter = WebhookAdapter()
            result = adapter.baslat()
            assert result is None

    def test_adapter_baslat_success(self):
        mock_gateway = MagicMock()
        mock_gateway.baslat.return_value = 18777

        # WEBHOOK_PORT must be set to avoid ValueError when gateway.webhook is imported
        with patch(
            "os.environ.get",
            lambda k, d=None: "8766" if k == "WEBHOOK_PORT" else (d or ""),
        ):
            with patch("gateway.webhook.WebhookGateway", return_value=mock_gateway):
                from gateway.platforms.webhook import WebhookAdapter

                adapter = WebhookAdapter()
                adapter._enabled = True
                result = adapter.baslat()
                assert result == 18777
                mock_gateway.baslat.assert_called_once()

    def test_adapter_durdur(self):
        mock_gateway = MagicMock()
        from gateway.platforms.webhook import WebhookAdapter

        adapter = WebhookAdapter()
        adapter._sunucu = mock_gateway
        adapter.durdur()
        mock_gateway.durdur.assert_called_once()
        assert adapter._sunucu is None

    def test_adapter_gonder(self):
        with patch(
            "gateway.platforms.webhook.mesaj_gonder",
            return_value="[Webhook]: Gonderildi (HTTP 200).",
        ):
            from gateway.platforms.webhook import WebhookAdapter

            adapter = WebhookAdapter()
            result = adapter.gonder("http://example.com/hook", "test")
            assert "Gonderildi" in result

    def test_adapter_connect_success(self):
        mock_gateway = MagicMock()
        mock_gateway.baslat.return_value = 18777

        with patch(
            "os.environ.get",
            lambda k, d=None: "8766" if k == "WEBHOOK_PORT" else (d or ""),
        ):
            with patch("gateway.webhook.WebhookGateway", return_value=mock_gateway):
                from gateway.platforms.webhook import WebhookAdapter

                adapter = WebhookAdapter()
                adapter._enabled = True
                import asyncio

                result = asyncio.run(adapter.connect())
                assert result is True

    def test_adapter_disconnect(self):
        from gateway.platforms.webhook import WebhookAdapter

        adapter = WebhookAdapter()
        adapter._sunucu = MagicMock()
        import asyncio

        asyncio.run(adapter.disconnect())
        assert adapter._sunucu is None

    def test_adapter_send_message(self):
        with patch(
            "gateway.platforms.webhook.mesaj_gonder",
            return_value="[Webhook]: Gonderildi (HTTP 200).",
        ):
            from gateway.platforms.webhook import WebhookAdapter

            adapter = WebhookAdapter()
            import asyncio

            result = asyncio.run(adapter.send_message("chat", "content"))
            assert result["success"] is True


class TestWebhookHelpers:
    def test_check_webhook_requirements(self):
        from gateway.platforms.webhook import check_webhook_requirements

        assert check_webhook_requirements() is True

    def test_security_constants(self):
        from gateway.platforms.webhook import (
            _INSECURE_NO_AUTH,
            _INSECURE_MODES,
            _DYNAMIC_ROUTES_FILENAME,
        )

        assert _INSECURE_NO_AUTH == "no_auth"
        assert "no_auth" in _INSECURE_MODES
        assert _DYNAMIC_ROUTES_FILENAME == "routes.json"
