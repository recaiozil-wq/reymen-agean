# -*- coding: utf-8 -*-
"""tests/test_cohere_plugin.py — CoherePlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.cohere_plugin import CoherePlugin
from providers.plugin_base import ProviderPlugin

class TestCoherePlugin:
    def test_import(self):
        assert issubclass(CoherePlugin, ProviderPlugin)
    def test_provider_adi(self): assert CoherePlugin().provider_adi == "cohere"
    def test_base_url(self): assert CoherePlugin().base_url == "https://api.cohere.ai"
    def test_base_url_custom(self): assert CoherePlugin(base_url="http://custom").base_url == "http://custom"
    def test_api_key_schema(self):
        s = CoherePlugin().api_key_schema
        assert s[0]["key"] == "COHERE_API_KEY"
    def test_modeller(self):
        m = CoherePlugin().modeller
        assert "command-r" in m
    def test_ping_no_key(self):
        ok, _ = CoherePlugin().ping()
        assert ok is False
    def test_test_no_key(self):
        ok, _ = CoherePlugin().test()
        assert ok is False
    def test_init_api_key(self):
        p = CoherePlugin(api_key="k")
        assert p._api_key == "k"
    def test_repr(self):
        assert "CoherePlugin" in repr(CoherePlugin())
    def test_ping_tuple_types(self):
        ok, msg = CoherePlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = CoherePlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
