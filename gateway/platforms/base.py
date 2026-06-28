# -*- coding: utf-8 -*-
"""gateway/platforms/base.py — Temel Platform Abstract Sinif."""

import dataclasses
import enum
import os
import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional, Tuple, List

# ── Re-exports for test compatibility ──────────────────────────────────
from gateway.config import Platform  # noqa: F401
from gateway.session import SessionSource as _SessionSource  # noqa


# ── MessageType ───────────────────────────────────────────────────────

class MessageType(enum.Enum):
    TEXT     = "text"
    MEDIA    = "media"
    PHOTO    = "photo"
    AUDIO    = "audio"
    VOICE    = "voice"
    VIDEO    = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    STICKER  = "sticker"
    REACTION = "reaction"
    COMMAND  = "command"
    SYSTEM   = "system"


# ── SendResult ────────────────────────────────────────────────────────

@dataclasses.dataclass
class SendResult:
    """Mesaj gönderme sonucu."""
    success: bool = True
    status: str = "basarili"
    message_id: Optional[str] = None
    error: Optional[str] = None
    raw_response: dict = dataclasses.field(default_factory=dict)


# ── ProcessingOutcome ─────────────────────────────────────────────────

@dataclasses.dataclass
class ProcessingOutcome:
    """Mesaj işleme sonucu."""
    status: str = "ok"
    data: dict = dataclasses.field(default_factory=dict)
    message_id: Optional[str] = None
    error: Optional[str] = None


# ── EphemeralReply ────────────────────────────────────────────────────

@dataclasses.dataclass
class EphemeralReply:
    """Geçici yanıt."""
    content: str = ""
    text: str = ""
    data: dict = dataclasses.field(default_factory=dict)


# ── SessionSource (local stub) ────────────────────────────────────────

@dataclasses.dataclass
class SessionSource:
    """Session kaynağı — re-export with default str fields."""
    platform: str = ""
    session_id: str = ""
    chat_id: str = ""
    chat_name: str = ""
    chat_type: str = "dm"
    user_id: str = ""
    user_name: str = ""
    thread_id: Optional[str] = None


# ── MessageEvent ──────────────────────────────────────────────────────

@dataclasses.dataclass
class MessageEvent:
    """Platform mesaj olayı."""
    platform: str = ""
    chat_id: str = ""
    user_id: str = ""
    user_name: str = ""
    text: str = ""
    message_id: str = ""
    thread_id: Optional[str] = None
    data: dict = dataclasses.field(default_factory=dict)
    chat_type: str = "dm"
    chat_name: str = ""
    message_type: MessageType = MessageType.TEXT


# ── PlatformBase (original abstract class) ───────────────────────────

class PlatformBase(ABC):
    """Tüm platformların türemesi gereken abstract temel sınıf."""

    @abstractmethod
    def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        ...

    @abstractmethod
    def ping(self) -> bool:
        ...

    @abstractmethod
    def parse_message(self, raw: dict, **kwargs) -> dict:
        ...

    def baslat(self):
        pass

    def durdur(self):
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


# ── Constants ─────────────────────────────────────────────────────────

SUPPORTED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}
SUPPORTED_AUDIO_TYPES = {"audio/mpeg", "audio/ogg", "audio/wav", "audio/aac", "audio/flac"}
SUPPORTED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "text/plain",
                             "application/zip", "application/x-tar"}


# ── BasePlatformAdapter ───────────────────────────────────────────────

