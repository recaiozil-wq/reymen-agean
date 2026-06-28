# -*- coding: utf-8 -*-
"""plugins/model_providers/deepseek.py — DeepSeek Model Saglayici.

DeepSeek API uzerinden modellere erisim saglar.
Opsiyonel bagimlilik: openai (DeepSeek OpenAI-uyumlu API kullanir)
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "deepseek"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "DeepSeek API model saglayici"

try:
    from openai import OpenAI
    DEEPSEEK_MEVCUT = True
except ImportError:
    DEEPSEEK_MEVCUT = False
    logger.debug("openai kutuphanesi yuklu degil (DeepSeek icin gerekli)")


def motor_kaydet(motor):
    """DeepSeek pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not DEEPSEEK_MEVCUT:
        logger.warning("[Plugin:deepseek] openai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def deepseek_sorgula(args):
        """DeepSeek modeline sorgu gonder."""
        try:
            client = OpenAI(
                api_key=args.get("api_key"),
                base_url="https://api.deepseek.com"
            )
            response = client.chat.completions.create(
                model=args.get("model", "deepseek-chat"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[DeepSeek] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("DEEPSEEK_SORGULA", deepseek_sorgula, "DeepSeek modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("DEEPSEEK_SORGULA", deepseek_sorgula)

    logger.info("[Plugin:deepseek] DeepSeek provider kayit edildi.")
