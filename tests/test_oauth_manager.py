# -*- coding: utf-8 -*-
"""
Test: reymen/core/oauth_manager.py — Kapsamli coverage testi (%90+ hedef).

Kapsanan alanlar:
  1. OAuthProvider ABC (abstract metotlar)
  2. GoogleOAuthProvider — HTTP mock, _http_post/_http_get hata durumlari
  3. GitHubOAuthProvider — callback, token_refresh (OAuthError), get_user_info
  4. DiscordOAuthProvider — Basic Auth callback, token_refresh, get_user_info
  5. OAuthTokenDeposu — JSON file cache CRUD, bozuk dosya
  6. OAuthToken — is_expired, expires_at
  7. OAuthManager — login, callback, refresh, logout, durum, gecerli_token
  8. Singleton — oauth_manager_al
  9. Motor Tools — OAUTH_GIRIS, OAUTH_DURUM
"""
from __future__ import annotations

import json
import os as os_module
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixture'lar
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def tmp_depo():
    """Gecici dizin uzerinde OAuthTokenDeposu olustur."""
    from reymen.core.oauth_manager import OAuthTokenDeposu
    with tempfile.TemporaryDirectory() as td:
        depo = OAuthTokenDeposu(base_path=Path(td))
        yield depo


@pytest.fixture
def manager_env(tmp_depo):
    """Env var'lar set edilmis OAuthManager (temp depo ile)."""
    from reymen.core.oauth_manager import OAuthManager
    with patch.dict(os_module.environ, {
        "GOOGLE_CLIENT_ID": "g-id",
        "GOOGLE_CLIENT_SECRET": "g-secret",
        "GITHUB_CLIENT_ID": "gh-id",
        "GITHUB_CLIENT_SECRET": "gh-secret",
        "DISCORD_CLIENT_ID": "dc-id",
        "DISCORD_CLIENT_SECRET": "dc-secret",
    }, clear=True):
        om = OAuthManager(deposu=tmp_depo)
        yield om


