# -*- coding: utf-8 -*-
"""gateway/session_context.py — Oturum Bağlamı.

Gateway oturum bilgilerini (platform, kanal, kullanıcı) saklar ve yönetir.
"""

import os
import threading
import time
import uuid
from typing import Any, Optional


class SessionContext:
    """Tek bir oturum bağlamı — platform, kanal, kullanıcı bilgileri."""

    def __init__(self, platform: str, kanal: str, kullanici: str,
                 kullanici_adi: str = ""):
        self.id = uuid.uuid4().hex[:12]
        self.platform = platform
        self.kanal = kanal
        self.kullanici = kullanici
        self.kullanici_adi = kullanici_adi or kullanici
        self.baslangic = time.time()
        self.son_aktivite = time.time()
        self._veri: dict[str, Any] = {}
        self._kilit = threading.Lock()

    # ── Veri Yönetimi ─────────────────────────────────────────────────

    def set(self, anahtar: str, deger: Any):
        """Oturum verisi sakla."""
        with self._kilit:
            self._veri[anahtar] = deger

    def get(self, anahtar: str, varsayilan: Any = None) -> Any:
        """Oturum verisi oku."""
        with self._kilit:
            return self._veri.get(anahtar, varsayilan)

    def sil(self, anahtar: str) -> bool:
        """Oturum verisi sil."""
        with self._kilit:
            return bool(self._veri.pop(anahtar, None))

    def veri_al(self) -> dict:
        """Tüm oturum verisini döndür."""
        with self._kilit:
            return dict(self._veri)

    # ── Durum ─────────────────────────────────────────────────────────

    def guncelle(self):
        """Son aktivite zamanını güncelle."""
        self.son_aktivite = time.time()

    def sure(self) -> float:
        """Oturum süresini döndür (saniye)."""
        return time.time() - self.baslangic

    def aktif_mi(self, timeout: int = 300) -> bool:
        """Oturum hala aktif mi (zaman aşımı kontrolü)."""
        return time.time() - self.son_aktivite < timeout

    def ozet(self) -> dict:
        """Oturum özetini döndür."""
        return {
            "id": self.id,
            "platform": self.platform,
            "kanal": self.kanal,
            "kullanici": self.kullanici,
            "kullanici_adi": self.kullanici_adi,
            "sure": round(self.sure()),
            "aktif": self.aktif_mi(),
        }


