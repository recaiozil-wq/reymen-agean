# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestWhatsAppBaslatDurdur:
    def test_baslat_logs_info(self):
        with patch("gateway.platforms.whatsapp.logger") as mock_log:
            with patch("gateway.platforms.whatsapp.node_mevcut", return_value=False):
                from gateway.platforms.whatsapp import baslat
                baslat()
                mock_log.info.assert_any_call("[whatsapp] Platform baslatildi")

    def test_durdur_logs_info(self):
        with patch("gateway.platforms.whatsapp.logger") as mock_log:
            from gateway.platforms.whatsapp import durdur
            durdur()
            mock_log.info.assert_called_once_with("[whatsapp] Platform durduruldu")


class TestWhatsAppToken:
    def test_token_al_returns_token(self):
        with patch("os.environ.get", return_value="valid_token_123"):
            from gateway.platforms.whatsapp import _token_al
            assert _token_al() == "valid_token_123"

    def test_token_al_empty(self):
        with patch("os.environ.get", return_value=""):
            from gateway.platforms.whatsapp import _token_al
            assert _token_al() == ""

    def test_token_al_redacted(self):
        with patch("os.environ.get", return_value="***redacted***"):
            from gateway.platforms.whatsapp import _token_al
            assert _token_al() == ""


class TestWhatsAppMesajGonder:
    def test_mesaj_gonder_no_requests(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", False):
            from gateway.platforms.whatsapp import mesaj_gonder
            result = mesaj_gonder("905551234567", "test")
            assert "requests" in result

    def test_mesaj_gonder_no_token(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value=""):
                from gateway.platforms.whatsapp import mesaj_gonder
                result = mesaj_gonder("905551234567", "test")
                assert "TOKEN" in result

    def test_mesaj_gonder_no_phone_id(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                with patch("gateway.platforms.whatsapp._config_str", return_value=""):
                    from gateway.platforms.whatsapp import mesaj_gonder
                    result = mesaj_gonder("905551234567", "test")
                    assert "PHONE_ID" in result

    def test_mesaj_gonder_dm_disabled(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    if key == "WHATSAPP_PHONE_ID":
                        return "12345"
                    if key == "WHATSAPP_DM_POLICY":
                        return "disabled"
                    return default
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    from gateway.platforms.whatsapp import mesaj_gonder
                    result = mesaj_gonder("905551234567", "test")
                    assert "DM izni" in result

    def test_mesaj_gonder_success(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"messages": [{"id": "wamid.123"}]}

        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0", "WHATSAPP_DM_POLICY": "open"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", return_value=mock_resp) as mock_post:
                        from gateway.platforms.whatsapp import mesaj_gonder
                        result = mesaj_gonder("905551234567", "Merhaba")
                        assert "gonderildi" in result.lower()
                        mock_post.assert_called_once()

    def test_mesaj_gonder_with_reply_to(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"messages": [{"id": "wamid.1"}]}

        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0", "WHATSAPP_DM_POLICY": "open"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", return_value=mock_resp) as mock_post:
                        from gateway.platforms.whatsapp import mesaj_gonder
                        mesaj_gonder("905551234567", "test", reply_to="orig_msg")
                        payload = mock_post.call_args[1]["json"]
                        assert payload["context"]["message_id"] == "orig_msg"

    def test_mesaj_gonder_error_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": {"message": "Unauthorized"}}

        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0", "WHATSAPP_DM_POLICY": "open"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", return_value=mock_resp):
                        from gateway.platforms.whatsapp import mesaj_gonder
                        result = mesaj_gonder("905551234567", "test")
                        assert "Unauthorized" in result

    def test_mesaj_gonder_exception(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0", "WHATSAPP_DM_POLICY": "open"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", side_effect=Exception("baglanti hatasi")):
                        from gateway.platforms.whatsapp import mesaj_gonder
                        result = mesaj_gonder("905551234567", "test")
                        assert "Hata" in result

    def test_mesaj_gonder_truncates_long(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"messages": [{"id": "wamid.1"}]}

        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0", "WHATSAPP_DM_POLICY": "open"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", return_value=mock_resp) as mock_post:
                        from gateway.platforms.whatsapp import mesaj_gonder
                        mesaj_gonder("905551234567", "a" * 5000)
                        payload = mock_post.call_args[1]["json"]
                        assert len(payload["text"]["body"]) <= 4096


