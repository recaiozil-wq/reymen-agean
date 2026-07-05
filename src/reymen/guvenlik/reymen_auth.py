# -*- coding: utf-8 -*-
"""
ğŸ” ReYMeN Auth System â€” Nous Portal alternative.

API key validation, JWT token management, permission levels and
multi-user support. Designed to work alongside the existing OAuth2 system.

Usage:
    from reymen.guvenlik.reymen_auth import auth_manager

    # API key validation
    key = "sk-xxxxxxxx..."
    provider = auth_manager.validate_api_key(key)
    if provider:
        print(f"Valid {provider} key")

    # Token creation
    token = auth_manager.create_token("kullanici_adi", role="admin")
    print(token.access_token)

    # Token verification
    payload = auth_manager.verify_token(token.access_token)
    if payload:
        print(f"Welcome {payload['sub']}")

    # Token refresh
    new_token = auth_manager.refresh_token(token.refresh_token)

Permission Levels:
    admin â†’ Full access to all operations
    user  â†’ Standard user operations
    guest â†’ Read-only operations
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Proje Yolu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DB_DIR = PROJE_KOK / ".ReYMeN" / "auth"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Veri YapÄ±larÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@dataclass
class AccessToken:
    """JWT access token."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # 1 saat
    refresh_token: str = ""
    scope: str = ""
    role: str = "user"
    user_id: str = ""
    issued_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.issued_at + self.expires_in - 60  # 60s grace

    @property
    def expires_at(self) -> str:
        dt = datetime.fromtimestamp(self.issued_at + self.expires_in, tz=timezone.utc)
        return dt.isoformat()


@dataclass
class User:
    """User information."""

    user_id: str
    username: str
    role: str = "user"  # admin / user / guest
    email: str = ""
    api_keys: list = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    last_login: float = 0.0
    metadata: dict = field(default_factory=dict)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# API Key DoÄŸrulama
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# Desteklenen provider'lar ve API key format regex'leri
API_KEY_PROVIDERS: dict[str, dict[str, Any]] = {
    # Ã–nce spesifik prefix'ler kontrol edilmeli (sk-ant-, sk-or-, vs.)
    # çünkü generic sk- bunlardan önce eÅŸleÅŸir
    "anthropic": {
        "regex": r"^sk-ant-[A-Za-z0-9_.-]{20,}$",
        "env_var": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1/models",
        "description": "Anthropic API (sk-ant- ile baÅŸlar)",
    },
    "openrouter": {
        "regex": r"^sk-or-[A-Za-z0-9_.-]{20,}$",
        "env_var": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/auth/key",
        "description": "OpenRouter API (sk-or- ile baÅŸlar)",
    },
    "deepseek": {
        "regex": r"^sk-[A-Za-z0-9_.-]{20,}$",
        "env_var": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1/models",
        "description": "DeepSeek API (sk- ile baÅŸlar)",
    },
    "openai": {
        "regex": r"^sk-[A-Za-z0-9_.-]{20,}$",
        "env_var": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1/models",
        "description": "OpenAI API (sk- ile baÅŸlar)",
    },
    "xai": {
        "regex": r"^xai-[A-Za-z0-9_.-]{20,}$",
        "env_var": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1/models",
        "description": "xAI/Grok API (xai- ile baÅŸlar)",
    },
    "groq": {
        "regex": r"^gsk_[A-Za-z0-9_.-]{20,}$",
        "env_var": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1/models",
        "description": "Groq API (gsk_ ile baÅŸlar)",
    },
}


def detect_api_key_provider(api_key: str) -> Optional[str]:
    """Detect which provider an API key belongs to."""
    if not api_key or api_key == "buraya_yaz":
        return None
    for provider, config in API_KEY_PROVIDERS.items():
        regex = config.get("regex")
        if regex and re.match(regex, api_key.strip()):
            return provider
    return None


def validate_api_key_format(api_key: str) -> tuple[bool, Optional[str], str]:
    """Validate API key format.

    Returns:
        (valid, provider_name, message)
    """
    if not api_key or api_key == "buraya_yaz":
        return False, None, "API anahtarÄ± boÅŸ"
    provider = detect_api_key_provider(api_key)
    if provider:
        desc = API_KEY_PROVIDERS[provider]["description"]
        return True, provider, f"Geçerli {desc}"
    return False, None, "Bilinmeyen API anahtarÄ± formatÄ±"