class SessionContextManager:
    """Oturum bağlam yöneticisi — tüm oturumları takip eder."""

    def __init__(self):
        self._oturumlar: dict[str, SessionContext] = {}
        self._kilit = threading.Lock()

    # ── Oluşturma ve Bulma ────────────────────────────────────────────

    def olustur(self, platform: str, kanal: str, kullanici: str,
                kullanici_adi: str = "") -> SessionContext:
        """Yeni oturum bağlamı oluştur."""
        ctx = SessionContext(platform, kanal, kullanici, kullanici_adi)
        with self._kilit:
            self._oturumlar[ctx.id] = ctx
        return ctx

    def get(self, ctx_id: str) -> Optional[SessionContext]:
        """ID ile oturum bağlamı bul."""
        with self._kilit:
            return self._oturumlar.get(ctx_id)

    def bul(self, platform: str, kullanici: str) -> Optional[SessionContext]:
        """Platform ve kullanıcı ile oturum bul."""
        with self._kilit:
            for ctx in self._oturumlar.values():
                if ctx.platform == platform and ctx.kullanici == kullanici and ctx.aktif_mi():
                    ctx.guncelle()
                    return ctx
        return None

    def platform_oturumlari(self, platform: str) -> list[SessionContext]:
        """Platformdaki tüm aktif oturumları döndür."""
        with self._kilit:
            return [ctx for ctx in self._oturumlar.values()
                    if ctx.platform == platform and ctx.aktif_mi()]

    def kullanici_oturumlari(self, kullanici: str) -> list[SessionContext]:
        """Kullanıcının tüm oturumlarını döndür."""
        with self._kilit:
            return [ctx for ctx in self._oturumlar.values()
                    if ctx.kullanici == kullanici and ctx.aktif_mi()]

    # ── Temizlik ──────────────────────────────────────────────────────

    def temizle(self, max_sure: int = 3600):
        """Zaman aşımına uğramış oturumları temizle."""
        with self._kilit:
            silinecek = [
                cid for cid, ctx in self._oturumlar.items()
                if not ctx.aktif_mi(max_sure)
            ]
            for cid in silinecek:
                del self._oturumlar[cid]

    def sil(self, ctx_id: str) -> bool:
        """Belirli bir oturumu sil."""
        with self._kilit:
            return bool(self._oturumlar.pop(ctx_id, None))

    # ── İstatistik ────────────────────────────────────────────────────

    def sayi(self) -> int:
        """Aktif oturum sayısı."""
        with self._kilit:
            return sum(1 for ctx in self._oturumlar.values() if ctx.aktif_mi())

    def liste(self) -> list[dict]:
        """Tüm aktif oturumların özet listesi."""
        with self._kilit:
            return [ctx.ozet() for ctx in self._oturumlar.values() if ctx.aktif_mi()]

    def platform_dagilimi(self) -> dict[str, int]:
        """Platform bazında oturum dağılımı."""
        dagilim: dict[str, int] = {}
        with self._kilit:
            for ctx in self._oturumlar.values():
                if ctx.aktif_mi():
                    dagilim[ctx.platform] = dagilim.get(ctx.platform, 0) + 1
        return dagilim

    # ── Ortak Gateway Metodları ───────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "session_context",
            "durum": "hazir",
            "aktif_oturum": self.sayi(),
            "platform_dagilimi": self.platform_dagilimi(),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Bir oturum bağlamına mesaj gönder.

        hedef: oturum ID'si veya "platform:kullanici" formatı
        """
        ctx: Optional[SessionContext] = None

        # Önce ID olarak dene
        ctx = self.get(hedef)

        # "platform:kullanici" formatını dene
        if not ctx and ":" in hedef:
            platform, kullanici = hedef.split(":", 1)
            ctx = self.bul(platform, kullanici)

        if ctx:
            ctx.set("son_mesaj", mesaj[:100])
            ctx.guncelle()
            return f"[Session] {ctx.platform}/{ctx.kullanici}: mesaj kaydedildi."
        return f"[Session]: '{hedef}' oturumu bulunamadı."


# Global instance
baglam = SessionContextManager()


# ── Session Environment Variable Helpers ─────────────────────────────

_SESSION_ENV_PREFIX = "ReYMeN_SESSION_"


def get_session_env(key: str) -> str:
    """Read a session environment variable by its full key name."""
    return os.environ.get(key, "")


def set_session_vars(**kwargs) -> list:
    """Set session env vars and return tokens for restoration.

    Each keyword arg name is uppercased and prefixed to form the
    env var key (e.g. platform → ReYMeN_SESSION_PLATFORM).
    Returns a list of (key, old_value) tuples for clear_session_vars.
    """
    tokens = []
    for k, v in kwargs.items():
        env_key = f"{_SESSION_ENV_PREFIX}{k.upper()}"
        old = os.environ.get(env_key, "")
        os.environ[env_key] = "" if v is None else str(v)
        tokens.append((env_key, old))
    return tokens


def clear_session_vars(tokens: list):
    """Restore session env vars to their previous values."""
    for env_key, old_val in tokens:
        if old_val:
            os.environ[env_key] = old_val
        else:
            os.environ.pop(env_key, None)


def set_current_session_id(session_id: str):
    """Set the current session ID in the environment."""
    os.environ["ReYMeN_CURRENT_SESSION_ID"] = session_id


def get_current_session_id() -> str:
    """Read the current session ID from the environment."""
    return os.environ.get("ReYMeN_CURRENT_SESSION_ID", "")


if __name__ == "__main__":
    sm = SessionContextManager()
    ctx = sm.olustur("telegram", "kanal_1", "user_abc", "Ahmet")
    print(f"Oturum: {ctx.ozet()}")
    ctx.set("son_komut", "/yardim")
    print(f"Veri: {ctx.get('son_komut')}")
    print(sm.ping())
