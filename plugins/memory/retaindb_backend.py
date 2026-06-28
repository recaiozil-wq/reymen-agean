# -*- coding: utf-8 -*-
"""plugins/memory/retaindb_backend.py — RetainDB Bellek Backend.

RetainDB veritabanini kullanarak hafiza yonetimi saglar.
Opsiyonel bagimlilik: retaindb
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "retaindb_backend"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "RetainDB bellek backend entegrasyonu"

try:
    from retaindb import RetainDB
    RETAINDB_MEVCUT = True
except ImportError:
    RETAINDB_MEVCUT = False
    logger.debug("retaindb kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """RetainDB backend'ini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not RETAINDB_MEVCUT:
        logger.warning("[Plugin:retaindb_backend] retaindb kutuphanesi bulunamadi, plugin atlandi.")
        return

    _db = None

    def _get_db(config=None):
        nonlocal _db
        if _db is None:
            _db = RetainDB(config or {})
        return _db

    def retaindb_kaydet(args):
        """RetainDB'ye bilgi kaydet."""
        try:
            db = _get_db(args.get("config"))
            anahtar = args.get("anahtar", "")
            deger = args.get("deger", "")
            if not anahtar:
                return "[RetainDB] anahtar gerekli."
            db.set(anahtar, deger)
            return f"[RetainDB] Kaydedildi: {anahtar}"
        except Exception as e:
            return f"[RetainDB] Kaydetme hatasi: {e}"

    def retaindb_getir(args):
        """RetainDB'den bilgi getir."""
        try:
            db = _get_db(args.get("config"))
            anahtar = args.get("anahtar", "")
            if not anahtar:
                return "[RetainDB] anahtar gerekli."
            deger = db.get(anahtar)
            return f"[RetainDB] {anahtar}: {deger}"
        except Exception as e:
            return f"[RetainDB] Getirme hatasi: {e}"

    def retaindb_sil(args):
        """RetainDB'den bilgi sil."""
        try:
            db = _get_db(args.get("config"))
            anahtar = args.get("anahtar", "")
            if not anahtar:
                return "[RetainDB] anahtar gerekli."
            db.delete(anahtar)
            return f"[RetainDB] Silindi: {anahtar}"
        except Exception as e:
            return f"[RetainDB] Silme hatasi: {e}"

    def retaindb_listele(args):
        """RetainDB'deki anahtarlari listele."""
        try:
            db = _get_db(args.get("config"))
            desen = args.get("desen", "*")
            anahtarlar = db.keys(desen)
            return f"[RetainDB] Anahtarlar: {anahtarlar}"
        except Exception as e:
            return f"[RetainDB] Listeleme hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("RETAINDB_KAYDET", retaindb_kaydet, "RetainDB'ye bilgi kaydeder")
        motor._plugin_arac_kaydet("RETAINDB_GETIR", retaindb_getir, "RetainDB'den bilgi getirir")
        motor._plugin_arac_kaydet("RETAINDB_SIL", retaindb_sil, "RetainDB'den bilgi siler")
        motor._plugin_arac_kaydet("RETAINDB_LISTELE", retaindb_listele, "RetainDB anahtarlarini listeler")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("RETAINDB_KAYDET", retaindb_kaydet)
        motor._registry.kaydet("RETAINDB_GETIR", retaindb_getir)
        motor._registry.kaydet("RETAINDB_SIL", retaindb_sil)
        motor._registry.kaydet("RETAINDB_LISTELE", retaindb_listele)

    logger.info("[Plugin:retaindb_backend] RetainDB backend kayit edildi.")
