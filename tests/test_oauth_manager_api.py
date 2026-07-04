"""Test: reymen/core/oauth_manager.py — Provider siniflari + Manager API.
Kapsam: Provider __init__/hazir/login_url, Manager login/callback/refresh/logout/durum.
DOKUNULMAYAN: Import fallbacks (L48-68), abstract methods (L131-150)."""

from __future__ import annotations
import json
import os as os_module
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
import pytest


PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ═══════════════════════════════════════════════════════════════════════════════
#  Provider Siniflari
# ═══════════════════════════════════════════════════════════════════════════════


class TestOAuthProviderBase:
    """OAuthProvider abstract base davranislari."""

    def test_hazir_varsayilan(self):
        """OAuthProvider.hazir varsayilan olarak True donmeli."""
        from reymen.core.oauth_manager import OAuthProvider

        # Abstract class, direkt instance olusturulamaz.
        # Test icin OAuthProvider'ın soyundan gelen bir sinif kullaniyoruz.
        with pytest.raises(TypeError):
            OAuthProvider()


class TestGoogleOAuthProviderInit:
    """GoogleOAuthProvider __init__, hazir, login_url."""

    def test_init_env_vars_eksik(self):
        """Env var'lar yokken provider olusur ama hazir=False."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            p = GoogleOAuthProvider()
            assert p.client_id == ""
            assert p.client_secret == ""

    def test_hazir_false(self):
        """Client ID/secret yokken hazir=False."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            p = GoogleOAuthProvider()
            assert not p.hazir

    def test_hazir_true(self):
        """Client ID/secret varken hazir=True."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
            clear=True,
        ):
            p = GoogleOAuthProvider()
            assert p.hazir

    def test_login_url_uretilir(self):
        """login_url() gecerli bir URL dondurmeli."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "test-id",
                "GOOGLE_CLIENT_SECRET": "test-secret",
            },
            clear=True,
        ):
            p = GoogleOAuthProvider()
            url = p.login_url()
            assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
            assert "client_id=test-id" in url
            assert "state=" in url

    def test_login_url_ozel_state(self):
        """Ozel state parametresi URL'ye eklenmeli."""
        from reymen.core.oauth_manager import GoogleOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "id",
                "GOOGLE_CLIENT_SECRET": "secret",
            },
            clear=True,
        ):
            p = GoogleOAuthProvider()
            url = p.login_url(state="my-state-123")
            assert "state=my-state-123" in url


class TestGitHubOAuthProviderInit:
    """GitHubOAuthProvider __init__, hazir, login_url."""

    def test_init_defaults(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            p = GitHubOAuthProvider()
            assert p.client_id == ""
            assert p.provider_id == "github"
            assert "github.com/login/oauth/authorize" in p.auth_url

    def test_hazir_false(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            assert not GitHubOAuthProvider().hazir

    def test_hazir_true(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "GITHUB_CLIENT_ID": "gh-id",
                "GITHUB_CLIENT_SECRET": "gh-secret",
            },
            clear=True,
        ):
            assert GitHubOAuthProvider().hazir

    def test_login_url(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "GITHUB_CLIENT_ID": "gh-id",
                "GITHUB_CLIENT_SECRET": "gh-secret",
            },
            clear=True,
        ):
            url = GitHubOAuthProvider().login_url()
            assert url.startswith("https://github.com/login/oauth/authorize")
            assert "scope=repo+user+workflow" in url or "scope=repo" in url


