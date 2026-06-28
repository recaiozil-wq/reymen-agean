# -*- coding: utf-8 -*-
"""test_proxy_config.py — ProxyConfig unit testleri."""
from __future__ import annotations

import json
import os

import pytest

from proxy.proxy_config import ProxyConfig


class TestProxyConfigDefaults:
    """ProxyConfig varsayilan deger testleri."""

    def test_default_port(self):
        cfg = ProxyConfig()
        assert cfg.port == 8080

    def test_default_auth(self):
        cfg = ProxyConfig()
        assert cfg.auth is None

    def test_default_whitelist(self):
        cfg = ProxyConfig()
        assert cfg.whitelist == []

    def test_default_upstream(self):
        cfg = ProxyConfig()
        assert cfg.upstream is None

    def test_default_timeout(self):
        cfg = ProxyConfig()
        assert cfg.timeout == 30

    def test_default_ssl(self):
        cfg = ProxyConfig()
        assert cfg.ssl is False

    def test_all_defaults_in_to_dict(self):
        cfg = ProxyConfig()
        d = cfg.to_dict()
        assert d["port"] == 8080
        assert d["auth"] is None
        assert d["whitelist"] == []
        assert d["upstream"] is None
        assert d["timeout"] == 30
        assert d["ssl"] is False
        assert len(d) == 6


class TestProxyConfigFromJSON:
    """JSON dosyasindan yukleme testleri."""

    def test_load_from_json(self, tmp_path):
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text(json.dumps({
            "port": 9090,
            "auth": {"username": "test", "password": "pass"},
            "timeout": 60,
        }), encoding="utf-8")
        cfg = ProxyConfig(str(config_file))
        assert cfg.port == 9090
        assert cfg.auth == {"username": "test", "password": "pass"}
        assert cfg.timeout == 60
        # Varsayilanlar korunmali
        assert cfg.whitelist == []
        assert cfg.upstream is None
        assert cfg.ssl is False

    def test_load_empty_json(self, tmp_path):
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text("{}", encoding="utf-8")
        cfg = ProxyConfig(str(config_file))
        assert cfg.port == 8080
        assert cfg.auth is None
        assert cfg.whitelist == []
        assert cfg.upstream is None
        assert cfg.timeout == 30
        assert cfg.ssl is False

    def test_load_partial_json(self, tmp_path):
        """Sadece port degistir, digerleri default kalsin."""
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text(json.dumps({"port": 3128}), encoding="utf-8")
        cfg = ProxyConfig(str(config_file))
        assert cfg.port == 3128
        assert cfg.auth is None
        assert cfg.timeout == 30

    def test_json_overrides_all_fields(self, tmp_path):
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text(json.dumps({
            "port": 8888,
            "auth": {"token": "abc123"},
            "whitelist": ["192.168.1.0/24"],
            "upstream": "http://proxy.example.com:3128",
            "timeout": 120,
            "ssl": True,
        }), encoding="utf-8")
        cfg = ProxyConfig(str(config_file))
        assert cfg.port == 8888
        assert cfg.auth == {"token": "abc123"}
        assert cfg.whitelist == ["192.168.1.0/24"]
        assert cfg.upstream == "http://proxy.example.com:3128"
        assert cfg.timeout == 120
        assert cfg.ssl is True

    def test_nonexistent_json_defaults(self, tmp_path):
        """Var olmayan dosya -> default degerler."""
        nonexistent = str(tmp_path / "nonexistent.json")
        cfg = ProxyConfig(nonexistent)
        assert cfg.port == 8080
        assert cfg.to_dict()["port"] == 8080


