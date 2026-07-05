# -*- coding: utf-8 -*-
"""Yuanbao sticker utilities â€” lookup, search, random selection."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional


# â”€â”€ Sticker Map â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

STICKER_MAP: Dict[str, Dict[str, str]] = {
    "å…­å…­å…­": {"sticker_id": "278", "package_id": "1003", "name": "å…­å…­å…­", "description": "awesome six"},
    "çˆ±å¿ƒ": {"sticker_id": "138", "package_id": "1003", "name": "çˆ±å¿ƒ", "description": "love heart"},
    "æŠ±æŠ±": {"sticker_id": "139", "package_id": "1003", "name": "æŠ±æŠ±", "description": "hug"},
    "ç‚¹èµ": {"sticker_id": "140", "package_id": "1003", "name": "ç‚¹èµ", "description": "thumbs up"},
    "å¼€å¿ƒ": {"sticker_id": "141", "package_id": "1003", "name": "å¼€å¿ƒ", "description": "happy"},
    "å¤§ç¬‘": {"sticker_id": "142", "package_id": "1003", "name": "å¤§ç¬‘", "description": "laugh"},
    "å“­": {"sticker_id": "143", "package_id": "1003", "name": "å“­", "description": "cry"},
    "ç”Ÿæ°”": {"sticker_id": "144", "package_id": "1003", "name": "ç”Ÿæ°”", "description": "angry"},
    "æƒŠè®¶": {"sticker_id": "145", "package_id": "1003", "name": "æƒŠè®¶", "description": "surprised"},
    "æ€è€ƒ": {"sticker_id": "146", "package_id": "1003", "name": "æ€è€ƒ", "description": "thinking"},
    "åŠ æ²¹": {"sticker_id": "147", "package_id": "1003", "name": "åŠ æ²¹", "description": "cheer up"},
    "æ™šå®‰": {"sticker_id": "148", "package_id": "1003", "name": "æ™šå®‰", "description": "good night"},
    "æ—©å®‰": {"sticker_id": "149", "package_id": "1003", "name": "æ—©å®‰", "description": "good morning"},
    "è°¢è°¢": {"sticker_id": "150", "package_id": "1003", "name": "è°¢è°¢", "description": "thank you"},
    "æ­å–œ": {"sticker_id": "151", "package_id": "1003", "name": "æ­å–œ", "description": "congratulations"},
    "å¹²æ¯": {"sticker_id": "152", "package_id": "1003", "name": "å¹²æ¯", "description": "cheers"},
    "æ¯”å¿ƒ": {"sticker_id": "153", "package_id": "1003", "name": "æ¯”å¿ƒ", "description": "finger heart"},
    "å‰å®³": {"sticker_id": "154", "package_id": "1003", "name": "å‰å®³", "description": "amazing"},
    "åŠ æ²¹é¸­": {"sticker_id": "155", "package_id": "1003", "name": "åŠ æ²¹é¸­", "description": "cheer duck"},
    "å†²é¸­": {"sticker_id": "156", "package_id": "1003", "name": "å†²é¸­", "description": "charge duck"},
}


# â”€â”€ Helper functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


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


# â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


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
