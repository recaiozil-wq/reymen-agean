"""reymen_gece_ogrenme_cron.py — Gece otomatik öğrenme döngüsü.

Periyodik cron tetiklemesi için:
- Kapalı öğrenme döngüsünü çalıştırır
- FTS5 indeksini günceller
- Durum raporu üretir
"""
import sys
import os
from pathlib import Path

_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
_env_path = _ROOT / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

# .env: once AppData, sonra proje koku
dotenv_path = Path(os.environ.get("LOCALAPPDATA", "")) / "ReYMeN" / ".env"
if not dotenv_path.exists():
    dotenv_path = _ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path, override=True)

import time


def _ogrenme_durum():
    """Kapalı öğrenme döngüsü durum raporu."""
    try:
        from closed_learning_loop import _get_loop

        loop = _get_loop()
        toplam = loop.toplam_beceri_sayisi()
        tumu = loop.tum_beceriler()

        satirlar = [
            "=== KAPALI OGRENME DONGUSU RAPORU ===",
            f"Toplam beceri: {toplam}",
            f"Zaman: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        if tumu:
            satirlar.append(f"\nSon {min(5, len(tumu))} beceri:")
            for b in tumu[-5:]:
                ad = b.get("ad", b.get("isim", "?"))
                kullanim = b.get("kullanim_sayisi", b.get("usage_count", 0))
                satirlar.append(f"  - {ad} (kullanim: {kullanim})")
        else:
            satirlar.append("\nHenuz beceri yok.")
        return "\n".join(satirlar)
    except Exception as e:
        return f"[HATA] Ogrenme dongusu: {e}"


def main():
    """Ana cron fonksiyonu."""
    rapor = _ogrenme_durum()
    print(rapor)


if __name__ == "__main__":
    main()
