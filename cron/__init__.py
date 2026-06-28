"""
cron/__init__.py — Cron job kayıt ve zamanlayıcı modülü.

Tüm cron job'larını kaydeder, zamanlayıcıyı başlatır.
ReYMeN altyapısı için görev zamanlama motoru.
"""


__all__ = ['datetime', 'job_kaydet', 'kayitli_joblar', 'timedelta', 'tum_joblari_calistir', 'zamanlayici_baslat']
import logging
import time
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Job kayıt defteri: {isim: {"calistir": func, "bilgi": func, "son_calisma": None}}
_JOB_REGISTRY = {}

def job_kaydet(calistir_func, bilgi_func):
    """
    Bir cron job'unu kayıt defterine ekler.

    Args:
        calistir_func: Job'un ana çalıştırma fonksiyonu.
        bilgi_func: Job metadata döndüren fonksiyon.
    """
    try:
        metadata = bilgi_func()
        isim = metadata.get("isim", calistir_func.__name__)
        _JOB_REGISTRY[isim] = {
            "calistir": calistir_func,
            "bilgi": bilgi_func,
            "metadata": metadata,
            "son_calisma": None,
            "son_durum": None,
        }
        logger.info("✅ Job kaydedildi: %s (interval: %s)", isim, metadata.get("interval", "?"))
    except Exception as e:
        logger.error("❌ Job kaydedilemedi: %s — %s", calistir_func.__name__, e)


def kayitli_joblar():
    """Kayıtlı tüm job'ların listesini döndürür."""
    return dict(_JOB_REGISTRY)


def tum_joblari_calistir():
    """Tüm kayıtlı job'ları sırayla çalıştırır."""
    sonuclar = {}
    for isim, kayit in _JOB_REGISTRY.items():
        try:
            logger.info("🚀 Job başlatılıyor: %s", isim)
            basla = time.time()
            kayit["calistir"]()
            gecen = time.time() - basla
            kayit["son_calisma"] = datetime.now()
            kayit["son_durum"] = "basarili"
            sonuclar[isim] = {"durum": "basarili", "sure": round(gecen, 2)}
            logger.info("✅ Job tamamlandı: %s (%.2fs)", isim, gecen)
        except Exception as e:
            kayit["son_durum"] = "hata"
            sonuclar[isim] = {"durum": "hata", "hata": str(e)}
            logger.error("❌ Job başarısız: %s — %s", isim, e)
    return sonuclar


def _zamanlayici_dongusu(interval_dk=30):
    """Arka planda belirli aralıklarla tüm job'ları çalıştırır."""
    while True:
        try:
            tum_joblari_calistir()
        except Exception as e:
            logger.error("Zamanlayıcı döngü hatası: %s", e)
        time.sleep(interval_dk * 60)


def zamanlayici_baslat(interval_dk=30, arka_plan=True):
    """
    Zamanlayıcıyı başlatır.

    Args:
        interval_dk: Çalıştırma aralığı (dakika).
        arka_plan: Arka plan thread'i olarak çalıştır.
    """
    if arka_plan:
        thread = threading.Thread(
            target=_zamanlayici_dongusu,
            args=(interval_dk,),
            daemon=True,
            name="CronZamanlayici",
        )
        thread.start()
        logger.info("⏰ Zamanlayıcı başlatıldı (interval: %d dk, arka plan)", interval_dk)
        return thread
    else:
        logger.info("⏰ Zamanlayıcı başlatıldı (interval: %d dk, ön plan)", interval_dk)
        _zamanlayici_dongusu(interval_dk)
        return None
