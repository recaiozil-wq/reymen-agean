"""
cron/memory_job.py — Hafıza bakım cron job'u.

MEMORY limitlerine yaklaşan dosyaları sıkıştırır, eski session'ları temizler.
ReYMeN hafıza yönetimi altyapısı için bakım görevi.
"""

import logging
import os
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Varsayılan limitler
LİMİTLER = {
    "max_session_gun": 90,         # Eski session'lar kaç gün sonra silinsin
    "max_dosya_boyutu_mb": 5,      # Sıkıştırma eşiği (MB)
    "max_bellek_mb": 100,          # Toplam bellek limiti (MB)
}

# Sıkıştırma dışı bırakılacak uzantılar
SIKIŞTIRMA_DISI = {".gz", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", ".db", ".sqlite"}


def _klasör_boyutu(klasor_path):
    """Bir klasörün toplam boyutunu MB cinsinden döndürür."""
    toplam = 0
    try:
        for dosya in Path(klasor_path).rglob("*"):
            if dosya.is_file():
                try:
                    toplam += dosya.stat().st_size
                except OSError:
                    logger.warning("[fix_01_sessiz_except] OSError")
    except (FileNotFoundError, PermissionError):
        logger.warning("[fix_01_sessiz_except] Exception")
    return toplam / 1048576


def _eski_sessionlari_temizle(memory_path, gun):
    """Belirtilen günden eski session dosyalarını temizler."""
    silinen = 0
    kesilen_mb = 0
    sinir_tarih = datetime.now() - timedelta(days=gun)

    try:
        for dosya in Path(memory_path).rglob("*"):
            if dosya.is_file() and dosya.suffix in (".json", ".jsonl", ".txt", ".md"):
                try:
                    mtime = datetime.fromtimestamp(dosya.stat().st_mtime)
                    if mtime < sinir_tarih:
                        boyut = dosya.stat().st_size
                        dosya.unlink()
                        silinen += 1
                        kesilen_mb += boyut / 1048576
                        logger.info("🗑 Session silindi: %s (%.2f MB)", dosya.name, boyut / 1048576)
                except (OSError, PermissionError) as e:
                    logger.warning("Session silinemedi: %s — %s", dosya, e)
    except FileNotFoundError:
        logger.debug("Memory klasörü bulunamadı: %s", memory_path)

    return silinen, round(kesilen_mb, 2)


def _buyuk_dosyalari_sikistir(memory_path, esik_mb):
    """Limit aşan dosyaları gzip ile sıkıştırır."""
    sikistirilan = 0
    kesilen_mb = 0

    try:
        for dosya in Path(memory_path).rglob("*"):
            if not dosya.is_file():
                continue
            if dosya.suffix in SIKIŞTIRMA_DISI:
                continue
            try:
                boyut_mb = dosya.stat().st_size / 1048576
                if boyut_mb > esik_mb and dosya.suffix != ".gz":
                    # Zaten sıkıştırılmış mı kontrol et
                    hedef = dosya.with_suffix(dosya.suffix + ".gz")
                    if hedef.exists():
                        logger.debug("Zaten sıkıştırılmış: %s", dosya.name)
                        continue

                    with open(dosya, "rb") as f_in:
                        with gzip.open(hedef, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    orj_boyut = dosya.stat().st_size
                    dosya.unlink()
                    sikistirilan += 1
                    yeni_boyut = hedef.stat().st_size
                    kazanc_mb = (orj_boyut - yeni_boyut) / 1048576
                    kesilen_mb += kazanc_mb
                    logger.info("📦 Sıkıştırıldı: %s (%.2f MB → %.2f MB, %%{:.1f} kazanç)".format(
                        (1 - yeni_boyut / orj_boyut) * 100
                    ), dosya.name, orj_boyut / 1048576, yeni_boyut / 1048576)
            except (OSError, PermissionError) as e:
                logger.warning("Sıkıştırılamadı: %s — %s", dosya, e)
    except FileNotFoundError:
        logger.debug("Memory klasörü bulunamadı: %s", memory_path)

    return sikistirilan, round(kesilen_mb, 2)


def calistir():
    """Hafıza bakım job'unun ana çalıştırma fonksiyonu."""
    try:
        # Memory klasörünü bul
        proje_kok = Path(__file__).resolve().parent.parent
        memory_path = proje_kok / ".ReYMeN" / "memory"

        if not memory_path.exists():
            logger.warning("Memory klasörü bulunamadı: %s", memory_path)
            # Alternatif: ReYMeN ana dizinindeki memory
            ReYMeN_memory = Path.home() / ".ReYMeN" / "memory"
            if ReYMeN_memory.exists():
                memory_path = ReYMeN_memory
                logger.info("ReYMeN memory kullanılıyor: %s", memory_path)
            else:
                logger.warning("Hiçbir memory klasörü bulunamadı")
                memory_path = None

        baslangic_mb = 0
        sonuc = {"tarih": datetime.now().isoformat()}

        if memory_path:
            baslangic_mb = _klasör_boyutu(memory_path)
            sonuc["baslangic_boyutu_mb"] = round(baslangic_mb, 2)

            # 1. Eski sessionları temizle
            try:
                silinen, silinen_mb = _eski_sessionlari_temizle(
                    str(memory_path),
                    LİMİTLER["max_session_gun"],
                )
                sonuc["silinen_session"] = silinen
                sonuc["silinen_session_mb"] = silinen_mb
                logger.info("🧠 Session temizliği: %d dosya, %.2f MB", silinen, silinen_mb)
            except Exception as e:
                sonuc["session_hatasi"] = str(e)
                logger.error("Session temizlik hatası: %s", e)

            # 2. Büyük dosyaları sıkıştır
            try:
                sikistirilan, sikistirilan_mb = _buyuk_dosyalari_sikistir(
                    str(memory_path),
                    LİMİTLER["max_dosya_boyutu_mb"],
                )
                sonuc["sikistirilan_dosya"] = sikistirilan
                sonuc["sikistirilan_kazanc_mb"] = sikistirilan_mb
                logger.info("🧠 Sıkıştırma: %d dosya, %.2f MB kazanç", sikistirilan, sikistirilan_mb)
            except Exception as e:
                sonuc["sikistirma_hatasi"] = str(e)
                logger.error("Sıkıştırma hatası: %s", e)

            # 3. Son durum
            bitis_mb = _klasör_boyutu(memory_path)
            sonuc["bitis_boyutu_mb"] = round(bitis_mb, 2)
            sonuc["kazanc_mb"] = round(baslangic_mb - bitis_mb, 2)
            logger.info("🧠 Hafıza bakımı: %.2f MB → %.2f MB (%.2f MB kazanç)",
                        baslangic_mb, bitis_mb, baslangic_mb - bitis_mb)

        # Bellek limit kontrolü
        if baslangic_mb > LİMİTLER["max_bellek_mb"]:
            logger.warning("⚠️ Bellek limit aşımı: %.2f / %d MB", baslangic_mb, LİMİTLER["max_bellek_mb"])

        return sonuc

    except Exception as e:
        logger.error("❌ Hafıza bakım job'ı başarısız: %s", e)
        return {"hata": str(e)}


def bilgi():
    """Job metadata döndürür."""
    return {
        "isim": "hafıza_bakimi",
        "interval": "günde 1 kez",
        "aciklama": "Memory limitlerine yaklaşan dosyaları sıkıştırır, eski session'ları temizler",
        "versiyon": "1.0.0",
    }
