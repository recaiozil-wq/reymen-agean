# -*- coding: utf-8 -*-
"""tests/test_anthropic_plugin.py — AnthropicPlugin birim testleri."""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

import pytest
from providers.anthropic_plugin import AnthropicPlugin
from providers.plugin_base import ProviderPlugin


class TestAnthropicPlugin:
    def test_import(self):
        assert AnthropicPlugin is not None
        assert issubclass(AnthropicPlugin, ProviderPlugin)

    def test_provider_adi(self):
        p = AnthropicPlugin()
        assert p.provider_adi == "anthropic"

    def test_base_url(self):
        p = AnthropicPlugin()
        assert p.base_url == "https://api.anthropic.com"

    def test_base_url_custom(self):
        p = AnthropicPlugin(base_url="https://custom.anthropic.com")
        assert p.base_url == "https://custom.anthropic.com"

    def test_api_key_schema(self):
        p = AnthropicPlugin()
        schema = p.api_key_schema
        assert isinstance(schema, list)
        assert len(schema) > 0
        assert schema[0]["key"] == "ANTHROPIC_API_KEY"

    def test_modeller(self):
        p = AnthropicPlugin()
        models = p.modeller
        assert isinstance(models, list)
        assert len(models) > 0
        assert "claude-sonnet-4-5" in models

    def test_ping_no_key(self):
        p = AnthropicPlugin()
        ok, msg = p.ping()
        assert ok is False
        assert "anahtar" in msg.lower() or "API" in msg

    def test_test_no_key(self):
        p = AnthropicPlugin()
        ok, msg = p.test()
        assert ok is False
        assert isinstance(msg, str)

    def test_init_with_api_key(self):
        p = AnthropicPlugin(api_key="test-key-123")
        assert p._api_key == "test-key-123"

    def test_repr(self):
        p = AnthropicPlugin()
        r = repr(p)
        assert "AnthropicPlugin" in r
        assert "anthropic" in r

    def test_ping_with_key_returns_bool_tuple(self):
        p = AnthropicPlugin(api_key="fake-key-for-testing")
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    def test_test_returns_bool_tuple(self):
        p = AnthropicPlugin(api_key="fake-key-for-testing")
        ok, msg = p.test()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    def test_api_key_schema_structure(self):
        p = AnthropicPlugin()
        schema = p.api_key_schema[0]
        assert "key" in schema
        assert "label" in schema
        assert isinstance(schema["key"], str)
        assert isinstance(schema["label"], str)
