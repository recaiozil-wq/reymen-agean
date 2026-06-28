# -*- coding: utf-8 -*-
"""plugins/model_providers/together.py — Together AI Model Saglayici.

Together AI API uzerinden bircok acik kaynak modele erisim saglar.
Opsiyonel bagimlilik: openai (Together AI OpenAI-uyumlu API kullanir)
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "together"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Together AI API model saglayici (acik kaynak modeller)"

try:
    from openai import OpenAI
    TOGETHER_MEVCUT = True
except ImportError:
    TOGETHER_MEVCUT = False
    logger.debug("openai kutuphanesi yuklu degil (Together AI icin gerekli)")


def motor_kaydet(motor):
    """Together AI pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not TOGETHER_MEVCUT:
        logger.warning("[Plugin:together] openai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def together_sorgula(args):
        """Together AI modeline sorgu gonder."""
        try:
            client = OpenAI(
                api_key=args.get("api_key"),
                base_url="https://api.together.xyz/v1"
            )
            response = client.chat.completions.create(
                model=args.get("model", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Together] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("TOGETHER_SORGULA", together_sorgula, "Together AI modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("TOGETHER_SORGULA", together_sorgula)

    logger.info("[Plugin:together] Together AI provider kayit edildi.")
