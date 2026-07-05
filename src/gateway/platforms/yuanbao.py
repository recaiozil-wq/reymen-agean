# -*- coding: utf-8 -*-
"""Yuanbao platform â€” constants + MarkdownProcessor."""

from __future__ import annotations

import re
from typing import List, Tuple


# â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

DEFAULT_WS_GATEWAY_URL = "wss://yuanbao.tencent.com/api/gateway"
DEFAULT_API_DOMAIN = "https://yuanbao.tencent.com"
HEARTBEAT_INTERVAL_SECONDS = 30.0
MAX_RECONNECT_ATTEMPTS = 100
NO_RECONNECT_CLOSE_CODES = {4012, 4013}
AUTH_FAILED_CODES = {4001, 4003}
AUTH_RETRYABLE_CODES = {4002, 4004}


# â”€â”€ MarkdownProcessor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class MarkdownProcessor:
    """Streaming markdown chunking and fence/table handling."""

    @staticmethod
    def has_unclosed_fence(text: str) -> bool:
        count = 0
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                count += 1
        return count % 2 != 0

    @staticmethod
    def ends_with_table_row(text: str) -> bool:
        if not text:
            return False
        lines = text.rstrip().split("\n")
        last = lines[-1].strip()
        return last.startswith("|") and last.endswith("|") and len(last) > 2

    @staticmethod
    def split_at_paragraph_boundary(text: str, max_chars: int) -> Tuple[str, str]:
        if len(text) <= max_chars:
            return text, ""
        search = text[:max_chars]
        # try blank line
        idx = search.rfind("\n\n")
        if idx > 0:
            return text[: idx + 2], text[idx + 2:]
        # try sentence end
        idx = search.rfind(". ")
        if idx > 0:
            return text[: idx + 2], text[idx + 2:]
        # try newline
        idx = search.rfind("\n")
        if idx > 0:
            return text[: idx + 1], text[idx + 1:]
        # force split
        return text[:max_chars], text[max_chars:]

    @staticmethod
    def is_fence_atom(text: str) -> bool:
        return text.lstrip().startswith("```")

    @staticmethod
    def is_table_atom(text: str) -> bool:
        return text.startswith("|") and text.endswith("|")

    @staticmethod
    def split_into_atoms(text: str) -> List[str]:
        if not text:
            return []
        atoms: List[str] = []
        current: List[str] = []
        in_fence = False

        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```") and not in_fence:
                if current:
                    atoms.append("\n".join(current))
                    current = []
                in_fence = True
                current.append(line)
            elif stripped.startswith("```") and in_fence:
                current.append(line)
                atoms.append("\n".join(current))
                current = []
                in_fence = False
            elif in_fence:
                current.append(line)
            elif line.startswith("|"):
                if current and not current[-1].startswith("|"):
                    atoms.append("\n".join(current))
                    current = []
                current.append(line)
            else:
                if current:
                    atoms.append("\n".join(current))
                    current = []
                current.append(line)

        if current:
            atoms.append("\n".join(current))

        return [a for a in atoms if a.strip()]

    @staticmethod
    def chunk_markdown_text(text: str, max_chars: int = 2000) -> List[str]:
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]

        atoms = MarkdownProcessor.split_into_atoms(text)
        chunks: List[str] = []
        current_chunk = ""

        for atom in atoms:
            if len(current_chunk) + len(atom) + 2 <= max_chars:
                current_chunk = (current_chunk + "\n\n" + atom).strip()
            elif current_chunk:
                chunks.append(current_chunk)
                current_chunk = atom
            else:
                # atom too large, force split
                while atom:
                    head, tail = MarkdownProcessor.split_at_paragraph_boundary(atom, max_chars)
                    chunks.append(head)
                    atom = tail

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def infer_block_separator(prev: str, next_block: str) -> str:
        if prev.rstrip().endswith("```") or next_block.lstrip().startswith("```"):
            return "\n"
        if prev.startswith("|") or next_block.startswith("|"):
            return "\n"
        return "\n\n"

    @staticmethod
    def merge_block_streaming_fences(chunks: List[str]) -> List[str]:
        if not chunks:
            return []
        if len(chunks) == 1:
            return chunks

        result: List[str] = []
        buf = ""
        in_fence = False

        for chunk in chunks:
            if in_fence:
                buf += chunk
                if "```" in chunk:
                    in_fence = False
                    result.append(buf)
                    buf = ""
            elif chunk.lstrip().startswith("```"):
                in_fence = True
                buf = chunk
            else:
                result.append(chunk)

        if buf:
            result.append(buf)

        return result

    @staticmethod
    def strip_outer_markdown_fence(text: str) -> str:
        lines = text.split("\n")
        if len(lines) < 3:
            return text
        first = lines[0].strip()
        last = lines[-1].strip()
        if first.startswith("```") and last == "```":
            lang = first[3:].strip()
            if not lang or lang in ("markdown", "md"):
                return "\n".join(lines[1:-1])
        return text

    @staticmethod
    def sanitize_markdown_table(text: str) -> str:
        return text
