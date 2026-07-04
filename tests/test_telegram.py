# -*- coding: utf-8 -*-
"""gateway/platforms/telegram.py testleri — actual API."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

try:
    from gateway.platforms.telegram import TelegramAdapter
    _GATEWAY_AVAILABLE = True
except (ImportError, TypeError, AttributeError):
    _GATEWAY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _GATEWAY_AVAILABLE,
    reason="gateway.platforms.telegram not importable (shim stub active or missing hermes_cli)"
)


class TestTelegramAdapter:
    def test_adapter_class_exists(self):
        from gateway.platforms.telegram import TelegramAdapter
        assert TelegramAdapter is not None

    def test_adapter_inherits_base(self):
        from gateway.platforms.telegram import TelegramAdapter
        from gateway.platforms.base import BasePlatformAdapter
        assert issubclass(TelegramAdapter, BasePlatformAdapter)

    def test_adapter_requires_config(self):
        from gateway.platforms.telegram import TelegramAdapter
        with pytest.raises(TypeError):
            TelegramAdapter()

    def test_adapter_init_with_config(self):
        from gateway.platforms.telegram import TelegramAdapter
        config = MagicMock()
        config.extra = {}
        adapter = TelegramAdapter(config=config)
        assert adapter.platform is not None

    def test_adapter_allowed_chats_empty(self):
        from gateway.platforms.telegram import TelegramAdapter
        config = MagicMock()
        config.extra = {}
        adapter = TelegramAdapter(config=config)
        result = adapter._telegram_allowed_chats()
        assert result == set()

    def test_adapter_allowed_chats_from_list(self):
        from gateway.platforms.telegram import TelegramAdapter
        config = MagicMock()
        config.extra = {"allowed_chats": ["123", "456"]}
        adapter = TelegramAdapter(config=config)
        result = adapter._telegram_allowed_chats()
        assert result == {"123", "456"}


class TestTelegramModule:
    def test_telegram_available(self):
        from gateway.platforms.telegram import TELEGRAM_AVAILABLE
        assert isinstance(TELEGRAM_AVAILABLE, bool)

    def test_telegram_check_requirements(self):
        from gateway.platforms.telegram import check_telegram_requirements
        assert callable(check_telegram_requirements)
