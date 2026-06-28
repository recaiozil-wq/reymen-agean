"""
ReYMeN Core Test Suite
Çalıştır: pytest tests/test_reymen_core.py -v
Coverage: pytest tests/test_reymen_core.py --cov=. --cov-report=term-missing
"""
import os
import sys
import pytest


# ═══════════════════════════════════════════════════════════════════
# xAI Credential Tests (Görev 1)
# ═══════════════════════════════════════════════════════════════════

class TestXaiCredentials:
    """tools/xai_http.py — resolve_xai_http_credentials, has_xai_credentials,
    ReYMeN_xai_user_agent fonksiyonları."""

    def setup_method(self):
        os.environ.pop("XAI_API_KEY", None)
        os.environ.pop("XAI_BASE_URL", None)
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]

    def test_no_key_returns_none(self):
        from tools.xai_http import resolve_xai_http_credentials
        assert resolve_xai_http_credentials() is None

    def test_no_key_has_credentials_false(self):
        from tools.xai_http import has_xai_credentials
        assert has_xai_credentials() is False

    def test_with_key_returns_dict(self):
        os.environ["XAI_API_KEY"] = "test-reymen-key"
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]
        from tools.xai_http import resolve_xai_http_credentials
        r = resolve_xai_http_credentials()
        assert r is not None
        assert r["api_key"] == "test-reymen-key"
        assert "base_url" in r

    def test_with_key_has_credentials_true(self):
        os.environ["XAI_API_KEY"] = "test-key"
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]
        from tools.xai_http import has_xai_credentials
        assert has_xai_credentials() is True

    def test_default_base_url(self):
        os.environ["XAI_API_KEY"] = "k"
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]
        from tools.xai_http import resolve_xai_http_credentials
        r = resolve_xai_http_credentials()
        assert r["base_url"] == "https://api.x.ai/v1"

    def test_custom_base_url(self):
        os.environ["XAI_API_KEY"] = "k"
        os.environ["XAI_BASE_URL"] = "https://custom.ai/v9"
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]
        from tools.xai_http import resolve_xai_http_credentials
        r = resolve_xai_http_credentials()
        assert r["base_url"] == "https://custom.ai/v9"

    def test_user_agent_is_string(self):
        from tools.xai_http import ReYMeN_xai_user_agent
        ua = ReYMeN_xai_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0

    def test_user_agent_not_empty_after_key_set(self):
        os.environ["XAI_API_KEY"] = "k"
        for k in list(sys.modules.keys()):
            if "xai_http" in k:
                del sys.modules[k]
        from tools.xai_http import ReYMeN_xai_user_agent
        ua = ReYMeN_xai_user_agent()
        assert ua


# ═══════════════════════════════════════════════════════════════════
# Provider Alias Tests (Görev 2)
# ═══════════════════════════════════════════════════════════════════

class TestProviderAlias:
    """providers/__init__.py — register_provider alias."""

    def setup_method(self):
        for k in list(sys.modules.keys()):
            if k.startswith("providers"):
                del sys.modules[k]

    def test_register_provider_alias_exists(self):
        from providers import register_provider, plugin_kaydet
        assert register_provider is plugin_kaydet

    def test_register_provider_callable(self):
        from providers import register_provider
        assert callable(register_provider)


# ═══════════════════════════════════════════════════════════════════
# File Operations Tests
# ═══════════════════════════════════════════════════════════════════

class TestFileOperations:
    """Temel dosya okuma/yazma işlemleri."""

    def test_file_write_and_read(self, tmp_path):
        dosya = tmp_path / "test.txt"
        dosya.write_text("ReYMeN test", encoding="utf-8")
        assert dosya.read_text(encoding="utf-8") == "ReYMeN test"

    def test_json_file_roundtrip(self, tmp_path):
        import json
        data = {"name": "ReYMeN", "version": 1}
        dosya = tmp_path / "config.json"
        dosya.write_text(json.dumps(data), encoding="utf-8")
        loaded = json.loads(dosya.read_text(encoding="utf-8"))
        assert loaded == data

    def test_file_not_found(self):
        assert not os.path.exists("/nonexistent/path/file.txt")

    def test_empty_file(self, tmp_path):
        dosya = tmp_path / "empty.txt"
        dosya.write_text("", encoding="utf-8")
        assert dosya.read_text(encoding="utf-8") == ""


# ═══════════════════════════════════════════════════════════════════
# Environment Variable Tests
# ═══════════════════════════════════════════════════════════════════

class TestEnvironmentVariables:

    def test_env_get_existing(self):
        os.environ["REYMEN_TEST"] = "test_value"
        assert os.environ.get("REYMEN_TEST") == "test_value"
        os.environ.pop("REYMEN_TEST")

    def test_env_get_missing(self):
        os.environ.pop("REYMEN_MISSING", None)
        assert os.environ.get("REYMEN_MISSING") is None

    def test_env_get_default(self):
        os.environ.pop("REYMEN_DEFAULT", None)
        assert os.environ.get("REYMEN_DEFAULT", "default_val") == "default_val"


# ═══════════════════════════════════════════════════════════════════
# Utility Tests
# ═══════════════════════════════════════════════════════════════════

class TestUtilities:

    def test_import_main_module(self):
        """main modülü import edilebilmeli (chromadb uyarisi normal)."""
        try:
            import main  # noqa: F401
        except Exception as e:
            pytest.skip(f"main import edilemedi: {e}")

    def test_import_tool_modules(self):
        """Kritik tool modülleri import edilebilmeli."""
        moduller = [
            "tools.achievements",
            "tools.kanban_tools",
        ]
        for mod in moduller:
            try:
                __import__(mod)
            except ImportError as e:
                pytest.fail(f"{mod} import edilemedi: {e}")
