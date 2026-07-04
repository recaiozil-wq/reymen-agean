"""Test: reymen/core/oauth_manager.py - HTTP mock L184-528"""

from __future__ import annotations
import os, sys, json, urllib
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


def _mock_response(data: dict, status: int = 200) -> MagicMock:
    """Create a mock urllib response"""
    body = json.dumps(data).encode("utf-8")
    m = MagicMock()
    m.__enter__.return_value = m
    m.read.return_value = body
    m.status = status
    m.getcode.return_value = status
    return m


def _mock_http_error(code: int = 400, body: str = "error") -> urllib.error.HTTPError:
    """Create a mock HTTPError"""
    return urllib.error.HTTPError(
        url="http://example.com",
        code=code,
        msg="Error",
        hdrs={},
        fp=io.BytesIO(body.encode("utf-8")),
    )


import io


class TestGoogleOAuthProvider:
    """L186-271: Google OAuth provider HTTP mock testleri"""

    def test_login_url_olusturur(self):
        """L186-199: State verilmeden login URL olusur"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id-123",
                "GOOGLE_CLIENT_SECRET": "test-secret-456",
            },
        ):
            p = GoogleOAuthProvider()
            url = p.login_url()
            assert "accounts.google.com" in url
            assert "client_id=test-id-123" in url

    def test_login_url_state_ile(self):
        """L188: State parametresi ile login URL"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id-123",
                "GOOGLE_CLIENT_SECRET": "test-secret-456",
            },
        ):
            p = GoogleOAuthProvider()
            url = p.login_url(state="my-state-abc")
            assert "state=my-state-abc" in url

    def test_hazir_true(self):
        """L183-184: hazir property dogru"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            assert p.hazir is True

    def test_hazir_false(self):
        """L183-184: Client bilgisi yoksa hazir=False"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(os.environ, {}, clear=True):
            p = GoogleOAuthProvider()
            assert p.hazir is False

    def test_callback_handler_basarili(self):
        """L201-228: Authorization code ile token al - HTTP mock"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()

            token_data = {
                "access_token": "ya29.token123",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "1//refresh456",
                "scope": "openid email profile",
            }
            user_data = {
                "id": "user-789",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.png",
            }

            mock_responses = [
                _mock_response(token_data),  # token endpoint
                _mock_response(user_data),  # userinfo endpoint
            ]

            with patch("urllib.request.urlopen", side_effect=mock_responses):
                token = p.callback_handler("auth-code-xyz")

            assert token.access_token == "ya29.token123"
            assert token.refresh_token == "1//refresh456"
            assert token.provider == "google"
            assert token.email == "test@example.com"
            assert token.user_id == "user-789"

    def test_callback_handler_http_error(self):
        """L259-261: Token alirken HTTP hatasi -> OAuthError"""
        from reymen.core.oauth_manager import GoogleOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=400,
                msg="Bad Request",
                hdrs={},
                fp=io.BytesIO(b"invalid_grant"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError) as exc:
                    p.callback_handler("bad-code")
                assert "HTTP 400" in str(exc.value)

    def test_callback_handler_userinfo_hatasi(self):
        """L226-227: Userinfo hatasi -> log, token yine de doner"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            token_data = {
                "access_token": "ya29.token123",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
            mock_responses = [
                _mock_response(token_data),
                urllib.error.HTTPError(
                    url="http://example.com",
                    code=401,
                    msg="Unauthorized",
                    hdrs={},
                    fp=io.BytesIO(b"invalid_token"),
                ),
            ]
            with patch("urllib.request.urlopen", side_effect=mock_responses):
                token = p.callback_handler("code")
            assert token.access_token == "ya29.token123"
            assert token.email == ""  # Userinfo alinamadi

    def test_token_refresh_basarili(self):
        """L230-244: Refresh token ile yeni access token"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            refresh_data = {
                "access_token": "new-token-abc",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "openid email",
            }
            with patch(
                "urllib.request.urlopen", return_value=_mock_response(refresh_data)
            ):
                token = p.token_refresh("old-refresh-token")
            assert token.access_token == "new-token-abc"
            assert token.refresh_token == "old-refresh-token"

    def test_get_user_info_basarili(self):
        """L246-247: Access token ile kullanici bilgisi"""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            user_data = {"email": "user@test.com", "name": "Test"}
            with patch(
                "urllib.request.urlopen", return_value=_mock_response(user_data)
            ):
                result = p.get_user_info("token-123")
            assert result["email"] == "user@test.com"

    def test_get_user_info_http_error(self):
        """L269-271: Userinfo HTTP hatasi -> OAuthError"""
        from reymen.core.oauth_manager import GoogleOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
        ):
            p = GoogleOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=403,
                msg="Forbidden",
                hdrs={},
                fp=io.BytesIO(b"access_denied"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.get_user_info("bad-token")


class TestGitHubOAuthProvider:
    """L286-381: GitHub OAuth provider HTTP mock testleri"""

    def test_login_url_olusturur(self):
        """L307-318: GitHub login URL"""
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "github-id",
                "GITHUB_CLIENT_SECRET": "github-secret",
            },
        ):
            p = GitHubOAuthProvider()
            url = p.login_url()
            assert "github.com/login/oauth/authorize" in url
            assert "client_id=github-id" in url

    def test_hazir_true(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ, {"GITHUB_CLIENT_ID": "id", "GITHUB_CLIENT_SECRET": "secret"}
        ):
            assert GitHubOAuthProvider().hazir is True

    def test_hazir_false(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(os.environ, {}, clear=True):
            assert GitHubOAuthProvider().hazir is False

    def test_callback_handler_basarili(self):
        """L320-359: GitHub callback HTTP mock"""
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "id",
                "GITHUB_CLIENT_SECRET": "secret",
            },
        ):
            p = GitHubOAuthProvider()
            token_data = {
                "access_token": "gho_token123",
                "token_type": "bearer",
                "scope": "repo",
            }
            user_data = {
                "id": 12345,
                "email": "dev@github.com",
                "name": "Dev",
                "login": "devuser",
                "avatar_url": "https://avatars.github.com/u/12345",
            }
            mock_responses = [
                _mock_response(token_data),
                _mock_response(user_data),
            ]
            with patch("urllib.request.urlopen", side_effect=mock_responses):
                token = p.callback_handler("code-xyz")
            assert token.access_token == "gho_token123"
            assert token.provider == "github"
            assert token.email == "dev@github.com"

    def test_callback_handler_http_error(self):
        """L338-340: GitHub callback HTTP hatasi"""
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "id",
                "GITHUB_CLIENT_SECRET": "secret",
            },
        ):
            p = GitHubOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=401,
                msg="Bad creds",
                hdrs={},
                fp=io.BytesIO(b"bad_verification_code"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.callback_handler("bad-code")

    def test_token_refresh_hata_firlatir(self):
        """L361-363: GitHub refresh token yok -> OAuthError"""
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "id",
                "GITHUB_CLIENT_SECRET": "secret",
            },
        ):
            p = GitHubOAuthProvider()
            with pytest.raises(OAuthError) as exc:
                p.token_refresh("old-token")
            assert "sureklidir" in str(exc.value).lower() or "süreklidir" in str(
                exc.value
            )

    def test_get_user_info_basarili(self):
        """L365-381: GitHub userinfo"""
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "id",
                "GITHUB_CLIENT_SECRET": "secret",
            },
        ):
            p = GitHubOAuthProvider()
            user_data = {"id": 999, "login": "testuser", "name": "Test"}
            with patch(
                "urllib.request.urlopen", return_value=_mock_response(user_data)
            ):
                result = p.get_user_info("token")
            assert result["id"] == 999

    def test_get_user_info_http_error(self):
        """L379-381: GitHub userinfo HTTPError"""
        from reymen.core.oauth_manager import GitHubOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "GITHUB_CLIENT_ID": "id",
                "GITHUB_CLIENT_SECRET": "secret",
            },
        ):
            p = GitHubOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=403,
                msg="Rate limit",
                hdrs={},
                fp=io.BytesIO(b"rate_limit_exceeded"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.get_user_info("bad-token")


class TestDiscordOAuthProvider:
    """L396-526: Discord OAuth provider HTTP mock testleri"""

    def test_login_url_olusturur(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "discord-id",
                "DISCORD_CLIENT_SECRET": "discord-secret",
            },
        ):
            p = DiscordOAuthProvider()
            url = p.login_url()
            assert "discord.com/api/oauth2/authorize" in url

    def test_hazir_true(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ, {"DISCORD_CLIENT_ID": "id", "DISCORD_CLIENT_SECRET": "secret"}
        ):
            assert DiscordOAuthProvider().hazir is True

    def test_hazir_false(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(os.environ, {}, clear=True):
            assert DiscordOAuthProvider().hazir is False

    def test_callback_handler_basarili(self):
        """L430-478: Discord callback HTTP mock"""
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "discord-id",
                "DISCORD_CLIENT_SECRET": "discord-secret",
            },
        ):
            p = DiscordOAuthProvider()
            token_data = {
                "access_token": "discord_token_abc",
                "token_type": "Bearer",
                "expires_in": 604800,
                "refresh_token": "discord_refresh_xyz",
                "scope": "identify email",
            }
            user_data = {
                "id": "123456789",
                "email": "user@discord.com",
                "global_name": "DiscordUser",
                "username": "discorduser",
                "avatar": "abc123",
            }
            mock_responses = [
                _mock_response(token_data),
                _mock_response(user_data),
            ]
            with patch("urllib.request.urlopen", side_effect=mock_responses):
                token = p.callback_handler("discord-code")
            assert token.access_token == "discord_token_abc"
            assert token.refresh_token == "discord_refresh_xyz"
            assert token.provider == "discord"
            assert token.email == "user@discord.com"
            assert "discordapp.com/avatars" in token.avatar_url

    def test_callback_handler_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "id",
                "DISCORD_CLIENT_SECRET": "secret",
            },
        ):
            p = DiscordOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=400,
                msg="Bad",
                hdrs={},
                fp=io.BytesIO(b"invalid_code"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.callback_handler("bad-code")

    def test_token_refresh_basarili(self):
        """L480-511: Discord token refresh HTTP mock"""
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "id",
                "DISCORD_CLIENT_SECRET": "secret",
            },
        ):
            p = DiscordOAuthProvider()
            refresh_data = {
                "access_token": "new_discord_token",
                "token_type": "Bearer",
                "expires_in": 604800,
                "refresh_token": "new_refresh",
                "scope": "identify",
            }
            with patch(
                "urllib.request.urlopen", return_value=_mock_response(refresh_data)
            ):
                token = p.token_refresh("old_refresh")
            assert token.access_token == "new_discord_token"
            assert token.provider == "discord"

    def test_token_refresh_http_error(self):
        """L500-502: Discord refresh HTTPError"""
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "id",
                "DISCORD_CLIENT_SECRET": "secret",
            },
        ):
            p = DiscordOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=429,
                msg="Rate limited",
                hdrs={},
                fp=io.BytesIO(b"too_many_requests"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.token_refresh("bad-refresh")

    def test_get_user_info_basarili(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "id",
                "DISCORD_CLIENT_SECRET": "secret",
            },
        ):
            p = DiscordOAuthProvider()
            user_data = {
                "id": "98765",
                "username": "discord_user",
                "global_name": "DiscordUser",
            }
            with patch(
                "urllib.request.urlopen", return_value=_mock_response(user_data)
            ):
                result = p.get_user_info("token")
            assert result["id"] == "98765"

    def test_get_user_info_http_error(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider, OAuthError

        with patch.dict(
            os.environ,
            {
                "DISCORD_CLIENT_ID": "id",
                "DISCORD_CLIENT_SECRET": "secret",
            },
        ):
            p = DiscordOAuthProvider()
            error_resp = urllib.error.HTTPError(
                url="http://example.com",
                code=401,
                msg="Unauthorized",
                hdrs={},
                fp=io.BytesIO(b"unauthorized"),
            )
            with patch("urllib.request.urlopen", side_effect=error_resp):
                with pytest.raises(OAuthError):
                    p.get_user_info("bad-token")


class TestOAuthToken:
    """OAuthToken yapisi - L76-99"""

    def test_is_expired_true(self):
        from reymen.core.oauth_manager import OAuthToken
        import time

        t = OAuthToken(access_token="tok", expires_in=1, obtained_at=time.time() - 100)
        assert t.is_expired is True

    def test_is_expired_false(self):
        from reymen.core.oauth_manager import OAuthToken
        import time

        t = OAuthToken(access_token="tok", expires_in=3600, obtained_at=time.time())
        assert t.is_expired is False

    def test_expires_at_formati(self):
        from reymen.core.oauth_manager import OAuthToken

        t = OAuthToken(access_token="tok", expires_in=3600)
        assert "T" in t.expires_at