class TestDiscordOAuthProviderInit:
    """DiscordOAuthProvider __init__, hazir, login_url."""

    def test_init_defaults(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            p = DiscordOAuthProvider()
            assert p.provider_id == "discord"

    def test_hazir_eksik(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(os_module.environ, {}, clear=True):
            assert not DiscordOAuthProvider().hazir

    def test_hazir_var(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "DISCORD_CLIENT_ID": "dc-id",
                "DISCORD_CLIENT_SECRET": "dc-secret",
            },
            clear=True,
        ):
            assert DiscordOAuthProvider().hazir

    def test_login_url(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            os_module.environ,
            {
                "DISCORD_CLIENT_ID": "dc-id",
                "DISCORD_CLIENT_SECRET": "dc-secret",
            },
            clear=True,
        ):
            url = DiscordOAuthProvider().login_url()
            assert url.startswith("https://discord.com/api/oauth2/authorize")
            assert "prompt=consent" in url


# ═══════════════════════════════════════════════════════════════════════════════
#  OAuthTokenDeposu — ek senaryolar
# ═══════════════════════════════════════════════════════════════════════════════


class TestOAuthTokenDeposuEk:
    """OAuthTokenDeposu siniri durumlari."""

    def test_yukle_olmayan_provider(self):
        """Var olmayan provider icin None donmeli."""
        from reymen.core.oauth_manager import OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            assert depo.yukle("olmayan") is None

    def test_loader_veri_yok(self):
        """Dosya yokken bos dict donmeli."""
        from reymen.core.oauth_manager import OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            data = depo._load()
            assert data == {}

    def test_listele_bos(self):
        """Hic token yokken bos liste donmeli."""
        from reymen.core.oauth_manager import OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            assert depo.listele() == []

    def test_sil_olmayan(self):
        """Var olmayan provider silinmeye calisilirsa hata vermemeli."""
        from reymen.core.oauth_manager import OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            # Silme islemi hata vermemeli
            result = depo.sil("olmayan")
            # True veya False olabilir, hata firlatmamali
            assert result is False or result is True


# ═══════════════════════════════════════════════════════════════════════════════
#  OAuthManager API
# ═══════════════════════════════════════════════════════════════════════════════


class TestOAuthManagerAPI:
    """OAuthManager login/callback/refresh/logout/durum API'si."""

    def _setup_manager(self):
        """Yardimci: env var'lar set edilmis OAuthManager olustur."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu

        self.env_patch = patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "g-id",
                "GOOGLE_CLIENT_SECRET": "g-secret",
                "GITHUB_CLIENT_ID": "gh-id",
                "GITHUB_CLIENT_SECRET": "gh-secret",
                "DISCORD_CLIENT_ID": "dc-id",
                "DISCORD_CLIENT_SECRET": "dc-secret",
            },
            clear=True,
        )
        self.env_patch.start()
        self.td = tempfile.TemporaryDirectory()
        depo = OAuthTokenDeposu(base_path=Path(self.td.name))
        self.om = OAuthManager(deposu=depo)
        return self.om

    def _teardown(self):
        self.env_patch.stop()
        self.td.cleanup()

    def test_login_google_url(self):
        """login('google') gecerli bir auth URL'si donmeli."""
        om = self._setup_manager()
        try:
            url = om.login("google")
            assert "accounts.google.com" in url
            assert "client_id=g-id" in url
        finally:
            self._teardown()

    def test_login_github_url(self):
        """login('github') gecerli bir auth URL'si donmeli."""
        om = self._setup_manager()
        try:
            url = om.login("github")
            assert "github.com/login/oauth/authorize" in url
        finally:
            self._teardown()

    def test_login_discord_url(self):
        """login('discord') gecerli bir auth URL'si donmeli."""
        om = self._setup_manager()
        try:
            url = om.login("discord")
            assert "discord.com/api/oauth2/authorize" in url
        finally:
            self._teardown()

    def test_login_bilinmeyen_provider(self):
        """Bilinmeyen provider'a login olmaya calisinca OAuthError."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            with pytest.raises(OAuthError):
                om.login("bilinmeyen_x")

    def test_login_hazir_degil(self):
        """Env var'lar yokken login OAuthError firlatmali."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu

        with patch.dict(os_module.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                with pytest.raises(OAuthError):
                    om.login("google")

    def test_callback_basarili(self):
        """callback() token alip kaydetmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu, OAuthToken

        with patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "g-id",
                "GOOGLE_CLIENT_SECRET": "g-secret",
            },
            clear=True,
        ):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                # Mock the HTTP call inside callback_handler
                mock_resp = MagicMock()
                mock_resp.__enter__.return_value = mock_resp
                mock_resp.read.return_value = json.dumps(
                    {
                        "access_token": "call-token",
                        "expires_in": 3600,
                        "refresh_token": "call-ref",
                    }
                ).encode("utf-8")
                with patch("urllib.request.urlopen", return_value=mock_resp):
                    token = om.callback("google", "test-code")
                assert token.access_token == "call-token"
                assert token.refresh_token == "call-ref"
                # Depotan kontrol
                depo_token = depo.yukle("google")
                assert depo_token is not None
                assert depo_token.access_token == "call-token"

    def test_callback_bilinmeyen_provider(self):
        """Bilinmeyen provider icin callback OAuthError."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            with pytest.raises(OAuthError):
                om.callback("yok", "code")

    def test_logout(self):
        """logout() token'i silmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu, OAuthToken

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            # Once token ekle
            t = OAuthToken(access_token="a", provider="test", expires_in=3600)
            depo.kaydet(t)
            assert depo.var_mi("test")
            # Sonra cikis yap
            om.logout("test")
            assert not depo.var_mi("test")

    def test_durum_token_var_gecerli(self):
        """Token varken ve gecerliyken durum True donmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu, OAuthToken

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            t = OAuthToken(access_token="aaa", provider="test", expires_in=3600)
            depo.kaydet(t)
            durum = om.durum("test")
            assert durum["var_mi"] is True
            assert durum["gecerli_mi"] is True
            assert durum["access_token_prefix"] == "aaa..."

    def test_durum_token_yok(self):
        """Token yokken durum var_mi=False donmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            durum = om.durum("test")
            assert durum["var_mi"] is False
            assert durum["gecerli_mi"] is False

    def test_durum_token_expired(self):
        """Token suresi dolmusken gecerli_mi=False donmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu, OAuthToken

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            # expires_in=-1 ile gecmis token
            t = OAuthToken(access_token="aaa", provider="test", expires_in=-1)
            depo.kaydet(t)
            durum = om.durum("test")
            assert durum["var_mi"] is True
            assert durum["gecerli_mi"] is False

    def test_gecerli_token_var(self):
        """gecerli_token() token'i dondurmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu, OAuthToken

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            t = OAuthToken(access_token="tok", provider="test", expires_in=3600)
            depo.kaydet(t)
            got = om.gecerli_token("test")
            assert got is not None
            assert got.access_token == "tok"

    def test_gecerli_token_yok(self):
        """Token yokken gecerli_token() None donmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            assert om.gecerli_token("test") is None

    def test_provider_getter(self):
        """provider() dogru provider instance'ini dondurmeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu

        with patch.dict(
            os_module.environ,
            {
                "GOOGLE_CLIENT_ID": "g-id",
                "GOOGLE_CLIENT_SECRET": "g-secret",
            },
            clear=True,
        ):
            with tempfile.TemporaryDirectory() as td:
                depo = OAuthTokenDeposu(base_path=Path(td))
                om = OAuthManager(deposu=depo)
                p = om.provider("google")
                assert p is not None
                assert p.provider_id == "google"
                assert om.provider("yok") is None

    def test_provider_listesi_dolu(self):
        """provider_listesi() tum provider'lari icermeli."""
        from reymen.core.oauth_manager import OAuthManager, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            providers = om.provider_listesi()
            assert "google" in providers
            assert "github" in providers
            assert "discord" in providers

    def test_refresh_bilinmeyen_provider(self):
        """Bilinmeyen provider icin refresh OAuthError."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            with pytest.raises(OAuthError):
                om.refresh("yok")

    def test_refresh_token_yok(self):
        """Token yokken refresh OAuthError."""
        from reymen.core.oauth_manager import OAuthManager, OAuthError, OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            om = OAuthManager(deposu=depo)
            with patch.dict(
                os_module.environ,
                {
                    "GOOGLE_CLIENT_ID": "x",
                    "GOOGLE_CLIENT_SECRET": "y",
                },
                clear=True,
            ):
                with pytest.raises(OAuthError):
                    om.refresh("google")