class BasePlatformAdapter:
    """Temel platform adaptörü — concrete sınıf, tüm metodlar default impl."""

    MAX_MESSAGE_LENGTH: ClassVar[int] = 4096
    enforces_own_access_policy: ClassVar[bool] = False

    def __init__(self, config: Any = None, platform: Any = None, **kwargs):
        self.config = config
        self.platform = platform
        self._yetki = None
        self.message_len_fn = len

    # ── media extraction ──────────────────────────────────────────────

    @classmethod
    def extract_media(cls, content: str) -> Tuple[List[Tuple[str, bool]], str]:
        """MEDIA:/path tags ve [[audio_as_voice]] marker'ını ayıklar."""
        if not content:
            return [], ""
        is_voice = "[[audio_as_voice]]" in content
        cleaned = content.replace("[[audio_as_voice]]", "").strip()
        media = []
        lines = []
        for line in cleaned.splitlines():
            m = re.match(r"^MEDIA:(.+)$", line.strip())
            if m:
                media.append((m.group(1).strip(), is_voice))
            else:
                lines.append(line)
        cleaned_text = "\n".join(lines).strip()
        return media, cleaned_text

    # ── message truncation ────────────────────────────────────────────

    def truncate_message(self, text: str, max_len: int) -> List[str]:
        if len(text) <= max_len:
            return [text]
        chunks = []
        current = []
        current_len = 0
        for line in text.splitlines(keepends=True):
            if current_len + len(line) > max_len and current:
                chunks.append("".join(current))
                current = []
                current_len = 0
            current.append(line)
            current_len += len(line)
        if current:
            chunks.append("".join(current))
        return chunks

    # ── misc ──────────────────────────────────────────────────────────

    def supports_draft_streaming(self) -> bool:
        return False

    def format_tool_event(self, event, mode: str = "preview", preview_max_len: int = 80) -> str:
        name = getattr(event, "tool_name", "?")
        preview = getattr(event, "preview", None)
        args = getattr(event, "args", None)
        if mode == "preview" and preview:
            return f"[{name}] {preview}"
        if args:
            arg_str = " ".join(f"{k}={v}" for k, v in (args.items() if hasattr(args, "items") else {}))
            return f"[{name}] {arg_str[:preview_max_len]}"
        return f"[{name}]"

    def render_message_event(self, event, sink) -> None:
        from gateway.stream_events import MessageChunk, MessageStop
        if isinstance(event, MessageChunk):
            sink.on_delta(event.text)
        elif isinstance(event, MessageStop):
            sink.finish()

    async def edit_message(self, chat_id: str, message_id: str, content: str) -> None:
        raise NotImplementedError("edit_message desteklenmiyor")

    async def send_draft(self, chat_id: str, draft: str, content: str) -> SendResult:
        return SendResult(success=False, error="send_draft desteklenmiyor")

    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        return False

    async def start(self):
        pass

    async def stop(self):
        pass

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        pass

    @classmethod
    def filter_local_delivery_paths(cls, candidates: list) -> list:
        return candidates

    @classmethod
    def filter_media_delivery_paths(cls, candidates: list) -> list:
        return candidates

    @classmethod
    def should_send_media_as_audio(cls, path: str) -> bool:
        return False

    @classmethod
    def delete_message_cls(cls, chat_id: str, message_id: str) -> None:
        pass

    @classmethod
    def edit_message_cls(cls, chat_id: str, message_id: str, text: str) -> None:
        pass


# ── Module-level helpers ──────────────────────────────────────────────

def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    return {"durum": "hata", "hata": "Platform secilmedi"}


def ping() -> bool:
    return False


def parse_message(raw: dict, **kwargs) -> dict:
    return {"gonderen": "", "metin": "", "platform": "bilinmiyor"}


def should_send_media_as_audio(platform: str, ext: str) -> bool:
    audio_exts = {".mp3", ".ogg", ".opus", ".aac", ".flac", ".wav", ".m4a"}
    return ext.lower() in audio_exts


def build_session_key(platform: str, *args: str) -> str:
    return ":".join([platform] + list(args))


def resolve_proxy_url() -> Optional[str]:
    return os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")


def merge_pending_message_event(base: MessageEvent, update: MessageEvent) -> MessageEvent:
    result = dataclasses.replace(base)
    for f in dataclasses.fields(update):
        val = getattr(update, f.name)
        if val and val != f.default:
            setattr(result, f.name, val)
    return result


def is_network_accessible(host: str) -> bool:
    loopback = ("127.", "::1", "localhost")
    return not any(host.startswith(p) for p in loopback)


def _custom_unit_to_cp(unit_str: str) -> int:
    unit_str = unit_str.strip().lower()
    m = re.match(r"^(\d+)(sec|s|min|m|h)$", unit_str)
    if not m:
        return int(unit_str) if unit_str.isdigit() else 0
    val, unit = int(m.group(1)), m.group(2)
    if unit in ("h",):
        return val * 3600
    if unit in ("min", "m"):
        return val * 60
    return val


class MessageDeduplicator:
    def __init__(self, max_size: int = 1000):
        self._seen: set = set()
        self._max_size = max_size

    def is_duplicate(self, message_id: str) -> bool:
        if message_id in self._seen:
            return True
        self._seen.add(message_id)
        if len(self._seen) > self._max_size:
            self._seen.pop()
        return False


def _reply_anchor_for_event(event: MessageEvent) -> Optional[str]:
    return event.message_id or None
