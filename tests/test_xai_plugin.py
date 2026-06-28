# -*- coding: utf-8 -*-
"""tests/test_xai_plugin.py — XAIPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.xai_plugin import XAIPlugin
from providers.plugin_base import ProviderPlugin

class TestXAIPlugin:
    def test_import(self): assert issubclass(XAIPlugin, ProviderPlugin)
    def test_provider_adi(self): assert XAIPlugin().provider_adi == "xai"
    def test_base_url(self): assert XAIPlugin().base_url == "https://api.x.ai"
    def test_base_url_custom(self): assert XAIPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert XAIPlugin().api_key_schema[0]["key"] == "XAI_API_KEY"
    def test_modeller(self): assert "grok" in XAIPlugin().modeller[0]
    def test_ping_no_key(self): ok, _ = XAIPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = XAIPlugin().test(); assert ok is False
    def test_init_api_key(self): assert XAIPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "XAIPlugin" in repr(XAIPlugin())
    def test_ping_tuple_types(self):
        ok, msg = XAIPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = XAIPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
