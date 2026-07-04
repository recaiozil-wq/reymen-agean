# -*- coding: utf-8 -*-
"""Yuanbao sticker utilities — lookup, search, random selection."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional


# ── Sticker Map ─────────────────────────────────────────────────────────────

STICKER_MAP: Dict[str, Dict[str, str]] = {
    "六六六": {"sticker_id": "278", "package_id": "1003", "name": "六六六", "description": "awesome six"},
    "爱心": {"sticker_id": "138", "package_id": "1003", "name": "爱心", "description": "love heart"},
    "抱抱": {"sticker_id": "139", "package_id": "1003", "name": "抱抱", "description": "hug"},
    "点赞": {"sticker_id": "140", "package_id": "1003", "name": "点赞", "description": "thumbs up"},
    "开心": {"sticker_id": "141", "package_id": "1003", "name": "开心", "description": "happy"},
    "大笑": {"sticker_id": "142", "package_id": "1003", "name": "大笑", "description": "laugh"},
    "哭": {"sticker_id": "143", "package_id": "1003", "name": "哭", "description": "cry"},
    "生气": {"sticker_id": "144", "package_id": "1003", "name": "生气", "description": "angry"},
    "惊讶": {"sticker_id": "145", "package_id": "1003", "name": "惊讶", "description": "surprised"},
    "思考": {"sticker_id": "146", "package_id": "1003", "name": "思考", "description": "thinking"},
    "加油": {"sticker_id": "147", "package_id": "1003", "name": "加油", "description": "cheer up"},
    "晚安": {"sticker_id": "148", "package_id": "1003", "name": "晚安", "description": "good night"},
    "早安": {"sticker_id": "149", "package_id": "1003", "name": "早安", "description": "good morning"},
    "谢谢": {"sticker_id": "150", "package_id": "1003", "name": "谢谢", "description": "thank you"},
    "恭喜": {"sticker_id": "151", "package_id": "1003", "name": "恭喜", "description": "congratulations"},
    "干杯": {"sticker_id": "152", "package_id": "1003", "name": "干杯", "description": "cheers"},
    "比心": {"sticker_id": "153", "package_id": "1003", "name": "比心", "description": "finger heart"},
    "厉害": {"sticker_id": "154", "package_id": "1003", "name": "厉害", "description": "amazing"},
    "加油鸭": {"sticker_id": "155", "package_id": "1003", "name": "加油鸭", "description": "cheer duck"},
    "冲鸭": {"sticker_id": "156", "package_id": "1003", "name": "冲鸭", "description": "charge duck"},
}


# ── Helper functions ────────────────────────────────────────────────────────


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().lower()


def _compact_text(text: str) -> str:
    return "".join(text.split())


def _multiset_char_hit_ratio(query: str, target: str) -> float:
    if not query or not target:
        return 0.0
    q_chars = {}
    for c in query:
        q_chars[c] = q_chars.get(c, 0) + 1
    t_chars = {}
    for c in target:
        t_chars[c] = t_chars.get(c, 0) + 1
    overlap = sum(min(q_chars[c], t_chars.get(c, 0)) for c in q_chars)
    return overlap / max(len(query), 1)


def _bigram_jaccard(a: str, b: str) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    a_bigrams = set(a[i:i+2] for i in range(len(a) - 1))
    b_bigrams = set(b[i:i+2] for i in range(len(b) - 1))
    if not a_bigrams or not b_bigrams:
        return 0.0
    return len(a_bigrams & b_bigrams) / len(a_bigrams | b_bigrams)


def _longest_subsequence_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    lcs_len = dp[m][n]
    return lcs_len / m if m else 0.0


def _score_field(query: str, field: str) -> float:
    q = _normalize_text(query)
    f = _normalize_text(field)
    if not q or not f:
        return 0.0
    if q == f:
        return 1.0
    if q in f:
        return 0.8
    return (
        _multiset_char_hit_ratio(q, f) * 0.4
        + _bigram_jaccard(q, f) * 0.3
        + _longest_subsequence_ratio(q, f) * 0.3
    )


# ── Public API ──────────────────────────────────────────────────────────────


def get_sticker_by_name(query: str) -> Optional[Dict[str, str]]:
    if not query:
        return None
    q = _normalize_text(query)
    best_score = 0.0
    best_sticker = None
    for name, sticker in STICKER_MAP.items():
        score = max(
            _score_field(q, name),
            _score_field(q, sticker.get("description", "")),
        )
        if score > best_score:
            best_score = score
            best_sticker = sticker
    return best_sticker if best_score > 0.5 else None


def get_random_sticker(category: Optional[str] = None) -> Dict[str, str]:
    if category:
        matches = [
            s for s in STICKER_MAP.values()
            if category.lower() in s.get("description", "").lower()
            or category.lower() in s.get("name", "").lower()
        ]
        if matches:
            return random.choice(matches)
    return random.choice(list(STICKER_MAP.values()))


def get_sticker_by_id(sticker_id: str) -> Optional[Dict[str, str]]:
    for sticker in STICKER_MAP.values():
        if sticker["sticker_id"] == sticker_id:
            return sticker
    return None


def search_stickers(query: str, limit: int = 10) -> List[Dict[str, str]]:
    if not query:
        return list(STICKER_MAP.values())[:limit]
    results = []
    for name, sticker in STICKER_MAP.items():
        score = max(
            _score_field(query, name),
            _score_field(query, sticker.get("description", "")),
        )
        if score > 0.3:
            results.append(sticker)
    return results[:limit]
