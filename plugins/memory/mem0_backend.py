# -*- coding: utf-8 -*-
"""plugins/memory/mem0_backend.py — Mem0.ai Bellek Backend.

Mem0.ai platformunu kullanarak hafiza yonetimi saglar.
Opsiyonel bagimlilik: mem0
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "mem0_backend"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Mem0.ai bellek backend entegrasyonu"

try:
    from mem0 import Memory
    MEM0_MEVCUT = True
except ImportError:
    MEM0_MEVCUT = False
    logger.debug("mem0 kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Mem0.ai backend'ini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not MEM0_MEVCUT:
        logger.warning("[Plugin:mem0_backend] mem0 kutuphanesi bulunamadi, plugin atlandi.")
        return

    _memory_client = None

    def _get_client(config=None):
        nonlocal _memory_client
        if _memory_client is None:
            _memory_client = Memory.from_config(config or {})
        return _memory_client

    def mem0_ekle(args):
        """Mem0.ai hafizasina bilgi ekle."""
        try:
            client = _get_client(args.get("config"))
            metin = args.get("metin", "")
            kullanici = args.get("kullanici", "default")
            if not metin:
                return "[Mem0] metin gerekli."
            sonuc = client.add(metin, user_id=kullanici)
            return f"[Mem0] Bilgi eklendi: {sonuc}"
        except Exception as e:
            return f"[Mem0] Ekleme hatasi: {e}"

    def mem0_ara(args):
        """Mem0.ai hafizasinda ara."""
        try:
            client = _get_client(args.get("config"))
            sorgu = args.get("sorgu", "")
            kullanici = args.get("kullanici", "default")
            if not sorgu:
                return "[Mem0] sorgu gerekli."
            sonuc = client.search(sorgu, user_id=kullanici)
            return str(sonuc)
        except Exception as e:
            return f"[Mem0] Arama hatasi: {e}"

    def mem0_sil(args):
        """Mem0.ai hafizasindan bilgi sil."""
        try:
            client = _get_client(args.get("config"))
            memory_id = args.get("memory_id", "")
            if not memory_id:
                return "[Mem0] memory_id gerekli."
            client.delete(memory_id)
            return f"[Mem0] Bilgi silindi: {memory_id}"
        except Exception as e:
            return f"[Mem0] Silme hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("MEM0_EKLE", mem0_ekle, "Mem0.ai hafizasina bilgi ekler")
        motor._plugin_arac_kaydet("MEM0_ARA", mem0_ara, "Mem0.ai hafizasinda arama yapar")
        motor._plugin_arac_kaydet("MEM0_SIL", mem0_sil, "Mem0.ai hafizasindan bilgi siler")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("MEM0_EKLE", mem0_ekle)
        motor._registry.kaydet("MEM0_ARA", mem0_ara)
        motor._registry.kaydet("MEM0_SIL", mem0_sil)

    logger.info("[Plugin:mem0_backend] Mem0.ai backend kayit edildi.")
