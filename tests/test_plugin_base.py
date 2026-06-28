# -*- coding: utf-8 -*-
"""tests/test_plugin_base.py — ProviderPlugin ABC birim testleri."""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

import pytest
from providers.plugin_base import ProviderPlugin, Renk


class TestRenk:
    def test_renk_constants(self):
        assert Renk.MOR != ""
        assert Renk.YESIL != ""
        assert Renk.KIRMIZI != ""
        assert Renk.RESET == "\033[0m"

    def test_renk_bold(self):
        assert Renk.BOLD == "\033[1m"


class TestProviderPlugin:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ProviderPlugin()

    def test_abc_properties(self):
        """Verify all abstract methods exist on the class."""
        import abc
        assert ProviderPlugin.__abstractmethods__ is not None
        assert "provider_adi" in ProviderPlugin.__abstractmethods__
        assert "base_url" in ProviderPlugin.__abstractmethods__
        assert "api_key_schema" in ProviderPlugin.__abstractmethods__
        assert "modeller" in ProviderPlugin.__abstractmethods__
        assert "ping" in ProviderPlugin.__abstractmethods__
        assert "test" in ProviderPlugin.__abstractmethods__

    def test_env_anahtar(self, monkeypatch):
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "test"
            @property
            def base_url(self): return "http://x"
            @property
            def api_key_schema(self): return [{"key": "TEST_KEY"}]
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        monkeypatch.setenv("TEST_KEY", "env_value")
        p = ConcretePlugin()
        result = p._env_anahtar("TEST_KEY")
        assert result == "env_value"

    def test_env_anahtar_missing(self):
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "test"
            @property
            def base_url(self): return "http://x"
            @property
            def api_key_schema(self): return []
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        p = ConcretePlugin()
        result = p._env_anahtar("NONEXISTENT_VAR_XYZ")
        assert result == ""

    def test_api_anahtari_uses_init_key(self):
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "test"
            @property
            def base_url(self): return "http://x"
            @property
            def api_key_schema(self): return [{"key": "ENV_KEY"}]
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        p = ConcretePlugin(api_key="direct-key")
        assert p._api_anahtari() == "direct-key"

    def test_api_anahtari_empty_schema(self):
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "test"
            @property
            def base_url(self): return "http://x"
            @property
            def api_key_schema(self): return []
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        p = ConcretePlugin()
        assert p._api_anahtari() == ""

    def test_http_get_timeout_returns_tuple(self, monkeypatch):
        """_http_get returns (0, str) on timeout/error."""
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "test"
            @property
            def base_url(self): return "http://x"
            @property
            def api_key_schema(self): return []
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        p = ConcretePlugin()
        kod, msg = p._http_get("http://192.0.2.1:1/nonexistent", zaman_asimi=0.1)
        assert kod == 0
        assert isinstance(msg, str)

    def test_repr_concrete(self):
        class ConcretePlugin(ProviderPlugin):
            @property
            def provider_adi(self): return "myprovider"
            @property
            def base_url(self): return "http://my.url"
            @property
            def api_key_schema(self): return []
            @property
            def modeller(self): return []
            def ping(self): return True, "ok"
            def test(self): return True, "ok"

        p = ConcretePlugin()
        r = repr(p)
        assert "ConcretePlugin" in r
        assert "myprovider" in r
        assert "my.url" in r
