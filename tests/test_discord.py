# -*- coding: utf-8 -*-
"""gateway/platforms/discord.py testleri."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestDiscordModule:
    def test_mesaj_gonder_alias(self):
        from gateway.platforms.discord import mesaj_gonder, send_message

        # mesaj_gonder calls send_message internally
        result = mesaj_gonder("123", "test")
        assert isinstance(result, dict)

    def test_send_message_no_requests(self):
        with patch("gateway.platforms.discord._REQUESTS_OK", False):
            from gateway.platforms.discord import send_message

            result = send_message("123", "test")
            assert result["durum"] == "hata"
            assert "requests" in result["hata"]

    def test_send_message_no_token(self):
        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value=""):
                from gateway.platforms.discord import send_message

                result = send_message("123", "test")
                assert result["durum"] == "hata"
                assert "DISCORD_BOT_TOKEN" in result["hata"]

    def test_send_message_token_truncated(self):
        from gateway.platforms.discord import send_message

        assert send_message("123", "test")["durum"] == "hata"  # no token is hata

    def test_send_message_200(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "msg123"}

        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch(
                "gateway.platforms.discord._token_al", return_value="valid_token"
            ):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.discord import send_message

                    result = send_message("123", "merhaba")
                    assert result["durum"] == "basarili"
                    assert result["mesaj_id"] == "msg123"
                    mock_post.assert_called_once()

    def test_send_message_truncates_long(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "m1"}

        long_msg = "a" * 5000
        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.discord import send_message

                    result = send_message("123", long_msg)
                    assert result["durum"] == "basarili"
                    sent_payload = mock_post.call_args[1]["json"]
                    assert len(sent_payload["content"]) <= 2000

    def test_send_message_http_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.discord import send_message

                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "403" in result["hata"]

    def test_send_message_timeout(self):
        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch(
                    "requests.post",
                    side_effect=__import__("requests").exceptions.Timeout("timeout"),
                ):
                    from gateway.platforms.discord import send_message

                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "Zaman asimi" in result["hata"]

    def test_send_message_exception(self):
        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", side_effect=Exception("baska hata")):
                    from gateway.platforms.discord import send_message

                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "baska hata" in result["hata"]

    def test_send_message_with_tts(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "m1"}

        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.discord import send_message

                    send_message("123", "test", tts=True)
                    assert mock_post.call_args[1]["json"]["tts"] is True

    def test_send_message_with_reply_to(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "m1"}

        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.discord import send_message

                    send_message("123", "test", reply_to="orig_id")
                    payload = mock_post.call_args[1]["json"]
                    assert payload["message_reference"]["message_id"] == "orig_id"

    def test_send_message_with_embeds(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "m1"}

        with patch("gateway.platforms.discord._REQUESTS_OK", True):
            with patch("gateway.platforms.discord._token_al", return_value="tok"):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.discord import send_message

                    embeds = [{"title": "Test"}]
                    send_message("123", "test", embeds=embeds)
                    assert mock_post.call_args[1]["json"]["embeds"] == embeds

    def test_token_al(self):
        from gateway.platforms.discord import _token_al

        with patch("os.environ.get", return_value="my_token"):
            assert _token_al() == "my_token"

    def test_ping_constant(self):
        from gateway.platforms.discord import _API_BASE

        assert _API_BASE == "https://discord.com/api/v10"

    def test_test_function(self):
        from gateway.platforms.discord import test

        with patch("builtins.print"):
            test()
