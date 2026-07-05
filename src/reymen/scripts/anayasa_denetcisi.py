# -*- coding: utf-8 -*-
"""
anayasa_denetcisi.py â€” Turkish content moderation / filtering module.

Exports:
    kural_varmi(text) -> (blocked: bool, reason: str)
    mesaj_guvenli_mi(text) -> bool
    _KESIN_GEC              â€” frozenset of safe Turkish words
    _ENGELLI_DESENLER       â€” list of compiled regex patterns for blocked content
    _KIBAR_IFADELER         â€” compiled regex matching polite Turkish phrases
"""

import re

# ---------------------------------------------------------------------------
# Safe words that are always allowed (kesin geçiÅŸ listesi)
# ---------------------------------------------------------------------------
_KESIN_GEC: frozenset = frozenset(
    {
        "merhaba",
        "selam",
        "teÅŸekkür",
        "teÅŸekkürler",
        "günaydÄ±n",
        "iyi geceler",
        "lütfen",
        "rica",
        "yardÄ±m",
    }
)

# ---------------------------------------------------------------------------
# Blocked content patterns (engelli desenler)
# ---------------------------------------------------------------------------
_ENGELLI_DESENLER: list = [
    # Turkish swear / profanity words (no trailing \b â€” catches substrings like siktir)
    re.compile(
        r"(?:\bamÄ±na\s*koyayÄ±m|"
        r"\bamk\b|"
        r"\bananÄ±\s*sik|"
        r"\borospu\s*[çc]o[cç]u[ÄŸg]u|"
        r"\boroÅ¡pu|"
        r"\boroÅŸpu|"
        r"\bsik(?:tir|ik|)\b|"
        r"\bpiç\b|"
        r"\bibne\b|"
        r"\byavÅŸak\b|"
        r"\baptal\s*herif|"
        r"\bmal\s*mal\b)",
        re.IGNORECASE,
    ),
    # Bomb / explosive / malware / harmful instructions
    re.compile(
        r"(?:\bbomba\s*yap|"
        r"\bpatlayÄ±cÄ±\s*yap|"
        r"\btnt\s*yap|"
        r"\bmolotof|"
        r"\bnapalm\b|"
        r"\bbomb\s*making|"
        r"\bexplosive\s*device|"
        r"\bzararl[Ä±i]\s*yazÄ±lÄ±m|"
        r"\bnasÄ±l\s*öldür|"
        r"\bcinayet\s*iÅŸle|"
        r"\badam\s*öldür|"
        r"\böldürmek\s*için)",
        re.IGNORECASE,
    ),
    # Three or more consecutive URLs (with OR without spaces between them)
    re.compile(
        r"(?:https?://[^\s<>\"]+|www\.[^\s<>\"]+)"
        r"(?:\s*(?:https?://[^\s<>\"]+|www\.[^\s<>\"]+)){2,}",
        re.IGNORECASE,
    ),
]

# ---------------------------------------------------------------------------
# Polite Turkish phrase patterns (kibar ifadeler)
# ---------------------------------------------------------------------------
_KIBAR_IFADELER: re.Pattern = re.compile(
    r"\b(?:"
    r"lütfen|teÅŸekkür\s*ederim|teÅŸekkürler|rica\s*ederim|"
    r"afferin|saÄŸ\s*ol|saÄŸol|ellerine\s*saÄŸlÄ±k|"
    r"memnun\s*oldum|kusura\s*bakma|özür\s*dilerim|"
    r"pardon|afedersiniz|yardÄ±mcÄ±\s*olabilir|"
    r"iyi\s*çalÄ±ÅŸmalar|kolay\s*gelsin|hayÄ±rlÄ±\s*iÅŸler"
    r")\b",
    re.IGNORECASE,
)


def _desen_tarama(text: str) -> tuple:
    """Check text against blocked patterns. Returns (blocked, reason)."""
    for pat in _ENGELLI_DESENLER:
        m = pat.search(text)
        if m:
            return (True, f"Uygunsuz içerik tespit edildi: '{m.group()}'")
    return (False, "")


def kural_varmi(text) -> tuple:
    """Check whether *text* violates any content rule.

    Returns:
        (blocked: bool, reason: str)
    """
    if not isinstance(text, str):
        return (False, "")

    text_stripped = text.strip()
    if not text_stripped:
        return (False, "")

    # Blocked patterns â€” checked before all exemptions
    blocked, reason = _desen_tarama(text_stripped)
    if blocked:
        return (blocked, reason)

    # Short-message exemption: <= 5 words = auto-pass
    word_count = len(text_stripped.split())
    if word_count <= 5:
        return (False, "")

    # Safe-word exemption: all tokens are known safe words
    tokens = set(tok.lower() for tok in text_stripped.split())
    if tokens.issubset(_KESIN_GEC):
        return (False, "")

    # Polite phrase filter: if >= 50% of tokens are polite, let it pass
    kibars = _KIBAR_IFADELER.findall(text_stripped)
    if kibars and (len(kibars) / word_count) >= 0.5:
        return (False, "")

    return (False, "")


def mesaj_guvenli_mi(text: str) -> bool:
    """Return True if the message is safe to forward."""
    blocked, _ = kural_varmi(text)
    return not blocked
