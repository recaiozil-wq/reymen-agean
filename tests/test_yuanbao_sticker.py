# -*- coding: utf-8 -*-
"""gateway/platforms/yuanbao_sticker.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestStickerMap:
    def test_sticker_map_size(self):
        from gateway.platforms.yuanbao_sticker import STICKER_MAP
        assert len(STICKER_MAP) > 0
        # Check required fields
        for key, sticker in STICKER_MAP.items():
            assert "sticker_id" in sticker
            assert "package_id" in sticker
            assert "name" in sticker
            assert sticker["package_id"] == "1003"

    def test_specific_stickers(self):
        from gateway.platforms.yuanbao_sticker import STICKER_MAP
        assert "六六六" in STICKER_MAP
        assert STICKER_MAP["六六六"]["sticker_id"] == "278"
        assert "爱心" in STICKER_MAP
        assert STICKER_MAP["爱心"]["sticker_id"] == "138"


class TestGetStickerByName:
    def test_exact_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_name
        result = get_sticker_by_name("六六六")
        assert result is not None
        assert result["sticker_id"] == "278"

    def test_partial_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_name
        result = get_sticker_by_name("六六")
        assert result is not None

    def test_description_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_name
        result = get_sticker_by_name("awesome")
        assert result is not None

    def test_no_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_name
        # Use a completely unique query that can't be in any description
        result = get_sticker_by_name("qwertyuiop1234567890")
        assert result is None

    def test_empty_query(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_name
        assert get_sticker_by_name("") is None
        assert get_sticker_by_name(None) is None


class TestGetRandomSticker:
    def test_random_no_category(self):
        from gateway.platforms.yuanbao_sticker import get_random_sticker
        result = get_random_sticker()
        assert result is not None
        assert "sticker_id" in result

    def test_random_with_category(self):
        from gateway.platforms.yuanbao_sticker import get_random_sticker
        result = get_random_sticker(category="love")
        assert result is not None
        assert "sticker_id" in result

    def test_random_unmatched_category(self):
        from gateway.platforms.yuanbao_sticker import get_random_sticker
        result = get_random_sticker(category="zzz_unmatched_category_xyz")
        assert result is not None  # falls back to full table


class TestGetStickerById:
    def test_exact_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_id
        result = get_sticker_by_id("278")
        assert result is not None
        assert result["name"] == "六六六"

    def test_no_match(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_id
        assert get_sticker_by_id("999999") is None

    def test_empty(self):
        from gateway.platforms.yuanbao_sticker import get_sticker_by_id
        assert get_sticker_by_id("") is None
        assert get_sticker_by_id(None) is None


class TestSearchStickers:
    def test_search_empty(self):
        from gateway.platforms.yuanbao_sticker import search_stickers
        results = search_stickers("")
        assert len(results) > 0  # returns all

    def test_search_by_name(self):
        from gateway.platforms.yuanbao_sticker import search_stickers
        results = search_stickers("六六六", limit=5)
        assert len(results) >= 1
        assert any(r["name"] == "六六六" for r in results)

    def test_search_by_keyword(self):
        from gateway.platforms.yuanbao_sticker import search_stickers
        results = search_stickers("awesome", limit=5)
        assert len(results) >= 1

    def test_search_limit(self):
        from gateway.platforms.yuanbao_sticker import search_stickers
        results = search_stickers("a", limit=3)
        assert len(results) <= 3

    def test_search_no_match(self):
        from gateway.platforms.yuanbao_sticker import search_stickers
        results = search_stickers("zzz_nonexistent_xyz_12345", limit=10)
        assert isinstance(results, list)


class TestInternals:
    def test_normalize_text(self):
        from gateway.platforms.yuanbao_sticker import _normalize_text
        assert _normalize_text("Merhaba") == "merhaba"
        assert _normalize_text("") == ""
        assert _normalize_text(None) == ""

    def test_compact_text(self):
        from gateway.platforms.yuanbao_sticker import _compact_text
        assert _compact_text("hello world") == "helloworld"

    def test_multiset_char_hit_ratio(self):
        from gateway.platforms.yuanbao_sticker import _multiset_char_hit_ratio
        ratio = _multiset_char_hit_ratio("abc", "abcde")
        assert ratio == 1.0
        ratio2 = _multiset_char_hit_ratio("xyz", "abcde")
        assert ratio2 == 0.0

    def test_bigram_jaccard(self):
        from gateway.platforms.yuanbao_sticker import _bigram_jaccard
        score = _bigram_jaccard("test", "test")
        assert score == 1.0
        score2 = _bigram_jaccard("abcd", "wxyz")
        assert score2 == 0.0
        score3 = _bigram_jaccard("a", "b")
        assert score3 == 0.0  # short strings

    def test_longest_subsequence_ratio(self):
        from gateway.platforms.yuanbao_sticker import _longest_subsequence_ratio
        ratio = _longest_subsequence_ratio("abc", "aXbXc")
        assert ratio == 1.0
        ratio2 = _longest_subsequence_ratio("abc", "def")
        assert ratio2 == 0.0
        ratio3 = _longest_subsequence_ratio("", "abc")
        assert ratio3 == 0.0

    def test_score_field(self):
        from gateway.platforms.yuanbao_sticker import _score_field
        score = _score_field("Merhaba Dunya", "Merhaba")
        assert score > 0
        score2 = _score_field("", "test")
        assert score2 == 0.0
        score3 = _score_field("test", "")
        assert score3 == 0.0
