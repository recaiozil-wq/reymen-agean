# -*- coding: utf-8 -*-
"""plugins/model_providers/mistral.py — Mistral AI Model Saglayici.

Mistral AI API uzerinden modellere erisim saglar.
Opsiyonel bagimlilik: mistralai
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "mistral"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Mistral AI API model saglayici"

try:
    from mistralai import Mistral
    MISTRAL_MEVCUT = True
except ImportError:
    MISTRAL_MEVCUT = False
    logger.debug("mistralai kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Mistral pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not MISTRAL_MEVCUT:
        logger.warning("[Plugin:mistral] mistralai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def mistral_sorgula(args):
        """Mistral modeline sorgu gonder."""
        try:
            client = Mistral(api_key=args.get("api_key"))
            response = client.chat.complete(
                model=args.get("model", "mistral-large-latest"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Mistral] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("MISTRAL_SORGULA", mistral_sorgula, "Mistral AI modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("MISTRAL_SORGULA", mistral_sorgula)

    logger.info("[Plugin:mistral] Mistral provider kayit edildi.")