class TestProxyConfigEnvOverride:
    """Ortam degiskeni override testleri."""

    def test_http_proxy_override(self, monkeypatch):
        monkeypatch.setenv("HTTP_PROXY", "http://proxy.test:8080")
        cfg = ProxyConfig()
        assert cfg.upstream == "http://proxy.test:8080"

    def test_https_proxy_override(self, monkeypatch):
        monkeypatch.setenv("HTTPS_PROXY", "https://proxy.test:8443")
        cfg = ProxyConfig()
        assert cfg.upstream == "https://proxy.test:8443"

    def test_http_proxy_lowercase(self, monkeypatch):
        monkeypatch.setenv("http_proxy", "http://lower.proxy:3128")
        cfg = ProxyConfig()
        assert cfg.upstream == "http://lower.proxy:3128"

    def test_https_proxy_lowercase(self, monkeypatch):
        monkeypatch.setenv("https_proxy", "https://lower.proxy:8443")
        cfg = ProxyConfig()
        assert cfg.upstream == "https://lower.proxy:8443"

    def test_env_priority_first_match(self, monkeypatch):
        """HTTP_PROXY onecek, HTTPS_PROXY'ye gerek kalmayacak."""
        monkeypatch.setenv("HTTP_PROXY", "http://first:8080")
        monkeypatch.setenv("HTTPS_PROXY", "https://second:8443")
        cfg = ProxyConfig()
        assert cfg.upstream == "http://first:8080"

    def test_env_json_priority(self, tmp_path, monkeypatch):
        """Env, JSON'daki upstream'i ezer."""
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text(json.dumps({
            "upstream": "http://json-upstream:8080",
        }), encoding="utf-8")
        monkeypatch.setenv("HTTP_PROXY", "http://env-override:9999")
        cfg = ProxyConfig(str(config_file))
        assert cfg.upstream == "http://env-override:9999"

    def test_env_empty_ignored(self, monkeypatch):
        """Bos env degeri igne edilmeli."""
        monkeypatch.setenv("HTTP_PROXY", "")
        cfg = ProxyConfig()
        assert cfg.upstream is None

    def test_no_env_no_override(self):
        """HTTP_PROXY yoksa upstream None."""
        if "HTTP_PROXY" in os.environ:
            pytest.skip("Bu test icin HTTP_PROXY ayarlanmamali")
        cfg = ProxyConfig()
        assert cfg.upstream is None


class TestProxyConfigToDict:
    """to_dict() metod testleri."""

    def test_to_dict_returns_copy(self):
        cfg = ProxyConfig()
        d = cfg.to_dict()
        d["port"] = 9999
        assert cfg.port == 8080  # Orijinal degismemeli

    def test_to_dict_after_json(self, tmp_path):
        config_file = tmp_path / "proxy_config.json"
        config_file.write_text(json.dumps({"port": 5050, "timeout": 45}), encoding="utf-8")
        cfg = ProxyConfig(str(config_file))
        d = cfg.to_dict()
        assert d["port"] == 5050
        assert d["timeout"] == 45
        assert d["auth"] is None
        assert d["whitelist"] == []

    def test_to_dict_after_env(self, monkeypatch):
        monkeypatch.setenv("HTTP_PROXY", "http://from-env:3128")
        cfg = ProxyConfig()
        d = cfg.to_dict()
        assert d["upstream"] == "http://from-env:3128"


class TestProxyConfigAttributeErrors:
    """Bilinmeyen attribute testleri."""

    def test_unknown_attribute_raises(self):
        cfg = ProxyConfig()
        with pytest.raises(AttributeError, match="ProxyConfig has no attribute 'unknown_attr'"):
            _ = cfg.unknown_attr

    def test_unknown_attribute_message(self):
        cfg = ProxyConfig()
        with pytest.raises(AttributeError) as exc_info:
            _ = cfg.does_not_exist
        assert "does_not_exist" in str(exc_info.value)

    def test_existing_attributes_dont_raise(self):
        cfg = ProxyConfig()
        # Bunlar calismali
        _ = cfg.port
        _ = cfg.auth
        _ = cfg.whitelist
        _ = cfg.upstream
        _ = cfg.timeout
        _ = cfg.ssl

    def test_to_dict_no_extras(self):
        cfg = ProxyConfig()
        d = cfg.to_dict()
        known = {"port", "auth", "whitelist", "upstream", "timeout", "ssl"}
        assert set(d.keys()) == known
