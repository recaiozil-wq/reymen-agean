# -*- coding: utf-8 -*-
"""Öncelik cache — basit selamlaşma/kısa yanıt patternleri için.

LLM çağrısı yapmadan direkt yanıt ver (0 maliyet).
"""

ONCELIK_CACHE: dict[str, str] = {
    "merhaba": "Merhaba! Nasil yardimci olabilirim?",
    "selam": "Selam! Ne yapabilirim?",
    "slm": "Selam! Ne yapabilirim?",
    "teşekkür": "Rica ederim, baska bir sey?",
    "tesekkur": "Rica ederim, baska bir sey?",
    "sagol": "Ne demek, her zaman!",
    "sağol": "Ne demek, her zaman!",
    "gorusuruz": "Gorusmek uzere!",
    "görüşürüz": "Görüşmek üzere!",
    "bye": "Gorusmek uzere!",
    "hadi": "Hadi bakalim, kolay gelsin!",
    "tamam": "Tamam, hemen yapiyorum.",
    "ok": "OK, hemen basliyorum.",
    "tmm": "Tamam, hemen yapiyorum.",
    "eyvallah": "Eyvallah, görüşürüz!",
}
