# -*- coding: utf-8 -*-
"""tests/test_together_plugin.py — TogetherPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.together_plugin import TogetherPlugin
from providers.plugin_base import ProviderPlugin

class TestTogetherPlugin:
    def test_import(self): assert issubclass(TogetherPlugin, ProviderPlugin)
    def test_provider_adi(self): assert TogetherPlugin().provider_adi == "together"
    def test_base_url(self): assert TogetherPlugin().base_url == "https://api.together.xyz"
    def test_base_url_custom(self): assert TogetherPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert TogetherPlugin().api_key_schema[0]["key"] == "TOGETHER_API_KEY"
    def test_modeller(self): assert "Llama" in TogetherPlugin().modeller[0]
    def test_ping_no_key(self): ok, _ = TogetherPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = TogetherPlugin().test(); assert ok is False
    def test_init_api_key(self): assert TogetherPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "TogetherPlugin" in repr(TogetherPlugin())
    def test_ping_tuple_types(self):
        ok, msg = TogetherPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = TogetherPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
