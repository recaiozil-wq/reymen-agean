# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp.py testleri — actual API."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

try:
    from gateway.platforms.whatsapp import WhatsAppAdapter
    _GATEWAY_AVAILABLE = True
except (ImportError, TypeError, AttributeError):
    _GATEWAY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _GATEWAY_AVAILABLE,
    reason="gateway.platforms.whatsapp not importable (shim stub active or missing hermes_cli)"
)


class TestWhatsAppAdapter:
    def test_adapter_class_exists(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        assert WhatsAppAdapter is not None

    def test_adapter_inherits_base(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        from gateway.platforms.base import BasePlatformAdapter
        assert issubclass(WhatsAppAdapter, BasePlatformAdapter)

    def test_adapter_requires_config(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        with pytest.raises(TypeError):
            WhatsAppAdapter()

    def test_adapter_init_with_config(self):
        from gateway.platforms.whatsapp import WhatsAppAdapter
        config = MagicMock()
        config.extra = {}
        adapter = WhatsAppAdapter(config=config)
        assert adapter.platform is not None


class TestWhatsAppModule:
    def test_whatsapp_imports(self):
        from gateway.platforms.whatsapp import WhatsAppBehaviorMixin
        assert WhatsAppBehaviorMixin is not None

    def test_check_requirements(self):
        from gateway.platforms.whatsapp import check_whatsapp_requirements
        assert callable(check_whatsapp_requirements)
