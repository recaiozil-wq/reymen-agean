# -*- coding: utf-8 -*-
"""
image_gen.py â€” ReYMeN tool arayÃ¼zÃ¼: GÃ¶rsel Ã¼retim araÃ§larÄ±.

Bu modÃ¼l, reymen.arac.image_gen_engine motorunu ReYMeN'in tool
sistemine baÄŸlar. Motor tarafÄ±ndan otomatik kaydedilir.

KullanÄ±m:
  RESIM_OLUSTUR(prompt="bir kedi", en="1024", boy="1024", backend="fal")
  RESIM_OLUSTUR_BACKEND_LISTELE()
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

try:
    from reymen.arac.image_gen_engine import (
        motor_kaydet,
        resim_olustur,
        image_gen_engine_listele,
    )
except ImportError as e:
    log.warning("[arac/image_gen] image_gen_engine yuklenemedi: %s", e)
    motor_kaydet = lambda motor: None
    resim_olustur = lambda prompt, en="1024", boy="1024", backend="": (
        f"[RESIM_OLUSTUR] Motor yuklenemedi: {prompt}"
    )
    image_gen_engine_listele = lambda: "[RESIM_OLUSTUR] Motor yuklenemedi."


__all__ = [
    "motor_kaydet",
    "resim_olustur",
    "image_gen_engine_listele",
]
