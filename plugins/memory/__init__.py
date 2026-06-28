# -*- coding: utf-8 -*-
"""plugins/memory/__init__.py — Bellek Plugin Yoneticisi.

Birden cok memory backend'ini yonetir (chroma, json dosya).
motor_kaydet(motor) fonksiyonu ile memory_tool'u kaydeder.
"""


__all__ = ['ChromaBackend', 'DosyaBackend', 'ara', 'ekle', 'motor_kaydet', 'sil']
import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "memory"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Coklu backend bellek sistemi (ChromaDB / JSON dosya)"

# Aktif backend
_backend = None
_backend_turu = None


def _backend_sec(backend_turu: str = "dosya"):
    """Kullanilacak backend'i secer ve baslatir.

    Args:
        backend_turu: "chroma" veya "dosya" (varsayilan: dosya)

    Returns:
        Backend ornegi veya None
    """
    global _backend, _backend_turu

    if backend_turu == "chroma":
        try:
            from plugins.memory.chroma_backend import ChromaBackend
            _backend = ChromaBackend()
            _backend_turu = "chroma"
            logger.info("Memory backend: ChromaDB")
            return _backend
        except Exception as e:
            logger.warning("ChromaDB backend yuklenemedi: %s", e)
            return None

    # Varsayilan: dosya backend
    try:
        from plugins.memory.dosya_backend import DosyaBackend
        _backend = DosyaBackend()
        _backend_turu = "dosya"
        logger.info("Memory backend: JSON Dosya")
        return _backend
    except Exception as e:
        logger.error("Dosya backend yuklenemedi: %s", e)
        return None


def ekle(metin: str, metadata: dict = None) -> str:
    """Hafizaya yeni bir ogre ekler.

    Args:
        metin: Eklenecek metin
        metadata: Ek bilgiler (sozluk)

    Returns:
        str: Islem sonucu
    """
    global _backend, _backend_turu
    if _backend is None:
        _backend_sec()

    if _backend is None:
        return "[Memory]: Backend yuklu degil."

    try:
        if _backend_turu == "chroma":
            return _backend.ekle(metin, metadata or {})
        else:
            # Dosya backend'inde anahtar otomatik uretilir
            import time
            anahtar = f"not_{int(time.time())}"
            return _backend.kaydet(anahtar, metin)
    except Exception as e:
        return f"[Memory]: Ekleme hatasi - {e}"


def ara(sorgu: str, limit: int = 5) -> str:
    """Hafizada arama yapar.

    Args:
        sorgu: Aranacak metin
        limit: Maksimum sonuc sayisi

    Returns:
        str: Arama sonuclari
    """
    global _backend, _backend_turu
    if _backend is None:
        _backend_sec()

    if _backend is None:
        return "[Memory]: Backend yuklu degil."

    try:
        if _backend_turu == "chroma":
            return _backend.ara(sorgu, limit=limit)
        else:
            # Dosya backend'inde basit metin arama
            sonuc = []
            for anahtar, deger in (_backend._veri or {}).items():
                if sorgu.lower() in str(deger).lower():
                    sonuc.append(f"{anahtar}: {deger}")
                    if len(sonuc) >= limit:
                        break
            if sonuc:
                return "\n".join(sonuc)
            return "[Memory]: Sonuc bulunamadi."
    except Exception as e:
        return f"[Memory]: Arama hatasi - {e}"


def sil(anahtar: str) -> str:
    """Hafizadan bir ogre siler.

    Args:
        anahtar: Silinecek anahtar veya ID

    Returns:
        str: Islem sonucu
    """
    global _backend, _backend_turu
    if _backend is None:
        _backend_sec()

    if _backend is None:
        return "[Memory]: Backend yuklu degil."

    try:
        if _backend_turu == "chroma":
            return _backend.sil(anahtar)
        else:
            return _backend.sil(anahtar)
    except Exception as e:
        return f"[Memory]: Silme hatasi - {e}"


def motor_kaydet(motor):
    """Plugin araclarini motor'a kaydeder.

    NOT: HAFIZA_EKLE/ARA/SIL kaldirildi — yeni FTS5 sistemi
    (hafiza_genislet.py) kullaniliyor. HAFIZA_KAYDET/ARA/SIL/DURUM
    vb. araclarla ayni isi FTS5 ile yapar.
    """
    # Backend'i baslat (chroma/json dosya — eski plugin kullananlar icin)
    _backend_sec()
    logger.info("[Plugin:memory] eski HAFIZA_* araclari devre disi (yerini hafiza_genislet aldi).")
