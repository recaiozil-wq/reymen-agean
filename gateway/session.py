# -*- coding: utf-8 -*-
"""gateway/session.py — Gateway Oturum Yonetimi.

Bagli istemcilerin oturumlarini takip eder.
"""

import dataclasses
import time
import threading
import uuid
from collections import OrderedDict
from typing import Any, Dict, Optional


# ── Existing classes ──────────────────────────────────────────────────


class GatewaySession:
    def __init__(self, platform: str, kullanici_id: str):
        self.id = uuid.uuid4().hex[:12]
        self.platform = platform
        self.kullanici_id = kullanici_id
        self.baslangic = time.time()
        self.son_aktivite = time.time()
        self._kilit = threading.Lock()
        self._veri: dict = {}

    def guncelle(self):
        with self._kilit:
            self.son_aktivite = time.time()

    def veri_al(self, anahtar: str, varsayilan=None):
        with self._kilit:
            return self._veri.get(anahtar, varsayilan)

    def veri_set(self, anahtar: str, deger):
        with self._kilit:
            self._veri[anahtar] = deger

    def sure(self) -> float:
        return time.time() - self.baslangic

    def aktif_mi(self, timeout: int = 300) -> bool:
        return time.time() - self.son_aktivite < timeout


class SessionManager:
    def __init__(self):
        self._oturumlar: dict[str, GatewaySession] = {}
        self._kilit = threading.Lock()

    def olustur(self, platform: str, kullanici_id: str) -> GatewaySession:
        with self._kilit:
            oturum = GatewaySession(platform, kullanici_id)
            self._oturumlar[oturum.id] = oturum
            return oturum

    def get(self, session_id: str) -> Optional[GatewaySession]:
        with self._kilit:
            return self._oturumlar.get(session_id)

    def platform_bul(self, platform: str, kullanici_id: str) -> Optional[GatewaySession]:
        with self._kilit:
            for s in self._oturumlar.values():
                if s.platform == platform and s.kullanici_id == kullanici_id and s.aktif_mi():
                    return s
        return None

    def temizle(self, max_sure: int = 3600):
        """Eski oturumlari temizle."""
        with self._kilit:
            silinecek = [sid for sid, s in self._oturumlar.items() if not s.aktif_mi(max_sure)]
            for sid in silinecek:
                del self._oturumlar[sid]

    def liste(self) -> list[dict]:
        with self._kilit:
            return [
                {"id": s.id, "platform": s.platform, "kullanici": s.kullanici_id, "sure": round(s.sure())}
                for s in self._oturumlar.values() if s.aktif_mi()
            ]


# ── Constants imported by tests ────────────────────────────────────────

# Hook isimleri — upstream Hermes'te gateway.session modulunde tanimli
VALID_HOOKS: tuple = (
    "pre_process_message",
    "post_process_message",
    "pre_send_message",
    "post_send_message",
    "pre_run_agent",
    "post_run_agent",
    "pre_llm_call",
    "post_llm_call",
)


# ── New classes imported by gateway/run.py ────────────────────────────


@dataclasses.dataclass
class SessionEntry:
    """Session kaydi — upstream Hermes uyumluluk katmani.

    Test ve gateway.run import zincirini kirabilmek icin minimum alanlari
    iceren dataclass.
    """
    session_key: str = ""
    session_id: str = ""
    created_at: Any = None  # datetime
    updated_at: Any = None  # datetime
    platform: Any = None  # gateway.config.Platform
    chat_type: str = "dm"


@dataclasses.dataclass
class SessionSource:
    """Session kaynagi — mesajin geldigi platform/kanal/kullanici bilgisi."""
    platform: Any = None
    chat_id: str = ""
    chat_name: str = ""
    chat_type: str = "dm"
    user_id: str = ""
    user_name: str = ""
    thread_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SessionSource":
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in dataclasses.fields(cls)}})


@dataclasses.dataclass
class SessionContext:
    """Session baglami — aktif oturum metaverisi."""
    platform: str = ""
    kanal: str = ""
    kullanici: str = ""
    kullanici_adi: str = ""
    baslangic: float = 0.0
    son_aktivite: float = 0.0


class SessionStore:
    """Session deposu — oturumlari yonetir.

    Minimal stub: gateway/run.py'nin import zincirini kirabilmek icin
    gereken minimum arayuzu saglar.
    """

    def __init__(self, sessions_dir: str, config: Any, *,
                 has_active_processes_fn=None):
        self._sessions_dir = sessions_dir
        self._config = config
        self._has_active_processes_fn = has_active_processes_fn
        self._entries: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._loaded = False

    def _ensure_loaded(self):
        pass

    def _ensure_loaded_locked(self):
        pass

    def _generate_session_key(self, source: SessionSource) -> str:
        return f"{source.platform}:{source.chat_id}:{source.user_id}"

    def _save(self):
        pass

    def _is_session_expired(self, entry) -> bool:
        return False

    def get_or_create_session(self, source: SessionSource):
        pass

    def switch_session(self, session_key: str, cli_session_id: str):
        return None

    def suspend_recently_active(self) -> int:
        return 0

    def prune_old_entries(self, max_age: float) -> int:
        return 0


# ── Functions imported by gateway/run.py ──────────────────────────────


def build_session_key(source: SessionSource, *,
                      group_sessions_per_user: bool = True,
                      thread_sessions_per_user: bool = False) -> str:
    """Session anahtari olustur."""
    parts = [str(source.platform or ""), str(source.chat_id or "")]
    if not thread_sessions_per_user and source.thread_id:
        parts.append(str(source.thread_id))
    if group_sessions_per_user:
        parts.append(str(source.user_id or ""))
    return ":".join(parts)


def build_session_context(source: SessionSource, **kwargs) -> SessionContext:
    """SessionContext olustur."""
    return SessionContext(
        platform=str(source.platform or ""),
        kanal=source.chat_id or "",
        kullanici=source.user_id or "",
        kullanici_adi=source.user_name or "",
    )


def build_session_context_prompt(context: SessionContext, *,
                                 redact_pii: bool = False) -> str:
    """Session baglam promptu olustur."""
    parts = [
        f"Platform: {context.platform}",
        f"Channel: {context.kanal}",
        f"User: {context.kullanici}",
    ]
    if context.kullanici_adi:
        parts.append(f"User Name: {context.kullanici_adi}")
    return "\n".join(parts)


def is_shared_multi_user_session(source: SessionSource) -> bool:
    """Cok kullanicili paylasimli session mu?"""
    return source.chat_type in ("group", "channel", "supergroup")


# Global instance
yonetici = SessionManager()
