# -*- coding: utf-8 -*-
"""tests/test_groq_plugin.py — GroqPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.groq_plugin import GroqPlugin
from providers.plugin_base import ProviderPlugin

class TestGroqPlugin:
    def test_import(self): assert issubclass(GroqPlugin, ProviderPlugin)
    def test_provider_adi(self): assert GroqPlugin().provider_adi == "groq"
    def test_base_url(self): assert GroqPlugin().base_url == "https://api.groq.com"
    def test_base_url_custom(self): assert GroqPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert GroqPlugin().api_key_schema[0]["key"] == "GROQ_API_KEY"
    def test_modeller(self): assert "llama" in GroqPlugin().modeller[0]
    def test_ping_no_key(self): ok, _ = GroqPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = GroqPlugin().test(); assert ok is False
    def test_init_api_key(self): assert GroqPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "GroqPlugin" in repr(GroqPlugin())
    def test_ping_tuple_types(self):
        ok, msg = GroqPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = GroqPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
