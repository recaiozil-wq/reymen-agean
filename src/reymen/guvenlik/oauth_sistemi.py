# -*- coding: utf-8 -*-
"""
ğŸ” OAuth Sistemi â€” Google, GitHub, Discord OAuth 2.0 Authorization Code Flow.

Bu modül, mevcut reymen/guvenlik/oauth2.py üzerine inÅŸa edilmiÅŸtir:
  - OAuthSistemi: üst seviye sÄ±nÄ±f (provider + token yönetimi)
  - GoogleOAuthProvider: Gmail, Drive, Calendar API'leri için OAuth
  - GitHubOAuthProvider: repo, user scope'larÄ± ile GitHub OAuth
  - DiscordOAuthProvider: bot token auth (stub / geniÅŸletilmiÅŸ)
  - SQLite token persistence (oauth_tokens.db)
  - Token yenileme (refresh_token) ve expiry kontrolü

KullanÄ±m:
    sistem = OAuthSistemi()
    url = sistem.google.get_auth_url()
    token = sistem.google.exchange_code("auth_code")
    sistem.google.save_token(token)
    token = sistem.google.load_token()
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
SQLITE_DB = PROJE_KOK / ".ReYMeN" / "oauth" / "oauth_tokens.db"


# ---------------------------------------------------------------------------
# Veri yapÄ±larÄ±
# ---------------------------------------------------------------------------


@dataclass
class OAuthToken:
    """Bir OAuth provider'dan alÄ±nan token bilgisi."""

    access_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str = ""
    scope: str = ""
    provider: str = ""
    user_id: str = ""
    email: str = ""
    display_name: str = ""
    avatar_url: str = ""
    obtained_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Token süresi dolmuÅŸ mu? (60 sn grace)"""
        return time.time() > self.obtained_at + self.expires_in - 60

    @property
    def expires_at(self) -> str:
        """Token bitiÅŸ zamanÄ± (ISO format)."""
        dt = datetime.fromtimestamp(self.obtained_at + self.expires_in, tz=timezone.utc)
        return dt.isoformat()

    @property
    def expires_at_local(self) -> str:
        """Token bitiÅŸ zamanÄ± (yerel saat)."""
        dt = datetime.fromtimestamp(self.obtained_at + self.expires_in)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Hata sÄ±nÄ±fÄ±
# ---------------------------------------------------------------------------


class OAuthError(Exception):
    """OAuth iÅŸlemleri sÄ±rasÄ±nda oluÅŸan hata."""

    def __init__(
        self,
        message: str,
        provider: str = "",
        status_code: int = 0,
        code: str = "oauth_error",
    ):
        self.provider = provider
        self.status_code = status_code
        self.code = code
        super().__init__(message)


# ---------------------------------------------------------------------------
# SQLite Token Deposu
# ---------------------------------------------------------------------------


class SQLiteTokenDeposu:
    """OAuth token'larÄ±nÄ± SQLite veritabanÄ±nda saklar.

    Tablo: oauth_tokens
      provider      TEXT PRIMARY KEY  (google, github, discord)
      user_id       TEXT
      access_token  TEXT
      refresh_token TEXT
      token_type    TEXT
      expires_in    INTEGER
      scope         TEXT
      email         TEXT
      display_name  TEXT
      avatar_url    TEXT
      obtained_at   REAL
      created_at    TEXT
      updated_at    TEXT
    """

    def __init__(self, db_path: Path | str | None = None):
        self._db_path = Path(db_path or SQLITE_DB)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _baglan(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self) -> None:
        with self._baglan() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    provider      TEXT PRIMARY KEY,
                    user_id       TEXT DEFAULT '',
                    access_token  TEXT DEFAULT '',
                    refresh_token TEXT DEFAULT '',
                    token_type    TEXT DEFAULT 'Bearer',
                    expires_in    INTEGER DEFAULT 3600,
                    scope         TEXT DEFAULT '',
                    email         TEXT DEFAULT '',
                    display_name  TEXT DEFAULT '',
                    avatar_url    TEXT DEFAULT '',
                    obtained_at   REAL DEFAULT 0,
                    created_at    TEXT DEFAULT (datetime('now')),
                    updated_at    TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.commit()

    def kaydet(self, provider: str, token: OAuthToken) -> None:
        """Token'Ä± kaydet (varsa güncelle, yoksa ekle)."""
        with self._baglan() as conn:
            conn.execute(
                """
                INSERT INTO oauth_tokens
                    (provider, user_id, access_token, refresh_token, token_type,
                     expires_in, scope, email, display_name, avatar_url, obtained_at,
                     updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(provider) DO UPDATE SET
                    user_id       = excluded.user_id,
                    access_token  = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    token_type    = excluded.token_type,
                    expires_in    = excluded.expires_in,
                    scope         = excluded.scope,
                    email         = excluded.email,
                    display_name  = excluded.display_name,
                    avatar_url    = excluded.avatar_url,
                    obtained_at   = excluded.obtained_at,
                    updated_at    = datetime('now')
            """,
                (
                    provider,
                    token.user_id,
                    token.access_token,
                    token.refresh_token,
                    token.token_type,
                    token.expires_in,
                    token.scope,
                    token.email,
                    token.display_name,
                    token.avatar_url,
                    token.obtained_at,
                ),
            )
            conn.commit()

    def yukle(self, provider: str) -> Optional[OAuthToken]:
        """Provider'a ait token'Ä± yükle."""
        with self._baglan() as conn:
            row = conn.execute(
                "SELECT * FROM oauth_tokens WHERE provider = ?", (provider,)
            ).fetchone()
            if row is None:
                return None
            return OAuthToken(
                access_token=row["access_token"],
                token_type=row["token_type"],
                expires_in=row["expires_in"],
                refresh_token=row["refresh_token"],
                scope=row["scope"],
                provider=row["provider"],
                user_id=row["user_id"],
                email=row["email"],
                display_name=row["display_name"],
                avatar_url=row["avatar_url"],
                obtained_at=row["obtained_at"],
            )

    def sil(self, provider: str) -> None:
        """Provider'a ait token'Ä± sil."""
        with self._baglan() as conn:
            conn.execute("DELETE FROM oauth_tokens WHERE provider = ?", (provider,))
            conn.commit()

    def listele(self) -> list[dict[str, Any]]:
        """Tüm kayÄ±tlÄ± token'larÄ± listele."""
        with self._baglan() as conn:
            rows = conn.execute(
                "SELECT provider, user_id, email, display_name, "
                "expires_in, obtained_at, updated_at, scope "
                "FROM oauth_tokens ORDER BY provider"
            ).fetchall()
            result = []
            for row in rows:
                token = OAuthToken(
                    access_token="***",
                    token_type="",
                    expires_in=row["expires_in"],
                    provider=row["provider"],
                    user_id=row["user_id"],
                    email=row["email"],
                    display_name=row["display_name"],
                    obtained_at=row["obtained_at"],
                )
                result.append(
                    {
                        "provider": row["provider"],
                        "user_id": row["user_id"],
                        "email": row["email"],
                        "display_name": row["display_name"],
                        "durum": "geçerli" if not token.is_expired else "süresi doldu",
                        "expires_at": token.expires_at_local,
                        "scope": row["scope"],
                        "updated_at": row["updated_at"],
                    }
                )
            return result

    def var_mi(self, provider: str) -> bool:
        """Provider için kayÄ±tlÄ± token var mÄ±?"""
        with self._baglan() as conn:
            row = conn.execute(
                "SELECT 1 FROM oauth_tokens WHERE provider = ?", (provider,)
            ).fetchone()
            return row is not None


