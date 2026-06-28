# -*- coding: utf-8 -*-
"""tests/test_lmstudio_plugin.py — LMStudioPlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.lmstudio_plugin import LMStudioPlugin
from providers.plugin_base import ProviderPlugin

class TestLMStudioPlugin:
    def test_import(self): assert issubclass(LMStudioPlugin, ProviderPlugin)
    def test_provider_adi(self): assert LMStudioPlugin().provider_adi == "lmstudio"
    def test_base_url(self): assert "localhost" in LMStudioPlugin().base_url
    def test_base_url_custom(self): assert LMStudioPlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema_empty(self): assert LMStudioPlugin().api_key_schema == []
    def test_modeller(self): assert len(LMStudioPlugin().modeller) > 0
    def test_ping_local(self):
        ok, msg = LMStudioPlugin().ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_local(self):
        ok, msg = LMStudioPlugin().test()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_init_api_key(self):
        p = LMStudioPlugin(api_key="k")
        assert p._api_key == "k"
    def test_repr(self): assert "LMStudioPlugin" in repr(LMStudioPlugin())