class TestWhatsAppSendJSON:
    def test_send_message_json_no_requests(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", False):
            from gateway.platforms.whatsapp import send_message_json
            result = send_message_json("90555", {"type": "text"})
            assert result["durum"] == "hata"

    def test_send_message_json_no_token(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value=""):
                from gateway.platforms.whatsapp import send_message_json
                result = send_message_json("90555", {})
                assert result["durum"] == "hata"

    def test_send_message_json_success(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"messages": [{"id": "m1"}]}

        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
                def mock_config(key, default=""):
                    vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0"}
                    return vals.get(key, default)
                with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                    with patch("requests.post", return_value=mock_resp):
                        from gateway.platforms.whatsapp import send_message_json
                        result = send_message_json("90555", {"type": "text", "text": {"body": "test"}})
                        assert result["durum"] == "basarili"


class TestWhatsAppPing:
    def test_ping_no_token(self):
        with patch("gateway.platforms.whatsapp._token_al", return_value=""):
            from gateway.platforms.whatsapp import ping
            assert ping() is False

    def test_ping_no_phone_id(self):
        with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
            with patch("gateway.platforms.whatsapp._config_str", return_value=""):
                from gateway.platforms.whatsapp import ping
                assert ping() is False

    def test_ping_success(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
            def mock_config(key, default=""):
                vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0"}
                return vals.get(key, default)
            with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                with patch("requests.get", return_value=mock_resp):
                    from gateway.platforms.whatsapp import ping
                    assert ping() is True

    def test_ping_error(self):
        with patch("gateway.platforms.whatsapp._token_al", return_value="tok"):
            def mock_config(key, default=""):
                vals = {"WHATSAPP_PHONE_ID": "12345", "WHATSAPP_API_VERSION": "v18.0"}
                return vals.get(key, default)
            with patch("gateway.platforms.whatsapp._config_str", side_effect=mock_config):
                with patch("requests.get", side_effect=Exception("hata")):
                    from gateway.platforms.whatsapp import ping
                    assert ping() is False


class TestWhatsAppAdapter:
    def test_adapter_init(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        adapter = WhatsAppAdapter()
        assert adapter.platform == "whatsapp"

    def test_adapter_connect_success(self):
        with patch("os.environ.get", return_value="exists"):
            from gateway.platforms.whatsapp import WhatsAppAdapter
            adapter = WhatsAppAdapter()
            import asyncio
            result = asyncio.run(adapter.connect())
            assert result is True

    def test_adapter_disconnect(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        adapter = WhatsAppAdapter()
        import asyncio
        asyncio.run(adapter.disconnect())

    def test_adapter_send(self):
        with patch("gateway.platforms.whatsapp.mesaj_gonder", return_value="[WhatsApp]: Mesaj gonderildi (ID: wamid.1)"):
            from gateway.platforms.whatsapp import WhatsAppAdapter
            adapter = WhatsAppAdapter()
            import asyncio
            result = asyncio.run(adapter.send("chat", "content"))
            assert result.success is True


class TestWhatsAppHelpers:
    def test_node_mevcut_no_node(self):
        from gateway.platforms.whatsapp import node_mevcut
        with patch("shutil.which", return_value=None):
            assert node_mevcut() is False

    def test_node_mevcut_error(self):
        from gateway.platforms.whatsapp import node_mevcut
        with patch("shutil.which", return_value="/usr/bin/node"):
            with patch("subprocess.run", side_effect=Exception("hata")):
                assert node_mevcut() is False

    def test_bridge_script_bul_not_found(self):
        from gateway.platforms.whatsapp import bridge_script_bul
        with patch("os.path.isfile", return_value=False):
            result = bridge_script_bul()
            assert result is None

    def test_config_bool_true(self):
        from gateway.platforms.whatsapp import _config_bool
        with patch("os.environ.get", return_value="true"):
            assert _config_bool("TEST") is True
        with patch("os.environ.get", return_value="1"):
            assert _config_bool("TEST") is True
        with patch("os.environ.get", return_value="yes"):
            assert _config_bool("TEST") is True
        with patch("os.environ.get", return_value="on"):
            assert _config_bool("TEST") is True

    def test_config_bool_false(self):
        from gateway.platforms.whatsapp import _config_bool
        with patch("os.environ.get", return_value="false"):
            assert _config_bool("TEST") is False
        with patch("os.environ.get", return_value="0"):
            assert _config_bool("TEST") is False
        with patch("os.environ.get", return_value=""):
            assert _config_bool("TEST") is False


class TestWhatsAppSendMedia:
    def test_send_media_no_requests(self):
        with patch("gateway.platforms.whatsapp._REQUESTS_OK", True):
            with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", False):
                from gateway.platforms.whatsapp import send_media
                result = send_media("90555", "/path/img.jpg")
                assert "requests" in result or "yuklenemedi" in result
