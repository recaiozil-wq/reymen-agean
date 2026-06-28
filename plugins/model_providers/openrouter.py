# -*- coding: utf-8 -*-
"""plugins/model_providers/openrouter.py — OpenRouter Model Saglayici.

OpenRouter API uzerinden bircok modele erisim saglar.
Opsiyonel bagimlilik: openai (OpenRouter OpenAI-uyumlu API kullanir)
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "openrouter"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "OpenRouter API model saglayici (coklu model)"

try:
    from openai import OpenAI
    OPENROUTER_MEVCUT = True
except ImportError:
    OPENROUTER_MEVCUT = False
    logger.debug("openai kutuphanesi yuklu degil (OpenRouter icin gerekli)")


def motor_kaydet(motor):
    """OpenRouter pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not OPENROUTER_MEVCUT:
        logger.warning("[Plugin:openrouter] openai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def openrouter_sorgula(args):
        """OpenRouter uzerinden modele sorgu gonder."""
        try:
            client = OpenAI(
                api_key=args.get("api_key"),
                base_url="https://openrouter.ai/api/v1"
            )
            response = client.chat.completions.create(
                model=args.get("model", "openai/gpt-4o"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenRouter] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("OPENROUTER_SORGULA", openrouter_sorgula, "OpenRouter uzerinden modele sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("OPENROUTER_SORGULA", openrouter_sorgula)

    logger.info("[Plugin:openrouter] OpenRouter provider kayit edildi.")