def validate_api_key_live(api_key: str, provider: str, timeout: int = 10) -> bool:
    """Validate API key live by making a request to the provider.

    Note: This requires network access and may take time.
    Default behavior is format-only validation.
    """
    config = API_KEY_PROVIDERS.get(provider)
    if not config:
        return False
    base_url = config.get("base_url")
    if not base_url:
        return False
    try:
        import urllib.request

        req = urllib.request.Request(
            base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception as e:
        logger.debug("[Auth] Live key doÄŸrulama baÅŸarÄ±sÄ±z (%s): %s", provider, e)
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JWT Token Yönetimi (standart kütüphane ile HMAC-SHA256)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class JWTManager:
    """HMAC-SHA256 JWT token management â€” no external dependencies.

    Token structure:
        header:  {"alg": "HS256", "typ": "JWT"}
        payload: {"sub": username, "role": role, "iat": ts, "exp": ts, "jti": id}
        signature: HMAC-SHA256(base64(header).base64(payload), secret)
    """

    def __init__(self, secret_key: Optional[str] = None):
        self._secret = secret_key or os.environ.get(
            "REYMEN_JWT_SECRET", self._generate_secret()
        )

    @staticmethod
    def _generate_secret() -> str:
        """Generate 32-byte random secret."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")

    def _base64_url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    def _base64_url_decode(self, data: str) -> bytes:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def encode(self, payload: dict[str, Any], expires_in: int = 3600) -> str:
        """Create JWT token."""
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())

        full_payload = {
            **payload,
            "iat": now,
            "exp": now + expires_in,
            "jti": secrets.token_hex(16),
        }

        header_b64 = self._base64_url_encode(
            json.dumps(header, separators=(",", ":")).encode("utf-8")
        )
        payload_b64 = self._base64_url_encode(
            json.dumps(full_payload, separators=(",", ":")).encode("utf-8")
        )

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(
            self._secret.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        signature_b64 = self._base64_url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def decode(self, token: str, verify: bool = True) -> Optional[dict[str, Any]]:
        """Decode and verify JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            if verify:
                signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
                expected_signature = hmac.new(
                    self._secret.encode("utf-8"), signing_input, hashlib.sha256
                ).digest()
                actual_signature = self._base64_url_decode(signature_b64)

                if not hmac.compare_digest(expected_signature, actual_signature):
                    logger.warning("[JWT] Ä°mza doÄŸrulama baÅŸarÄ±sÄ±z")
                    return None

            payload_data = json.loads(
                self._base64_url_decode(payload_b64).decode("utf-8")
            )

            # Expiry kontrolü
            now = int(time.time())
            if payload_data.get("exp", 0) < now:
                logger.warning("[JWT] Token süresi dolmuÅŸ")
                return None

            return payload_data

        except Exception as e:
            logger.debug("[JWT] Ã‡özümleme hatasÄ±: %s", e)
            return None

    def refresh_token(self, token: str, expires_in: int = 3600) -> Optional[str]:
        """Refresh an existing token (by decoding JWT, not using refresh_token)."""
        payload = self.decode(token, verify=True)
        if payload is None:
            return None
        # Yeni token oluÅŸtur (süreyi uzat)
        new_payload = {
            k: v for k, v in payload.items() if k not in ("iat", "exp", "jti")
        }
        return self.encode(new_payload, expires_in=expires_in)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# KullanÄ±cÄ± ve Token Deposu (SQLite)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AuthStorage:
    """Stores user and token information in SQLite.

    Tables:
        users:      user_id, username, role, email, password_hash, api_keys,
                    is_active, created_at, last_login, metadata
        tokens:     token_id, user_id, token_type, access_token, refresh_token,
                    expires_at, role, scope, revoked, created_at
        api_keys:   key_id, user_id, key_hash, provider, label, is_active, created_at
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or (DEFAULT_DB_DIR / "auth.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id        TEXT PRIMARY KEY,
                    username       TEXT UNIQUE NOT NULL,
                    role           TEXT NOT NULL DEFAULT 'user',
                    email          TEXT DEFAULT '',
                    password_hash  TEXT DEFAULT '',
                    api_keys       TEXT DEFAULT '[]',
                    is_active      INTEGER DEFAULT 1,
                    created_at     REAL NOT NULL,
                    last_login     REAL DEFAULT 0,
                    metadata       TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS tokens (
                    token_id       TEXT PRIMARY KEY,
                    user_id        TEXT NOT NULL,
                    token_type     TEXT NOT NULL DEFAULT 'bearer',
                    access_token   TEXT NOT NULL,
                    refresh_token  TEXT DEFAULT '',
                    expires_at     REAL NOT NULL,
                    role           TEXT DEFAULT 'user',
                    scope          TEXT DEFAULT '',
                    revoked        INTEGER DEFAULT 0,
                    created_at     REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE INDEX IF NOT EXISTS idx_tokens_user
                    ON tokens(user_id);
                CREATE INDEX IF NOT EXISTS idx_tokens_access
                    ON tokens(access_token);
                CREATE INDEX IF NOT EXISTS idx_tokens_refresh
                    ON tokens(refresh_token);

                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id         TEXT PRIMARY KEY,
                    user_id        TEXT NOT NULL,
                    key_hash       TEXT NOT NULL,
                    provider       TEXT DEFAULT '',
                    label          TEXT DEFAULT '',
                    is_active      INTEGER DEFAULT 1,
                    created_at     REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE INDEX IF NOT EXISTS idx_apikeys_user
                    ON api_keys(user_id);
            """)
            conn.commit()
        finally:
            conn.close()

    # â”€â”€ KullanÄ±cÄ± Ä°ÅŸlemleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def create_user(
        self,
        username: str,
        role: str = "user",
        email: str = "",
        password_hash: str = "",
    ) -> User:
        conn = self._get_conn()
        try:
            user_id = str(uuid.uuid4())
            now = time.time()
            conn.execute(
                """INSERT INTO users (user_id, username, role, email, password_hash,
                   is_active, created_at, metadata)
                   VALUES (?, ?, ?, ?, ?, 1, ?, '{}')""",
                (user_id, username, role, email, password_hash, now),
            )
            conn.commit()
            return User(
                user_id=user_id,
                username=username,
                role=role,
                email=email,
                created_at=now,
                is_active=True,
            )
        except sqlite3.IntegrityError:
            logger.warning("[AuthStorage] KullanÄ±cÄ± zaten var: %s", username)
            return self.get_user_by_username(username)
        finally:
            conn.close()

    def get_user(self, user_id: str) -> Optional[User]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row:
                return self._row_to_user(row)
            return None
        finally:
            conn.close()

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            if row:
                return self._row_to_user(row)
            return None
        finally:
            conn.close()

    def list_users(self) -> list[User]:
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()
            return [self._row_to_user(r) for r in rows]
        finally:
            conn.close()

    def update_user(self, user_id: str, **kwargs) -> bool:
        allowed = {
            "role",
            "email",
            "is_active",
            "last_login",
            "password_hash",
            "metadata",
        }
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        conn = self._get_conn()
        try:
            conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    def delete_user(self, user_id: str) -> bool:
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM api_keys WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    # â”€â”€ Token Ä°ÅŸlemleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def save_token(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        role: str = "user",
        scope: str = "",
    ) -> str:
        conn = self._get_conn()
        try:
            token_id = str(uuid.uuid4())
            now = time.time()
            expires_at = now + expires_in
            conn.execute(
                """INSERT INTO tokens (token_id, user_id, access_token,
                   refresh_token, expires_at, role, scope, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    token_id,
                    user_id,
                    access_token,
                    refresh_token,
                    expires_at,
                    role,
                    scope,
                    now,
                ),
            )
            conn.commit()
            return token_id
        finally:
            conn.close()

    def get_token_by_access(self, access_token: str) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                """SELECT * FROM tokens WHERE access_token = ?
                   AND revoked = 0 AND expires_at > ?""",
                (access_token, time.time()),
            ).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def get_token_by_refresh(self, refresh_token: str) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        try:
            row = conn.execute(
                """SELECT * FROM tokens WHERE refresh_token = ?
                   AND revoked = 0""",
                (refresh_token,),
            ).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def revoke_token(self, access_token: str) -> bool:
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE tokens SET revoked = 1 WHERE access_token = ?",
                (access_token,),
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    def revoke_user_tokens(self, user_id: str) -> int:
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE tokens SET revoked = 1 WHERE user_id = ?",
                (user_id,),
            )
            conn.commit()
            return conn.total_changes
        finally:
            conn.close()

    def list_tokens(self, user_id: Optional[str] = None) -> list[dict[str, Any]]:
        conn = self._get_conn()
        try:
            if user_id:
                rows = conn.execute(
                    """SELECT * FROM tokens WHERE user_id = ?
                       ORDER BY created_at DESC""",
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tokens ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # â”€â”€ API Key Ä°ÅŸlemleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def save_api_key(
        self, user_id: str, key_hash: str, provider: str = "", label: str = ""
    ) -> str:
        conn = self._get_conn()
        try:
            key_id = str(uuid.uuid4())
            now = time.time()
            conn.execute(
                """INSERT INTO api_keys (key_id, user_id, key_hash,
                   provider, label, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (key_id, user_id, key_hash, provider, label, now),
            )
            conn.commit()
            return key_id
        finally:
            conn.close()

    def list_api_keys(self, user_id: Optional[str] = None) -> list[dict[str, Any]]:
        conn = self._get_conn()
        try:
            if user_id:
                rows = conn.execute(
                    """SELECT * FROM api_keys WHERE user_id = ?
                       ORDER BY created_at DESC""",
                    (user_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM api_keys ORDER BY created_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def revoke_api_key(self, key_id: str) -> bool:
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE api_keys SET is_active = 0 WHERE key_id = ?",
                (key_id,),
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    # â”€â”€ YardÄ±mcÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            user_id=row["user_id"],
            username=row["username"],
            role=row["role"],
            email=row["email"] or "",
            api_keys=json.loads(row["api_keys"] or "[]"),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            last_login=row["last_login"] or 0.0,
            metadata=json.loads(row["metadata"] or "{}"),
        )

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens."""
        conn = self._get_conn()
        try:
            cur = conn.execute(
                "DELETE FROM tokens WHERE expires_at < ?",
                (time.time(),),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ana Auth Yöneticisi
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AuthManager:
    """ReYMeN Auth System â€” Main manager class.

    Combines API key validation, JWT token management, user management
    and authorization operations in a single interface.

    Usage:
        manager = AuthManager()
        token = manager.create_token("kullanici", role="admin")
        payload = manager.verify_token(token.access_token)
        user = manager.authenticate("apikey123")
    """

    def __init__(
        self,
        jwt_secret: Optional[str] = None,
        db_path: Optional[Path] = None,
        storage: Optional[AuthStorage] = None,
    ):
        self.jwt = JWTManager(secret_key=jwt_secret)
        self.storage = storage or AuthStorage(db_path=db_path)
        self._ensure_default_admin()

    def _ensure_default_admin(self) -> None:
        """Create default admin user on first run."""
        admin = self.storage.get_user_by_username("admin")
        if admin is None:
            user = self.storage.create_user(
                "admin", role="admin", email="admin@reymen.local"
            )
            logger.info(
                "[Auth] VarsayÄ±lan admin kullanÄ±cÄ±sÄ± oluÅŸturuldu: %s", user.user_id
            )

    # â”€â”€ API Key DoÄŸrulama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key format and return provider name."""
        valid, provider, _ = validate_api_key_format(api_key)
        return provider if valid else None

    def detect_api_key(self, api_key: str) -> Optional[str]:
        return detect_api_key_provider(api_key)

    # â”€â”€ Token Yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def create_token(
        self,
        username: str,
        role: str = "user",
        expires_in: int = 3600,
        scope: str = "",
    ) -> Optional[AccessToken]:
        """Create access + refresh tokens for a user.

        Args:
            username: Username (auto-created)
            role:     Permission level (admin/user/guest)
            expires_in: Token validity duration (seconds)

        Returns:
            AccessToken object or None (on error)
        """
        if role not in ("admin", "user", "guest"):
            logger.error("[Auth] Geçersiz rol: %s", role)
            return None

        # KullanÄ±cÄ±yÄ± bul veya oluÅŸtur
        user = self.storage.get_user_by_username(username)
        if user is None:
            user = self.storage.create_user(username, role=role)
        elif role != user.role:
            self.storage.update_user(user.user_id, role=role)
            user.role = role

        # Access token oluÅŸtur
        payload = {
            "sub": username,
            "role": role,
            "uid": user.user_id,
        }
        access_token_str = self.jwt.encode(payload, expires_in=expires_in)

        # Refresh token oluÅŸtur (daha uzun süreli)
        refresh_payload = {
            "sub": username,
            "role": role,
            "uid": user.user_id,
            "type": "refresh",
        }
        refresh_token_str = self.jwt.encode(refresh_payload, expires_in=expires_in * 24)

        # Token'Ä± veritabanÄ±na kaydet
        self.storage.save_token(
            user_id=user.user_id,
            access_token=access_token_str,
            refresh_token=refresh_token_str,
            expires_in=expires_in,
            role=role,
            scope=scope,
        )

        # Son giriÅŸ zamanÄ±nÄ± güncelle
        self.storage.update_user(user.user_id, last_login=time.time())

        return AccessToken(
            access_token=access_token_str,
            refresh_token=refresh_token_str,
            expires_in=expires_in,
            role=role,
            scope=scope,
            user_id=user.user_id,
        )

    def verify_token(self, token: str) -> Optional[dict[str, Any]]:
        """Verify JWT token and return payload.

        First checks JWT signature/expiry, then queries the database.
        """
        payload = self.jwt.decode(token, verify=True)
        if payload is None:
            return None

        # VeritabanÄ±nda token'Ä±n revoked olmadÄ±ÄŸÄ±nÄ± kontrol et
        db_token = self.storage.get_token_by_access(token)
        if db_token is None:
            logger.warning("[Auth] Token veritabanÄ±nda bulunamadÄ± veya iptal edilmiÅŸ")
            return None

        return payload

    def refresh_token(self, refresh_token: str) -> Optional[AccessToken]:
        """Create new access token using a refresh token."""
        # Refresh token'Ä± doÄŸrula
        payload = self.jwt.decode(refresh_token, verify=True)
        if payload is None:
            logger.warning("[Auth] Geçersiz refresh token")
            return None

        # VeritabanÄ±nda kontrol et
        db_token = self.storage.get_token_by_refresh(refresh_token)
        if db_token is None:
            logger.warning("[Auth] Refresh token veritabanÄ±nda bulunamadÄ±")
            return None

        username = payload.get("sub", "")
        role = payload.get("role", "user")

        # Eski token'Ä± iptal et
        if db_token.get("access_token"):
            self.storage.revoke_token(db_token["access_token"])

        # Yeni token oluÅŸtur
        return self.create_token(username, role=role)

    def revoke_token(self, access_token: str) -> bool:
        """Revoke an access token."""
        return self.storage.revoke_token(access_token)

    def revoke_user_tokens(self, username: str) -> int:
        """Revoke all tokens for a user."""
        user = self.storage.get_user_by_username(username)
        if user is None:
            return 0
        return self.storage.revoke_user_tokens(user.user_id)

    # â”€â”€ KullanÄ±cÄ± Yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def create_user(
        self, username: str, role: str = "user", email: str = ""
    ) -> Optional[User]:
        """Create a new user."""
        if role not in ("admin", "user", "guest"):
            logger.error("[Auth] Geçersiz rol: %s", role)
            return None
        return self.storage.create_user(username, role=role, email=email)

    def list_users(self) -> list[User]:
        """List all users."""
        return self.storage.list_users()

    def get_user(self, username: str) -> Optional[User]:
        """Find user by username."""
        return self.storage.get_user_by_username(username)

    def delete_user(self, username: str) -> bool:
        """Delete user (along with their tokens)."""
        user = self.storage.get_user_by_username(username)
        if user is None:
            return False
        return self.storage.delete_user(user.user_id)

    def update_user_role(self, username: str, role: str) -> bool:
        """Change user permission level."""
        if role not in ("admin", "user", "guest"):
            return False
        user = self.storage.get_user_by_username(username)
        if user is None:
            return False
        return self.storage.update_user(user.user_id, role=role)

    # â”€â”€ Yetkilendirme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def check_permission(self, user_role: str, required_role: str) -> bool:
        """Check if the user's permission level is sufficient.

        Permission hierarchy: guest < user < admin
        """
        hierarchy = {"guest": 0, "user": 1, "admin": 2}
        user_level = hierarchy.get(user_role, -1)
        required_level = hierarchy.get(required_role, 0)
        return user_level >= required_level

    def require_role(self, token: str, required_role: str) -> bool:
        """Check if the JWT token has the required role."""
        payload = self.verify_token(token)
        if payload is None:
            return False
        user_role = payload.get("role", "guest")
        return self.check_permission(user_role, required_role)

    # â”€â”€ Token Bilgisi ve Liste â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def list_tokens(self, username: Optional[str] = None) -> list[dict[str, Any]]:
        """List tokens."""
        if username:
            user = self.storage.get_user_by_username(username)
            if user is None:
                return []
            return self.storage.list_tokens(user_id=user.user_id)
        return self.storage.list_tokens()

    def list_api_keys(self, username: Optional[str] = None) -> list[dict[str, Any]]:
        """List API keys."""
        if username:
            user = self.storage.get_user_by_username(username)
            if user is None:
                return []
            return self.storage.list_api_keys(user_id=user.user_id)
        return self.storage.list_api_keys()

    # â”€â”€ BakÄ±m â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def cleanup(self) -> int:
        """Clean up expired tokens."""
        return self.storage.cleanup_expired_tokens()

    def status(self) -> dict[str, Any]:
        """Auth system status information."""
        users = self.list_users()
        tokens = self.list_tokens()
        active_tokens = [t for t in tokens if not t.get("revoked")]
        return {
            "kullanicilar": len(users),
            "aktif_token": len(active_tokens),
            "toplam_token": len(tokens),
            "adminler": sum(1 for u in users if u.role == "admin"),
            "kullanicilar_liste": [
                {"username": u.username, "role": u.role, "is_active": u.is_active}
                for u in users
            ],
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Singleton
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

auth_manager = AuthManager()


# KullanÄ±m kolaylÄ±ÄŸÄ± için doÄŸrudan fonksiyonlar
def validate_key(key: str) -> Optional[str]:
    """Validate API key, return provider name."""
    return auth_manager.validate_api_key(key)


def create_token(
    username: str, role: str = "user", expires_in: int = 3600
) -> Optional[str]:
    """Create token for user, return access_token string."""
    token = auth_manager.create_token(username, role=role, expires_in=expires_in)
    return token.access_token if token else None


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify token, return payload."""
    return auth_manager.verify_token(token)


def check_role(token: str, required_role: str = "user") -> bool:
    """Check if the token's role is sufficient."""
    return auth_manager.require_role(token, required_role)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Test / CLI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # HÄ±zlÄ± test
        print("=== ReYMeN Auth Test ===")
        print()

        # API key test
        key = "sk-testkey12345678901234567890"
        provider = detect_api_key_provider(key)
        print(f"API Key tespiti: {key} â†’ {provider}")

        key2 = "xai-testkey12345678901234567890"
        provider2 = detect_api_key_provider(key2)
        print(f"API Key tespiti: {key2} â†’ {provider2}")

        print()

        # Token test
        jwt = JWTManager("test-secret-key-32-bytes-long-for-hmac")
        token = jwt.encode({"sub": "testuser", "role": "admin"})
        print(f"JWT Token: {token}")

        decoded = jwt.decode(token)
        print(f"Decoded: {decoded}")

        print()

        # Auth manager test
        m = AuthManager(jwt_secret="test-secret-key-32-bytes-long-for-hmac")
        token_obj = m.create_token("testuser", role="admin")
        if token_obj:
            print(f"Access Token: {token_obj.access_token[:50]}...")
            print(f"Refresh Token: {token_obj.refresh_token[:50]}...")
            payload = m.verify_token(token_obj.access_token)
            print(f"DoÄŸrulama: {payload}")
            print(f"Yetki admin mi?: {m.require_role(token_obj.access_token, 'admin')}")
            print(f"Yetki user mi?: {m.require_role(token_obj.access_token, 'user')}")

        print()
        print("Auth durumu:")
        print(json.dumps(m.status(), indent=2, ensure_ascii=False))
    else:
        print("ReYMeN Auth Sistemi v1.0")
        print("KullanÄ±m: python reymen_auth.py test")
