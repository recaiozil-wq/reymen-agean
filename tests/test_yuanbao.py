# -*- coding: utf-8 -*-
"""gateway/platforms/yuanbao.py testleri — MarkdownProcessor ve sabitler."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestYuanbaoConstants:
    def test_default_constants(self):
        from gateway.platforms.yuanbao import (
            DEFAULT_WS_GATEWAY_URL,
            DEFAULT_API_DOMAIN,
            HEARTBEAT_INTERVAL_SECONDS,
            MAX_RECONNECT_ATTEMPTS,
            NO_RECONNECT_CLOSE_CODES,
            AUTH_FAILED_CODES,
            AUTH_RETRYABLE_CODES,
        )
        assert "wss://" in DEFAULT_WS_GATEWAY_URL
        assert "https://" in DEFAULT_API_DOMAIN
        assert HEARTBEAT_INTERVAL_SECONDS == 30.0
        assert MAX_RECONNECT_ATTEMPTS == 100
        assert 4012 in NO_RECONNECT_CLOSE_CODES
        assert 4001 in AUTH_FAILED_CODES


class TestMarkdownProcessor:
    def test_has_unclosed_fence_closed(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "once\n```\nkod\n```\nsonra"
        assert MarkdownProcessor.has_unclosed_fence(text) is False

    def test_has_unclosed_fence_open(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "once\n```\nkod henuz kapanmadi"
        assert MarkdownProcessor.has_unclosed_fence(text) is True

    def test_has_unclosed_fence_no_fence(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.has_unclosed_fence("sadece metin") is False

    def test_ends_with_table_row_true(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "baslik\n|hucre1|hucre2|"
        assert MarkdownProcessor.ends_with_table_row(text) is True

    def test_ends_with_table_row_false(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.ends_with_table_row("sadece metin") is False

    def test_ends_with_table_row_empty(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.ends_with_table_row("") is False

    def test_split_at_paragraph_boundary_short(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        head, tail = MarkdownProcessor.split_at_paragraph_boundary("kisa", 100)
        assert head == "kisa"
        assert tail == ""

    def test_split_at_paragraph_boundary_blank_line(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "paragraf1\n\nparagraf2\n\nparagraf3"
        head, tail = MarkdownProcessor.split_at_paragraph_boundary(text, 15)
        assert head == "paragraf1\n\n"
        assert "paragraf2" in tail

    def test_split_at_paragraph_boundary_sentence_end(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "Cumle bitti.\nDevam ediyor.\nDaha fazla."
        head, tail = MarkdownProcessor.split_at_paragraph_boundary(text, 20)
        assert "bitti" in head
        assert "Devam" in tail

    def test_split_at_paragraph_boundary_newline(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "satir1\nsatir2\nsatir3"
        head, tail = MarkdownProcessor.split_at_paragraph_boundary(text, 10)
        assert "satir1" in head
        assert "satir2" in tail or "satir3" in tail

    def test_split_at_paragraph_boundary_force(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "abcdefghijklmnopqrstuvwxyz"
        head, tail = MarkdownProcessor.split_at_paragraph_boundary(text, 10)
        assert len(head) == 10
        assert head + tail == text

    def test_is_fence_atom_true(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.is_fence_atom("```python") is True
        assert MarkdownProcessor.is_fence_atom("  ```bash") is True

    def test_is_fence_atom_false(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.is_fence_atom("normal text") is False

    def test_is_table_atom_true(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.is_table_atom("|a|b|c|") is True

    def test_is_table_atom_false(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.is_table_atom("not a table") is False

    def test_split_into_atoms_empty(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.split_into_atoms("") == []

    def test_split_into_atoms_paragraphs(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "paragraf1\n\nparagraf2\n\nparagraf3"
        atoms = MarkdownProcessor.split_into_atoms(text)
        assert len(atoms) == 3
        assert all("paragraf" in a for a in atoms)

    def test_split_into_atoms_fence(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "once\n```\nkod\n```\nsonra"
        atoms = MarkdownProcessor.split_into_atoms(text)
        assert len(atoms) == 3
        assert atoms[1] == "```\nkod\n```"

    def test_split_into_atoms_table(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "once\n|a|b|\n|c|d|\nsonra"
        atoms = MarkdownProcessor.split_into_atoms(text)
        assert len(atoms) == 3

    def test_chunk_markdown_text_short(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        chunks = MarkdownProcessor.chunk_markdown_text("kisa metin", max_chars=100)
        assert chunks == ["kisa metin"]

    def test_chunk_markdown_text_empty(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.chunk_markdown_text("") == []

    def test_chunk_markdown_text_long(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "paragraf1\n\nparagraf2\n\nparagraf3\n\nparagraf4"
        chunks = MarkdownProcessor.chunk_markdown_text(text, max_chars=15)
        assert len(chunks) >= 2
        assert "".join(chunks).replace("\n\n", "") == text.replace("\n\n", "")

    def test_chunk_markdown_text_fence_not_split(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "kisa\n```\nuzun kod blogu burada\ncok satirli\n```\nson"
        chunks = MarkdownProcessor.chunk_markdown_text(text, max_chars=20)
        assert len(chunks) >= 1
        fence_content = [c for c in chunks if "```" in c]
        assert len(fence_content) >= 1

    def test_chunk_markdown_text_merge_small(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "a\n\nb\n\nc\n\nd"
        chunks = MarkdownProcessor.chunk_markdown_text(text, max_chars=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_infer_block_separator_fence(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        sep = MarkdownProcessor.infer_block_separator("text```", "```more")
        assert sep == "\n"

    def test_infer_block_separator_table(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        sep = MarkdownProcessor.infer_block_separator("|a|b|", "|c|d|")
        assert sep == "\n"

    def test_infer_block_separator_default(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        sep = MarkdownProcessor.infer_block_separator("normal", "metin")
        assert sep == "\n\n"

    def test_merge_block_streaming_fences_empty(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.merge_block_streaming_fences([]) == []

    def test_merge_block_streaming_fences_single(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        result = MarkdownProcessor.merge_block_streaming_fences(["sadece"])
        assert result == ["sadece"]

    def test_merge_block_streaming_fences_merge(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        chunks = ["```\nkod", "devam\n```", "son"]
        result = MarkdownProcessor.merge_block_streaming_fences(chunks)
        assert len(result) < 3  # merged
        assert "```" in result[0]

    def test_strip_outer_markdown_fence_true(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "```markdown\nmerhaba dunya\n```"
        result = MarkdownProcessor.strip_outer_markdown_fence(text)
        assert result == "merhaba dunya"

    def test_strip_outer_markdown_fence_short(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        assert MarkdownProcessor.strip_outer_markdown_fence("a\nb") == "a\nb"

    def test_strip_outer_markdown_fence_no_fence(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "normal metin\ncok satirli"
        result = MarkdownProcessor.strip_outer_markdown_fence(text)
        assert result == text

    def test_strip_outer_markdown_fence_md_alias(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        text = "```md\nmerhaba\n```"
        result = MarkdownProcessor.strip_outer_markdown_fence(text)
        assert result == "merhaba"

    def test_sanitize_markdown_table(self):
        from gateway.platforms.yuanbao import MarkdownProcessor
        result = MarkdownProcessor.sanitize_markdown_table("test")
        assert result == "test"
