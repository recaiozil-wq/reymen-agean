# -*- coding: utf-8 -*-
"""plugins/model_providers/groq.py — Groq Model Saglayici.

Groq API uzerinden hizli inferans modellerine erisim saglar.
Opsiyonel bagimlilik: groq
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "groq"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Groq API model saglayici (hizli inferans)"

try:
    from groq import Groq
    GROQ_MEVCUT = True
except ImportError:
    GROQ_MEVCUT = False
    logger.debug("groq kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Groq pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not GROQ_MEVCUT:
        logger.warning("[Plugin:groq] groq kutuphanesi bulunamadi, plugin atlandi.")
        return

    def groq_sorgula(args):
        """Groq modeline sorgu gonder."""
        try:
            client = Groq(api_key=args.get("api_key"))
            response = client.chat.completions.create(
                model=args.get("model", "llama-3.3-70b-versatile"),
                messages=args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                temperature=args.get("temperature", 0.7),
                max_tokens=args.get("max_tokens", 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Groq] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("GROQ_SORGULA", groq_sorgula, "Groq modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("GROQ_SORGULA", groq_sorgula)

    logger.info("[Plugin:groq] Groq provider kayit edildi.")
