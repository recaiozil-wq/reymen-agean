# -*- coding: utf-8 -*-
"""tests/test_openai_plugin.py — OpenAIPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.openai_plugin import OpenAIPlugin
from providers.plugin_base import ProviderPlugin

class TestOpenAIPlugin:
    def test_import(self): assert issubclass(OpenAIPlugin, ProviderPlugin)
    def test_provider_adi(self): assert OpenAIPlugin().provider_adi == "openai"
    def test_base_url(self): assert OpenAIPlugin().base_url == "https://api.openai.com"
    def test_base_url_custom(self): assert OpenAIPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert OpenAIPlugin().api_key_schema[0]["key"] == "OPENAI_API_KEY"
    def test_modeller(self): assert "gpt-4o" in OpenAIPlugin().modeller
    def test_ping_no_key(self): ok, _ = OpenAIPlugin().ping(); assert ok is False
    def test_test_no_key(self): ok, _ = OpenAIPlugin().test(); assert ok is False
    def test_init_api_key(self): assert OpenAIPlugin(api_key="k")._api_key == "k"
    def test_repr(self): assert "OpenAIPlugin" in repr(OpenAIPlugin())
    def test_ping_tuple_types(self):
        ok, msg = OpenAIPlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = OpenAIPlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
