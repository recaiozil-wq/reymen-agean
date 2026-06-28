# -*- coding: utf-8 -*-
"""tests/test_openrouter_plugin.py — OpenRouterPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.openrouter_plugin import OpenRouterPlugin
from providers.plugin_base import ProviderPlugin

class TestOpenRouterPlugin:
    def test_import(self): assert issubclass(OpenRouterPlugin, ProviderPlugin)
    def test_provider_adi(self): assert OpenRouterPlugin().provider_adi == "openrouter"
    def test_base_url(self): assert OpenRouterPlugin().base_url == "https://openrouter.ai/api"
    def test_base_url_custom(self): assert OpenRouterPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert OpenRouterPlugin().api_key_schema[0]["key"] == "OPENROUTER_API_KEY"
    def test_modeller(self): assert "openrouter/auto" in OpenRouterPlugin().modeller
    def test_ping_no_key(self): ok, _ = OpenRouterPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = OpenRouterPlugin().test(); assert ok is False
    def test_init_api_key(self): assert OpenRouterPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "OpenRouterPlugin" in repr(OpenRouterPlugin())
    def test_ping_tuple_types(self):
        ok, msg = OpenRouterPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = OpenRouterPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
