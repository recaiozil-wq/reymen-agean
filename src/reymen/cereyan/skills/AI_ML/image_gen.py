# -*- coding: utf-8 -*-
"""
image_gen.py â€” AI_ML skill: GÃ¶rsel Ã¼retim (Image Generation) motoru.

BaÄŸÄ±mlÄ±lÄ±klar:
  - reymen.arac.image_gen_engine â€” FAL, OpenAI, xAI, Stub engine'leri

KullanÄ±m:
  from reymen.cereyan.skills.AI_ML.image_gen import image_olustur
  sonuc = image_olustur("bir kedi", en=1024, boy=1024, backend="fal")
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# Engine'i iÃ§e aktar
try:
    from reymen.arac.image_gen_engine import (
        FALEngine,
        ImageGenRegistry,
        OpenAIEngine,
        StubEngine,
        image_gen_engine_listele,
        resim_olustur,
        xAIEngine,
    )
except ImportError as e:
    log.warning("[AI_ML/image_gen] image_gen_engine yuklenemedi: %s", e)
    FALEngine = None  # type: ignore
    OpenAIEngine = None  # type: ignore
    StubEngine = None  # type: ignore
    xAIEngine = None  # type: ignore
    ImageGenRegistry = None  # type: ignore
    resim_olustur = (
        lambda prompt,
        en="1024",
        boy="1024",
        backend="": f"[ImageGen] Motor yuklenemedi: {prompt}"
    )
    image_gen_engine_listele = lambda: "[ImageGen] Motor yuklenemedi."


def image_olustur(
    prompt: str,
    en: int = 1024,
    boy: int = 1024,
    backend: str = "",
) -> str:
    """GÃ¶rsel Ã¼ret â€” skill arayÃ¼zÃ¼.

    Args:
        prompt: GÃ¶rsel tanÄ±mÄ±.
        en: GeniÅŸlik (piksel).
        boy: YÃ¼kseklik (piksel).
        backend: "fal", "openai", "xai", "stub" veya boÅŸ (varsayÄ±lan).

    Returns:
        [MEDIA] formatÄ±nda sonuÃ§ veya hata mesajÄ±.
    """
    return resim_olustur(prompt, str(en), str(boy), backend)


__all__ = [
    "FALEngine",
    "ImageGenRegistry",
    "OpenAIEngine",
    "StubEngine",
    "image_gen_engine_listele",
    "image_olustur",
    "resim_olustur",
    "xAIEngine",
]
