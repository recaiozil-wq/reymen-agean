# -*- coding: utf-8 -*-
"""gateway/platforms/base.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestPlatformBase:
    def test_abstract_class_cannot_instantiate(self):
        from gateway.platforms.base import PlatformBase
        with pytest.raises(TypeError):
            PlatformBase()

    def test_abstract_methods_defined(self):
        from gateway.platforms.base import PlatformBase
        import abc
        methods = ["send_message", "ping", "parse_message"]
        for m in methods:
            assert hasattr(PlatformBase, m)
            # Check if method is abstract via metaclass registry
            assert m in PlatformBase.__abstractmethods__


class TestModuleFunctions:
    def test_send_message_returns_error(self):
        from gateway.platforms.base import send_message
        result = send_message("hedef", "test")
        assert result["durum"] == "hata"
        assert "Platform secilmedi" in result["hata"]

    def test_ping_returns_false(self):
        from gateway.platforms.base import ping
        assert ping() is False

    def test_parse_message_returns_default(self):
        from gateway.platforms.base import parse_message
        result = parse_message({})
        assert result["gonderen"] == ""
        assert result["metin"] == ""
        assert result["platform"] == "bilinmiyor"


class TestSendResult:
    def test_default_values(self):
        from gateway.platforms.base import SendResult
        sr = SendResult()
        assert sr.success is True
        assert sr.message_id is None
        assert sr.error is None
        assert sr.raw_response == {}

    def test_custom_values(self):
        from gateway.platforms.base import SendResult
        sr = SendResult(success=False, error="hata", message_id="123", raw_response={"key": "val"})
        assert sr.success is False
        assert sr.error == "hata"
        assert sr.message_id == "123"
        assert sr.raw_response == {"key": "val"}


class TestMessageEvent:
    def test_default_values(self):
        from gateway.platforms.base import MessageEvent, MessageType
        ev = MessageEvent()
        assert ev.message_id == ""
        assert ev.text == ""
        assert ev.message_type == MessageType.TEXT
        assert ev.platform == ""

    def test_custom_values(self):
        from gateway.platforms.base import MessageEvent, MessageType
        ev = MessageEvent(message_id="m1", chat_id="c1", text="merhaba",
                          platform="test", message_type=MessageType.PHOTO)
        assert ev.message_id == "m1"
        assert ev.chat_id == "c1"
        assert ev.text == "merhaba"
        assert ev.platform == "test"
        assert ev.message_type == MessageType.PHOTO


class TestBasePlatformAdapter:
    def test_instance_creation(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        assert adapter._yetki is None

    def test_extract_media_empty(self):
        from gateway.platforms.base import BasePlatformAdapter
        media, cleaned = BasePlatformAdapter.extract_media("")
        assert media == []
        assert cleaned == ""

    def test_extract_media_no_tags(self):
        from gateway.platforms.base import BasePlatformAdapter
        media, cleaned = BasePlatformAdapter.extract_media("sadece metin")
        assert media == []
        assert "sadece metin" in cleaned

    def test_extract_media_with_tags(self):
        from gateway.platforms.base import BasePlatformAdapter
        content = "biraz metin\nMEDIA:/tmp/foto.png\ndaha fazla"
        media, cleaned = BasePlatformAdapter.extract_media(content)
        assert len(media) == 1
        assert media[0][0] == "/tmp/foto.png"
        assert "MEDIA:" not in cleaned

    def test_extract_media_with_voice_marker(self):
        from gateway.platforms.base import BasePlatformAdapter
        content = "ses mesaji\n[[audio_as_voice]]\nMEDIA:/tmp/ses.ogg"
        media, cleaned = BasePlatformAdapter.extract_media(content)
        assert len(media) == 1
        assert media[0][1] is True  # is_voice
        assert "[[audio_as_voice]]" not in cleaned

    def test_filter_media_delivery_paths_empty(self):
        from gateway.platforms.base import BasePlatformAdapter
        result = BasePlatformAdapter.filter_media_delivery_paths([])
        assert result == []

    def test_truncate_message_short(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        chunks = adapter.truncate_message("kisa", 10)
        assert chunks == ["kisa"]

    def test_truncate_message_long(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        text = "satir1\nsatir2\nsatir3\nsatir4"
        chunks = adapter.truncate_message(text, 10)
        assert len(chunks) >= 2
        # Verify all content is preserved
        reconstructed = "".join(chunks).replace("\n", "")
        assert reconstructed == text.replace("\n", "")

    def test_message_len_fn_default(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        assert adapter.message_len_fn == len

    def test_max_message_length_default(self):
        from gateway.platforms.base import BasePlatformAdapter
        assert BasePlatformAdapter.MAX_MESSAGE_LENGTH == 4096

    def test_supports_draft_streaming_default(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        assert adapter.supports_draft_streaming() is False

    def test_format_tool_event_preview(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        class FakeEvent:
            tool_name = "test_tool"
            preview = "calisiyor"
            args = None
        result = adapter.format_tool_event(FakeEvent(), mode="preview")
        assert "test_tool" in result
        assert "calisiyor" in result

    def test_format_tool_event_verbose(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        class FakeEvent:
            tool_name = "hesapla"
            preview = None
            args = {"a": "1", "b": "2"}
        result = adapter.format_tool_event(FakeEvent(), mode="verbose", preview_max_len=40)
        assert "hesapla" in result
        assert "a=1" in result

    def test_render_message_event_chunk(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        from gateway.stream_events import MessageChunk
        event = MessageChunk(text="merhaba")
        sink = MagicMock()
        adapter.render_message_event(event, sink)
        sink.on_delta.assert_called_once_with("merhaba")

    def test_render_message_event_stop_final(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        from gateway.stream_events import MessageStop
        event = MessageStop(final=True)
        sink = MagicMock()
        adapter.render_message_event(event, sink)
        sink.finish.assert_called_once()

    def test_edit_message_not_implemented(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        with pytest.raises(NotImplementedError):
            import asyncio
            asyncio.run(adapter.edit_message("c", "m", "c"))

    def test_send_draft_default(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        import asyncio
        result = asyncio.run(adapter.send_draft("c", "d", "c"))
        assert result.success is False

    def test_delete_message_default(self):
        from gateway.platforms.base import BasePlatformAdapter
        adapter = BasePlatformAdapter()
        import asyncio
        result = asyncio.run(adapter.delete_message("c", "m"))
        assert result is False


class TestHelpers:
    def test_should_send_media_as_audio(self):
        from gateway.platforms.base import should_send_media_as_audio
        assert should_send_media_as_audio("telegram", ".mp3") is True
        assert should_send_media_as_audio("telegram", ".png") is False
        assert should_send_media_as_audio("telegram", ".ogg") is True

    def test_session_source_default(self):
        from gateway.platforms.base import SessionSource
        ss = SessionSource()
        assert ss.platform == ""
        assert ss.session_id == ""

    def test_ephemeral_reply_default(self):
        from gateway.platforms.base import EphemeralReply
        er = EphemeralReply(content="test")
        assert er.content == "test"

    def test_processing_outcome_default(self):
        from gateway.platforms.base import ProcessingOutcome
        po = ProcessingOutcome()
        assert po.status == "ok"
        assert po.data == {}

    def test_message_deduplicator(self):
        from gateway.platforms.base import MessageDeduplicator
        md = MessageDeduplicator()
        assert md.is_duplicate("mesaj1") is False
        assert md.is_duplicate("mesaj1") is True
        assert md.is_duplicate("mesaj2") is False

    def test_build_session_key(self):
        from gateway.platforms.base import build_session_key
        assert build_session_key("whatsapp", "90555") == "whatsapp:90555"
        assert build_session_key("telegram", "123", "456") == "telegram:123:456"

    def test_resolve_proxy_url(self):
        from gateway.platforms.base import resolve_proxy_url
        with patch("os.environ.get", return_value="http://proxy:8080"):
            assert resolve_proxy_url() == "http://proxy:8080"

    def test_message_type_enum_values(self):
        from gateway.platforms.base import MessageType
        assert MessageType.TEXT.value == "text"
        assert MessageType.PHOTO.value == "photo"
        assert MessageType.VOICE.value == "voice"
        assert MessageType.STICKER.value == "sticker"

    def test_merge_pending_message_event(self):
        from gateway.platforms.base import MessageEvent, merge_pending_message_event
        base = MessageEvent(message_id="m1", text="eski")
        update = MessageEvent(text="yeni", platform="test")
        merged = merge_pending_message_event(base, update)
        assert merged.message_id == "m1"
        assert merged.text == "yeni"
        assert merged.platform == "test"

    def test_is_network_accessible_loopback(self):
        from gateway.platforms.base import is_network_accessible
        assert is_network_accessible("127.0.0.1") is False

    def test_is_network_accessible_public(self):
        from gateway.platforms.base import is_network_accessible
        assert is_network_accessible("8.8.8.8") is True

    def test_custom_unit_to_cp(self):
        from gateway.platforms.base import _custom_unit_to_cp
        assert _custom_unit_to_cp("60sec") == 60
        assert _custom_unit_to_cp("1min") == 60
        assert _custom_unit_to_cp("1h") == 3600

    def test_supported_types_sets(self):
        from gateway.platforms.base import SUPPORTED_VIDEO_TYPES, SUPPORTED_AUDIO_TYPES, SUPPORTED_DOCUMENT_TYPES
        assert "video/mp4" in SUPPORTED_VIDEO_TYPES
        assert "audio/mpeg" in SUPPORTED_AUDIO_TYPES
        assert "application/pdf" in SUPPORTED_DOCUMENT_TYPES
