"""🔐 JWT Auth — giriş/çıkış/session yönetimi + roller + izinler.

Kullanim:
    from reymen.web_ui.auth import AuthConfig, UserManager, TokenManager, Role

    # Rol bazlı kullanıcı
    um.kullanici_ekle("admin", "sifre", role=Role.ADMIN)
    um.kullanici_ekle("operator", "sifre", role=Role.OPERATOR)
    um.kullanici_ekle("viewer", "sifre", role=Role.VIEWER)

    # İzin kontrolü
    if um.has_permission("admin", "gateway.restart"): ...
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROJE_KOK = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Roller
# ---------------------------------------------------------------------------

class Role(str, Enum):
    """Kullanıcı rolleri — yetki hiyerarşisi."""
    ADMIN = "admin"       # Tam yetki
    OPERATOR = "operator" # Araç kullanabilir, yapılandıramaz
    VIEWER = "viewer"     # Sadece görüntüleme

# İzin tanımları: rol -> izin seti
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        "gateway.baslat", "gateway.durdur", "gateway.restart", "gateway.ayarlar",
        "plugin.aktif_et", "plugin.devre_disina_al",
        "user.ekle", "user.sil", "user.sifre_degistir",
        "system.yeniden_baslat", "system.guncelle",
        "log.goruntule", "log.temizle",
        "a2a.yonet", "a2a.mesaj_gonder",
        "maliyet.goruntule", "kalite.goruntule",
        "kanban.yonet",
    },
    Role.OPERATOR: {
        "gateway.baslat", "gateway.durdur",
        "plugin.aktif_et", "plugin.devre_disina_al",
        "log.goruntule",
        "a2a.mesaj_gonder",
        "maliyet.goruntule", "kalite.goruntule",
        "kanban.yonet",
    },
    Role.VIEWER: {
        "log.goruntule",
        "maliyet.goruntule", "kalite.goruntule",
    },
}

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class AuthConfig:
    secret: str = field(default_factory=lambda: os.getenv(
        "WEB_UI_SECRET",
        hashlib.sha256(f"ReYMeN-web-ui-{os.getpid()}-{time.time()}".encode()).hexdigest()[:32]
    ))
    token_expiry: int = 86400          # 24 saat
    cookie_name: str = "reymen_token"
    users_file: Path = field(default_factory=lambda: PROJE_KOK / ".ReYMeN" / "web" / "users.json")

# ---------------------------------------------------------------------------
# Kullanıcı yönetimi
# ---------------------------------------------------------------------------

@dataclass
class UserData:
    """Kullanıcı verisi (role dahil)."""
    password_hash: str
    role: str = Role.VIEWER.value
    created: float = field(default_factory=time.time)

class UserManager:
    """users.json ile kullanıcı yönetimi + roller."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config
        self._users: dict[str, dict] = {}  # username -> {password_hash, role, created}
        self._load()

    def _load(self) -> None:
        dosya = self.config.users_file
        if dosya.exists():
            try:
                data = json.loads(dosya.read_text(encoding="utf-8"))
                # Eski format uyumluluğu: sadece hash varsa role ekle
                for k, v in data.items():
                    if isinstance(v, str):
                        self._users[k] = {"password_hash": v, "role": Role.ADMIN.value, "created": 0}
                    elif isinstance(v, dict):
                        if "role" not in v:
                            v["role"] = Role.ADMIN.value
                        self._users[k] = v
            except Exception as e:
                logger.warning("users.json okunamadi: %s", e)
                self._default_users()
        else:
            self._default_users()
            self._save()

    def _default_users(self) -> None:
        self._users = {
            "admin": {
                "password_hash": self._hash("reymen"),
                "role": Role.ADMIN.value,
                "created": time.time(),
            }
        }

    def _save(self) -> None:
        self.config.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.users_file.write_text(
            json.dumps(self._users, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, username: str, password: str) -> bool:
        user = self._users.get(username)
        if not user:
            return False
        return user["password_hash"] == self._hash(password)

    def kullanici_ekle(self, username: str, password: str,
                       role: str = Role.VIEWER.value) -> tuple[bool, str]:
        """Kullanıcı ekle. Var olanı güncellemez."""
        if username in self._users:
            return False, "Kullanici zaten var"
        try:
            Role(role)  # validate
        except ValueError:
            return False, f"Gecersiz rol: {role}. Gecerliler: {[r.value for r in Role]}"
        self._users[username] = {
            "password_hash": self._hash(password),
            "role": role,
            "created": time.time(),
        }
        self._save()
        return True, f"Kullanici eklendi: {username} ({role})"

    def kullanici_sil(self, username: str) -> tuple[bool, str]:
        if username not in self._users:
            return False, "Kullanici bulunamadi"
        if username == "admin":
            return False, "admin kullanicisi silinemez"
        del self._users[username]
        self._save()
        return True, f"Kullanici silindi: {username}"

    def set_password(self, username: str, password: str,
                     old_password: str | None = None) -> tuple[bool, str]:
        """Şifre değiştir. admin her zaman değiştirebilir."""
        if username not in self._users:
            return False, "Kullanici bulunamadi"
        # Eski şifre kontrolü (admin bypass)
        if old_password and self._users[username]["password_hash"] != self._hash(old_password):
            return False, "Eski sifre yanlis"
        self._users[username]["password_hash"] = self._hash(password)
        self._save()
        return True, "Sifre degistirildi"

    def set_role(self, username: str, role: str) -> tuple[bool, str]:
        if username not in self._users:
            return False, "Kullanici bulunamadi"
        try:
            Role(role)
        except ValueError:
            return False, f"Gecersiz rol: {role}"
        self._users[username]["role"] = role
        self._save()
        return True, f"Rol degistirildi: {username} -> {role}"

    def get_role(self, username: str) -> str | None:
        user = self._users.get(username)
        if user:
            return user.get("role", Role.VIEWER.value)
        return None

    def has_permission(self, username: str, permission: str) -> bool:
        """Kullanıcının belirli bir izni var mı?"""
        role_str = self.get_role(username)
        if not role_str:
            return False
        try:
            role = Role(role_str)
        except ValueError:
            return False
        return permission in ROLE_PERMISSIONS.get(role, set())

    def list_users(self) -> list[dict]:
        """Kullanıcı listesi (şifresiz)."""
        return [
            {"username": k, "role": v.get("role", Role.VIEWER.value),
             "created": v.get("created", 0)}
            for k, v in self._users.items()
        ]

# ---------------------------------------------------------------------------
# JWT Token
# ---------------------------------------------------------------------------

class TokenManager:
    """HMAC-SHA256 JWT benzeri token + role bilgisi."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def create(self, username: str, role: str = Role.VIEWER.value) -> str:
        payload = json.dumps({
            "user": username,
            "role": role,
            "exp": int(time.time()) + self.config.token_expiry,
            "iat": int(time.time()),
        }, separators=(",", ":"))
        b64 = self._b64_encode(payload.encode())
        sig = self._sign(b64)
        return f"{b64}.{sig}"

    def verify(self, token: str) -> Optional[dict]:
        """Token doğrula, {user, role, exp} döndür veya None."""
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            b64, sig = parts
            expected_sig = self._sign(b64)
            if not hmac.compare_digest(sig, expected_sig):
                return None
            payload = json.loads(self._b64_decode(b64))
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None

    def get_user(self, token: str) -> Optional[str]:
        data = self.verify(token)
        return data.get("user") if data else None

    def get_role(self, token: str) -> Optional[str]:
        data = self.verify(token)
        return data.get("role") if data else None

    def _sign(self, data: str) -> str:
        return hmac.new(
            self.config.secret.encode(), data.encode(), hashlib.sha256
        ).hexdigest()[:16]

    @staticmethod
    def _b64_encode(data: bytes) -> str:
        return data.hex()

    @staticmethod
    def _b64_decode(data: str) -> bytes:
        return bytes.fromhex(data)

# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_config = AuthConfig()
user_manager = UserManager(_config)
token_manager = TokenManager(_config)
