# -*- coding: utf-8 -*-
"""tests/test_perplexity_plugin.py — PerplexityPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.perplexity_plugin import PerplexityPlugin
from providers.plugin_base import ProviderPlugin

class TestPerplexityPlugin:
    def test_import(self): assert issubclass(PerplexityPlugin, ProviderPlugin)
    def test_provider_adi(self): assert PerplexityPlugin().provider_adi == "perplexity"
    def test_base_url(self): assert PerplexityPlugin().base_url == "https://api.perplexity.ai"
    def test_base_url_custom(self): assert PerplexityPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert PerplexityPlugin().api_key_schema[0]["key"] == "PERPLEXITY_API_KEY"
    def test_modeller(self): assert "sonar" in PerplexityPlugin().modeller[0]
    def test_ping_no_key(self): ok, _ = PerplexityPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = PerplexityPlugin().test(); assert ok is False
    def test_init_api_key(self): assert PerplexityPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "PerplexityPlugin" in repr(PerplexityPlugin())
    def test_ping_tuple_types(self):
        ok, msg = PerplexityPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = PerplexityPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
