# -*- coding: utf-8 -*-
"""gateway/config.py — Gateway Yapılandırması.

gateway_config.json okuma/yazma, platform bazlı ayarlar.
"""

import json
import os
import threading
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Optional, Dict
import logging
logger = logging.getLogger(__name__)


# ── Streaming sabitleri ──────────────────────────────────────────────────────
DEFAULT_STREAMING_EDIT_INTERVAL: float = 0.4
DEFAULT_STREAMING_BUFFER_THRESHOLD: int = 60
DEFAULT_STREAMING_CURSOR: str = "▊"


class Platform(StrEnum):
    """Desteklenen platform enum'lari."""
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    MATRIX = "matrix"
    EMAIL = "email"
    WEBHOOK = "webhook"
    QQBOT = "qqbot"
    DINGTALK = "dingtalk"
    FEISHU = "feishu"
    BLUEBUBBLES = "bluebubbles"
    HOMEASSISTANT = "homeassistant"
    SIGNAL = "signal"
    MATTERMOST = "mattermost"
    SMS = "sms"
    LOCAL = "local"
    API_SERVER = "api_server"
    MSGRAPH_WEBHOOK = "msgraph_webhook"
    WECOM_CALLBACK = "wecom_callback"
    WECOM = "wecom"
    WEIXIN = "weixin"
    YUANBAO = "yuanbao"
    GOOGLE_CHAT = "google_chat"
    IRC = "irc"
    LINE = "line"
    NTFY = "ntfy"
    SIMPLEX = "simplex"
    TEAMS = "teams"
    PHOTON = "photon"
    RAFT = "raft"


_BUILTIN_PLATFORM_VALUES: set = {m.value for m in Platform}


@dataclass
class HomeChannel:
    """Bir platform icin ev kanali bilgisi."""
    platform: Any
    chat_id: str
    name: str = ""
    thread_id: Optional[str] = None


@dataclass
class PlatformConfig:
    """Bir platform ozel yapilandirmasi."""
    enabled: bool = True
    home_channel: Optional[HomeChannel] = None
    extra: dict = field(default_factory=dict)


def load_gateway_config(path: Optional[str] = None) -> "GatewayConfig":
    """Gateway yapilandirmasini yukle."""
    return GatewayConfig(path or GATEWAY_CONFIG_PATH)


GATEWAY_CONFIG_PATH = os.environ.get(
    "GATEWAY_CONFIG_PATH",
    os.path.join(os.path.dirname(__file__), "gateway_config.json"),
)

VARSAYILAN_YAPI = {
    # Streaming ayarlari
    "STREAMING_EDIT_INTERVAL": 0.4,
    "STREAMING_BUFFER_THRESHOLD": 60,
    "STREAMING_CURSOR": "▊",
    "genel": {
        "max_mesaj_uzunlugu": 4096,
        "varsayilan_platform": "telegram",
        "zaman_asimi": 30,
        "tekrar_deneme": 3,
    },
    "platformlar": {},
}