# ---------------------------------------------------------------------------
# OAuthProvider ABC
# ---------------------------------------------------------------------------


class OAuthProvider(ABC):
    """OAuth 2.0 saÄŸlayÄ±cÄ± temel sÄ±nÄ±fÄ± (Authorization Code Flow).

    Alt sÄ±nÄ±flar ÅŸu alanlarÄ± tanÄ±mlamalÄ±:
      - provider_id: str
      - client_id, client_secret (env var'dan okunur)
      - auth_url, token_url, userinfo_url
      - scopes: list[str]
    """

    provider_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    auth_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    scopes: list[str] = []
    redirect_uri: str = ""

    @property
    def hazir(self) -> bool:
        """Provider kullanÄ±ma hazÄ±r mÄ±? (client_id ve client_secret var mÄ±)"""
        return bool(self.client_id and self.client_secret)

    def get_auth_url(self, state: str = "", redirect_uri: str = "") -> str:
        """KullanÄ±cÄ±yÄ± OAuth onay sayfasÄ±na yönlendirecek URL."""
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        if not state:
            state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str = "") -> dict[str, Any]:
        """Authorization code ile token al."""
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        return self._http_post(self.token_url, data)

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh token ile yeni access token al."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        return self._http_post(self.token_url, data)

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Access token ile kullanÄ±cÄ± bilgisi al."""
        req = urllib.request.Request(
            self.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            logger.error("[OAuth] get_user_info HTTP %d: %s", e.code, body[:500])
            raise OAuthError(
                f"KullanÄ±cÄ± bilgisi alÄ±namadÄ±: HTTP {e.code}",
                provider=self.provider_id,
                status_code=e.code,
            ) from e
        except (urllib.error.URLError, OSError) as e:
            logger.error("[OAuth] get_user_info baÄŸlantÄ± hatasÄ±: %s", e)
            raise OAuthError(
                f"KullanÄ±cÄ± bilgisi alÄ±namadÄ±: {e}",
                provider=self.provider_id,
            ) from e

    @abstractmethod
    def normalize_user_info(self, raw: dict[str, Any]) -> OAuthToken:
        """Provider'a özel raw yanÄ±tÄ± OAuthToken'a dönüÅŸtür."""
        ...

    def token_from_raw(self, raw: dict[str, Any]) -> OAuthToken:
        """Ham token yanÄ±tÄ±ndan OAuthToken oluÅŸtur."""
        return OAuthToken(
            access_token=raw.get("access_token", ""),
            token_type=raw.get("token_type", "Bearer"),
            expires_in=raw.get("expires_in", 3600),
            refresh_token=raw.get("refresh_token", ""),
            scope=raw.get("scope", " ".join(self.scopes)),
            provider=self.provider_id,
        )

    def _http_post(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        """application/x-www-form-urlencoded POST isteÄŸi."""
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            logger.error("[OAuth] POST %s HTTP %d: %s", url, e.code, body[:500])
            raise OAuthError(
                f"Token alÄ±namadÄ±: HTTP {e.code}",
                provider=self.provider_id,
                status_code=e.code,
            ) from e
        except (urllib.error.URLError, OSError) as e:
            logger.error("[OAuth] POST %s baÄŸlantÄ± hatasÄ±: %s", url, e)
            raise OAuthError(
                f"Token alÄ±namadÄ±: {e}",
                provider=self.provider_id,
            ) from e


# ---------------------------------------------------------------------------
# GoogleOAuthProvider â€” Gmail, Drive, Calendar API'leri
# ---------------------------------------------------------------------------

GOOGLE_SCOPE_GMAIL = "https://www.googleapis.com/auth/gmail.modify"
GOOGLE_SCOPE_DRIVE = "https://www.googleapis.com/auth/drive.file"
GOOGLE_SCOPE_CALENDAR = "https://www.googleapis.com/auth/calendar"
GOOGLE_SCOPE_USERINFO_EMAIL = "https://www.googleapis.com/auth/userinfo.email"
GOOGLE_SCOPE_USERINFO_PROFILE = "https://www.googleapis.com/auth/userinfo.profile"


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 saÄŸlayÄ±cÄ±sÄ±.

    Gereken env vars:
      GOOGLE_CLIENT_ID
      GOOGLE_CLIENT_SECRET

    VarsayÄ±lan scope'lar:
      - gmail.modify   (Gmail okuma/yazma)
      - drive.file     (Drive dosya yönetimi)
      - calendar       (Google Calendar)
      - userinfo.email, userinfo.profile
    """

    provider_id = "google"
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, scopes: Optional[list[str]] = None, redirect_uri: str = ""):
        self.scopes = scopes or [
            GOOGLE_SCOPE_GMAIL,
            GOOGLE_SCOPE_DRIVE,
            GOOGLE_SCOPE_CALENDAR,
            GOOGLE_SCOPE_USERINFO_EMAIL,
            GOOGLE_SCOPE_USERINFO_PROFILE,
        ]
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        if not self.client_id or not self.client_secret:
            logger.warning(
                "[OAuth:Google] GOOGLE_CLIENT_ID veya GOOGLE_CLIENT_SECRET "
                "ortam deÄŸiÅŸkeni bulunamadÄ±. Google giriÅŸi çalÄ±ÅŸmayacak."
            )
        self.redirect_uri = redirect_uri or os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:5000/auth/callback/google",
        )

    def normalize_user_info(self, raw: dict[str, Any]) -> OAuthToken:
        """Google userinfo yanÄ±tÄ±nÄ± OAuthToken'a dönüÅŸtür."""
        token = OAuthToken(provider=self.provider_id)
        token.user_id = raw.get("id", raw.get("sub", ""))
        token.email = raw.get("email", "")
        token.display_name = raw.get("name", raw.get("given_name", ""))
        token.avatar_url = raw.get("picture", "")
        return token

    def token_from_raw(self, raw: dict[str, Any]) -> OAuthToken:
        """Google token yanÄ±tÄ±ndan OAuthToken oluÅŸtur + kullanÄ±cÄ± bilgisi ekle."""
        token = super().token_from_raw(raw)
        try:
            user_raw = self.get_user_info(token.access_token)
            user_info = self.normalize_user_info(user_raw)
            token.user_id = user_info.user_id
            token.email = user_info.email
            token.display_name = user_info.display_name
            token.avatar_url = user_info.avatar_url
        except Exception as e:
            logger.warning("[OAuth:Google] KullanÄ±cÄ± bilgisi alÄ±namadÄ±: %s", e)
        return token


