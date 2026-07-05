# -*- coding: utf-8 -*-
"""
hata_analiz.py â€” Hata SonrasÄ± Analiz ve Otomatik DÃ¼zeltme.

GÃ¶rev hata verdiÄŸinde conversation_loop.py tarafÄ±ndan Ã§aÄŸrÄ±lÄ±r:
  1. Hata mesajÄ±nÄ± parse et
  2. Benzer hata geÃ§miÅŸini hafÄ±zada ara
  3. Ã‡Ã¶zÃ¼m Ã¶nerisi Ã¼ret
  4. Otomatik dÃ¼zeltme dene (seÃ§ilen hata tipleri iÃ§in)

AkÄ±ÅŸ:
  GÃ¶rev â†’ HATA â†’ analiz_et(hata, hedef)
    â”œâ”€ HafÄ±zada benzer hata var mÄ±?
    â”‚  â”œâ”€ EVET â†’ Ã¶nceki Ã§Ã¶zÃ¼mÃ¼ uygula
    â”‚  â””â”€ HAYIR â†’ Ã§Ã¶zÃ¼m Ã¶nerisi Ã¼ret
    â”œâ”€ Otomatik dÃ¼zeltilebilir mi?
    â”‚  â”œâ”€ EVET â†’ dÃ¼zelt ve tekrar dene
    â”‚  â””â”€ HAYIR â†’ raporla
    â””â”€ Kaydet (yeni hata + Ã§Ã¶zÃ¼m)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

log = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(__file__).parent.resolve()  # reymen/hafiza/
PROJE = ROOT.parent.parent  # hermes_projesi/

# KaydedilmiÅŸ hata Ã§Ã¶zÃ¼mleri (HATA_COZUM_DB)
HATA_DB_YOLU = PROJE / ".ReYMeN" / "hata_cozumleri.md"
SKILLS_DIR = PROJE / ".ReYMeN" / "skills"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HATA SINIFLANDIRMA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class HataSinifi:
    """Hata tÃ¼rÃ¼ ve dÃ¼zeltme stratejisi."""

    MODUL_EKSIK = "modul_eksik"  # ImportError
    DOSYA_EKSIK = "dosya_eksik"  # FileNotFoundError
    IZIN_REDDI = "izin_reddi"  # PermissionError
    BAGLANTI_HATASI = "baglanti_hatasi"  # ConnectionError / timeout
    API_HATASI = "api_hatasi"  # API dÃ¶ndÃ¼ hata
    SENTAKS_HATASI = "sentaks_hatasi"  # SyntaxError / lint
    TIP_HATASI = "tip_hatasi"  # TypeError
    DIGER = "diger"  # SÄ±nÄ±flandÄ±rÄ±lamayan


HATA_SINIFLARI = {
    "modul_eksik": {
        "desen": r"(ImportError|ModuleNotFoundError|No module named)",
        "cozum": "pip install veya import kontrol",
        "otomatik": True,
    },
    "dosya_eksik": {
        "desen": r"(FileNotFoundError|No such file|dosya bulunamadÄ±)",
        "cozum": "Dosya yolunu kontrol et, oluÅŸtur",
        "otomatik": True,
    },
    "izin_reddi": {
        "desen": r"(PermissionError|Access denied|EACCES)",
        "cozum": "Yetki kontrolÃ¼, admin modu",
        "otomatik": False,
    },
    "baglanti_hatasi": {
        "desen": r"(ConnectionError|Connection refused|timeout|TIMEOUT|network unreachable)",
        "cozum": "BaÄŸlantÄ± kontrolÃ¼, yeniden dene",
        "otomatik": True,
    },
    "api_hatasi": {
        "desen": r"(HTTPError|4\d{2}|5\d{2}|API hatasÄ±|rate limit)",
        "cozum": "API anahtarÄ± / limit / endpoint kontrol",
        "otomatik": False,
    },
    "sentaks_hatasi": {
        "desen": r"(SyntaxError|invalid syntax|syntax error|lint hatasÄ±)",
        "cozum": "Kod dÃ¼zeltme",
        "otomatik": True,
    },
    "tip_hatasi": {
        "desen": r"(TypeError|expected.*got|unsupported operand)",
        "cozum": "Tip dÃ¶nÃ¼ÅŸÃ¼mÃ¼, parametre kontrolÃ¼",
        "otomatik": True,
    },
}


def hata_siniflandir(hata_mesaji: str) -> Tuple[str, dict]:
    """Hata mesajÄ±nÄ± parse et ve sÄ±nÄ±fÄ±nÄ± belirle.

    Args:
        hata_mesaji: Ham hata metni veya traceback.

    Returns:
        (sinif_adi, sinif_bilgisi): Ã–rn. ("modul_eksik", {...})
    """
    if not hata_mesaji:
        return ("diger", HATA_SINIFLARI["diger"])

    for sinif_adi, sinif_bilgi in HATA_SINIFLARI.items():
        desen = sinif_bilgi.get("desen", "")
        if desen and re.search(desen, hata_mesaji, re.IGNORECASE):
            return (sinif_adi, sinif_bilgi)

    return ("diger", {"cozum": "Manuel analiz gerekli", "otomatik": False})


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HAFIZADA HATA Ã‡Ã–ZÃœMÃœ ARA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def hata_cozumu_ara(hata_sinifi: str, hedef: str) -> Optional[str]:
    """Daha Ã¶nce kaydedilmiÅŸ hata Ã§Ã¶zÃ¼mlerini hafÄ±zada ara.

    Args:
        hata_sinifi: Hata sÄ±nÄ±fÄ± (Ã¶rn. "modul_eksik")
        hedef: GÃ¶revin hedef metni

    Returns:
        str: Ã‡Ã¶zÃ¼m metni (varsa), None: bulunamadÄ±
    """
    # 1. HATA_COZUM_DB'ye bak
    try:
        if HATA_DB_YOLU.exists():
            icerik = HATA_DB_YOLU.read_text(encoding="utf-8", errors="replace")

            # Hata sÄ±nÄ±fÄ±na gÃ¶re bÃ¶lÃ¼me bak
            bolum_ici = icerik.find(f"## {hata_sinifi}")
            if bolum_ici != -1:
                bolum_sonu = icerik.find("\n## ", bolum_ici + 3)
                if bolum_sonu == -1:
                    bolum_sonu = len(icerik)
                bolum = icerik[bolum_ici:bolum_sonu]

                # Hedefle ilgili satÄ±r var mÄ±?
                kelimeler = [k.lower() for k in hedef.split() if len(k) > 3]
                for satir in bolum.split("\n"):
                    satir_lower = satir.lower()
                    if (
                        sum(1 for k in kelimeler if k in satir_lower)
                        >= len(kelimeler) // 2
                    ):
                        return satir.strip()

    except Exception as e:
        log.warning("Hata Ã§Ã¶zÃ¼mÃ¼ aranirken hata: %s", e)

    return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‡Ã–ZÃœM KAYDET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def hata_cozumu_kaydet(hata_sinifi: str, hata_mesaji: str, cozum: str, hedef: str):
    """Bulunan/kullanÄ±lan hata Ã§Ã¶zÃ¼mÃ¼nÃ¼ HATA_COZUM_DB'ye kaydet.

    Args:
        hata_sinifi: Hata sÄ±nÄ±fÄ±
        hata_mesaji: Orijinal hata mesajÄ±
        cozum: Uygulanan Ã§Ã¶zÃ¼m
        hedef: GÃ¶revin hedefi
    """
    try:
        from datetime import datetime

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M")
        yeni_kayit = (
            f"- **{hedef[:80]}** ({zaman})\n"
            f"  - Hata: `{hata_mesaji[:200]}`\n"
            f"  - Cozum: {cozum[:200]}\n"
        )

        if HATA_DB_YOLU.exists():
            mevcut = HATA_DB_YOLU.read_text(encoding="utf-8", errors="replace")

            # BÃ¶lÃ¼m baÅŸlÄ±ÄŸÄ± var mÄ±?
            bolum_basligi = f"## {hata_sinifi}"
            if bolum_basligi in mevcut:
                mevcut = mevcut.replace(bolum_basligi, f"{bolum_basligi}\n{yeni_kayit}")
            else:
                mevcut += f"\n\n{bolum_basligi}\n{yeni_kayit}"

            HATA_DB_YOLU.write_text(mevcut, encoding="utf-8")
        else:
            HATA_DB_YOLU.parent.mkdir(parents=True, exist_ok=True)
            icerik = (
                f"# Hata Ã‡Ã¶zÃ¼mleri â€” ReYMeN\n\n"
                f"_Otomatik kaydedilen hata-Ã§Ã¶zÃ¼m eÅŸleÅŸmeleri._\n\n"
                f"## {hata_sinifi}\n{yeni_kayit}\n"
            )
            HATA_DB_YOLU.write_text(icerik, encoding="utf-8")

        log.info("Hata Ã§Ã¶zÃ¼mÃ¼ kaydedildi: %s â†’ %s", hata_sinifi, cozum[:60])

    except Exception as e:
        log.warning("Hata Ã§Ã¶zÃ¼mÃ¼ kaydedilirken hata: %s", e)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANA ANALÄ°Z FONKSÄ°YONU
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def hata_analiz_et(hata_mesaji: str, hedef: str) -> dict:
    """Hata analizini yap, Ã§Ã¶zÃ¼m Ã¶nerisi Ã¼ret.

    Args:
        hata_mesaji: Hata mesajÄ± (veya traceback)
        hedef: GÃ¶revin hedef metni

    Returns:
        dict: {
            "sinif": "modul_eksik",
            "otomatik": True/False,
            "cozum_onerisi": "...",
            "hafizada_var": True/False,
            "hafiza_cozumu": "...",
            "kaydedildi": True/False,
        }
    """
    # 1. SÄ±nÄ±flandÄ±r
    sinif_adi, sinif_bilgi = hata_siniflandir(hata_mesaji)

    # 2. HafÄ±zada Ã§Ã¶zÃ¼m ara
    hafiza_cozum = hata_cozumu_ara(sinif_adi, hedef)

    # 3. Ã‡Ã¶zÃ¼m Ã¶nerisi oluÅŸtur
    if hafiza_cozum:
        cozum_onerisi = hafiza_cozum
    else:
        cozum_onerisi = sinif_bilgi.get(
            "cozum", "Bilinmeyen hata, manuel analiz gerekli"
        )

    # 4. Kaydet (yeni hata olarak)
    if not hafiza_cozum:
        hata_cozumu_kaydet(sinif_adi, hata_mesaji, cozum_onerisi, hedef)

    return {
        "sinif": sinif_adi,
        "otomatik": sinif_bilgi.get("otomatik", False),
        "cozum_onerisi": cozum_onerisi,
        "hafizada_var": hafiza_cozum is not None,
        "hafiza_cozumu": hafiza_cozum,
        "kaydedildi": not hafiza_cozum,  # yeni hata = kaydedildi
    }
