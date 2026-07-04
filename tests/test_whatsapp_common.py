# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp_common.py testleri — actual API."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

try:
    from gateway.platforms.whatsapp_common import WhatsAppBehaviorMixin
    _GATEWAY_AVAILABLE = True
except (ImportError, TypeError, AttributeError):
    _GATEWAY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _GATEWAY_AVAILABLE,
    reason="gateway.platforms.whatsapp_common not importable (shim stub active or missing hermes_cli)"
)


class TestWhatsAppCommonModule:
    def test_whatsapp_behavior_mixin_import(self):
        from gateway.platforms.whatsapp_common import WhatsAppBehaviorMixin
        assert WhatsAppBehaviorMixin is not None

    def test_whatsapp_behavior_mixin_has_methods(self):
        from gateway.platforms.whatsapp_common import WhatsAppBehaviorMixin
        assert hasattr(WhatsAppBehaviorMixin, "format_message")

    def test_module_has_json(self):
        import gateway.platforms.whatsapp_common as wc
        assert hasattr(wc, "json")

    def test_module_has_re(self):
        import gateway.platforms.whatsapp_common as wc
        assert hasattr(wc, "re")
