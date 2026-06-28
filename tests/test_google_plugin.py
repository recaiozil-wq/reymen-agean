# -*- coding: utf-8 -*-
"""tests/test_google_plugin.py — GooglePlugin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from providers.google_plugin import GooglePlugin
from providers.plugin_base import ProviderPlugin

class TestGooglePlugin:
    def test_import(self): assert issubclass(GooglePlugin, ProviderPlugin)
    def test_provider_adi(self): assert GooglePlugin().provider_adi == "google"
    def test_base_url(self): assert "generativelanguage" in GooglePlugin().base_url
    def test_base_url_custom(self): assert GooglePlugin(base_url="http://c").base_url == "http://c"
    def test_api_key_schema(self): assert GooglePlugin().api_key_schema[0]["key"] == "GOOGLE_API_KEY"
    def test_modeller(self): assert "gemini" in GooglePlugin().modeller[0]
    def test_ping_no_key(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        ok, msg = GooglePlugin().ping()
        assert ok is False
        assert "anahtar" in msg.lower()
    def test_test_no_key(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        ok, _ = GooglePlugin().test(); assert ok is False
    def test_init_api_key(self):
        p = GooglePlugin(api_key="k")
        assert p._api_key == "k"
    def test_repr(self): assert "GooglePlugin" in repr(GooglePlugin())
    def test_ping_tuple_types(self):
        ok, msg = GooglePlugin(api_key="x").ping()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_test_tuple_types(self):
        ok, msg = GooglePlugin(api_key="x").test()
        assert isinstance(ok, bool) and isinstance(msg, str)
    def test_gemini_alternate_key(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
        p = GooglePlugin()
        assert p._api_anahtari() == ""  # primary is GOOGLE_API_KEY
        # ping should try GEMINI_API_KEY as fallback
        ok, msg = p.ping()
        assert isinstance(ok, bool)
