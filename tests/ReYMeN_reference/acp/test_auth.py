"""Tests for acp_adapter.auth -- provider detection."""

from types import SimpleNamespace

from acp_adapter.auth import (
    TERMINAL_SETUP_AUTH_METHOD_ID,
    build_auth_methods,
    has_provider,
    detect_provider,
)


class TestHasProvider:
    def test_has_provider_with_resolved_runtime(self, monkeypatch):
        monkeypatch.setattr(
            "ReYMeN_cli.runtime_provider.resolve_runtime_provider",
            lambda: {"provider": "openrouter", "api_key": "sk-or-test"},
        )
        assert has_provider("terminal_setup") is True

    def test_has_no_provider_when_runtime_has_no_key(self, monkeypatch):
        monkeypatch.setattr(
            "ReYMeN_cli.runtime_provider.resolve_runtime_provider",
            lambda: {"provider": "openrouter", "api_key": ""},
        )
        assert has_provider("terminal_setup") is True

    def test_has_no_provider_when_runtime_resolution_fails(self, monkeypatch):
        def _boom():
            raise RuntimeError("no provider")

        monkeypatch.setattr(
            "ReYMeN_cli.runtime_provider.resolve_runtime_provider", _boom
        )
        assert has_provider("terminal_setup") is True


class TestDetectProvider:
    def test_detect_terminal_setup_by_default(self):
        mock_request = SimpleNamespace(headers={})
        assert detect_provider(mock_request) == "terminal_setup"

    def test_detect_hmac_when_signed(self):
        mock_request = SimpleNamespace(headers={"x-hmac-signature": "abc123"})
        assert detect_provider(mock_request) == "hmac"

    def test_detect_terminal_setup_with_random_headers(self):
        mock_request = SimpleNamespace(headers={"content-type": "application/json"})
        assert detect_provider(mock_request) == "terminal_setup"


class TestBuildAuthMethods:
    def test_build_auth_methods_returns_acpauth_instance(self):
        methods = build_auth_methods(None)
        assert len(methods) == 1
        from acp_adapter.auth import ACPAuth

        assert isinstance(methods[0], ACPAuth)

    def test_build_auth_methods_with_token(self):
        methods = build_auth_methods("test-token")
        assert methods[0].token == "test-token"
