"""Test: reymen/core/oauth_manager.py - HTTP/urllib mock ile provider testleri"""

from __future__ import annotations
import os, sys, json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGoogleOAuthMock:
    def test_login_url_olusturma(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "test_id", "GOOGLE_CLIENT_SECRET": "test_secret"},
        ):
            p = GoogleOAuthProvider()
            url = p.login_url(state="test_state")
            assert "test_id" in url
            assert "test_state" in url

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ, {"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "secret"}
        ):
            p = GoogleOAuthProvider()
            with patch.object(
                p,
                "_http_post",
                return_value={
                    "access_token": "ya29.mock",
                    "expires_in": 3600,
                    "refresh_token": "rf",
                    "token_type": "Bearer",
                },
            ):
                with patch.object(
                    p, "get_user_info", return_value={"sub": "123", "email": "a@b.com"}
                ):
                    token = p.callback_handler("code_xyz")
                    assert token.access_token == "ya29.mock"
                    assert token.provider == "google"

    def test_callback_error_response(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ, {"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "secret"}
        ):
            p = GoogleOAuthProvider()
            # Hata response'u da token olusturur (bos access_token ile)
            with patch.object(p, "_http_post", return_value={"error": "invalid_grant"}):
                with patch.object(p, "get_user_info", return_value={}):
                    token = p.callback_handler("wrong_code")
                    assert token.access_token == ""

    def test_token_refresh(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ, {"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "secret"}
        ):
            p = GoogleOAuthProvider()
            with patch.object(
                p,
                "_http_post",
                return_value={"access_token": "new_token", "expires_in": 3600},
            ):
                token = p.token_refresh("old_refresh")
                assert token.access_token == "new_token"

    def test_user_info(self):
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ, {"GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "secret"}
        ):
            p = GoogleOAuthProvider()
            with patch.object(
                p, "_http_get", return_value={"sub": "12345", "email": "test@gmail.com"}
            ):
                info = p.get_user_info("valid_token")
                assert info["email"] == "test@gmail.com"

    def test_token_expired(self):
        from reymen.core.oauth_manager import OAuthToken
        import time

        t = OAuthToken(
            access_token="old",
            provider="google",
            expires_in=1,
            obtained_at=time.time() - 10,
        )
        assert t.is_expired is True

    def test_token_not_expired(self):
        from reymen.core.oauth_manager import OAuthToken

        t = OAuthToken(access_token="new", provider="google", expires_in=3600)
        assert t.is_expired is False


class TestGitHubOAuthMock:
    def test_login_url(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ,
            {"GITHUB_CLIENT_ID": "gh_id", "GITHUB_CLIENT_SECRET": "gh_secret"},
        ):
            p = GitHubOAuthProvider()
            url = p.login_url(state="s1")
            assert "github.com" in url

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthToken

        with patch.dict(
            os.environ, {"GITHUB_CLIENT_ID": "id", "GITHUB_CLIENT_SECRET": "secret"}
        ):
            p = GitHubOAuthProvider()
            # urllib.request.urlopen mock
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(
                {"access_token": "gh_token"}
            ).encode()
            mock_resp.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(
                    p, "get_user_info", return_value={"id": 1, "login": "user"}
                ):
                    token = p.callback_handler("code123")
                    assert token.access_token == "gh_token"

    def test_callback_http_error(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError

        with patch.dict(
            os.environ, {"GITHUB_CLIENT_ID": "id", "GITHUB_CLIENT_SECRET": "secret"}
        ):
            p = GitHubOAuthProvider()
            import urllib.error

            error_resp = urllib.error.HTTPError(
                "http://example.com", 401, "Unauthorized", {}, None
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.callback_handler("bad_code")

    def test_user_info(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ, {"GITHUB_CLIENT_ID": "id", "GITHUB_CLIENT_SECRET": "secret"}
        ):
            p = GitHubOAuthProvider()
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(
                {"login": "testuser", "id": 123}
            ).encode()
            mock_resp.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_resp):
                info = p.get_user_info("token123")
                assert info["login"] == "testuser"

    def test_token_refresh_raises(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError

        with patch.dict(
            os.environ, {"GITHUB_CLIENT_ID": "id", "GITHUB_CLIENT_SECRET": "secret"}
        ):
            p = GitHubOAuthProvider()
            with pytest.raises(OAuthError):
                p.token_refresh("anything")


class TestDiscordOAuthMock:
    def test_login_url(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ,
            {"DISCORD_CLIENT_ID": "dc_id", "DISCORD_CLIENT_SECRET": "dc_secret"},
        ):
            p = DiscordOAuthProvider()
            url = p.login_url(state="s1")
            assert "discord.com" in url

    def test_callback_basarili(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ, {"DISCORD_CLIENT_ID": "id", "DISCORD_CLIENT_SECRET": "secret"}
        ):
            p = DiscordOAuthProvider()
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(
                {
                    "access_token": "dc_token",
                    "expires_in": 3600,
                    "refresh_token": "dc_refresh",
                    "token_type": "Bearer",
                }
            ).encode()
            mock_resp.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_resp):
                with patch.object(
                    p, "get_user_info", return_value={"id": "1", "username": "user"}
                ):
                    token = p.callback_handler("code456")
                    assert token.access_token == "dc_token"
                    assert token.refresh_token == "dc_refresh"

    def test_token_refresh(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ, {"DISCORD_CLIENT_ID": "id", "DISCORD_CLIENT_SECRET": "secret"}
        ):
            p = DiscordOAuthProvider()
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(
                {"access_token": "new_dc"}
            ).encode()
            mock_resp.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_resp):
                token = p.token_refresh("old_refresh")
                assert token.access_token == "new_dc"

    def test_user_info(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ, {"DISCORD_CLIENT_ID": "id", "DISCORD_CLIENT_SECRET": "secret"}
        ):
            p = DiscordOAuthProvider()
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(
                {"id": "12345", "username": "testuser", "global_name": "Test"}
            ).encode()
            mock_resp.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_resp):
                info = p.get_user_info("valid_token")
                assert info["username"] == "testuser"

    def test_callback_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError

        with patch.dict(
            os.environ, {"DISCORD_CLIENT_ID": "id", "DISCORD_CLIENT_SECRET": "secret"}
        ):
            p = DiscordOAuthProvider()
            import urllib.error

            error_resp = urllib.error.HTTPError(
                "http://example.com", 400, "Bad Request", {}, None
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.callback_handler("bad_code")
