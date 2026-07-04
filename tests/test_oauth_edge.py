"""Test: oauth_manager.py kalan sinir durumlari."""

from __future__ import annotations
import json, sys, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestOAuthEdgeCases:
    """OAuth sinir durumlari: avatar yok, userinfo error, refresh hata."""

    def test_discord_avatar_yok(self):
        from reymen.core.oauth_manager import DiscordOAuthProvider

        with patch.dict(
            "os.environ",
            {"DISCORD_CLIENT_ID": "d", "DISCORD_CLIENT_SECRET": "s"},
            clear=True,
        ):
            p = DiscordOAuthProvider()
            m1 = MagicMock()
            m1.__enter__.return_value = m1
            m1.read.return_value = json.dumps(
                {"access_token": "t", "expires_in": 3600}
            ).encode()
            m2 = MagicMock()
            m2.__enter__.return_value = m2
            m2.read.return_value = json.dumps(
                {"id": "123", "username": "u", "avatar": None}
            ).encode()
            with patch("urllib.request.urlopen") as m:
                m.side_effect = [m1, m2]
                token = p.callback_handler("c")
                assert token.avatar_url == ""

    def test_github_userinfo_hatasi(self):
        from reymen.core.oauth_manager import GitHubOAuthProvider
        from urllib.error import HTTPError

        with patch.dict(
            "os.environ",
            {"GITHUB_CLIENT_ID": "g", "GITHUB_CLIENT_SECRET": "s"},
            clear=True,
        ):
            p = GitHubOAuthProvider()
            m1 = MagicMock()
            m1.__enter__.return_value = m1
            m1.read.return_value = json.dumps(
                {"access_token": "t", "token_type": "bearer"}
            ).encode()
            err_fp = MagicMock()
            err_fp.read.return_value = b"{}"
            http_err = HTTPError("http://x", 403, "Forbidden", {}, err_fp)
            with patch("urllib.request.urlopen") as m:
                m.side_effect = [m1, http_err]
                token = p.callback_handler("c")
                assert token.access_token == "t"
                assert token.user_id == ""

    def test_oauth_error_code(self):
        from reymen.core.oauth_manager import OAuthError

        e = OAuthError("msg", provider="test", status_code=403, code="custom_err")
        assert e.code == "custom_err"
        assert e.status_code == 403
        assert str(e) == "msg"

    def test_token_expired(self):
        from reymen.core.oauth_manager import OAuthToken

        t = OAuthToken(access_token="t", provider="p", expires_in=-10)
        assert t.is_expired is True

    def test_depo_bozuk_json(self):
        from reymen.core.oauth_manager import OAuthTokenDeposu

        with tempfile.TemporaryDirectory() as td:
            depo = OAuthTokenDeposu(base_path=Path(td))
            (Path(td) / "oauth_tokens.json").write_text("bozuk json {{{")
            data = depo._load()
            assert data == {}
