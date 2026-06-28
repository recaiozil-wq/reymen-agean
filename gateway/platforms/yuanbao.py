# -*- coding: utf-8 -*-
"""gateway/platforms/yuanbao.py — Yuanbao Platformu.

Yuanbao gruplarina mesaj gonderme ve upstream uyumluluk katmani.
"""

import os
import re
from typing import Optional

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

# ---------------------------------------------------------------------------
# Constants (upstream Hermes uyumlu)
# ---------------------------------------------------------------------------
DEFAULT_WS_GATEWAY_URL: str = "wss://yuanbao.woa.com/ws"
DEFAULT_API_DOMAIN: str = "https://api.yuanbao.cn"
HEARTBEAT_INTERVAL_SECONDS: float = 30.0
MAX_RECONNECT_ATTEMPTS: int = 100
NO_RECONNECT_CLOSE_CODES: frozenset = frozenset({4012, 4013})
AUTH_FAILED_CODES: frozenset = frozenset({4001, 4002, 4003, 4010})
AUTH_RETRYABLE_CODES: frozenset = frozenset({4001, 4002})

# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Yuanbao grubuna mesaj gonder.

    Args:
        hedef: Grup kodu
        mesaj: Mesaj icerigi

    Returns:
        Durum mesaji
    """
    token = os.environ.get("YUANBAO_TOKEN", "")
    if not token:
        return "[Yuanbao]: YUANBAO_TOKEN ayarlanmamis."
    if not _REQUESTS_OK:
        return "[Yuanbao]: requests kutuphanesi yok."
    try:
        r = requests.post(
            f"https://api.yuanbao.cn/v1/groups/{hedef}/messages",
            json={"content": mesaj[:2000]},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "[Yuanbao]: Mesaj gonderildi."
        return f"[Yuanbao]: Hata {r.status_code}"
    except Exception as e:
        return f"[Yuanbao]: Hata: {e}"


# ---------------------------------------------------------------------------
# Upstream Hermes uyumluluk siniflari (stub)
# ---------------------------------------------------------------------------


class YuanbaoAdapter:
    """Stub — upstream Hermes YuanbaoAdapter.

    Gercek WebSocket baglantisi ve mesaj yonetimi.
    ReYMeN ortaminda kullanilmiyor, sadece import uyumlulugu.
    """
    pass


class SignManager:
    """Stub — upstream Hermes SignManager."""
    pass


class ConnectionManager:
    """Stub — upstream Hermes ConnectionManager."""
    pass


class OutboundManager:
    """Stub — upstream Hermes OutboundManager."""
    pass


class MessageSender:
    """Stub — upstream Hermes MessageSender."""
    pass


class HeartbeatManager:
    """Stub — upstream Hermes HeartbeatManager."""
    pass


class SlowResponseNotifier:
    """Stub — upstream Hermes SlowResponseNotifier."""
    pass


class MarkdownProcessor:
    """Markdown islemcisi — upstream Hermes uyumluluk katmani.

    Yuanbao platformu icin markdown analiz ve bolme araclari.
    """

    @staticmethod
    def process(text: str) -> str:
        """Markdown metnini platforma uygun formata cevir."""
        return text

    @staticmethod
    def has_unclosed_fence(text: str) -> bool:
        """Kapanmamis kod blogu (```) var mi?"""
        count = text.count("```")
        return count % 2 != 0

    @staticmethod
    def ends_with_table_row(text: str) -> bool:
        """Metnin son satiri tablo satiri mi?"""
        lines = text.strip().split("\n")
        if not lines:
            return False
        last_line = lines[-1].strip()
        return bool(last_line.startswith("|") and last_line.endswith("|"))

    @staticmethod
    def split_at_paragraph_boundary(text: str, max_chars: int) -> tuple:
        """Metni paragraf sinirinda bol.

        Args:
            text: Bolunecek metin
            max_chars: Maksimum karakter (head)

        Returns:
            (head, tail) ikilisi
        """
        if len(text) <= max_chars:
            return text, ""

        # Once paragraf araliginda (bos satir) bolmeyi dene
        para_match = list(re.finditer(r"\n\n", text[:max_chars + 2]))
        if para_match:
            cut = para_match[-1].end()
            return text[:cut], text[cut:]

        # Sonra cumle sonunda bolmeyi dene
        sentence_match = list(re.finditer(r"(?<=[.!?])\s+", text[:max_chars + 2]))
        if sentence_match:
            cut = sentence_match[-1].end()
            return text[:cut], text[cut:]

        # En kotu: yeni satirda
        newline = text.rfind("\n", 0, max_chars)
        if newline > 0:
            return text[:newline], text[newline:]

        # Zorla max_chars'tan kes
        return text[:max_chars], text[max_chars:]

    @staticmethod
    def is_fence_atom(text: str) -> bool:
        """Metin kod blogu basligi mi (```xxx)?"""
        return bool(re.match(r"^\s*```", text))

    @staticmethod
    def is_table_atom(text: str) -> bool:
        """Metin tablo atomu mu (| ile baslayip biten satir)?"""
        return bool(text.strip().startswith("|") and text.strip().endswith("|"))

    @staticmethod
    def split_into_atoms(text: str) -> list:
        """Metni atomik parcalara ayir (fence ve tablo korumali).

        Her paragraf ve kod blogu bir atom.
        """
        if not text:
            return []

        atoms: list[str] = []
        lines = text.split("\n")
        current_atom: list[str] = []
        in_fence = False
        in_table = False

        def flush():
            if current_atom:
                chunk = "\n".join(current_atom)
                if chunk.strip():
                    atoms.append(chunk)
                current_atom.clear()

        def is_table_line(s: str) -> bool:
            stripped = s.strip()
            return bool(stripped.startswith("|") and stripped.endswith("|"))

        for line in lines:
            stripped = line.strip()

            # Fence handling
            if stripped.startswith("```"):
                if not in_fence:
                    flush()
                    current_atom.append(line)
                    in_fence = True
                else:
                    current_atom.append(line)
                    in_fence = False
                    flush()
                in_table = False
            elif in_fence:
                current_atom.append(line)
            # Table handling
            elif is_table_line(line):
                if not in_table:
                    flush()
                    in_table = True
                current_atom.append(line)
            elif in_table:
                # End of table block
                flush()
                in_table = False
                if stripped:
                    current_atom.append(line)
                else:
                    # Empty line — already flushed, continue
                    pass
            elif stripped == "":
                flush()
            else:
                current_atom.append(line)

        flush()
        return atoms

    # ------------------------------------------------------------------
    # Upstream Hermes uyumluluk metodlari
    # ------------------------------------------------------------------

    @staticmethod
    def chunk_markdown_text(text: str, max_chars: int = 2000) -> list:
        """Markdown metnini max_chars boyutunda parcalara bol.

        Kod blogu bolunmez, paragraflar duzgun sinirda kesilir.
        """
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]

        chunks: list[str] = []
        atoms = MarkdownProcessor.split_into_atoms(text)
        current: list[str] = []

        for atom in atoms:
            if MarkdownProcessor._is_atomic_block(atom):
                # Kod blogu vs. — bolunemez
                if current:
                    merged = "".join(current).strip()
                    if merged:
                        chunks.append(merged)
                    current = []
                chunks.append(atom)
            elif len(atom) > max_chars:
                # Uzun paragraf — force kes
                if current:
                    merged = "".join(current).strip()
                    if merged:
                        chunks.append(merged)
                    current = []
                for i in range(0, len(atom), max_chars):
                    chunks.append(atom[i:i + max_chars])
            else:
                current_len = sum(len(s) for s in current) + len(current)
                if current_len + len(atom) > max_chars and current:
                    merged = "".join(current).strip()
                    if merged:
                        chunks.append(merged)
                    current = []
                current.append(atom)

        if current:
            merged = "".join(current).strip()
            if merged:
                chunks.append(merged)

        return chunks

    @staticmethod
    def _is_atomic_block(atom: str) -> bool:
        """Kod blogu veya tablo gibi bolunemez atom mu?"""
        if "```" in atom:
            return True
        lines = atom.strip().split("\n")
        return bool(len(lines) > 1 and all(
            l.strip().startswith("|") and l.strip().endswith("|")
            for l in lines
        ))

    @staticmethod
    def infer_block_separator(prev_block: str, next_block: str) -> str:
        """Iki blok arasinda kullanilacak ayiract.

        Args:
            prev_block: Onceki blok metni
            next_block: Sonraki blok metni

        Returns:
            Ayirac: kod/fence arasi "\\n", tablo arasi "\\n",
                    normal blok arasi "\\n\\n"
        """
        if "```" in prev_block or "```" in next_block:
            return "\n"
        if (prev_block.strip().startswith("|") and prev_block.strip().endswith("|")
                and next_block.strip().startswith("|") and next_block.strip().endswith("|")):
            return "\n"
        return "\n\n"

    @staticmethod
    def merge_block_streaming_fences(chunks: list) -> list:
        """Streaming chunk'larinda bolunmus fence'lari birlestirir.

        Args:
            chunks: Metin parcaciklari listesi

        Returns:
            Birlestirilmis parcalar
        """
        if not chunks:
            return []
        merged: list = []
        buffer: list = []
        in_fence = False

        def flush():
            if buffer:
                merged.append("".join(buffer))
                buffer.clear()

        for chunk in chunks:
            fence_count = chunk.count("```")
            if fence_count % 2 != 0:
                in_fence = not in_fence

            if in_fence or (fence_count > 0 and not in_fence and buffer):
                buffer.append(chunk)
                if not in_fence:
                    flush()
            else:
                if buffer:
                    flush()
                merged.append(chunk)

        if buffer:
            flush()
        return merged

    @staticmethod
    def strip_outer_markdown_fence(text: str) -> str:
        """Dis markdown fence'ini (```markdown/```md) kaldir.

        Args:
            text: Islenecek metin

        Returns:
            Fence'siz metin
        """
        lines = text.split("\n")
        if len(lines) >= 3:
            first = lines[0].strip()
            last = lines[-1].strip()
            if first.startswith("```") and last == "```":
                return "\n".join(lines[1:-1])
        return text

    @staticmethod
    def sanitize_markdown_table(text: str) -> str:
        """Markdown tablosunu platform uyumlu hale getir.

        Su an passthrough, upstream uyumluluk icin.
        """
        return text