class GatewayConfig:
    """Gateway yapılandırma yöneticisi."""

    def __init__(self, json_path: str = GATEWAY_CONFIG_PATH):
        self._json_path = json_path
        self._kilit = threading.Lock()
        self._veri: dict = {}
        self._yukle()

    # ── JSON Depolama ──────────────────────────────────────────────────

    def _yukle(self):
        """JSON dosyasından yapılandırmayı yükle."""
        try:
            if os.path.exists(self._json_path):
                with open(self._json_path, "r", encoding="utf-8") as f:
                    self._veri = json.load(f)
            else:
                self._veri = dict(VARSAYILAN_YAPI)
                self._kaydet()
        except (json.JSONDecodeError, OSError):
            self._veri = dict(VARSAYILAN_YAPI)

    def _kaydet(self):
        """Yapılandırmayı JSON dosyasına yaz."""
        try:
            with open(self._json_path, "w", encoding="utf-8") as f:
                json.dump(self._veri, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise RuntimeError(f"Config kaydedilemedi: {e}")

    # ── Genel Ayarlar ──────────────────────────────────────────────────

    def get(self, anahtar: str, varsayilan: Any = None) -> Any:
        """Genel ayar oku."""
        with self._kilit:
            return self._veri.get("genel", {}).get(anahtar, varsayilan)

    def set(self, anahtar: str, deger: Any):
        """Genel ayar yaz."""
        with self._kilit:
            if "genel" not in self._veri:
                self._veri["genel"] = {}
            self._veri["genel"][anahtar] = deger
            self._kaydet()

    # ── Platform Bazlı Ayarlar ─────────────────────────────────────────

    def platform_ayari(self, platform: str, anahtar: str,
                       varsayilan: Any = None) -> Any:
        """Platforma özel ayar oku."""
        with self._kilit:
            return (self._veri.get("platformlar", {})
                    .get(platform, {}).get(anahtar, varsayilan))

    def platform_ayari_set(self, platform: str, anahtar: str, deger: Any):
        """Platforma özel ayar yaz."""
        with self._kilit:
            if "platformlar" not in self._veri:
                self._veri["platformlar"] = {}
            if platform not in self._veri["platformlar"]:
                self._veri["platformlar"][platform] = {}
            self._veri["platformlar"][platform][anahtar] = deger
            self._kaydet()

    def platform_ayarlari(self, platform: str) -> dict:
        """Platformun tüm ayarlarını döndür."""
        with self._kilit:
            return dict(self._veri.get("platformlar", {}).get(platform, {}))

    def platform_listele(self) -> list[str]:
        """Kayıtlı platformları listele."""
        with self._kilit:
            return list(self._veri.get("platformlar", {}).keys())

    # ── Toplu İşlemler ─────────────────────────────────────────────────

    def tamamini_al(self) -> dict:
        """Tüm yapılandırmayı döndür."""
        with self._kilit:
            return dict(self._veri)

    def sifirla(self):
        """Varsayılan yapılandırmaya dön."""
        with self._kilit:
            self._veri = dict(VARSAYILAN_YAPI)
            self._kaydet()

    def json_yolu(self) -> str:
        return self._json_path

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "config",
            "durum": "hazir",
            "platform_sayisi": len(self.platform_listele()),
            "dosya": self._json_path,
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Yapılandırma üzerinden mesaj gönder (platform ayarı olarak kaydeder)."""
        try:
            self.platform_ayari_set(hedef, "_not", mesaj[:200])
            return f"[Config]: {hedef} için not kaydedildi."
        except Exception as e:
            return f"[Config]: Hata — {e}"


def _apply_env_overrides(config_obj: GatewayConfig) -> None:
    """Ortam degiskenleri ile yapilandirmayi guncelle.

    Upstream Hermes uyumluluk fonksiyonu.
    Ortam degiskenlerinden alinan degerleri GatewayConfig uzerine uygular.

    Args:
        config_obj: GatewayConfig ornegi
    """
    _stream_interval = os.environ.get("STREAMING_EDIT_INTERVAL")
    if _stream_interval:
        config_obj.set("STREAMING_EDIT_INTERVAL", float(_stream_interval))
    _buffer = os.environ.get("STREAMING_BUFFER_THRESHOLD")
    if _buffer:
        config_obj.set("STREAMING_BUFFER_THRESHOLD", int(_buffer))


def get_active_skin() -> Any:
    """Aktif temayi (skin) dondur.

    Upstream Hermes uyumluluk fonksiyonu.
    ReYMeN'de skin ReYMeN_cli.skin_engine uzerinden yonetilir.

    Returns:
        Skin nesnesi veya None
    """
    try:
        from ReYMeN_cli.skin_engine import get_active_skin as _real_get_active_skin
        return _real_get_active_skin()
    except ImportError:
        return None


# Global instance
config = GatewayConfig()


if __name__ == "__main__":
    gc = GatewayConfig()
    print("Varsayılan:", gc.get("max_mesaj_uzunlugu"))
    gc.platform_ayari_set("telegram", "token", "abc123")
    print("Telegram:", gc.platform_ayarlari("telegram"))
    print(gc.ping())
