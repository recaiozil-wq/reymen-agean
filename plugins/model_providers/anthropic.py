# -*- coding: utf-8 -*-
"""plugins/model_providers/anthropic.py — Anthropic Model Saglayici.

Anthropic API uzerinden Claude modellerine erisim saglar.
Opsiyonel bagimlilik: anthropic
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "anthropic"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Anthropic API model saglayici (Claude)"

try:
    import anthropic
    ANTHROPIC_MEVCUT = True
except ImportError:
    ANTHROPIC_MEVCUT = False
    logger.debug("anthropic kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Anthropic pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not ANTHROPIC_MEVCUT:
        logger.warning("[Plugin:anthropic] anthropic kutuphanesi bulunamadi, plugin atlandi.")
        return

    def anthropic_sorgula(args):
        """Anthropic Claude modeline sorgu gonder."""
        try:
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=args.get("model", "claude-sonnet-4-20250514"),
                max_tokens=args.get("max_tokens", 1024),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}])
            )
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("ANTHROPIC_SORGULA", anthropic_sorgula, "Anthropic Claude modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("ANTHROPIC_SORGULA", anthropic_sorgula)

    logger.info("[Plugin:anthropic] Anthropic provider kayit edildi.")
