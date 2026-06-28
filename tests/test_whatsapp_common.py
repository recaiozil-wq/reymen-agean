# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp_common.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestMesajTemizle:
    def test_empty(self):
        from gateway.platforms.whatsapp_common import mesaj_temizle
        assert mesaj_temizle("") == ""
        assert mesaj_temizle(None) == ""

    def test_strips_html(self):
        from gateway.platforms.whatsapp_common import mesaj_temizle
        result = mesaj_temizle("<b>bold</b> text")
        assert "<b>" not in result
        assert "bold" in result

    def test_strips_markdown_links(self):
        from gateway.platforms.whatsapp_common import mesaj_temizle
        result = mesaj_temizle("[link](http://example.com) here")
        assert "http://" not in result
        assert "link" in result

    def test_collapses_newlines(self):
        from gateway.platforms.whatsapp_common import mesaj_temizle
        result = mesaj_temizle("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_truncates_long(self):
        from gateway.platforms.whatsapp_common import mesaj_temizle
        long = "kelime " * 1000
        result = mesaj_temizle(long, max_uzunluk=100)
        assert len(result) <= 103  # "..." eklenir
        assert result.endswith("...")


class TestFormatMessage:
    def test_empty(self):
        from gateway.platforms.whatsapp_common import format_message
        assert format_message("") == ""
        assert format_message(None) is None

    def test_bold_conversion(self):
        from gateway.platforms.whatsapp_common import format_message
        result = format_message("**bold** text")
        assert "**bold**" not in result
        assert "*bold*" in result

    def test_strikethrough_conversion(self):
        from gateway.platforms.whatsapp_common import format_message
        result = format_message("~~striked~~")
        assert "~~striked~~" not in result
        assert "~striked~" in result

    def test_header_conversion(self):
        from gateway.platforms.whatsapp_common import format_message
        result = format_message("# Baslik")
        assert "*Baslik*" in result

    def test_link_conversion(self):
        from gateway.platforms.whatsapp_common import format_message
        result = format_message("[metin](http://url.com)")
        assert "metin (http://url.com)" in result

    def test_code_block_preserved(self):
        from gateway.platforms.whatsapp_common import format_message
        content = "once\n```\nkod burada\n```\nsonra"
        result = format_message(content)
        assert "```" in result

    def test_inline_code_preserved(self):
        from gateway.platforms.whatsapp_common import format_message
        result = format_message("`kod` burada")
        assert "`kod`" in result


class TestNumaraDogrula:
    def test_valid_numbers(self):
        from gateway.platforms.whatsapp_common import numara_dogrula
        assert numara_dogrula("+905551234567") is True
        assert numara_dogrula("905551234567") is True
        assert numara_dogrula("+1234567890") is True

    def test_invalid_numbers(self):
        from gateway.platforms.whatsapp_common import numara_dogrula
        assert numara_dogrula("") is False
        assert numara_dogrula("abc") is False
        assert numara_dogrula("123") is False  # too short

    def test_normalize(self):
        from gateway.platforms.whatsapp_common import numara_dogrula
        assert numara_dogrula("+90 (555) 123-45-67") is True


class TestNumaraNormalize:
    def test_normalize(self):
        from gateway.platforms.whatsapp_common import numara_normalize
        assert numara_normalize("+90 (555) 123-45-67") == "905551234567"
        assert numara_normalize("") == ""
        assert numara_normalize(None) == ""


class TestJidToWaId:
    def test_jid_extraction(self):
        from gateway.platforms.whatsapp_common import jid_to_wa_id
        assert jid_to_wa_id("90555@s.whatsapp.net") == "90555"
        assert jid_to_wa_id("") == ""
        assert jid_to_wa_id(None) == ""


class TestIsBroadcastChat:
    def test_broadcast_detection(self):
        from gateway.platforms.whatsapp_common import is_broadcast_chat
        assert is_broadcast_chat("status@broadcast") is True
        assert is_broadcast_chat("12345@broadcast") is True
        assert is_broadcast_chat("12345@newsletter") is True
        assert is_broadcast_chat("12345@s.whatsapp.net") is False
        assert is_broadcast_chat("") is False


class TestDMIzinli:
    def test_open_policy(self):
        from gateway.platforms.whatsapp_common import dm_izinli
        assert dm_izinli("90555", "open") is True

    def test_disabled_policy(self):
        from gateway.platforms.whatsapp_common import dm_izinli
        assert dm_izinli("90555", "disabled") is False

    def test_allowlist_match(self):
        from gateway.platforms.whatsapp_common import dm_izinli
        assert dm_izinli("90555", "allowlist", {"90555"}) is True

    def test_allowlist_no_match(self):
        from gateway.platforms.whatsapp_common import dm_izinli
        assert dm_izinli("90555", "allowlist", {"11111"}) is False


class TestGrupIzinli:
    def test_open_policy(self):
        from gateway.platforms.whatsapp_common import grup_izinli
        assert grup_izinli("123", "open") is True

    def test_disabled_policy(self):
        from gateway.platforms.whatsapp_common import grup_izinli
        assert grup_izinli("123", "disabled") is False

    def test_allowlist_match(self):
        from gateway.platforms.whatsapp_common import grup_izinli
        assert grup_izinli("grup_123", "allowlist", {"grup_123"}) is True


class TestMentionPatterns:
    def test_mention_patterns_derle_none(self):
        from gateway.platforms.whatsapp_common import mention_patterns_derle
        assert mention_patterns_derle(None) == []

    def test_mention_patterns_derle_string(self):
        from gateway.platforms.whatsapp_common import mention_patterns_derle
        patterns = mention_patterns_derle(r"test.*pattern")
        assert len(patterns) == 1
        assert patterns[0].search("test_xyz_pattern") is not None

    def test_mention_patterns_derle_invalid_regex(self):
        from gateway.platforms.whatsapp_common import mention_patterns_derle
        patterns = mention_patterns_derle(r"[invalid")
        assert patterns == []

    def test_mesaj_mention_iceriyor_direct(self):
        from gateway.platforms.whatsapp_common import mesaj_mention_iceriyor
        assert mesaj_mention_iceriyor("@bot123 hello", "bot123") is True

    def test_mesaj_mention_iceriyor_no_mention(self):
        from gateway.platforms.whatsapp_common import mesaj_mention_iceriyor
        assert mesaj_mention_iceriyor("just text", "bot123") is False

    def test_mesaj_mention_iceriyor_pattern(self):
        from gateway.platforms.whatsapp_common import mesaj_mention_iceriyor
        patterns = [__import__("re").compile(r"hey_bot", __import__("re").IGNORECASE)]
        assert mesaj_mention_iceriyor("Hey_Bot!", "bot123", patterns) is True

    def test_mesaj_mention_iceriyor_empty_body(self):
        from gateway.platforms.whatsapp_common import mesaj_mention_iceriyor
        assert mesaj_mention_iceriyor("", "bot") is False


class TestMedyaYukle:
    def test_medya_yukle_no_requests(self):
        with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", False):
            from gateway.platforms.whatsapp_common import medya_yukle
            result = medya_yukle("/path/file.jpg")
            assert result["durum"] == "hata"

    def test_medya_yukle_file_not_found(self):
        with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", True):
            with patch("os.path.isfile", return_value=False):
                from gateway.platforms.whatsapp_common import medya_yukle
                result = medya_yukle("/nonexistent.jpg")
                assert result["durum"] == "hata"
                assert "bulunamadi" in result["hata"]

    def test_medya_yukle_no_credentials(self):
        with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", True):
            with patch("os.path.isfile", return_value=True):
                with patch("os.environ.get", return_value=""):
                    from gateway.platforms.whatsapp_common import medya_yukle
                    result = medya_yukle("/path/file.jpg")
                    assert result["durum"] == "hata"

    def test_medya_yukle_success(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "media_123"}

        with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", True):
            with patch("os.path.isfile", return_value=True):
                with patch("os.environ.get", return_value="credential"):
                    with patch("builtins.open", MagicMock()):
                        with patch("requests.post", return_value=mock_resp) as mock_post:
                            from gateway.platforms.whatsapp_common import medya_yukle
                            result = medya_yukle("/path/file.jpg")
                            assert result["durum"] == "basarili"
                            assert result["media_id"] == "media_123"

    def test_medya_yukle_error(self):
        with patch("gateway.platforms.whatsapp_common._REQUESTS_OK", True):
            with patch("os.path.isfile", return_value=True):
                with patch("os.environ.get", return_value="credential"):
                    with patch("builtins.open", MagicMock()):
                        with patch("requests.post", side_effect=Exception("upload failed")):
                            from gateway.platforms.whatsapp_common import medya_yukle
                            result = medya_yukle("/path/file.jpg")
                            assert result["durum"] == "hata"


class TestWhatsAppCommonPing:
    def test_ping(self):
        from gateway.platforms.whatsapp_common import ping
        assert ping() is True
