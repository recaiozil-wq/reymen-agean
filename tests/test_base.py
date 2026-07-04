# -*- coding: utf-8 -*-
"""gateway/platforms/base.py testleri — actual API."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

# Skip all tests if gateway module can't be properly imported (conftest_shim stub)
try:
    from gateway.platforms.base import SendResult, MessageEvent, MessageType
    _GATEWAY_AVAILABLE = True
except (ImportError, TypeError, AttributeError):
    _GATEWAY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _GATEWAY_AVAILABLE,
    reason="gateway.platforms.base not importable (shim stub active or missing hermes_cli)"
)


class TestSendResult:
    def test_required_success(self):
        from gateway.platforms.base import SendResult

        sr = SendResult(success=True)
        assert sr.success is True
        assert sr.message_id is None
        assert sr.error is None

    def test_custom_values(self):
        from gateway.platforms.base import SendResult

        sr = SendResult(
            success=False, error="hata", message_id="123", raw_response={"key": "val"}
        )
        assert sr.success is False
        assert sr.error == "hata"
        assert sr.message_id == "123"
        assert sr.raw_response == {"key": "val"}

    def test_retryable(self):
        from gateway.platforms.base import SendResult

        sr = SendResult(success=False, error="timeout", retryable=True)
        assert sr.retryable is True


class TestMessageEvent:
    def test_required_text(self):
        from gateway.platforms.base import MessageEvent, MessageType

        ev = MessageEvent(text="merhaba")
        assert ev.text == "merhaba"
        assert ev.message_type == MessageType.TEXT

    def test_custom_values(self):
        from gateway.platforms.base import MessageEvent, MessageType

        ev = MessageEvent(
            text="merhaba",
            message_type=MessageType.TEXT,
            message_id="m1",
        )
        assert ev.message_id == "m1"
        assert ev.text == "merhaba"

    def test_message_type_enum_values(self):
        from gateway.platforms.base import MessageType

        assert MessageType.TEXT.value == "text"
        assert MessageType.PHOTO.value == "photo"
        assert MessageType.VOICE.value == "voice"
        assert MessageType.STICKER.value == "sticker"


class TestBasePlatformAdapter:
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
        assert media[0][1] is True
        assert "[[audio_as_voice]]" not in cleaned

    def test_filter_media_delivery_paths_empty(self):
        from gateway.platforms.base import BasePlatformAdapter

        result = BasePlatformAdapter.filter_media_delivery_paths([])
        assert result == []


class TestHelpers:
    def test_should_send_media_as_audio(self):
        from gateway.platforms.base import should_send_media_as_audio

        assert should_send_media_as_audio("telegram", ".mp3") is True
        assert should_send_media_as_audio("telegram", ".png") is False
        assert should_send_media_as_audio("telegram", ".ogg") is False

    def test_build_session_key(self):
        from gateway.platforms.base import build_session_key, SessionSource, Platform

        source = SessionSource(platform=Platform.WHATSAPP, chat_id="90555")
        result = build_session_key(source)
        assert isinstance(result, str)
        assert "whatsapp" in result

    def test_is_network_accessible_loopback(self):
        from gateway.platforms.base import is_network_accessible

        assert is_network_accessible("127.0.0.1") is False

    def test_is_network_accessible_public(self):
        from gateway.platforms.base import is_network_accessible

        assert is_network_accessible("8.8.8.8") is True

    def test_custom_unit_to_cp(self):
        from gateway.platforms.base import _custom_unit_to_cp

        result = _custom_unit_to_cp("60sec", 1000, len)
        assert isinstance(result, int)
        assert result > 0

    def test_supported_types_sets(self):
        from gateway.platforms.base import (
            SUPPORTED_VIDEO_TYPES,
            SUPPORTED_DOCUMENT_TYPES,
        )

        assert ".mp4" in SUPPORTED_VIDEO_TYPES
        assert ".pdf" in SUPPORTED_DOCUMENT_TYPES

    def test_merge_pending_message_event(self):
        from gateway.platforms.base import MessageEvent, merge_pending_message_event

        base = MessageEvent(text="eski", message_id="m1")
        update = MessageEvent(text="yeni")
        pending = {"session1": base}
        merge_pending_message_event(pending, "session1", update)
        assert pending["session1"].text == "yeni"
