"""
cron/cleanup_job.py — Disk temizleme cron job'u.

Eskimiş logları, geçici dosyaları, önbelleği temizler.
ReYMeN bakım altyapısı için periyodik temizlik görevi.
"""

import logging
import os
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Varsayılan temizlik yolları ve gün eşikleri
TEMIZLIK_YOLLARI = {
    "temp": {"yol": os.environ.get("TEMP", "/tmp"), "gun": 7},
    "log": {"yol": None, "gun": 30},  # proje log/ klasörü
    "cache": {"yol": None, "gun": 14},  # proje .cache/ klasörü
}


def _boyut_oku(path):
    """Bir dosyanın veya klasörün toplam boyutunu döndürür."""
    try:
        path = Path(path)
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            toplam = 0
            for f in path.rglob("*"):
                if f.is_file():
                    try:
                        toplam += f.stat().st_size
                    except OSError:
                        logger.warning("[fix_01_sessiz_except] OSError")
            return toplam
    except OSError:
        return 0
    return 0


def _yasli_dosyalari_sil(klasor, gun):
    """Belirtilen günden eski dosyaları siler. Silinen sayısını döndürür."""
    silinen = 0
    kesilen = 0
    sinir_zamani = time.time() - (gun * 86400)
    try:
        for entry in Path(klasor).iterdir():
            try:
                mtime = entry.stat().st_mtime
                if mtime < sinir_zamani:
                    if entry.is_file():
                        entry.unlink()
                        silinen += 1
                    elif entry.is_dir():
                        shutil.rmtree(entry, ignore_errors=True)
                        silinen += 1
                    kesilen += _boyut_oku(entry)
            except (OSError, PermissionError) as e:
                logger.warning("Silinemedi: %s — %s", entry, e)
    except FileNotFoundError:
        logger.debug("Klasör bulunamadı: %s", klasor)
    except PermissionError as e:
        logger.warning("Erişim reddedildi: %s — %s", klasor, e)
    return silinen, kesilen


def calistir():
    """Disk temizleme job'unun ana çalıştırma fonksiyonu."""
    sonuclar = {}
    toplam_silinen = 0
    toplam_boyut = 0

    try:
        # 1. Geçici dosyalar
        temp_yol = TEMIZLIK_YOLLARI["temp"]["yol"]
        if temp_yol and os.path.exists(temp_yol):
            sil, boy = _yasli_dosyalari_sil(temp_yol, TEMIZLIK_YOLLARI["temp"]["gun"])
            toplam_silinen += sil
            toplam_boyut += boy
            sonuclar["temp"] = {"silinen": sil, "boyut": boy}
            logger.info("🧹 Temp temizliği: %d dosya, %.2f MB", sil, boy / 1048576)

        # 2. Proje log klasörü
        for prefix in [".", ".."]:
            log_yol = os.path.join(os.path.dirname(__file__), "..", "log")
            log_yol = os.path.abspath(log_yol)
            if os.path.exists(log_yol):
                sil, boy = _yasli_dosyalari_sil(log_yol, TEMIZLIK_YOLLARI["log"]["gun"])
                toplam_silinen += sil
                toplam_boyut += boy
                sonuclar["log"] = {"silinen": sil, "boyut": boy}
                logger.info("🧹 Log temizliği: %d dosya, %.2f MB", sil, boy / 1048576)
                break

        # 3. Önbellek klasörü
        for prefix in [".", ".."]:
            cache_yol = os.path.join(os.path.dirname(__file__), "..", ".cache")
            cache_yol = os.path.abspath(cache_yol)
            if os.path.exists(cache_yol):
                sil, boy = _yasli_dosyalari_sil(cache_yol, TEMIZLIK_YOLLARI["cache"]["gun"])
                toplam_silinen += sil
                toplam_boyut += boy
                sonuclar["cache"] = {"silinen": sil, "boyut": boy}
                logger.info("🧹 Cache temizliği: %d dosya, %.2f MB", sil, boy / 1048576)
                break

        logger.info("🧹 Temizlik tamamlandı: %d dosya, %.2f MB silindi", toplam_silinen, toplam_boyut / 1048576)
        return sonuclar

    except Exception as e:
        logger.error("❌ Temizlik job'ı başarısız: %s", e)
        return {"hata": str(e)}


def bilgi():
    """Job metadata döndürür."""
    return {
        "isim": "disk_temizleme",
        "interval": "günde 1 kez",
        "aciklama": "Eskimiş logları, geçici dosyaları ve önbelleği temizler",
        "versiyon": "1.0.0",
    }
