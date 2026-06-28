# -*- coding: utf-8 -*-
"""plugins/model_providers/xai.py — xAI/Grok Model Saglayici.

xAI API uzerinden Grok modellerine erisim saglar.
Opsiyonel bagimlilik: openai (xAI OpenAI-uyumlu API kullanir)
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "xai"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "xAI Grok API model saglayici"

try:
    from openai import OpenAI
    XAI_MEVCUT = True
except ImportError:
    XAI_MEVCUT = False
    logger.debug("openai kutuphanesi yuklu degil (xAI icin gerekli)")


def motor_kaydet(motor):
    """xAI pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not XAI_MEVCUT:
        logger.warning("[Plugin:xai] openai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def xai_sorgula(args):
        """xAI Grok modeline sorgu gonder."""
        try:
            client = OpenAI(
                api_key=args.get("api_key"),
                base_url="https://api.x.ai/v1"
            )
            response = client.chat.completions.create(
                model=args.get("model", "grok-2-1212"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[xAI] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("XAI_SORGULA", xai_sorgula, "xAI Grok modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("XAI_SORGULA", xai_sorgula)

    logger.info("[Plugin:xai] xAI provider kayit edildi.")
