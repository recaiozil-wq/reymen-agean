# -*- coding: utf-8 -*-
"""Background review — konusma sonrasi memory + skill otomatik guncelleme.

Hermes agent/background_review.py'den adapte edilmistir.
ReYMeN'e ozgu: ConversationLoop fork ile konusma analizi.
"""
from __future__ import annotations

import json
import logging
import threading
import os as _os
from typing import Any, List, Optional

logger = logging.getLogger("conversation_loop")

_REVIEW_SYSTEM_PROMPT = (
    "Sen ReYMeN, otonom bir yazilim ajanisin. "
    "Gorevin: sana verilen konusmayi analiz et ve ogrendiklerini kaydet.\n\n"
    "[ZORUNLU KURALLAR]\n"
    "1. Kullanici hakkinda yeni bilgi (isim, tercih, proje) kesfettiysen -> once_hafiza_ara/once_hafiza_kaydet tool'unu kullan\n"
    "2. Yeni bir cozum patterni kesfettiysen -> skill_ekle tool'unu kullan\n"
    "3. Yeni bisey yoksa bos cevap ver, islem yapma\n"
    "4. Sadece OnceHafiza ve skill araclarini kullan, baska arac kullanma\n"
    "5. Kisa ve oz ol, islem raporu ver"
)


def _fork_review_agent(messages: list, provider: str = "deepseek-v4-flash") -> List[str]:
    """ConversationLoop fork'u olustur, review yaptir, sonuclari topla.

    Hermes'teki fork AIAgent pattern'inin ReYMeN versiyonu.
    Yeni bir ConversationLoop instance'i olusturur, ayni provider ile
    konusmayi analiz ettirir. Fork:
    - Ayni provider/model/API key kullanir
    - Sadece OnceHafiza ve skill araclarina erisir
    - Konusma mesajlarini context olarak alir
    """
    try:
        from reymen.cereyan.conversation_loop import ConversationLoop

        # Fork agent: minimal ayarlarla yeni instance
        fork = ConversationLoop(max_tur=1)

        # Fork'un provider'ini parent ile ayni yap
        api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
        if fork.beyin and hasattr(fork.beyin, "api_key") and api_key:
            fork.beyin.api_key = api_key
        if fork.beyin and hasattr(fork.beyin, "model"):
            fork.beyin.model = provider

        # Parent mesajlarini fork'un gecmisine ekle
        if hasattr(fork, "_konusma_gecmisi"):
            fork._konusma_gecmisi = list(messages[-30:]) if len(messages) > 30 else list(messages)

        # Fork'a toolkit yukle (OnceHafiza + Skill)
        _fork_toolset_yukle(fork)

        # Review prompt'u calistir
        review_hedef = (
            "[BACKGROUND REVIEW] Asagidaki konusmayi analiz et.\n"
            "Kullanici hakkinda yeni bilgiler (isim, tercih, proje) "
            "veya yeni cozum patternleri var mi?\n\n"
            "VARSA:\n"
            "- once_hafiza_kaydet tool'unu kullanarak kaydet\n"
            "- skill_ekle tool'unu kullanarak yeni skill olustur\n\n"
            "YOKSA:\n"
            "- Sadece 'Nothing to update.' de\n"
        )

        sonuc = fork.run_conversation(review_hedef)
        yanit = sonuc.get("yanit", "")
        if yanit and "Nothing to update" not in yanit:
            return [yanit.strip()[:300]]
        return []

    except Exception as e:
        logger.debug("[BackgroundReview] Fork hatasi: %s", e)
        return []
    finally:
        pass


def _fork_toolset_yukle(fork) -> None:
    """Fork agent'a OnceHafiza ve skill araclarini yukle."""
    try:
        if not hasattr(fork, "motor") or fork.motor is None:
            return

        motor = fork.motor

        # once_hafiza_kaydet tool
        if not hasattr(motor, "_plugin_arac_kaydet"):
            return

        def _oh_kaydet(hedef: str = "", cozum: str = "", kategori: str = "genel") -> str:
            """Yeni bilgiyi OnceHafiza'ya kaydet."""
            try:
                from reymen.sistem.once_hafiza import kaydet as _k
                _k(hedef=hedef, cozum=cozum, kategori=kategori, kaynak="background_review_fork")
                return f"Kaydedildi: {hedef}"
            except Exception as e:
                return f"Hata: {e}"

        def _oh_ara(sorgu: str = "") -> str:
            """OnceHafiza'da ara."""
            try:
                from reymen.sistem.once_hafiza import hafizada_ara as _ha
                s = _ha(sorgu)
                return str(s or "Bulunamadi")
            except Exception as e:
                return f"Hata: {e}"

        motor._plugin_arac_kaydet("once_hafiza_kaydet", _oh_kaydet, "Bilgiyi OnceHafiza'ya kaydet")
        motor._plugin_arac_kaydet("once_hafiza_ara", _oh_ara, "OnceHafiza'da ara")
        logger.debug("[BackgroundReview] Fork toolset yuklendi")
    except Exception as e:
        logger.debug("[BackgroundReview] Toolset yukleme hatasi: %s", e)


def spawn_background_review(
    messages: list,
    *,
    notification_mode: str = "on",
    provider: str = "deepseek-v4-flash",
) -> List[str]:
    """Konusma sonrasi background review baslat.

    Fork AIAgent pattern: ConversationLoop fork'u olustur,
    konusmayi analiz ettir, memory/skill guncellemelerini yap.

    Args:
        messages: Konusma mesajlari
        notification_mode: "off" | "on" | "verbose"
        provider: Kullanilacak model/provider

    Returns:
        Yapilan islemlerin listesi
    """
    if notification_mode == "off" or len(messages) < 3:
        return []

    # Fork review (Hermes pattern)
    actions = _fork_review_agent(messages, provider=provider)

    # Log
    for a in actions:
        logger.info("[BackgroundReview] %s", a)

    return actions


def background_review_sonucu_formatla(actions: List[str]) -> str:
    """Background review sonuclarini kullaniciya gostermek icin formatla."""
    if not actions:
        return ""
    satirlar = ["[Arka Plan Review]", "-" * 30]
    for a in actions:
        satirlar.append(f"  {a}")
    satirlar.append("-" * 30)
    return "\n".join(satirlar)
