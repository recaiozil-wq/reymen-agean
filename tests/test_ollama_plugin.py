# -*- coding: utf-8 -*-
"""tests/test_ollama_plugin.py — OllamaPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.ollama_plugin import OllamaPlugin
from providers.plugin_base import ProviderPlugin

class TestOllamaPlugin:
    def test_import(self): assert issubclass(OllamaPlugin, ProviderPlugin)
    def test_provider_adi(self): assert OllamaPlugin().provider_adi == "ollama"
    def test_base_url(self): assert "localhost" in OllamaPlugin().base_url
    def test_base_url_custom(self): assert OllamaPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema_empty(self): assert OllamaPlugin().api_key_schema == []
    def test_modeller(self): assert len(OllamaPlugin().modeller) > 0
    def test_ping_local(self):
        ok, msg = OllamaPlugin().ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_local(self):
        ok, msg = OllamaPlugin().test()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_init_api_key(self):
        p = OllamaPlugin(api_key="k")
        assert p._api_key == "k"
    def test_repr(self): assert "OllamaPlugin" in repr(OllamaPlugin())
