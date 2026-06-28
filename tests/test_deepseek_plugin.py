# -*- coding: utf-8 -*-
"""tests/test_deepseek_plugin.py — DeepSeekPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.deepseek_plugin import DeepSeekPlugin
from providers.plugin_base import ProviderPlugin

class TestDeepSeekPlugin:
    def test_import(self): assert issubclass(DeepSeekPlugin, ProviderPlugin)
    def test_provider_adi(self): assert DeepSeekPlugin().provider_adi == "deepseek"
    def test_base_url(self): assert DeepSeekPlugin().base_url == "https://api.deepseek.com"
    def test_base_url_custom(self): assert DeepSeekPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert DeepSeekPlugin().api_key_schema[0]["key"] == "DEEPSEEK_API_KEY"
    def test_modeller(self): assert "deepseek-chat" in DeepSeekPlugin().modeller
    def test_ping_no_key(self): ok, _ = DeepSeekPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = DeepSeekPlugin().test(); assert ok is False
    def test_init_api_key(self): assert DeepSeekPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "DeepSeekPlugin" in repr(DeepSeekPlugin())
    def test_ping_tuple_types(self):
        ok, msg = DeepSeekPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = DeepSeekPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
