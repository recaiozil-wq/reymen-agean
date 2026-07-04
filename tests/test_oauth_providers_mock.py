"""Test: reymen/core/oauth_manager.py — HTTP mock ile provider testleri.
Kapsanan satirlar: 184-528 (Google, GitHub, Discord saglayicilari).
Senaryolar: token expire, API error, user info hatasi."""

from __future__ import annotations
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import urllib.request
import urllib.error

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ── Yardimcilar ──────────────────────────────────────────────────────────────


def _mock_urlopen(status=200, data=None):
    """Mock urllib.request.urlopen donen bir context manager."""
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status = status
    body = json.dumps(data or {}).encode("utf-8")
    mock_resp.read.return_value = body
    mock_resp.__enter__.return_value.read.return_value = body
    return mock_resp


def _mock_http_error(code=400, body="Hata"):
    """Mock HTTPError yukselten bir urlopen."""
    mock_err = MagicMock()
    mock_err.code = code
    mock_err.fp = MagicMock()
    mock_err.fp.read.return_value = json.dumps({"error": body}).encode("utf-8")
    return urllib.error.HTTPError(
        url="http://test.com", code=code, msg=body, hdrs={}, fp=mock_err.fp
    )


class TestGoogleOAuthProviderHTTP:
    """Google saglayicisi HTTP mock testleri."""

    def test_callback_handler_basarili(self):
        """Callback: basarili token alimi + kullanici bilgisi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()
        provider.client_id = "test-id"
        provider.client_secret = "test-secret"
        provider.redirect_uri = "http://localhost/callback"

        token_data = {
            "access_token": "abc123",
            "expires_in": 3600,
            "refresh_token": "ref1",
            "token_type": "Bearer",
            "scope": "email profile",
        }
        user_data = {
            "id": "user1",
            "email": "a@b.com",
            "name": "Test User",
            "picture": "http://pic",
        }

        with patch("urllib.request.urlopen") as m:
            # Ilk cagri (token) -> token_data
            # Ikinci cagri (userinfo) -> user_data
            m.side_effect = [
                _mock_urlopen(data=token_data),
                _mock_urlopen(data=user_data),
            ]
            token = provider.callback_handler("authcode123")
            assert token.access_token == "abc123"
            assert token.refresh_token == "ref1"
            assert token.user_id == "user1"
            assert token.email == "a@b.com"
            assert token.display_name == "Test User"

    def test_callback_handler_http_hatasi(self):
        """Callback: token endpoint HTTP hatasi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()
        provider.client_id = "test-id"
        provider.client_secret = "test-secret"

        with patch(
            "urllib.request.urlopen", side_effect=_mock_http_error(400, "invalid_grant")
        ):
            with pytest.raises(Exception) as exc:
                provider.callback_handler("bad-code")
            assert "400" in str(exc.value) or "invalid_grant" in str(exc.value)

    def test_callback_handler_userinfo_hatasi(self):
        """Callback: token basarili ama userinfo hatasi -> token yine de doner."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()
        provider.client_id = "test-id"
        provider.client_secret = "test-secret"

        with patch("urllib.request.urlopen") as m:
            m.side_effect = [
                _mock_urlopen(data={"access_token": "abc", "expires_in": 3600}),
                _mock_http_error(401, "invalid_token"),
            ]
            token = provider.callback_handler("code")
            assert token.access_token == "abc"
            # Kullanici bilgisi bos olmali (hata yutuldu)
            assert token.user_id == ""

    def test_token_refresh_basarili(self):
        """Token yenileme basarili."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()
        provider.client_id = "test-id"
        provider.client_secret = "test-secret"

        with patch("urllib.request.urlopen") as m:
            m.return_value = _mock_urlopen(
                data={
                    "access_token": "new-token",
                    "expires_in": 3600,
                }
            )
            token = provider.token_refresh("old-refresh")
            assert token.access_token == "new-token"
            assert token.refresh_token == "old-refresh"

    def test_token_refresh_http_hatasi(self):
        """Token yenileme: HTTP hatasi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()
        provider.client_id = "test-id"
        provider.client_secret = "test-secret"

        with patch(
            "urllib.request.urlopen", side_effect=_mock_http_error(401, "invalid_token")
        ):
            with pytest.raises(Exception):
                provider.token_refresh("bad-refresh")

    def test_get_user_info_basarili(self):
        """Kullanici bilgisi alma."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()

        with patch("urllib.request.urlopen") as m:
            m.return_value = _mock_urlopen(
                data={"sub": "u123", "email": "x@y.com", "name": "User"}
            )
            info = provider.get_user_info("token123")
            assert info["email"] == "x@y.com"
            assert info["name"] == "User"

    def test_get_user_info_http_hatasi(self):
        """Kullanici bilgisi: HTTP hatasi."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        provider = GoogleOAuthProvider()

        with patch(
            "urllib.request.urlopen", side_effect=_mock_http_error(403, "forbidden")
        ):
            with pytest.raises(Exception):
                provider.get_user_info("bad-token")


class TestGitHubOAuthProviderHTTP:
    """GitHub saglayicisi HTTP mock testleri."""

    def test_callback_handler_basarili(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        provider = GitHubOAuthProvider()
        provider.client_id = "gh-id"
        provider.client_secret = "gh-secret"

        with patch("urllib.request.urlopen") as m:
            m.side_effect = [
                _mock_urlopen(
                    data={
                        "access_token": "gh-token",
                        "token_type": "bearer",
                        "scope": "repo",
                    }
                ),
                _mock_urlopen(
                    data={
                        "id": 42,
                        "login": "ghuser",
                        "email": "gh@b.com",
                        "name": "GH User",
                        "avatar_url": "http://av",
                    }
                ),
            ]
            token = provider.callback_handler("gh-code")
            assert token.access_token == "gh-token"
            assert token.user_id == "42"
            assert token.provider == "github"

    def test_callback_handler_http_hatasi(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        provider = GitHubOAuthProvider()
        provider.client_id = "gh-id"
        provider.client_secret = "gh-secret"

        with patch(
            "urllib.request.urlopen",
            side_effect=_mock_http_error(401, "bad_verification_code"),
        ):
            with pytest.raises(Exception):
                provider.callback_handler("bad-code")

    def test_token_refresh_hata_firlatir(self):
        """GitHub'ta refresh_token yok -> OAuthError firlar."""
        from reymen.core.oauth_manager import GitHubOAuthProvider

        provider = GitHubOAuthProvider()
        with pytest.raises(Exception) as exc:
            provider.token_refresh("anything")
        assert "refresh gerekmez" in str(exc.value)

    def test_get_user_info(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        provider = GitHubOAuthProvider()

        with patch("urllib.request.urlopen") as m:
            m.return_value = _mock_urlopen(data={"login": "ghuser", "id": 1})
            info = provider.get_user_info("tok")
            assert info["login"] == "ghuser"


class TestDiscordOAuthProviderHTTP:
    """Discord saglayicisi HTTP mock testleri (Basic Auth ile)."""

    def test_callback_handler_basarili(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        provider.client_id = "dc-id"
        provider.client_secret = "dc-secret"

        with patch("urllib.request.urlopen") as m:
            m.side_effect = [
                _mock_urlopen(
                    data={
                        "access_token": "dc-tok",
                        "token_type": "Bearer",
                        "expires_in": 3600,
                        "refresh_token": "dc-ref",
                    }
                ),
                _mock_urlopen(
                    data={
                        "id": "12345",
                        "email": "dc@x.com",
                        "global_name": "DC User",
                        "username": "dcuser",
                        "avatar": "abc123",
                    }
                ),
            ]
            token = provider.callback_handler("dc-code")
            assert token.access_token == "dc-tok"
            assert token.refresh_token == "dc-ref"
            assert token.user_id == "12345"
            assert token.email == "dc@x.com"
            assert token.display_name == "DC User"

    def test_callback_handler_avatar_gif(self):
        """a_ ile baslayan avatar hash -> gif uzantisi."""
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        provider.client_id = "dc-id"
        provider.client_secret = "dc-secret"

        with patch("urllib.request.urlopen") as m:
            m.side_effect = [
                _mock_urlopen(data={"access_token": "t", "expires_in": 3600}),
                _mock_urlopen(
                    data={"id": "99", "username": "u", "avatar": "a_animated123"}
                ),
            ]
            token = provider.callback_handler("code")
            assert "gif" in token.avatar_url

    def test_callback_handler_http_hatasi(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        provider.client_id = "dc-id"
        provider.client_secret = "dc-secret"

        with patch(
            "urllib.request.urlopen", side_effect=_mock_http_error(400, "invalid_code")
        ):
            with pytest.raises(Exception):
                provider.callback_handler("bad")

    def test_token_refresh_basarili(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        provider.client_id = "dc-id"
        provider.client_secret = "dc-secret"

        with patch("urllib.request.urlopen") as m:
            m.return_value = _mock_urlopen(
                data={
                    "access_token": "new-dc-tok",
                    "expires_in": 3600,
                }
            )
            token = provider.token_refresh("old-ref")
            assert token.access_token == "new-dc-tok"
            assert token.refresh_token == "old-ref"

    def test_token_refresh_http_hatasi(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        provider.client_id = "dc-id"
        provider.client_secret = "dc-secret"

        with patch(
            "urllib.request.urlopen", side_effect=_mock_http_error(401, "invalid_token")
        ):
            with pytest.raises(Exception):
                provider.token_refresh("bad-ref")

    def test_get_user_info(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        provider = DiscordOAuthProvider()
        with patch("urllib.request.urlopen") as m:
            m.return_value = _mock_urlopen(data={"id": "1", "username": "u"})
            info = provider.get_user_info("tok")
            assert info["id"] == "1"
