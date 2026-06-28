"""
cron/backup_job.py — Otomatik yedekleme cron job'u.

.ReYMeN/ önemli dosyalarını yedekler.
ReYMeN veri koruma altyapısı için periyodik yedekleme görevi.
"""

import logging
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import zipfile

logger = logging.getLogger(__name__)

# Yedeklenecek dizinler ve dosyalar
YEDEK_KAYNAKLARI = [
    ".ReYMeN",
    "cron",
    "skills",
    "plugins",
]

DISLANACAKLAR = {
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    ".trash",
}


def _tarama_yap(kaynak_path):
    """Belirtilen yoldaki yedeklenecek dosya ve klasörleri tarar."""
    bulunanlar = []
    try:
        for item in Path(kaynak_path).iterdir():
            if item.name in DISLANACAKLAR:
                continue
            bulunanlar.append(str(item))
    except FileNotFoundError:
        logger.debug("Kaynak bulunamadı: %s", kaynak_path)
    except PermissionError as e:
        logger.warning("Erişim engeli: %s — %s", kaynak_path, e)
    return bulunanlar


def _yedek_olustur(kaynak, hedef_zip):
    """Belirtilen kaynak dizini zip dosyasına yedekler."""
    eklenen = 0
    try:
        with zipfile.ZipFile(hedef_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            kaynak_path = Path(kaynak)
            if kaynak_path.is_dir():
                for dosya in kaynak_path.rglob("*"):
                    if any(disilanacak in dosya.parts for disilanacak in DISLANACAKLAR):
                        continue
                    if dosya.is_file():
                        try:
                            arcname = str(dosya.relative_to(kaynak_path.parent))
                            zf.write(dosya, arcname)
                            eklenen += 1
                        except (OSError, PermissionError) as e:
                            logger.warning("Dosya eklenemedi: %s — %s", dosya, e)
            elif kaynak_path.is_file():
                zf.write(kaynak_path, kaynak_path.name)
                eklenen = 1
        return eklenen
    except Exception as e:
        logger.error("Zip oluşturulamadı: %s", e)
        return 0


def calistir():
    """Yedekleme job'unun ana çalıştırma fonksiyonu."""
    try:
        # Proje kök dizinini bul
        proje_kok = Path(__file__).resolve().parent.parent

        # Yedek klasörü
        yedek_klasor = proje_kok / ".yedek"
        yedek_klasor.mkdir(exist_ok=True)

        # Zaman damgası
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        genel_durum = {}
        toplam_dosya = 0

        for kaynak_adi in YEDEK_KAYNAKLARI:
            kaynak_path = proje_kok / kaynak_adi
            if not kaynak_path.exists():
                logger.debug("Kaynak mevcut değil, atlanıyor: %s", kaynak_adi)
                continue

            hedef_zip = yedek_klasor / f"{kaynak_adi}_{zaman_damgasi}.zip"

            try:
                dosya_sayisi = _yedek_olustur(str(kaynak_path), str(hedef_zip))
                toplam_dosya += dosya_sayisi
                genel_durum[kaynak_adi] = {
                    "durum": "basarili",
                    "dosya_sayisi": dosya_sayisi,
                    "yedek": str(hedef_zip),
                }
                logger.info("💾 Yedeklendi: %s → %s (%d dosya)", kaynak_adi, hedef_zip.name, dosya_sayisi)
            except Exception as e:
                genel_durum[kaynak_adi] = {"durum": "hata", "hata": str(e)}
                logger.error("Yedekleme hatası: %s — %s", kaynak_adi, e)

        # Özet raporu yaz
        rapor = {
            "tarih": zaman_damgasi,
            "toplam_dosya": toplam_dosya,
            "durumlar": genel_durum,
        }
        rapor_yolu = yedek_klasor / f"rapor_{zaman_damgasi}.json"
        with open(rapor_yolu, "w", encoding="utf-8") as f:
            json.dump(rapor, f, ensure_ascii=False, indent=2)

        logger.info("💾 Yedekleme tamamlandı: %d kaynak, %d dosya", len(genel_durum), toplam_dosya)
        return genel_durum

    except Exception as e:
        logger.error("❌ Yedekleme job'ı başarısız: %s", e)
        return {"hata": str(e)}


def bilgi():
    """Job metadata döndürür."""
    return {
        "isim": "otomatik_yedekleme",
        "interval": "günde 1 kez",
        "aciklama": ".ReYMeN/ ve önemli dosyaları .yedek/ klasörüne yedekler",
        "versiyon": "1.0.0",
    }
