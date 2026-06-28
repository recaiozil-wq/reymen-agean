# -*- coding: utf-8 -*-
"""tests/test_fireworks_plugin.py — FireworksPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.fireworks_plugin import FireworksPlugin
from providers.plugin_base import ProviderPlugin

class TestFireworksPlugin:
    def test_import(self): assert issubclass(FireworksPlugin, ProviderPlugin)
    def test_provider_adi(self): assert FireworksPlugin().provider_adi == "fireworks"
    def test_base_url(self): assert FireworksPlugin().base_url == "https://api.fireworks.ai"
    def test_base_url_custom(self): assert FireworksPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert FireworksPlugin().api_key_schema[0]["key"] == "FIREWORKS_API_KEY"
    def test_modeller(self): assert len(FireworksPlugin().modeller) > 0
    def test_ping_no_key(self): ok, _ = FireworksPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = FireworksPlugin().test(); assert ok is False
    def test_init_api_key(self): assert FireworksPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "FireworksPlugin" in repr(FireworksPlugin())
    def test_ping_tuple_types(self):
        ok, msg = FireworksPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = FireworksPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
