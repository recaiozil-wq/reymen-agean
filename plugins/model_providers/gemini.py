# -*- coding: utf-8 -*-
"""plugins/model_providers/gemini.py — Google Gemini Model Saglayici.

Google Gemini API uzerinden modellere erisim saglar.
Opsiyonel bagimlilik: google-generativeai
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "gemini"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Google Gemini API model saglayici"

try:
    import google.generativeai as genai
    GEMINI_MEVCUT = True
except ImportError:
    GEMINI_MEVCUT = False
    logger.debug("google-generativeai kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Gemini pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not GEMINI_MEVCUT:
        logger.warning("[Plugin:gemini] google-generativeai kutuphanesi bulunamadi, plugin atlandi.")
        return

    def gemini_sorgula(args):
        """Gemini modeline sorgu gonder."""
        try:
            genai.configure(api_key=args.get("api_key"))
            model = genai.GenerativeModel(args.get("model", "gemini-2.0-flash"))
            response = model.generate_content(args.get("prompt", ""))
            return response.text
        except Exception as e:
            return f"[Gemini] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("GEMINI_SORGULA", gemini_sorgula, "Google Gemini modeline sorgu gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("GEMINI_SORGULA", gemini_sorgula)

    logger.info("[Plugin:gemini] Gemini provider kayit edildi.")
