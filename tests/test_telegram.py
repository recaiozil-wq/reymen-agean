# -*- coding: utf-8 -*-
"""gateway/platforms/telegram.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestTelegramSendMessage:
    def test_mesaj_gonder_alias(self):
        from gateway.platforms.telegram import mesaj_gonder, send_message
        # mesaj_gonder calls send_message internally
        result = mesaj_gonder("123", "test")
        assert isinstance(result, dict)

    def test_send_message_no_token(self):
        with patch("gateway.platforms.telegram._token_al", return_value=""):
            from gateway.platforms.telegram import send_message
            result = send_message("123", "test")
            assert result["durum"] == "hata"
            assert "TELEGRAM_BOT_TOKEN" in result["hata"]

    def test_send_message_no_requests(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", False):
                from gateway.platforms.telegram import send_message
                result = send_message("123", "test")
                assert result["durum"] == "hata"
                assert "requests" in result["hata"]

    def test_send_message_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "ok": True,
            "result": {"message_id": 42, "chat": {"id": "123"}}
        }

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_message
                    result = send_message("123", "Merhaba")
                    assert result["durum"] == "basarili"
                    assert result["mesaj_id"] == 42
                    mock_post.assert_called_once()

    def test_send_message_api_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "ok": False,
            "error_code": 400,
            "description": "Bad Request: chat not found"
        }

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import send_message
                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "400" in result["hata"]

    def test_send_message_timeout(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", side_effect=__import__("requests").exceptions.Timeout):
                    from gateway.platforms.telegram import send_message
                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "zaman asimi" in result["hata"].lower()

    def test_send_message_connection_error(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", side_effect=__import__("requests").exceptions.ConnectionError):
                    from gateway.platforms.telegram import send_message
                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "baglanti" in result["hata"].lower()

    def test_send_message_exception(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", side_effect=Exception("beklenmeyen")):
                    from gateway.platforms.telegram import send_message
                    result = send_message("123", "test")
                    assert result["durum"] == "hata"
                    assert "beklenmeyen" in result["hata"]

    def test_send_message_truncates_long(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1, "chat": {"id": "123"}}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_message
                    send_message("123", "a" * 5000)
                    payload = mock_post.call_args[1]["json"]
                    assert len(payload["text"]) <= 4096

    def test_send_message_parse_mode(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1, "chat": {"id": "123"}}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_message
                    send_message("123", "text", parse_mode="HTML")
                    assert mock_post.call_args[1]["json"]["parse_mode"] == "HTML"

    def test_send_message_reply_markup(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1, "chat": {"id": "123"}}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_message
                    send_message("123", "text", reply_markup={"inline_keyboard": [[{"text": "Tıkla", "callback_data": "x"}]]})
                    assert "reply_markup" in mock_post.call_args[1]["json"]

    def test_send_message_keyword_args(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1, "chat": {"id": "123"}}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_message
                    send_message("123", "text", disable_web_page_preview=True, disable_notification=True, reply_to_message_id=99)
                    payload = mock_post.call_args[1]["json"]
                    assert payload["disable_web_page_preview"] is True
                    assert payload["disable_notification"] is True
                    assert payload["reply_to_message_id"] == 99


class TestTelegramPhoto:
    def test_send_photo_no_token(self):
        with patch("gateway.platforms.telegram._token_al", return_value=""):
            from gateway.platforms.telegram import send_photo
            result = send_photo("123", "http://foto.jpg")
            assert result["durum"] == "hata"

    def test_send_photo_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 10}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import send_photo
                    result = send_photo("123", "http://foto.jpg", "aciklama")
                    assert result["durum"] == "basarili"
                    payload = mock_post.call_args[1]["json"]
                    assert payload["photo"] == "http://foto.jpg"
                    assert payload["caption"] == "aciklama"

    def test_send_photo_error(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", side_effect=Exception("foto hatasi")):
                    from gateway.platforms.telegram import send_photo
                    result = send_photo("123", "http://foto.jpg")
                    assert result["durum"] == "hata"


class TestTelegramWebhook:
    def test_set_webhook_no_token(self):
        with patch("gateway.platforms.telegram._token_al", return_value=""):
            from gateway.platforms.telegram import set_webhook
            result = set_webhook("https://example.com/webhook")
            assert result["durum"] == "hata"

    def test_set_webhook_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "description": "Webhook was set"}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import set_webhook
                    result = set_webhook("https://example.com/hook", drop_pending_updates=True)
                    assert result["durum"] == "basarili"
                    assert mock_post.call_args[1]["json"]["drop_pending_updates"] is True

    def test_set_webhook_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": False, "description": "Invalid URL"}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import set_webhook
                    result = set_webhook("http://not-https.com")
                    assert result["durum"] == "hata"

    def test_delete_webhook_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import delete_webhook
                    result = delete_webhook()
                    assert result["durum"] == "basarili"

    def test_get_webhook_info_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"url": "https://hook.com"}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.get", return_value=mock_resp):
                    from gateway.platforms.telegram import get_webhook_info
                    result = get_webhook_info()
                    assert result["durum"] == "basarili"
                    assert result["info"]["url"] == "https://hook.com"


class TestTelegramParseMessage:
    def test_parse_message_basic(self):
        from gateway.platforms.telegram import parse_message
        raw = {
            "message": {
                "message_id": 1,
                "text": "Merhaba",
                "chat": {"id": 123, "type": "private"},
                "from": {"id": 456, "first_name": "Ali", "username": "ali"}
            }
        }
        result = parse_message(raw)
        assert result["metin"] == "Merhaba"
        assert result["gonderen"] == "456"
        assert result["platform"] == "telegram"
        assert result["chat_id"] == "123"

    def test_parse_message_edited(self):
        from gateway.platforms.telegram import parse_message
        raw = {
            "edited_message": {
                "message_id": 2,
                "text": "duzeltilmis",
                "chat": {"id": 999, "type": "group"},
                "from": {"id": 111, "first_name": "Veli"}
            }
        }
        result = parse_message(raw)
        assert result["metin"] == "duzeltilmis"
        assert result["chat_id"] == "999"

    def test_parse_message_caption(self):
        from gateway.platforms.telegram import parse_message
        raw = {
            "message": {
                "message_id": 3,
                "caption": "foto aciklamasi",
                "chat": {"id": 1, "type": "private"},
                "from": {"id": 2, "first_name": "A"}
            }
        }
        result = parse_message(raw)
        assert result["metin"] == "foto aciklamasi"

    def test_parse_message_empty(self):
        from gateway.platforms.telegram import parse_message
        result = parse_message({})
        assert result["metin"] == ""
        assert result["gonderen"] == ""
        assert result["platform"] == "telegram"

    def test_parse_message_exception(self):
        from gateway.platforms.telegram import parse_message
        result = parse_message(None)
        assert result["metin"] == ""
        assert result["platform"] == "telegram"


class TestTelegramPing:
    def test_ping_no_token(self):
        with patch("gateway.platforms.telegram._token_al", return_value=""):
            from gateway.platforms.telegram import ping
            assert ping() is False

    def test_ping_success(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.get", return_value=mock_resp):
                    from gateway.platforms.telegram import ping
                    assert ping() is True

    def test_ping_failure(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.get", side_effect=Exception("hata")):
                    from gateway.platforms.telegram import ping
                    assert ping() is False


class TestTelegramEditMessage:
    def test_edit_message_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import edit_message
                    result = edit_message("123", 1, "yeni metin")
                    assert result["durum"] == "basarili"

    def test_edit_message_not_modified(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": False, "description": "message is not modified"}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import edit_message
                    result = edit_message("123", 1, "ayni")
                    assert result["durum"] == "basarili"
                    assert result.get("degismedi") is True

    def test_edit_message_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": False, "description": "message not found"}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp):
                    from gateway.platforms.telegram import edit_message
                    result = edit_message("123", 999, "yeni")
                    assert result["durum"] == "hata"


class TestTelegramSetReaction:
    def test_set_reaction_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("requests.post", return_value=mock_resp) as mock_post:
                    from gateway.platforms.telegram import set_reaction
                    result = set_reaction("123", 1, "👍")
                    assert result["durum"] == "basarili"
                    payload = mock_post.call_args[1]["json"]
                    assert payload["reaction"][0]["emoji"] == "👍"


class TestTelegramSendStream:
    def test_send_stream_short_message(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1, "chat": {"id": "123"}}}

        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("gateway.platforms.telegram.send_message", return_value={"durum": "basarili", "mesaj_id": 1, "chunk_sayisi": 1}):
                    from gateway.platforms.telegram import send_stream
                    result = send_stream("123", "kisa mesaj")
                    assert result["durum"] == "basarili"

    def test_send_stream_long_message(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("gateway.platforms.telegram.send_message", return_value={"durum": "basarili", "mesaj_id": 1}):
                    with patch("gateway.platforms.telegram.edit_message", return_value={"durum": "basarili"}):
                        with patch("time.sleep"):
                            from gateway.platforms.telegram import send_stream
                            result = send_stream("123", "a" * 5000, chunk_size=2000)
                            assert result["durum"] == "basarili"

    def test_send_stream_fails_first_chunk(self):
        with patch("gateway.platforms.telegram._token_al", return_value="tok"):
            with patch("gateway.platforms.telegram._REQUESTS_OK", True):
                with patch("gateway.platforms.telegram.send_message", return_value={"durum": "hata"}):
                    from gateway.platforms.telegram import send_stream
                    result = send_stream("123", "a" * 5000)
                    assert result["durum"] == "hata"


class TestTelegramAdapter:
    def test_adapter_init(self):
        from gateway.platforms.telegram import TelegramAdapter
        adapter = TelegramAdapter()
        assert adapter.platform == "telegram"

    def test_adapter_init_with_config(self):
        from gateway.platforms.telegram import TelegramAdapter
        config = MagicMock()
        config.extra = {}
        adapter = TelegramAdapter(config=config)
        assert adapter.platform == "telegram"

    def test_adapter_compile_patterns_no_bot(self):
        from gateway.platforms.telegram import TelegramAdapter
        adapter = TelegramAdapter()
        patterns = adapter._compile_mention_patterns()
        assert patterns == []

    def test_adapter_telegram_allowed_chats(self):
        from gateway.platforms.telegram import TelegramAdapter
        adapter = TelegramAdapter()
        assert adapter._telegram_allowed_chats() == set()

    def test_adapter_allowed_chats_from_list(self):
        from gateway.platforms.telegram import TelegramAdapter
        config = MagicMock()
        config.extra = {"allowed_chats": ["123", "456"]}
        adapter = TelegramAdapter(config=config)
        result = adapter._telegram_allowed_chats()
        assert result == {"123", "456"}
