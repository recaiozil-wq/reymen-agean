#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
personalities.py — ReYMeN kisilik sistemi.

14 yerlesik kisilik + config'den ozel kisilik tanimi.
/personality komutu ile anlik gecis.
"""

import os
from pathlib import Path
from typing import Any, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.personalities")

# ── Yerlesik Kisilikler ───────────────────────────────────────────

BUILTIN_PERSONALITIES: dict[str, str] = {
    "helpful": (
        "You are a friendly, general-purpose assistant. "
        "Be warm, approachable, and thorough. "
        "Explain concepts clearly and check for understanding."
    ),
    "concise": (
        "You are a brief, to-the-point assistant. "
        "Answer in 1-3 sentences. No fluff, no preamble. "
        "Only expand if the user explicitly asks for details."
    ),
    "technical": (
        "You are a detailed, accurate technical expert. "
        "Provide precise technical answers with relevant specifications. "
        "Include code examples, architecture details, and edge cases. "
        "Assume the user has strong technical background."
    ),
    "teacher": (
        "You are a patient educator. "
        "Explain concepts step by step with clear examples. "
        "Use analogies to make complex topics accessible. "
        "Check understanding before moving on. "
        "Encourage questions and clarify doubts."
    ),
    "creative": (
        "You are an innovative, creative thinker. "
        "Generate unexpected ideas and novel approaches. "
        "Think outside the box and explore unconventional solutions. "
        "Encourage creative risk-taking."
    ),
    "hacker": (
        "You are a pragmatic hacker focused on getting things done. "
        "Prefer working solutions over perfect architecture. "
        "Use duct tape and clever shortcuts when appropriate. "
        "Optimize for speed and results."
    ),
    "detective": (
        "You are a meticulous debugger and problem solver. "
        "Trace problems to their root cause systematically. "
        "Question assumptions, verify hypotheses with evidence. "
        "Document every step of the investigation."
    ),
    "architect": (
        "You think in systems and abstractions. "
        "Design for scalability, maintainability, and clarity. "
        "Consider trade-offs explicitly. "
        "Document architectural decisions and their rationale."
    ),
    "minimalist": (
        "You believe less is more. "
        "Remove unnecessary code, dependencies, and complexity. "
        "Prefer simple solutions that are easy to understand. "
        "Question whether something is needed at all."
    ),
    "turkce": (
        "Tamamen Turkce konusursun. "
        "Kisa, net ve dogrudan cevaplar verirsin. "
        "Gereksiz detaydan kacinir, ozu soylersin. "
        "Turkce teknoloji terimlerini tercih edersin."
    ),
    "socratic": (
        "You answer questions with questions. "
        "Guide the user to discover answers themselves. "
        "Challenge assumptions and probe deeper. "
        "Never give direct answers — lead with inquiry."
    ),
    "mentor": (
        "You are a senior developer mentoring a junior. "
        "Explain the reasoning behind decisions. "
        "Point out potential pitfalls the user might miss. "
        "Suggest best practices and coding standards. "
        "Be supportive but honest about quality."
    ),
    "sysadmin": (
        "You are a seasoned systems administrator. "
        "Focus on reliability, security, and observability. "
        "Check logs first. Automate everything. "
        "Document procedures for the next on-call. "
        "Always have a rollback plan."
    ),
    "default": "",  # Bos = SOUL.md kimligini kullan
}


class PersonalityManager:
    """Kisilik yoneticisi — gecerli kisiligi tutar ve uygular."""

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        self._aktif: str = "default"
        self._ozel_kisilikler: dict[str, str] = {}

        # Config'den ozel kisilikleri yukle
        self._ozel_kisilikler = (self._config.get("agent") or {}).get(
            "personalities", {}
        )

    @property
    def aktif(self) -> str:
        return self._aktif

    def kisilik_sec(self, ad: str) -> tuple[bool, str]:
        """Kisilik sec, aciklamasini don.

        Args:
            ad: Kisilik adi (builtin, ozel veya "default")

        Returns:
            (basarili_mi, mesaj_veya_aciklama)
        """
        ad = ad.lower().strip()

        if ad == "default":
            self._aktif = "default"
            return True, "Varsayilan kisilik (SOUL.md)"

        if ad in self._ozel_kisilikler:
            self._aktif = ad
            return True, self._ozel_kisilikler[ad]

        if ad in BUILTIN_PERSONALITIES:
            self._aktif = ad
            return True, BUILTIN_PERSONALITIES[ad]

        mevcut = self.kisilik_listele()
        return False, (
            f"Kisilik bulunamadi: '{ad}'. "
            f"Mevcut: {', '.join(mevcut)}"
        )

    def kisilik_listele(self) -> list[str]:
        """Tum kullanilabilir kisilik adlarini listele."""
        adlar = list(BUILTIN_PERSONALITIES.keys())
        adlar.extend(self._ozel_kisilikler.keys())
        return sorted(set(adlar))

    def aktif_aciklama(self) -> str:
        """Gecerli kisiligin aciklamasini don."""
        if self._aktif == "default":
            return "Varsayilan (SOUL.md)"
        if self._aktif in self._ozel_kisilikler:
            return self._ozel_kisilikler[self._aktif]
        return BUILTIN_PERSONALITIES.get(self._aktif, "")

    def sistem_prompt_eki(self) -> str:
        """Sistem prompt'una eklenecek kisilik yonergesini don.

        Sadece "default" degilse eklenir.
        """
        if self._aktif == "default":
            return ""
        aciklama = self.aktif_aciklama()
        if not aciklama:
            return ""
        return (
            f"\n## Aktif Kisilik: {self._aktif}\n"
            f"{aciklama}\n"
        )

    def komut_islem(self, args: str = "") -> str:
        """/personality komutunu isle.

        Args:
            args: Komut parametresi (kisilik adi, "list" veya bos)

        Returns:
            Kullaniciya gosterilecek mesaj
        """
        if args.lower() in ("list", "liste", ""):
            adlar = self.kisilik_listele()
            aktif = self._aktif
            satirlar = [
                "Mevcut kisilikler:",
                f"  * default (SOUL.md)" +
                (" [AKTIF]" if aktif == "default" else ""),
            ]
            for ad in adlar:
                if ad == "default":
                    continue
                isaret = " [AKTIF]" if ad == aktif else ""
                satirlar.append(f"  * {ad}{isaret}")
            satirlar.append("")
            satirlar.append(
                "Kullanım: /personality <ad>  (ornek: /personality concise)"
            )
            return "\n".join(satirlar)

        basarili, mesaj = self.kisilik_sec(args)
        if basarili:
            return (
                f"Kisilik degistirildi: {self._aktif}\n"
                f"---\n{mesaj}"
            )
        return mesaj


def motor_kaydet(motor) -> None:
    """Personality tool'larını Motor'a kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        logger.warning("Motor'da _plugin_arac_kaydet metodu yok")
        return

    # Config'i motordan al
    cfg = getattr(motor, "config", None)
    mgr = personality_manager(cfg)

    motor._plugin_arac_kaydet(
        "PERSONALITY_LISTELE",
        lambda: mgr.komut_islem("list"),
        "Kullanilabilir kisilikleri listeler",
    )
    motor._plugin_arac_kaydet(
        "PERSONALITY_SEC",
        lambda ad="": mgr.komut_islem(ad),
        "Kisilik secer (PERSONALITY_SEC ad) veya listeler (PERSONALITY_SEC list)",
    )
    logger.info(f"Personality: {len(mgr.kisilik_listele())} kisilik kaydedildi")


# ── Conversation Loop entegrasyonu ────────────────────────────────

def sistem_prompt_ekle(mevcut_prompt: str, config: Optional[dict] = None) -> str:
    """Sistem prompt'una aktif kisilik yonergesini ekler.

    Kullanim (conversation_loop.py icinde):
        from agent.personalities import sistem_prompt_ekle
        prompt = sistem_prompt_ekle(prompt, motor.config)
    """
    mgr = personality_manager(config)
    ek = mgr.sistem_prompt_eki()
    if ek:
        return mevcut_prompt + ek
    return mevcut_prompt


# ── Tekil ornek (singleton) ───────────────────────────────────────
_mgr: Optional[PersonalityManager] = None


def personality_manager(config: Optional[dict] = None) -> PersonalityManager:
    """Singleton PersonalityManager doner."""
    global _mgr
    if _mgr is None:
        _mgr = PersonalityManager(config)
    return _mgr
