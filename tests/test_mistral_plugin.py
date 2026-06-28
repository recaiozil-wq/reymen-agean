# -*- coding: utf-8 -*-
"""tests/test_mistral_plugin.py — MistralPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.mistral_plugin import MistralPlugin
from providers.plugin_base import ProviderPlugin

class TestMistralPlugin:
    def test_import(self): assert issubclass(MistralPlugin, ProviderPlugin)
    def test_provider_adi(self): assert MistralPlugin().provider_adi == "mistral"
    def test_base_url(self): assert MistralPlugin().base_url == "https://api.mistral.ai"
    def test_base_url_custom(self): assert MistralPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert MistralPlugin().api_key_schema[0]["key"] == "MISTRAL_API_KEY"
    def test_modeller(self): assert "mistral" in MistralPlugin().modeller[0]
    def test_ping_no_key(self): ok, _ = MistralPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = MistralPlugin().test(); assert ok is False
    def test_init_api_key(self): assert MistralPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "MistralPlugin" in repr(MistralPlugin())
    def test_ping_tuple_types(self):
        ok, msg = MistralPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = MistralPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
