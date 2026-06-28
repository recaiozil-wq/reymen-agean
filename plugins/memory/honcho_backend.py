# -*- coding: utf-8 -*-
"""plugins/memory/honcho_backend.py — Honcho Bellek Backend.

Honcho (honcho.ai) platformunu kullanarak hafiza yonetimi saglar.
Opsiyonel bagimlilik: honcho
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "honcho_backend"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Honcho bellek backend entegrasyonu"

try:
    from honcho import Honcho
    HONCHO_MEVCUT = True
except ImportError:
    HONCHO_MEVCUT = False
    logger.debug("honcho kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Honcho backend'ini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not HONCHO_MEVCUT:
        logger.warning("[Plugin:honcho_backend] honcho kutuphanesi bulunamadi, plugin atlandi.")
        return

    _honcho_client = None

    def _get_client():
        nonlocal _honcho_client
        if _honcho_client is None:
            _honcho_client = Honcho()
        return _honcho_client

    def honcho_ekle(args):
        """Honcho hafizasina bilgi ekle."""
        try:
            client = _get_client()
            kullanici = args.get("kullanici", "default")
            metin = args.get("metin", "")
            oturum = args.get("oturum", "default")
            if not metin:
                return "[Honcho] metin gerekli."
            user = client.get_or_create_user(kullanici)
            session = user.get_or_create_session(oturum)
            session.add_message(metin)
            return f"[Honcho] Bilgi eklendi: {kullanici}/{oturum}"
        except Exception as e:
            return f"[Honcho] Ekleme hatasi: {e}"

    def honcho_getir(args):
        """Honcho hafizasindan bilgi getir."""
        try:
            client = _get_client()
            kullanici = args.get("kullanici", "default")
            oturum = args.get("oturum", "default")
            limit = args.get("limit", 10)
            user = client.get_or_create_user(kullanici)
            session = user.get_or_create_session(oturum)
            mesajlar = session.get_messages(limit=limit)
            return str(mesajlar)
        except Exception as e:
            return f"[Honcho] Getirme hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("HONCHO_EKLE", honcho_ekle, "Honcho hafizasina bilgi ekler")
        motor._plugin_arac_kaydet("HONCHO_GETIR", honcho_getir, "Honcho hafizasindan bilgi getirir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("HONCHO_EKLE", honcho_ekle)
        motor._registry.kaydet("HONCHO_GETIR", honcho_getir)

    logger.info("[Plugin:honcho_backend] Honcho backend kayit edildi.")
