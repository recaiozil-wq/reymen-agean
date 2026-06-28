# -*- coding: utf-8 -*-
"""plugins/model_providers/openai.py — OpenAI Model Saglayici.

OpenAI API uzerinden modellere erisim saglar (GPT-4, GPT-3.5, vb.).
Opsiyonel bagimlilik: openai
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "openai"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "OpenAI API model saglayici (GPT-4, GPT-3.5)"

# OpenAI kutuphanesini dene
try:
    import openai
    OPENAI_MEVCUT = True
except ImportError:
    OPENAI_MEVCUT = False
    logger.debug("openai kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """OpenAI pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not OPENAI_MEVCUT:
        logger.warning("[Plugin:openai] openai kutuphanesi bulunamadi, plugin atlandi.")
        return

    # OpenAI aracini kaydet
    def openai_sorgula(args):
        """OpenAI modeline sorgu gonder."""
        try:
            response = openai.chat.completions.create(
                model=args.get("model", "gpt-4"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("OPENAI_SORGULA", openai_sorgula, "OpenAI modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("OPENAI_SORGULA", openai_sorgula)

    logger.info("[Plugin:openai] OpenAI provider kayit edildi.")
