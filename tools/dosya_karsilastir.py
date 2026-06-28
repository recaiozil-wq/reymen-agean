# -*- coding: utf-8 -*-
"""tools/dosya_karsilastir.py — Iki dosyayi satir satir karsilastir.

difflib ile unified diff ve ozet fark gosterimi.
"""

import difflib
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def run(dosya1: str = "", dosya2: str = "", satir_baglam: int = 3,
        ozet: bool = False, **kwargs) -> dict:
    """Iki dosyayi satir satir karsilastir ve farklari goster.

    Args:
        dosya1: Ilk dosya yolu (zorunlu)
        dosya2: Ikinci dosya yolu (zorunlu)
        satir_baglam: Fark gosteriminde satir baglam miktari (varsayilan: 3)
        ozet: True ise sadece fark istatistigini goster (varsayilan: False)

    Returns:
        dict: {"basarili": bool, "cikti": str/list, "hata": str,
               "istatistik": {...}}
    """
    try:
        if not dosya1 or not dosya2:
            return {
                "basarili": False, "cikti": "", "hata": "dosya1 ve dosya2 parametreleri zorunludur."
            }

        dosya1_yol = Path(dosya1).resolve()
        dosya2_yol = Path(dosya2).resolve()

        if not dosya1_yol.exists():
            return {
                "basarili": False, "cikti": "",
                "hata": f"Dosya bulunamadi: {dosya1_yol}"
            }
        if not dosya2_yol.exists():
            return {
                "basarili": False, "cikti": "",
                "hata": f"Dosya bulunamadi: {dosya2_yol}"
            }

        # Kodlama algilamasi
        icerik1, hata1 = _dosya_oku(dosya1_yol)
        if hata1:
            return {"basarili": False, "cikti": "", "hata": hata1}

        icerik2, hata2 = _dosya_oku(dosya2_yol)
        if hata2:
            return {"basarili": False, "cikti": "", "hata": hata2}

        satirlar1 = icerik1.splitlines(keepends=True)
        satirlar2 = icerik2.splitlines(keepends=True)

        istatistik = _fark_istatistik(satirlar1, satirlar2)

        if ozet:
            return {
                "basarili": True,
                "cikti": _ozet_metni(dosya1_yol, dosya2_yol, istatistik),
                "hata": "",
                "istatistik": istatistik
            }
        else:
            # Unified diff
            fark = list(difflib.unified_diff(
                satirlar1, satirlar2,
                fromfile=str(dosya1_yol.name),
                tofile=str(dosya2_yol.name),
                n=satir_baglam,
                lineterm=""
            ))
            fark_metni = "\n".join(fark) if fark else "(Dosyalar ayni, fark yok)"

            return {
                "basarili": True,
                "cikti": fark_metni,
                "hata": "",
                "istatistik": istatistik
            }

    except Exception as e:
        logger.exception("Dosya karsilastirma hatasi")
        return {
            "basarili": False, "cikti": "",
            "hata": f"Beklenmeyen hata: {str(e)}"
        }


def _dosya_oku(dosya_yolu: Path) -> tuple:
    """Dosyayi UTF-8 ile okumayi dene, basarisiz olursa Latin-1 dene.

    Returns:
        (icerik, hata) — hata yoksa hata = ""
    """
    for kodlama in ["utf-8", "latin-1", "cp1254", "iso-8859-9"]:
        try:
            with open(dosya_yolu, "r", encoding=kodlama) as f:
                return f.read(), ""
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception as e:
            return "", f"Dosya okuma hatasi ({dosya_yolu}): {str(e)}"
    return "", f"Dosya okunamadi: {dosya_yolu} (desteklenen kodlamalar denenemadi)"


def _fark_istatistik(satirlar1: list, satirlar2: list) -> dict:
    """Iki satir listesi arasindaki fark istatistiklerini hesapla."""
    matcher = difflib.SequenceMatcher(None, satirlar1, satirlar2)
    eklenen = 0
    silinen = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            eklenen += j2 - j1
        elif tag == "delete":
            silinen += i2 - i1
        elif tag == "replace":
            eklenen += j2 - j1
            silinen += i2 - i1

    return {
        "dosya1_satir": len(satirlar1),
        "dosya2_satir": len(satirlar2),
        "eklenen_satir": eklenen,
        "silinen_satir": silinen,
        "degisen_satir": eklenen + silinen,
        "ayni_mi": eklenen == 0 and silinen == 0
    }


def _ozet_metni(dosya1: Path, dosya2: Path, istatistik: dict) -> str:
    """Ozet raporu metni olustur."""
    satir = "-" * 50
    if istatistik["ayni_mi"]:
        durum = "DOSYALAR AYNI (fark yok)"
    else:
        durum = "DOSYALAR FARKLI"
    return (
        f"{satir}\n"
        f"Dosya Karsilastirma Ozeti\n"
        f"{satir}\n"
        f"Dosya 1: {dosya1} ({istatistik['dosya1_satir']} satir)\n"
        f"Dosya 2: {dosya2} ({istatistik['dosya2_satir']} satir)\n"
        f"Durum: {durum}\n"
        f"Eklenen satir: {istatistik['eklenen_satir']}\n"
        f"Silinen satir: {istatistik['silinen_satir']}\n"
        f"Toplam degisiklik: {istatistik['degisen_satir']}\n"
        f"{satir}"
    )


if __name__ == "__main__":
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f1:
        f1.write("satir 1\nsatir 2\nsatir 3\n")
        p1 = f1.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f2:
        f2.write("satir 1\nsatir X\nsatir 3\nsatir 4\n")
        p2 = f2.name

    print("=== DOSYA KARSILASTIR (detayli) ===")
    print(run(dosya1=p1, dosya2=p2))

    print("\n=== DOSYA KARSILASTIR (ozet) ===")
    print(run(dosya1=p1, dosya2=p2, ozet=True))

    os.unlink(p1)
    os.unlink(p2)
