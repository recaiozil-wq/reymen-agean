"""
cron/health_job.py — Sistem sağlığı cron job'u.

Disk alanı, bellek, servis durumu kontrolü.
ReYMeN sistem izleme altyapısı için sağlık denetim görevi.
"""

import logging
import os
import shutil
import platform
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Uyarı eşikleri
UYARI_EŞIKLERI = {
    "disk_min_mb": 500,        # Minimum boş disk alanı (MB)
    "disk_yuzde_max": 90,      # Maksimum disk kullanım yüzdesi
    "bellek_yuzde_max": 85,    # Maksimum bellek kullanım yüzdesi
}


def _disk_durumu(path="."):
    """Belirtilen yolun disk kullanım bilgilerini döndürür."""
    try:
        toplam, kullanilan, bos = shutil.disk_usage(path)
        return {
            "toplam_mb": round(toplam / 1048576, 2),
            "kullanilan_mb": round(kullanilan / 1048576, 2),
            "bos_mb": round(bos / 1048576, 2),
            "kullanim_yuzde": round((kullanilan / toplam) * 100, 1),
        }
    except (FileNotFoundError, PermissionError) as e:
        logger.warning("Disk durumu okunamadı: %s", e)
        return {"hata": str(e)}


def _bellek_durumu():
    """Sistem belleği kullanım bilgilerini döndürür."""
    try:
        import psutil
        bellek = psutil.virtual_memory()
        return {
            "toplam_mb": round(bellek.total / 1048576, 2),
            "kullanilan_mb": round(bellek.used / 1048576, 2),
            "bos_mb": round(bellek.available / 1048576, 2),
            "kullanim_yuzde": bellek.percent,
        }
    except ImportError:
        # psutil yoksa basit ölçüm dene
        try:
            if platform.system() == "Linux":
                with open("/proc/meminfo") as f:
                    satirlar = f.readlines()
                toplam = None
                bos = None
                for satir in satirlar:
                    if satir.startswith("MemTotal:"):
                        toplam = int(satir.split()[1]) // 1024
                    elif satir.startswith("MemAvailable:"):
                        bos = int(satir.split()[1]) // 1024
                if toplam and bos:
                    return {
                        "toplam_mb": round(toplam, 2),
                        "kullanilan_mb": round(toplam - bos, 2),
                        "bos_mb": round(bos, 2),
                        "kullanim_yuzde": round(((toplam - bos) / toplam) * 100, 1),
                    }
        except (FileNotFoundError, IndexError, ValueError):
            logger.warning("[fix_01_sessiz_except] Exception")
        return {"hata": "psutil yok, bellek okunamadı"}
    except Exception as e:
        logger.warning("Bellek durumu okunamadı: %s", e)
        return {"hata": str(e)}


def _servis_durumu():
        """Kritik servislerin durumunu kontrol eder."""
        servisler = {}
        try:
            # Python çalışıyor mu?
            import sys
            servisler["python"] = {"durum": "calisiyor", "versiyon": sys.version.split()[0]}
        except Exception:
            servisler["python"] = {"durum": "bilinmiyor"}

        try:
            # Git var mı?
            import subprocess
            sonuc = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if sonuc.returncode == 0:
                servisler["git"] = {"durum": "calisiyor", "versiyon": sonuc.stdout.strip()}
            else:
                servisler["git"] = {"durum": "bulunamadi"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            servisler["git"] = {"durum": "bulunamadi"}

        return servisler


def _kontrol_et(disk, bellek, servisler):
    """Sağlık kontrol sonuçlarını değerlendirir, uyarıları döndürür."""
    uyarilar = []
    try:
        if "bos_mb" in disk and disk["bos_mb"] < UYARI_EŞIKLERI["disk_min_mb"]:
            uyarilar.append(f"KRİTİK: Disk alanı az! ({disk['bos_mb']} MB boş)")
        if "kullanim_yuzde" in disk and disk["kullanim_yuzde"] > UYARI_EŞIKLERI["disk_yuzde_max"]:
            uyarilar.append(f"UYARI: Disk kullanımı %%{disk['kullanim_yuzde']} (eşik: %%{UYARI_EŞIKLERI['disk_yuzde_max']})")
        if isinstance(bellek, dict) and "kullanim_yuzde" in bellek and bellek["kullanim_yuzde"] > UYARI_EŞIKLERI["bellek_yuzde_max"]:
            uyarilar.append(f"UYARI: Bellek kullanımı %%{bellek['kullanim_yuzde']} (eşik: %%{UYARI_EŞIKLERI['bellek_yuzde_max']})")
    except Exception as e:
        logger.warning("Kontrol değerlendirme hatası: %s", e)
    return uyarilar


def calistir():
    """Sistem sağlığı job'unun ana çalıştırma fonksiyonu."""
    try:
        sonuc = {
            "tarih": datetime.now().isoformat(),
            "sistem": platform.system(),
            "host": platform.node(),
        }

        # Disk kontrolü
        try:
            disk = _disk_durumu()
            sonuc["disk"] = disk
            logger.info("🖥 Disk: %s", disk)
        except Exception as e:
            sonuc["disk"] = {"hata": str(e)}
            logger.error("Disk kontrol hatası: %s", e)

        # Bellek kontrolü
        try:
            bellek = _bellek_durumu()
            sonuc["bellek"] = bellek
            logger.info("🖥 Bellek: %s", bellek)
        except Exception as e:
            sonuc["bellek"] = {"hata": str(e)}
            logger.error("Bellek kontrol hatası: %s", e)

        # Servis kontrolü
        try:
            servisler = _servis_durumu()
            sonuc["servisler"] = servisler
            logger.info("🖥 Servisler: %s", servisler)
        except Exception as e:
            sonuc["servisler"] = {"hata": str(e)}
            logger.error("Servis kontrol hatası: %s", e)

        # Uyarılar
        uyarilar = _kontrol_et(
            sonuc.get("disk", {}),
            sonuc.get("bellek", {}),
            sonuc.get("servisler", {}),
        )
        sonuc["uyarilar"] = uyarilar
        sonuc["saglikli"] = len(uyarilar) == 0

        if uyarilar:
            for uyari in uyarilar:
                logger.warning("⚠️ %s", uyari)
        else:
            logger.info("✅ Sistem sağlıklı")

        return sonuc

    except Exception as e:
        logger.error("❌ Sağlık job'ı başarısız: %s", e)
        return {"hata": str(e)}


def bilgi():
    """Job metadata döndürür."""
    return {
        "isim": "sistem_sagligi",
        "interval": "saatte 1 kez",
        "aciklama": "Disk alanı, bellek kullanımı ve servis durumu kontrolü",
        "versiyon": "1.0.0",
    }