def _mock_urlopen_response(data: dict, status: int = 200) -> MagicMock:
    """urllib.request.urlopen icin basarili mock response."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status = status
    return mock_resp


def _mock_urlopen_httperror(url: str = "http://example.com",
                            code: int = 400,
                            msg: str = "Bad Request") -> None:
    """HTTPError firlatan MagicMock doner."""
    import urllib.error
    return urllib.error.HTTPError(url, code, msg, {}, None)


# ═══════════════════════════════════════════════════════════════════════════════
#  1. OAuthProvider ABC
# ═══════════════════════════════════════════════════════════════════════════════

class TestOAuthProviderABC:
    """OAuthProvider abstract base class davranisi."""

    def test_abstract_cannot_instantiate(self):
        """ABC direkt instance olusturulamaz."""
        from reymen.core.oauth_manager import OAuthProvider
        with pytest.raises(TypeError):
            OAuthProvider()  # type: ignore[abstract]

    def test_hazir_varsayilan_true(self):
        """hazir property varsayilan olarak True doner."""
        from reymen.core.oauth_manager import OAuthProvider

        # Abstract metotlari concrete yapip test et
        class ConcreteProvider(OAuthProvider):
            provider_id = "test"

            def login_url(self, state=""):
                return "http://example.com/login"

            def callback_handler(self, code, redirect_uri=""):
                from reymen.core.oauth_manager import OAuthToken
                return OAuthToken(access_token="t")

            def token_refresh(self, refresh_token):
                from reymen.core.oauth_manager import OAuthToken
                return OAuthToken(access_token="t")

            def get_user_info(self, access_token):
                return {"id": "1"}

        p = ConcreteProvider()
        assert p.hazir is True

    def test_abstract_metot_imzalari(self):
        """Abstract metotlarin dogru imzalara sahip oldugunu dogrula."""
        import inspect
        from reymen.core.oauth_manager import OAuthProvider

        # login_url(self, state: str = "") -> str
        sig = inspect.signature(OAuthProvider.login_url)
        assert "state" in sig.parameters
        assert sig.parameters["state"].default == ""

        # callback_handler(self, code: str, redirect_uri: str = "") -> OAuthToken
        sig2 = inspect.signature(OAuthProvider.callback_handler)
        assert "code" in sig2.parameters
        assert "redirect_uri" in sig2.parameters

        # token_refresh(self, refresh_token: str) -> OAuthToken
        sig3 = inspect.signature(OAuthProvider.token_refresh)
        assert "refresh_token" in sig3.parameters

        # get_user_info(self, access_token: str) -> dict
        sig4 = inspect.signature(OAuthProvider.get_user_info)
        assert "access_token" in sig4.parameters


# ═══════════════════════════════════════════════════════════════════════════════
#  2. OAuthToken & OAuthError
# ═══════════════════════════════════════════════════════════════════════════════

class TestOAuthToken:
    """OAuthToken veri yapisi testleri."""

    def test_default_fields(self):
        from reymen.core.oauth_manager import OAuthToken
        t = OAuthToken()
        assert t.access_token == ""
        assert t.token_type == "Bearer"
        assert t.expires_in == 3600
        assert t.provider == ""
        assert t.obtained_at > 0

    def test_is_expired_false(self):
        from reymen.core.oauth_manager import OAuthToken
        t = OAuthToken(access_token="t", provider="p", expires_in=3600)
        assert not t.is_expired

    def test_is_expired_true(self):
        from reymen.core.oauth_manager import OAuthToken
        t = OAuthToken(
            access_token="t", provider="p",
            expires_in=1, obtained_at=time.time() - 10,
        )
        assert t.is_expired is True

    def test_is_expired_boundary(self):
        """Expiry buffer (60sn) sinirinda test."""
        from reymen.core.oauth_manager import OAuthToken
        # 59 seconds ago, expires_in=120 → should NOT be expired
        t = OAuthToken(
            access_token="t", provider="p",
            expires_in=120, obtained_at=time.time() - 59,
        )
        assert not t.is_expired
        # 61 seconds ago, expires_in=120 → should be expired
        t2 = OAuthToken(
            access_token="t", provider="p",
            expires_in=120, obtained_at=time.time() - 61,
        )
        assert t2.is_expired

    def test_expires_at_format(self):
        """expires_at ISO formatinda string doner."""
        from reymen.core.oauth_manager import OAuthToken
        t = OAuthToken(access_token="t", provider="p", expires_in=3600)
        expiry_str = t.expires_at
        assert isinstance(expiry_str, str)
        # ISO format dogrulama
        dt = datetime.fromisoformat(expiry_str)
        assert dt.tzinfo is not None  # timezone-aware olmali

    def test_expires_at_value(self):
        """expires_at dogru zamani gosterir."""
        from reymen.core.oauth_manager import OAuthToken
        now = time.time()
        t = OAuthToken(
            access_token="t", provider="p",
            expires_in=60, obtained_at=now,
        )
        dt = datetime.fromisoformat(t.expires_at)
        expected = datetime.fromtimestamp(now + 60, tz=timezone.utc)
        assert abs(dt.timestamp() - expected.timestamp()) < 1


class TestOAuthError:
    """OAuthError exception testleri."""

    def test_default_values(self):
        from reymen.core.oauth_manager import OAuthError
        e = OAuthError("hata")
        assert str(e) == "hata"
        assert e.provider == ""
        assert e.status_code == 0
        assert e.code == "oauth_error"

    def test_full_init(self):
        from reymen.core.oauth_manager import OAuthError
        e = OAuthError("msg", provider="google", status_code=401, code="auth_fail")
        assert e.provider == "google"
        assert e.status_code == 401
        assert e.code == "auth_fail"


# ═══════════════════════════════════════════════════════════════════════════════
#  3. GoogleOAuthProvider
# ═══════════════════════════════════════════════════════════════════════════════

class TestGoogleOAuthProvider:
    """GoogleOAuthProvider — init, hazir, login_url."""

    def test_init_env_eksik(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            p = GoogleOAuthProvider()
            assert p.client_id == ""
            assert p.client_secret == ""
            assert not p.hazir
            assert p.provider_id == "google"

    def test_init_env_var(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "id",
            "GOOGLE_CLIENT_SECRET": "secret",
        }, clear=True):
            p = GoogleOAuthProvider()
            assert p.hazir
            assert p.client_id == "id"

    def test_login_url_no_state(self):
        """State verilmezse otomatik uretilir."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "gid",
            "GOOGLE_CLIENT_SECRET": "gsec",
        }, clear=True):
            with patch("secrets.token_urlsafe", return_value="auto-state-123"):
                p = GoogleOAuthProvider()
                url = p.login_url()
                assert "state=auto-state-123" in url

    def test_login_url_custom_state(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "gid",
            "GOOGLE_CLIENT_SECRET": "gsec",
        }, clear=True):
            p = GoogleOAuthProvider()
            url = p.login_url(state="custom-state")
            assert "state=custom-state" in url
            assert "accounts.google.com" in url
            assert "client_id=gid" in url
            assert "access_type=offline" in url

    def test_login_url_redirect_uri_override(self):
        """Ozel redirect_uri constructor parametresi calisir."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "id",
            "GOOGLE_CLIENT_SECRET": "sec",
        }, clear=True):
            p = GoogleOAuthProvider(redirect_uri="https://app.example/cb")
            url = p.login_url("s")
            assert "redirect_uri=https%3A%2F%2Fapp.example%2Fcb" in url

    def test_hazir_false(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            p = GoogleOAuthProvider()
            assert not p.hazir

    def test_hazir_true(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "x", "GOOGLE_CLIENT_SECRET": "y",
        }, clear=True):
            assert GoogleOAuthProvider().hazir


class TestGoogleOAuthProviderHTTP:
    """GoogleOAuthProvider — HTTP mock ile callback/refresh/userinfo."""

    ENV = {"GOOGLE_CLIENT_ID": "g-id", "GOOGLE_CLIENT_SECRET": "g-secret"}

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_post", return_value={
                "access_token": "ya29.mock",
                "expires_in": 3600,
                "refresh_token": "rf1",
                "token_type": "Bearer",
            }):
                with patch.object(p, "get_user_info", return_value={
                    "sub": "12345", "email": "user@gmail.com",
                    "name": "Test User", "picture": "https://pic",
                }):
                    token = p.callback_handler("auth-code-xyz")
                    assert token.access_token == "ya29.mock"
                    assert token.refresh_token == "rf1"
                    assert token.provider == "google"
                    assert token.email == "user@gmail.com"
                    assert token.display_name == "Test User"

    def test_callback_ozel_redirect_uri(self):
        """callback_handler'a redirect_uri parametresi gecilebilir."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_post", return_value={
                "access_token": "t", "expires_in": 3600,
            }) as mock_post:
                with patch.object(p, "get_user_info", return_value={}):
                    p.callback_handler("code", redirect_uri="https://my/cb")
                    # _http_post cagrisinin redirect_uri icerdigini kontrol et
                    call_data = mock_post.call_args[0][1]
                    assert call_data["redirect_uri"] == "https://my/cb"

    def test_callback_get_user_info_hata(self):
        """get_user_info hata verse bile token doner."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_post", return_value={
                "access_token": "tok", "expires_in": 3600,
            }):
                with patch.object(p, "get_user_info",
                                  side_effect=ValueError("API hatasi")):
                    token = p.callback_handler("code")
                    assert token.access_token == "tok"
                    # Kullanici bilgileri bos olmali
                    assert token.email == ""

    def test_callback_error_response(self):
        """Hatali response (error iceriyor) bos token doner."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_post", return_value={"error": "invalid_grant"}):
                with patch.object(p, "get_user_info", return_value={}):
                    token = p.callback_handler("bad-code")
                    assert token.access_token == ""

    def test_token_refresh(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_post", return_value={
                "access_token": "new-at",
                "expires_in": 3600,
                "refresh_token": "new-rt",
            }):
                token = p.token_refresh("old-rt")
                assert token.access_token == "new-at"
                assert token.refresh_token == "new-rt"
                assert token.provider == "google"

    def test_get_user_info(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            with patch.object(p, "_http_get", return_value={
                "sub": "1", "email": "a@b.com", "name": "Alice",
            }):
                info = p.get_user_info("valid-token")
                assert info["email"] == "a@b.com"
                assert info["name"] == "Alice"

    def test_http_post_httperror(self):
        """_http_post HTTPError yakalar ve OAuthError firlatir."""
        from reymen.core.oauth_manager import GoogleOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            import urllib.error
            fp = MagicMock()
            fp.read.return_value = b'{"error":"invalid_request"}'
            http_err = urllib.error.HTTPError(
                "http://example.com", 400, "Bad Request", {}, fp,
            )
            with patch("urllib.request.urlopen", side_effect=http_err):
                with pytest.raises(OAuthError) as exc:
                    p._http_post("http://example.com", {"key": "val"})
                assert exc.value.status_code == 400
                assert exc.value.provider == "google"

    def test_http_get_httperror(self):
        """_http_get HTTPError yakalar ve OAuthError firlatir."""
        from reymen.core.oauth_manager import GoogleOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            import urllib.error
            fp = MagicMock()
            fp.read.return_value = b'{"error":"unauthorized"}'
            http_err = urllib.error.HTTPError(
                "http://example.com", 401, "Unauthorized", {}, fp,
            )
            with patch("urllib.request.urlopen", side_effect=http_err):
                with pytest.raises(OAuthError) as exc:
                    p._http_get("http://example.com", "bad-token")
                assert exc.value.status_code == 401

    def test_http_post_basarili(self):
        """_http_post basarili HTTP istegi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            mock_resp = _mock_urlopen_response({"access_token": "t"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = p._http_post("http://example.com", {"key": "val"})
                assert result["access_token"] == "t"

    def test_http_get_basarili(self):
        """_http_get basarili HTTP istegi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GoogleOAuthProvider()
            mock_resp = _mock_urlopen_response({"sub": "1"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = p._http_get("http://example.com", "t")
                assert result["sub"] == "1"


# ═══════════════════════════════════════════════════════════════════════════════
#  4. GitHubOAuthProvider
# ═══════════════════════════════════════════════════════════════════════════════

class TestGitHubOAuthProvider:
    """GitHubOAuthProvider — init, hazir, login_url."""

    ENV = {"GITHUB_CLIENT_ID": "gh-id", "GITHUB_CLIENT_SECRET": "gh-secret"}

    def test_init_env_eksik(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            p = GitHubOAuthProvider()
            assert not p.hazir
            assert p.provider_id == "github"

    def test_hazir(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            assert GitHubOAuthProvider().hazir

    def test_login_url_no_state(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            with patch("secrets.token_urlsafe", return_value="auto-gh"):
                p = GitHubOAuthProvider()
                url = p.login_url()
                assert "state=auto-gh" in url

    def test_login_url_custom_state(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            url = p.login_url(state="my-gh-state")
            assert "state=my-gh-state" in url
            assert "github.com/login/oauth/authorize" in url

    def test_login_url_ozel_redirect_uri(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider(redirect_uri="https://myapp/cb")
            url = p.login_url("s")
            assert "redirect_uri=https%3A%2F%2Fmyapp%2Fcb" in url


class TestGitHubOAuthProviderHTTP:
    """GitHubOAuthProvider — HTTP mock ile callback/refresh/userinfo."""

    ENV = {"GITHUB_CLIENT_ID": "gh-id", "GITHUB_CLIENT_SECRET": "gh-secret"}

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            mock_resp = _mock_urlopen_response({"access_token": "gho_token"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info", return_value={
                    "id": 42, "login": "testuser", "email": "t@github.com",
                    "name": "Test", "avatar_url": "https://avatars/1",
                }):
                    token = p.callback_handler("code-xyz")
                    assert token.access_token == "gho_token"
                    assert token.provider == "github"
                    assert token.user_id == "42"
                    assert token.email == "t@github.com"
                    assert token.display_name == "Test"
                    assert token.avatar_url == "https://avatars/1"

    def test_callback_ozel_redirect_uri(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            mock_resp = _mock_urlopen_response({"access_token": "t"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info", return_value={}):
                    token = p.callback_handler("code", redirect_uri="https://my/cb")
                    assert token.access_token == "t"

    def test_callback_get_user_info_hata(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            mock_resp = _mock_urlopen_response({"access_token": "gho"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info",
                                  side_effect=ValueError("API down")):
                    token = p.callback_handler("code")
                    assert token.access_token == "gho"
                    assert token.email == ""

    def test_callback_http_error(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            with patch("urllib.request.urlopen",
                       side_effect=_mock_urlopen_httperror(code=401)):
                with pytest.raises(OAuthError) as exc:
                    p.callback_handler("bad-code")
                assert exc.value.provider == "github"

    def test_token_refresh_raises(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            with pytest.raises(OAuthError) as exc:
                p.token_refresh("anything")
            assert "süreklidir" in str(exc.value)
            assert exc.value.provider == "github"

    def test_get_user_info(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "login": "octocat", "id": 1, "email": "o@github.com",
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                info = p.get_user_info("valid-token")
                assert info["login"] == "octocat"

    def test_get_user_info_http_error(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = GitHubOAuthProvider()
            with patch("urllib.request.urlopen",
                       side_effect=_mock_urlopen_httperror(code=403)):
                with pytest.raises(OAuthError) as exc:
                    p.get_user_info("bad-token")
                assert exc.value.provider == "github"

    def test_hazir_false(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            assert not GitHubOAuthProvider().hazir


# ═══════════════════════════════════════════════════════════════════════════════
#  5. DiscordOAuthProvider
# ═══════════════════════════════════════════════════════════════════════════════

class TestDiscordOAuthProvider:
    """DiscordOAuthProvider — init, hazir, login_url."""

    ENV = {"DISCORD_CLIENT_ID": "dc-id", "DISCORD_CLIENT_SECRET": "dc-secret"}

    def test_init_env_eksik(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            p = DiscordOAuthProvider()
            assert not p.hazir
            assert p.provider_id == "discord"

    def test_hazir(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            assert DiscordOAuthProvider().hazir

    def test_login_url_no_state(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            with patch("secrets.token_urlsafe", return_value="dc-auto"):
                p = DiscordOAuthProvider()
                url = p.login_url()
                assert "state=dc-auto" in url

    def test_login_url_custom_state(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            url = p.login_url(state="discord-state")
            assert "state=discord-state" in url
            assert "discord.com/api/oauth2/authorize" in url
            assert "prompt=consent" in url


class TestDiscordOAuthProviderHTTP:
    """DiscordOAuthProvider — HTTP mock ile callback/refresh/userinfo."""

    ENV = {"DISCORD_CLIENT_ID": "dc-id", "DISCORD_CLIENT_SECRET": "dc-secret"}

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "access_token": "dc_token",
                "expires_in": 3600,
                "refresh_token": "dc_refresh",
                "token_type": "Bearer",
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info", return_value={
                    "id": "12345", "username": "testuser",
                    "global_name": "TestUser", "avatar": "abc123",
                }):
                    token = p.callback_handler("code456")
                    assert token.access_token == "dc_token"
                    assert token.refresh_token == "dc_refresh"
                    assert token.provider == "discord"
                    assert token.display_name == "TestUser"
                    assert "cdn.discordapp.com" in token.avatar_url

    def test_callback_basic_auth_header(self):
        """Discord Basic Auth header dogru sekilde olusturulur."""
        from reymen.core.oauth_manager import DiscordOAuthProvider
        import base64
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            expected_basic = base64.b64encode(
                b"dc-id:dc-secret"
            ).decode()
            mock_resp = _mock_urlopen_response({
                "access_token": "t", "expires_in": 3600,
            })
            with patch("urllib.request.urlopen", return_value=mock_resp) as mock_uo:
                with patch.object(p, "get_user_info", return_value={}):
                    p.callback_handler("code")
                    # urlopen cagrisindaki Authorization header'ini kontrol et
                    call_req = mock_uo.call_args[0][0]
                    auth_val = call_req.headers.get("Authorization", "")
                    assert expected_basic in auth_val
                    assert auth_val.startswith("Basic ")

    def test_callback_ozel_redirect_uri(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({"access_token": "t", "expires_in": 3600})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info", return_value={}):
                    token = p.callback_handler("code", redirect_uri="https://my/cb")
                    assert token.access_token == "t"

    def test_callback_avatar_gif(self):
        """Animated avatar (a_) .gif uzantisi kullanir."""
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "access_token": "t", "expires_in": 3600,
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info", return_value={
                    "id": "999", "username": "anim", "avatar": "a_abc123",
                }):
                    token = p.callback_handler("code")
                    assert token.avatar_url.endswith(".gif")

    def test_callback_get_user_info_hata(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "access_token": "t", "expires_in": 3600,
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(p, "get_user_info",
                                  side_effect=ValueError("fail")):
                    token = p.callback_handler("code")
                    assert token.access_token == "t"
                    assert token.display_name == ""

    def test_callback_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            with patch("urllib.request.urlopen",
                       side_effect=_mock_urlopen_httperror(code=400)):
                with pytest.raises(OAuthError) as exc:
                    p.callback_handler("bad-code")
                assert exc.value.provider == "discord"

    def test_token_refresh(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "access_token": "new-dc",
                "expires_in": 3600,
                "refresh_token": "new-ref",
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                token = p.token_refresh("old-ref")
                assert token.access_token == "new-dc"
                assert token.refresh_token == "new-ref"
                assert token.provider == "discord"

    def test_token_refresh_basic_auth(self):
        """token_refresh'te de Basic Auth kullanilir."""
        from reymen.core.oauth_manager import DiscordOAuthProvider
        import base64
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            expected_basic = base64.b64encode(
                b"dc-id:dc-secret"
            ).decode()
            mock_resp = _mock_urlopen_response({"access_token": "t"})
            with patch("urllib.request.urlopen", return_value=mock_resp) as mock_uo:
                p.token_refresh("old-ref")
                call_req = mock_uo.call_args[0][0]
                auth_val = call_req.headers.get("Authorization", "")
                assert expected_basic in auth_val

    def test_token_refresh_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            with patch("urllib.request.urlopen",
                       side_effect=_mock_urlopen_httperror(code=401)):
                with pytest.raises(OAuthError) as exc:
                    p.token_refresh("bad-ref")
                assert exc.value.provider == "discord"

    def test_get_user_info(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            mock_resp = _mock_urlopen_response({
                "id": "123", "username": "testuser",
                "global_name": "Test", "email": "t@discord.com",
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                info = p.get_user_info("valid-token")
                assert info["username"] == "testuser"

    def test_get_user_info_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError
        with patch.dict(os_module.environ, self.ENV, clear=True):
            p = DiscordOAuthProvider()
            with patch("urllib.request.urlopen",
                       side_effect=_mock_urlopen_httperror(code=429)):
                with pytest.raises(OAuthError) as exc:
                    p.get_user_info("bad-token")
                assert exc.value.provider == "discord"

    def test_hazir_false(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider
        with patch.dict(os_module.environ, {}, clear=True):
            assert not DiscordOAuthProvider().hazir


# ═══════════════════════════════════════════════════════════════════════════════
#  6. OAuthTokenDeposu
# ═══════════════════════════════════════════════════════════════════════════════

class TestOAuthTokenDeposu:
    """OAuthTokenDeposu — JSON file cache CRUD + hata durumlari."""

    def test_olusum(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            # Base path parent olusturulur (tmp), alt dizin _save ile olusur
            assert depo._base == Path(td)
            assert "tokens_cache.json" in str(depo._dosya)

    def test_kaydet_yukle(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu, OAuthToken
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            t = OAuthToken(
                access_token="at1", provider="prov1",
                expires_in=3600, refresh_token="rt1",
                user_id="u1", email="e@mail.com",
            )
            depo.kaydet(t)
            yuklenen = depo.yukle("prov1")
            assert yuklenen is not None
            assert yuklenen.access_token == "at1"
            assert yuklenen.refresh_token == "rt1"
            assert yuklenen.email == "e@mail.com"

    def test_yukle_olmayan(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            assert depo.yukle("olmayan") is None

    def test_sil_var(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu, OAuthToken
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            t = OAuthToken(access_token="a", provider="sil_test", expires_in=3600)
            depo.kaydet(t)
            assert depo.var_mi("sil_test")
            result = depo.sil("sil_test")
            assert result is True
            assert not depo.var_mi("sil_test")

    def test_sil_olmayan(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            result = depo.sil("yok")
            assert result is False

    def test_listele(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu, OAuthToken
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            t1 = OAuthToken(access_token="a1", provider="p1", expires_in=3600)
            t2 = OAuthToken(access_token="a2", provider="p2", expires_in=3600)
            depo.kaydet(t1)
            depo.kaydet(t2)
            liste = depo.listele()
            assert len(liste) == 2
            providers = {item["provider"] for item in liste}
            assert "p1" in providers
            assert "p2" in providers

    def test_listele_bos(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            assert depo.listele() == []

    def test_var_mi_true(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu, OAuthToken
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            t = OAuthToken(access_token="a", provider="p", expires_in=3600)
            depo.kaydet(t)
            assert depo.var_mi("p") is True

    def test_var_mi_false(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            assert depo.var_mi("yok") is False

    def test_load_dosya_yok(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            data = depo._load()
            assert data == {}

    def test_load_bozuk_json(self):
        """Bozuk JSON dosyasi bos dict ile sonuclanir."""
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            depo._dosya.parent.mkdir(parents=True, exist_ok=True)
            depo._dosya.write_text("not valid json{{{", encoding="utf-8")
            data = depo._load()
            assert data == {}

    def test_save_create_dir(self):
        """_save otomatik olarak dizin yapisini olusturur."""
        from reymen.core.oauth_manager import OAuthTokenDeposu
        with tempfile.TemporaryDirectory() as td:
            deep_path = Path(td) / "sub" / "dir"
            depo = OAuthTokenDeposu(base_path=deep_path)
            depo._save({"test": "data"})
            assert depo._dosya.exists()
            loaded = json.loads(depo._dosya.read_text(encoding="utf-8"))
            assert loaded["test"] == "data"

    def test_listele_expired_status(self):
        """listele() expired token durumunu dogru gosterir."""
        from reymen.core.oauth_manager import OAuthTokenDeposu, OAuthToken
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            t = OAuthToken(
                access_token="old", provider="exp_prov",
                expires_in=1, obtained_at=time.time() - 100,
            )
            depo.kaydet(t)
            liste = depo.listele()
            for item in liste:
                if item["provider"] == "exp_prov":
                    assert item["durum"] == "suresi doldu"


# ═══════════════════════════════════════════════════════════════════════════════
#  7. OAuthManager
# ═══════════════════════════════════════════════════════════════════════════════

class TestOAuthManagerInit:
    """OAuthManager baslangic durumu."""

    def test_olusum_empty_env(self):
        """Env var'lar yokken de OAuthManager olusur."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu
        with patch.dict(os_module.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                # Provider listesinde olmali ama hazir degil
                providers = om.provider_listesi()
                assert "google" in providers
                assert "github" in providers
                assert "discord" in providers

    def test_olusum_with_env(self):
        """Env var'lar varken tum provider'lar hazir."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "g",
            "GITHUB_CLIENT_ID": "gh", "GITHUB_CLIENT_SECRET": "gh",
            "DISCORD_CLIENT_ID": "dc", "DISCORD_CLIENT_SECRET": "dc",
        }, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                for p_id in ["google", "github", "discord"]:
                    p = om.provider(p_id)
                    assert p is not None
                    assert p.hazir


class TestOAuthManagerLogin:
    """OAuthManager.login() testleri."""

    def test_login_google(self, manager_env):
        url = manager_env.login("google")
        assert "accounts.google.com" in url
        assert "client_id=g-id" in url

    def test_login_github(self, manager_env):
        url = manager_env.login("github")
        assert "github.com/login/oauth/authorize" in url

    def test_login_discord(self, manager_env):
        url = manager_env.login("discord")
        assert "discord.com/api/oauth2/authorize" in url

    def test_login_custom_state(self, manager_env):
        url = manager_env.login("google", state="ozel-state")
        assert "state=ozel-state" in url

    def test_login_bilinmeyen_provider(self, manager_env):
        from reymen.core.oauth_manager import OAuthError
        with pytest.raises(OAuthError) as exc:
            manager_env.login("bilinmeyen")
        assert "Bilinmeyen" in str(exc.value)

    def test_login_hazir_degil(self):
        """Env var'lar yokken login OAuthError."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu
        with patch.dict(os_module.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                with pytest.raises(OAuthError) as exc:
                    om.login("google")
                assert "eksik" in str(exc.value) or "yapilandirma" in str(exc.value)


class TestOAuthManagerCallback:
    """OAuthManager.callback() testleri."""

    def test_callback_google(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            mock_resp = _mock_urlopen_response({
                "access_token": "cb-token", "expires_in": 3600,
                "refresh_token": "cb-ref",
            })
            with patch("urllib.request.urlopen", return_value=mock_resp):
                token = om.callback("google", "test-code")
            assert token.access_token == "cb-token"
            assert token.refresh_token == "cb-ref"
            # Depotan kontrol
            depo_token = tmp_depo.yukle("google")
            assert depo_token is not None
            assert depo_token.access_token == "cb-token"

    def test_callback_github(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager
        with patch.dict(os_module.environ, {
            "GITHUB_CLIENT_ID": "gh", "GITHUB_CLIENT_SECRET": "ghs",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            mock_resp = _mock_urlopen_response({"access_token": "gh-token"})
            with patch("urllib.request.urlopen", return_value=mock_resp):
                token = om.callback("github", "code")
            assert token.access_token == "gh-token"

    def test_callback_bilinmeyen_provider(self, manager_env):
        from reymen.core.oauth_manager import OAuthError
        with pytest.raises(OAuthError):
            manager_env.callback("yok", "code")


class TestOAuthManagerRefresh:
    """OAuthManager.refresh() testleri."""

    def test_refresh_bilinmeyen_provider(self, manager_env):
        from reymen.core.oauth_manager import OAuthError
        with pytest.raises(OAuthError):
            manager_env.refresh("yok")

    def test_refresh_token_yok(self, manager_env):
        from reymen.core.oauth_manager import OAuthError
        with pytest.raises(OAuthError) as exc:
            manager_env.refresh("google")
        assert "bulunamadi" in str(exc.value)

    def test_refresh_no_refresh_token(self, tmp_depo):
        """Token var ama refresh_token yok (non-GitHub)."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthToken
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            # refresh_token'suz token kaydet
            t = OAuthToken(access_token="old", provider="google", expires_in=3600, refresh_token="")
            tmp_depo.kaydet(t)
            with pytest.raises(OAuthError) as exc:
                om.refresh("google")
            assert "Refresh token yok" in str(exc.value)

    def test_refresh_github_no_refresh_needed(self, tmp_depo):
        """GitHub token'i var ama refresh gerekmez."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthToken
        with patch.dict(os_module.environ, {
            "GITHUB_CLIENT_ID": "gh", "GITHUB_CLIENT_SECRET": "ghs",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            t = OAuthToken(access_token="old", provider="github", expires_in=3600, refresh_token="")
            tmp_depo.kaydet(t)
            with pytest.raises(OAuthError) as exc:
                om.refresh("github")
            assert "sureklidir" in str(exc.value)

    def test_refresh_basarili(self, tmp_depo):
        """Basarili token refresh."""
        from reymen.core.oauth_manager import OAuthManager, OAuthToken, GoogleOAuthProvider
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            t = OAuthToken(
                access_token="old", provider="google",
                expires_in=3600, refresh_token="rt-123",
                user_id="uid1", email="e@mail.com",
            )
            tmp_depo.kaydet(t)
            # Mock the provider's token_refresh
            with patch.object(om.provider("google"), "token_refresh",
                              return_value=OAuthToken(
                                  access_token="new-at", provider="google",
                                  expires_in=3600, refresh_token="rt-123",
                              )):
                new_token = om.refresh("google")
                assert new_token.access_token == "new-at"
                # Kullanici bilgileri korunmali
                assert new_token.user_id == "uid1"
                assert new_token.email == "e@mail.com"
                # Guncellenen depo
                depo_token = tmp_depo.yukle("google")
                assert depo_token.access_token == "new-at"


class TestOAuthManagerLogout:
    """OAuthManager.logout() testleri."""

    def test_logout_var(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(access_token="a", provider="test", expires_in=3600)
        tmp_depo.kaydet(t)
        assert tmp_depo.var_mi("test")
        result = om.logout("test")
        assert result is True
        assert not tmp_depo.var_mi("test")

    def test_logout_yok(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager
        om = OAuthManager(deposu=tmp_depo)
        result = om.logout("olmayan")
        assert result is False


class TestOAuthManagerDurum:
    """OAuthManager.durum() testleri."""

    def test_durum_token_yok(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager
        om = OAuthManager(deposu=tmp_depo)
        durum = om.durum("test")
        assert durum["var_mi"] is False
        assert durum["gecerli_mi"] is False

    def test_durum_token_var_gecerli(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(
            access_token="abc123token", provider="test",
            expires_in=3600, email="u@test.com",
            display_name="User", user_id="42",
        )
        tmp_depo.kaydet(t)
        durum = om.durum("test")
        assert durum["var_mi"] is True
        assert durum["gecerli_mi"] is True
        assert durum["access_token_prefix"] == "abc123toke..."
        assert durum["email"] == "u@test.com"
        assert durum["display_name"] == "User"
        assert durum["user_id"] == "42"
        assert durum["refresh_token_var"] is False  # bos refresh_token

    def test_durum_token_expired(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(
            access_token="old", provider="test",
            expires_in=1, obtained_at=time.time() - 100,
        )
        tmp_depo.kaydet(t)
        durum = om.durum("test")
        assert durum["var_mi"] is True
        assert durum["gecerli_mi"] is False

    def test_durum_token_with_refresh(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(
            access_token="tok", provider="test",
            expires_in=3600, refresh_token="rt",
        )
        tmp_depo.kaydet(t)
        durum = om.durum("test")
        assert durum["refresh_token_var"] is True


class TestOAuthManagerGecerliToken:
    """OAuthManager.gecerli_token() testleri."""

    def test_no_token(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager
        om = OAuthManager(deposu=tmp_depo)
        assert om.gecerli_token("test") is None

    def test_valid_token(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(access_token="valid", provider="test", expires_in=3600)
        tmp_depo.kaydet(t)
        result = om.gecerli_token("test")
        assert result is not None
        assert result.access_token == "valid"

    def test_expired_no_refresh(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(
            access_token="exp", provider="test",
            expires_in=1, obtained_at=time.time() - 100,
            refresh_token="",
        )
        tmp_depo.kaydet(t)
        result = om.gecerli_token("test")
        assert result is None  # expired + no refresh → None

    def test_expired_with_refresh_auto(self, tmp_depo):
        """Suresi dolmus token otomatik yenilenir."""
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            t = OAuthToken(
                access_token="exp", provider="google",
                expires_in=1, obtained_at=time.time() - 100,
                refresh_token="rt-456",
                user_id="u1", email="e@m.com",
            )
            tmp_depo.kaydet(t)
            # Mock refresh
            with patch.object(om, "refresh", return_value=OAuthToken(
                access_token="new-tok", provider="google",
                expires_in=3600, refresh_token="rt-456",
                user_id="u1", email="e@m.com",
            )):
                result = om.gecerli_token("google")
                assert result is not None
                assert result.access_token == "new-tok"

    def test_expired_with_refresh_fails(self, tmp_depo):
        """Refresh basarisiz olursa None doner."""
        from reymen.core.oauth_manager import OAuthManager, OAuthToken, OAuthError
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            om = OAuthManager(deposu=tmp_depo)
            t = OAuthToken(
                access_token="exp", provider="google",
                expires_in=1, obtained_at=time.time() - 100,
                refresh_token="rt-fail",
            )
            tmp_depo.kaydet(t)
            with patch.object(om, "refresh",
                              side_effect=OAuthError("refresh failed")):
                result = om.gecerli_token("google")
                assert result is None


class TestOAuthManagerListeleProvider:
    """OAuthManager.listele(), provider(), provider_listesi()."""

    def test_listele(self, tmp_depo):
        from reymen.core.oauth_manager import OAuthManager, OAuthToken
        om = OAuthManager(deposu=tmp_depo)
        t = OAuthToken(access_token="a", provider="p1", expires_in=3600)
        tmp_depo.kaydet(t)
        liste = om.listele()
        assert len(liste) == 1
        assert liste[0]["provider"] == "p1"

    def test_provider_getter(self, manager_env):
        p = manager_env.provider("google")
        assert p is not None
        assert p.provider_id == "google"
        assert manager_env.provider("yok") is None

    def test_provider_listesi(self, manager_env):
        providers = manager_env.provider_listesi()
        assert isinstance(providers, list)
        assert "google" in providers
        assert "github" in providers
        assert "discord" in providers


# ═══════════════════════════════════════════════════════════════════════════════
#  8. Singleton
# ═══════════════════════════════════════════════════════════════════════════════

class TestSingleton:
    """oauth_manager_al singleton testi."""

    def test_singleton_ayni_instance(self):
        from reymen.core.oauth_manager import oauth_manager_al
        # Singleton'u sifirla
        import reymen.core.oauth_manager as om_mod
        om_mod._oauth_manager_instance = None
        o1 = oauth_manager_al()
        o2 = oauth_manager_al()
        assert o1 is o2

    def test_singleton_instance_type(self):
        from reymen.core.oauth_manager import oauth_manager_al, OAuthManager
        import reymen.core.oauth_manager as om_mod
        om_mod._oauth_manager_instance = None
        instance = oauth_manager_al()
        assert isinstance(instance, OAuthManager)


# ═══════════════════════════════════════════════════════════════════════════════
#  9. Motor Tools
# ═══════════════════════════════════════════════════════════════════════════════

class TestMotorTools:
    """motor_kaydet, OAUTH_GIRIS, OAUTH_DURUM testleri."""

    def _make_motor(self):
        """Mock motor olustur."""
        class MockMotor:
            def __init__(self):
                self.tools = {}
            def _plugin_arac_kaydet(self, ad, func, desc=""):
                self.tools[ad] = func
        return MockMotor()

    def _reset_singleton(self):
        """Singleton'u sifirla."""
        import reymen.core.oauth_manager as om_mod
        om_mod._oauth_manager_instance = None

    def test_motor_kaydet_araclar(self):
        """motor_kaydet 2 arac kaydeder: OAUTH_GIRIS ve OAUTH_DURUM."""
        from reymen.core.oauth_manager import motor_kaydet
        self._reset_singleton()
        m = self._make_motor()
        motor_kaydet(m)
        assert "OAUTH_GIRIS" in m.tools
        assert "OAUTH_DURUM" in m.tools

    def test_oauth_giris_kwarg_provider(self):
        """OAUTH_GIRIS provider kwarg ile calisir."""
        from reymen.core.oauth_manager import motor_kaydet, OAuthManager, OAuthTokenDeposu
        self._reset_singleton()
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                import reymen.core.oauth_manager as om_mod
                om_mod._oauth_manager_instance = om
                m = self._make_motor()
                motor_kaydet(m)
                result = m.tools["OAUTH_GIRIS"](provider="google")
                assert "[OAUTH]" in result
                assert "accounts.google.com" in result

    def test_oauth_giris_args_provider(self):
        """OAUTH_GIRIS args[0] ile provider alir."""
        from reymen.core.oauth_manager import motor_kaydet, OAuthManager, OAuthTokenDeposu
        self._reset_singleton()
        with patch.dict(os_module.environ, {
            "GOOGLE_CLIENT_ID": "g", "GOOGLE_CLIENT_SECRET": "s",
        }, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                import reymen.core.oauth_manager as om_mod
                om_mod._oauth_manager_instance = om
                m = self._make_motor()
                motor_kaydet(m)
                result = m.tools["OAUTH_GIRIS"](args=["google"])
                assert "[OAUTH]" in result

    def test_oauth_giris_no_provider(self):
        """OAUTH_GIRIS provider verilmezse hata mesaji doner."""
        from reymen.core.oauth_manager import motor_kaydet, OAuthManager, OAuthTokenDeposu
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            m = self._make_motor()
            motor_kaydet(m)
            result = m.tools["OAUTH_GIRIS"](args=[])
            assert "[HATA]" in result
            assert "zorunlu" in result

    def test_oauth_giris_hata(self):
        """OAUTH_GIRIS bilinmeyen provider ile hata mesaji doner."""
        from reymen.core.oauth_manager import motor_kaydet, OAuthManager, OAuthTokenDeposu
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            m = self._make_motor()
            motor_kaydet(m)
            result = m.tools["OAUTH_GIRIS"](provider="bilinmeyen")
            assert "[HATA]" in result

    def test_oauth_durum_kwarg_var_mi(self):
        """OAUTH_DURUM token var+gecerli iken durum gosterir."""
        from reymen.core.oauth_manager import (motor_kaydet, OAuthManager,
                                                OAuthToken, OAuthTokenDeposu)
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            t = OAuthToken(access_token="t", provider="giris_test",
                           expires_in=3600, email="a@b.com")
            depo.kaydet(t)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            m = self._make_motor()
            motor_kaydet(m)
            result = m.tools["OAUTH_DURUM"](provider="giris_test")
            assert "[OAUTH]" in result
            assert "Token Durumu" in result

    def test_oauth_durum_kwarg_yok(self):
        """OAUTH_DURUM token yokken uygun mesaj doner."""
        from reymen.core.oauth_manager import (motor_kaydet, OAuthManager,
                                                OAuthTokenDeposu)
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            m = self._make_motor()
            motor_kaydet(m)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            result = m.tools["OAUTH_DURUM"](provider="yok_prov")
            assert "bulunamadi" in result

    def test_oauth_durum_no_provider_all(self):
        """OAUTH_DURUM provider verilmezse tum provider durumlarini gosterir."""
        from reymen.core.oauth_manager import (motor_kaydet, OAuthManager,
                                                OAuthTokenDeposu)
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            m = self._make_motor()
            motor_kaydet(m)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            result = m.tools["OAUTH_DURUM"]()
            assert "OAUTH" in result

    def test_oauth_durum_args(self):
        """OAUTH_DURUM args[0] ile provider alir."""
        from reymen.core.oauth_manager import (motor_kaydet, OAuthManager,
                                                OAuthTokenDeposu)
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            m = self._make_motor()
            motor_kaydet(m)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            result = m.tools["OAUTH_DURUM"](args=["yok_prov"])
            assert "bulunamadi" in result

    def test_oauth_durum_gecerli_token(self):
        """OAUTH_DURUM gecerli token bilgilerini gosterir."""
        from reymen.core.oauth_manager import (motor_kaydet, OAuthManager,
                                                OAuthToken, OAuthTokenDeposu)
        self._reset_singleton()
        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            t = OAuthToken(
                access_token="abc", provider="test_gecerli",
                expires_in=3600, email="e@mail.com",
                display_name="TestUser", scope="read write",
            )
            depo.kaydet(t)
            m = self._make_motor()
            motor_kaydet(m)
            import reymen.core.oauth_manager as om_mod
            om_mod._oauth_manager_instance = om
            result = m.tools["OAUTH_DURUM"](provider="test_gecerli")
            assert "✅" in result
            assert "e@mail.com" in result
            assert "TestUser" in result
            assert "read write" in result