# ---------------------------------------------------------------------------
# GitHubOAuthProvider â€” repo, user scope'larÄ±
# ---------------------------------------------------------------------------

GITHUB_SCOPE_REPO = "repo"
GITHUB_SCOPE_USER = "user"
GITHUB_SCOPE_WORKFLOW = "workflow"
GITHUB_SCOPE_ADMIN_ORG = "admin:org"


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth 2.0 saÄŸlayÄ±cÄ±sÄ±.

    Gereken env vars:
      GITHUB_CLIENT_ID
      GITHUB_CLIENT_SECRET

    VarsayÄ±lan scope'lar:
      - repo      (özel repositoriler dahil tam eriÅŸim)
      - user      (kullanÄ±cÄ± profili bilgisi)
      - workflow  (GitHub Actions workflow yönetimi)

    Not: GitHub OAuth'da refresh_token yoktur; access_token'lar
    süresizdir (expires_in gelmez). Token'Ä± yenilemek için
    kullanÄ±cÄ±nÄ±n yeniden yetkilendirmesi gerekir.
    """

    provider_id = "github"
    auth_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    userinfo_url = "https://api.github.com/user"

    def __init__(self, scopes: Optional[list[str]] = None, redirect_uri: str = ""):
        self.scopes = scopes or [
            GITHUB_SCOPE_REPO,
            GITHUB_SCOPE_USER,
            GITHUB_SCOPE_WORKFLOW,
        ]
        self.client_id = os.getenv("GITHUB_CLIENT_ID", "")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
        if not self.client_id or not self.client_secret:
            logger.warning(
                "[OAuth:GitHub] GITHUB_CLIENT_ID veya GITHUB_CLIENT_SECRET "
                "ortam deÄŸiÅŸkeni bulunamadÄ±. GitHub giriÅŸi çalÄ±ÅŸmayacak."
            )
        self.redirect_uri = redirect_uri or os.getenv(
            "GITHUB_REDIRECT_URI",
            "http://localhost:5000/auth/callback/github",
        )

    def get_auth_url(self, state: str = "", redirect_uri: str = "") -> str:
        """GitHub OAuth URL'si (access_type ve prompt yok)."""
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        if not state:
            state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str = "") -> dict[str, Any]:
        """GitHub authorization code ile token al.

        GitHub, yanÄ±tÄ± JSON yerine form-encoded dönebilir.
        Accept header ile JSON iste.
        """
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(self.token_url, data=encoded, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            logger.error("[OAuth:GitHub] POST HTTP %d: %s", e.code, body[:500])
            raise OAuthError(
                f"GitHub token alÄ±namadÄ±: HTTP {e.code}",
                provider=self.provider_id,
                status_code=e.code,
            ) from e
        except (urllib.error.URLError, OSError) as e:
            logger.error("[OAuth:GitHub] POST baÄŸlantÄ± hatasÄ±: %s", e)
            raise OAuthError(
                f"GitHub token alÄ±namadÄ±: {e}",
                provider=self.provider_id,
            ) from e

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """GitHub'da refresh_token yoktur. Hata fÄ±rlat."""
        raise OAuthError(
            "GitHub OAuth'da refresh_token desteÄŸi yoktur. "
            "Token kalÄ±cÄ±dÄ±r, yeniden yetkilendirme gerekmez.",
            provider=self.provider_id,
            code="github_no_refresh",
        )

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """GitHub API ile kullanÄ±cÄ± bilgisi al."""
        req = urllib.request.Request(
            self.userinfo_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ReYMeN-Ajan/1.0",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            logger.error("[OAuth:GitHub] get_user_info HTTP %d: %s", e.code, body[:500])
            raise OAuthError(
                f"GitHub kullanÄ±cÄ± bilgisi alÄ±namadÄ±: HTTP {e.code}",
                provider=self.provider_id,
                status_code=e.code,
            ) from e
        except (urllib.error.URLError, OSError) as e:
            logger.error("[OAuth:GitHub] get_user_info baÄŸlantÄ± hatasÄ±: %s", e)
            raise OAuthError(
                f"GitHub kullanÄ±cÄ± bilgisi alÄ±namadÄ±: {e}",
                provider=self.provider_id,
            ) from e

    def normalize_user_info(self, raw: dict[str, Any]) -> OAuthToken:
        """GitHub API yanÄ±tÄ±nÄ± OAuthToken'a dönüÅŸtür."""
        token = OAuthToken(provider=self.provider_id)
        token.user_id = str(raw.get("id", ""))
        token.email = raw.get("email", "") or raw.get("login", "")
        token.display_name = raw.get("name", raw.get("login", ""))
        token.avatar_url = raw.get("avatar_url", "")
        return token

    def token_from_raw(self, raw: dict[str, Any]) -> OAuthToken:
        """GitHub token yanÄ±tÄ±ndan OAuthToken oluÅŸtur.

        GitHub token'larÄ± süresizdir, expires_in gelmez.
        10 yÄ±l (315360000 sn) varsayÄ±lan süre.
        """
        token = super().token_from_raw(raw)
        if token.expires_in == 3600 and "expires_in" not in raw:
            token.expires_in = 315360000  # 10 yÄ±l (pratikte süresiz)
        try:
            user_raw = self.get_user_info(token.access_token)
            user_info = self.normalize_user_info(user_raw)
            token.user_id = user_info.user_id
            token.email = user_info.email
            token.display_name = user_info.display_name
            token.avatar_url = user_info.avatar_url
        except Exception as e:
            logger.warning("[OAuth:GitHub] KullanÄ±cÄ± bilgisi alÄ±namadÄ±: %s", e)
        return token


# ---------------------------------------------------------------------------
# DiscordOAuthProvider â€” bot token auth (stub / geniÅŸletilmiÅŸ)
# ---------------------------------------------------------------------------

DISCORD_SCOPE_IDENTIFY = "identify"
DISCORD_SCOPE_EMAIL = "email"
DISCORD_SCOPE_GUILDS = "guilds"
DISCORD_SCOPE_BOT = "bot"


class DiscordOAuthProvider(OAuthProvider):
    """Discord OAuth 2.0 saÄŸlayÄ±cÄ±sÄ±.

    Gereken env vars:
      DISCORD_CLIENT_ID
      DISCORD_CLIENT_SECRET

    VarsayÄ±lan scope'lar:
      - identify  (kullanÄ±cÄ± adÄ±, avatar)
      - email     (e-posta adresi)
      - guilds    (sunucu listesi)

    Bot token auth için DISCORD_BOT_TOKEN env var'Ä± kullanÄ±lÄ±r.
    """

    provider_id = "discord"
    auth_url = "https://discord.com/api/oauth2/authorize"
    token_url = "https://discord.com/api/oauth2/token"
    userinfo_url = "https://discord.com/api/users/@me"

    def __init__(self, scopes: Optional[list[str]] = None, redirect_uri: str = ""):
        self.scopes = scopes or [
            DISCORD_SCOPE_IDENTIFY,
            DISCORD_SCOPE_EMAIL,
            DISCORD_SCOPE_GUILDS,
        ]
        self.client_id = os.getenv("DISCORD_CLIENT_ID", "")
        self.client_secret = os.getenv("DISCORD_CLIENT_SECRET", "")
        if not self.client_id or not self.client_secret:
            logger.warning(
                "[OAuth:Discord] DISCORD_CLIENT_ID veya DISCORD_CLIENT_SECRET "
                "ortam deÄŸiÅŸkeni bulunamadÄ±. Discord giriÅŸi çalÄ±ÅŸmayacak."
            )
        self.redirect_uri = redirect_uri or os.getenv(
            "DISCORD_REDIRECT_URI",
            "http://localhost:5000/auth/callback/discord",
        )

    def get_auth_url(self, state: str = "", redirect_uri: str = "") -> str:
        """Discord OAuth URL'si (access_type ve prompt yok)."""
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        if not state:
            state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def normalize_user_info(self, raw: dict[str, Any]) -> OAuthToken:
        """Discord /users/@me yanÄ±tÄ±nÄ± OAuthToken'a dönüÅŸtür."""
        token = OAuthToken(provider=self.provider_id)
        avatar_hash = raw.get("avatar", "")
        user_id = str(raw.get("id", ""))
        avatar_url = ""
        if avatar_hash and user_id:
            ext = "gif" if avatar_hash.startswith("a_") else "png"
            avatar_url = (
                f"https://cdn.discordapp.com/avatars/" f"{user_id}/{avatar_hash}.{ext}"
            )
        token.user_id = user_id
        token.email = raw.get("email", "")
        token.display_name = raw.get("global_name") or raw.get("username", "")
        token.avatar_url = avatar_url
        return token

    def token_from_raw(self, raw: dict[str, Any]) -> OAuthToken:
        """Discord token yanÄ±tÄ±ndan OAuthToken oluÅŸtur + kullanÄ±cÄ± bilgisi ekle."""
        token = super().token_from_raw(raw)
        try:
            user_raw = self.get_user_info(token.access_token)
            user_info = self.normalize_user_info(user_raw)
            token.user_id = user_info.user_id
            token.email = user_info.email
            token.display_name = user_info.display_name
            token.avatar_url = user_info.avatar_url
        except Exception as e:
            logger.warning("[OAuth:Discord] KullanÄ±cÄ± bilgisi alÄ±namadÄ±: %s", e)
        return token

    @staticmethod
    def bot_token_hazir() -> bool:
        """Discord bot token'Ä± ortamda var mÄ±?"""
        return bool(os.getenv("DISCORD_BOT_TOKEN", ""))


# ---------------------------------------------------------------------------
# OAuthSistemi â€” üst seviye OAuth yöneticisi
# ---------------------------------------------------------------------------


class OAuthSistemi:
    """OAuth 2.0 sistemi â€” tüm provider'larÄ± ve token yönetimini birleÅŸtirir.

    KullanÄ±m:
        sistem = OAuthSistemi()
        # Google
        url = sistem.google.get_auth_url()
        token = sistem.google.exchange_code("auth_code")
        sistem.token_kaydet("google", token)
        # GitHub
        url = sistem.github.get_auth_url()
        token = sistem.github.exchange_code("auth_code")
        sistem.token_kaydet("github", token)
        # Token kontrol
        durum = sistem.token_durum("google")
        # Token yenileme
        yeni_token = sistem.token_yenile("google")
    """

    def __init__(
        self,
        deposu: Optional[SQLiteTokenDeposu] = None,
        google_scopes: Optional[list[str]] = None,
        github_scopes: Optional[list[str]] = None,
        discord_scopes: Optional[list[str]] = None,
    ):
        self._depo = deposu or SQLiteTokenDeposu()
        self._google = GoogleOAuthProvider(scopes=google_scopes)
        self._github = GitHubOAuthProvider(scopes=github_scopes)
        self._discord = DiscordOAuthProvider(scopes=discord_scopes)

    # â”€â”€ Provider'lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @property
    def google(self) -> GoogleOAuthProvider:
        """Google OAuth provider."""
        return self._google

    @property
    def github(self) -> GitHubOAuthProvider:
        """GitHub OAuth provider."""
        return self._github

    @property
    def discord(self) -> DiscordOAuthProvider:
        """Discord OAuth provider."""
        return self._discord

    def provider(self, ad: str) -> OAuthProvider:
        """Provider adÄ±na göre provider döndür."""
        provider_map = {
            "google": self._google,
            "github": self._github,
            "discord": self._discord,
        }
        p = provider_map.get(ad.lower())
        if p is None:
            raise OAuthError(
                f"Bilinmeyen OAuth provider: {ad}. "
                f"Bilinenler: {', '.join(provider_map.keys())}",
                provider=ad,
            )
        return p

    # â”€â”€ Token Yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def token_kaydet(self, provider: str, token: OAuthToken) -> None:
        """Token'Ä± SQLite deposuna kaydet."""
        if not token.provider:
            token.provider = provider
        self._depo.kaydet(provider, token)
        logger.info(
            "[OAuthSistemi] Token kaydedildi: %s (kullanÄ±cÄ±: %s)",
            provider,
            token.email or token.user_id or "?",
        )

    def token_yukle(self, provider: str) -> Optional[OAuthToken]:
        """Token'Ä± SQLite deposundan yükle."""
        return self._depo.yukle(provider)

    def token_sil(self, provider: str) -> None:
        """Token'Ä± SQLite deposundan sil."""
        self._depo.sil(provider)
        logger.info("[OAuthSistemi] Token silindi: %s", provider)

    def token_durum(self, provider: str) -> dict[str, Any]:
        """Provider için token durumunu döndür.

        Dönen:
            {
                "provider": "google",
                "var_mi": True,
                "gecerli_mi": True/False,
                "email": "...",
                "display_name": "...",
                "expires_at": "2025-01-01 12:00:00",
                "scope": "...",
                "sure_doldu_mu": True/False,
            }
        """
        token = self._depo.yukle(provider)
        if token is None:
            return {
                "provider": provider,
                "var_mi": False,
                "gecerli_mi": False,
                "mesaj": "Token bulunamadÄ±. Ã–nce giriÅŸ yapmalÄ±sÄ±nÄ±z.",
            }
        return {
            "provider": provider,
            "var_mi": True,
            "gecerli_mi": not token.is_expired,
            "sure_doldu_mu": token.is_expired,
            "email": token.email,
            "display_name": token.display_name,
            "user_id": token.user_id,
            "expires_at": token.expires_at_local,
            "scope": token.scope,
            "token_tipi": token.token_type,
        }

    def token_yenile(self, provider: str) -> Optional[OAuthToken]:
        """Refresh token ile yeni access token al ve kaydet.

        Returns:
            Yeni OAuthToken veya None (refresh_token yoksa/hata varsa)
        """
        eski = self._depo.yukle(provider)
        if eski is None:
            logger.warning(
                "[OAuthSistemi] Token yenileme: %s için token bulunamadÄ±", provider
            )
            return None
        if not eski.refresh_token:
            logger.warning(
                "[OAuthSistemi] Token yenileme: %s için refresh_token yok", provider
            )
            return None

        try:
            p = self.provider(provider)
            raw = p.refresh_access_token(eski.refresh_token)
            yeni_token = OAuthToken(
                access_token=raw.get("access_token", ""),
                token_type=raw.get("token_type", "Bearer"),
                expires_in=raw.get("expires_in", 3600),
                refresh_token=raw.get("refresh_token", eski.refresh_token),
                scope=raw.get("scope", eski.scope),
                provider=provider,
                user_id=eski.user_id,
                email=eski.email,
                display_name=eski.display_name,
                avatar_url=eski.avatar_url,
            )
            self._depo.kaydet(provider, yeni_token)
            logger.info("[OAuthSistemi] Token yenilendi: %s", provider)
            return yeni_token
        except OAuthError as e:
            logger.error("[OAuthSistemi] Token yenileme hatasÄ± (%s): %s", provider, e)
            return None
        except Exception as e:
            logger.error("[OAuthSistemi] Token yenileme hatasÄ± (%s): %s", provider, e)
            return None

    def token_listele(self) -> list[dict[str, Any]]:
        """Tüm kayÄ±tlÄ± token'larÄ± listele."""
        return self._depo.listele()

    def giris_yap(self, provider: str) -> Optional[str]:
        """Provider için auth URL'si döndür.

        Returns:
            Auth URL (kullanÄ±cÄ±nÄ±n tarayÄ±cÄ±da açmasÄ± gereken)
            veya None (provider hazÄ±r deÄŸilse)
        """
        p = self.provider(provider)
        if not p.hazir:
            logger.warning("[OAuthSistemi] Provider hazÄ±r deÄŸil: %s", provider)
            return None
        return p.get_auth_url()

    def callback_islem(self, provider: str, code: str) -> Optional[OAuthToken]:
        """Authorization code ile token al ve kaydet.

        Args:
            provider: Provider adÄ±
            code: Authorization code (callback'ten gelen)

        Returns:
            OAuthToken veya None (hata varsa)
        """
        try:
            p = self.provider(provider)
            raw = p.exchange_code(code)
            token = p.token_from_raw(raw)
            self._depo.kaydet(provider, token)
            return token
        except OAuthError as e:
            logger.error("[OAuthSistemi] Callback hatasÄ± (%s): %s", provider, e)
            return None
        except Exception as e:
            logger.error("[OAuthSistemi] Callback hatasÄ± (%s): %s", provider, e)
            return None

    def cikis_yap(self, provider: str) -> bool:
        """Provider'dan çÄ±kÄ±ÅŸ yap (token'Ä± sil).

        Returns:
            True baÅŸarÄ±lÄ±, False token yoksa
        """
        var_mi = self._depo.var_mi(provider)
        if var_mi:
            self._depo.sil(provider)
            logger.info("[OAuthSistemi] Ã‡Ä±kÄ±ÅŸ yapÄ±ldÄ±: %s", provider)
            return True
        logger.warning("[OAuthSistemi] Ã‡Ä±kÄ±ÅŸ: %s için token bulunamadÄ±", provider)
        return False

    def gecerli_token(self, provider: str) -> Optional[OAuthToken]:
        """Geçerli (süresi dolmamÄ±ÅŸ) token'Ä± döndür.

        Süresi dolmuÅŸsa ve refresh_token varsa otomatik yenile.
        """
        token = self._depo.yukle(provider)
        if token is None:
            return None
        if token.is_expired:
            if token.refresh_token:
                logger.info(
                    "[OAuthSistemi] Token süresi dolmuÅŸ, yenileniyor: %s", provider
                )
                return self.token_yenile(provider)
            logger.warning(
                "[OAuthSistemi] Token süresi dolmuÅŸ, refresh_token yok: %s", provider
            )
            return None
        return token


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

oauth_sistemi = OAuthSistemi()
