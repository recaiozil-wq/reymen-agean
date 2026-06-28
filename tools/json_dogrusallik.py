# -*- coding: utf-8 -*-
"""tools/json_dogrusallik.py — JSON string dogrulama, formatlama ve minify.

json.loads/dumps ile dogrulama, guzel yazdirma ve kucultme islemleri.
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def run(islem: str = "dogrula", veri: str = "", girinti: int = 2,
        sirala: bool = False, **kwargs) -> dict:
    """JSON string uzerinde dogrulama, formatlama veya minify yap.

    Args:
        islem: "dogrula" (varsayilan), "formatla", "minify"
        veri: Islenecek JSON string
        girinti: "formatla" isleminde kullanilacak girinti miktari (varsayilan: 2)
        sirala: "formatla" isleminde anahtarlari sirala (varsayilan: False)

    Returns:
        dict: {"basarili": bool, "cikti": str|dict, "hata": str}
    """
    try:
        if not veri:
            if islem == "dogrula":
                return {
                    "basarili": False, "cikti": "",
                    "hata": "veri parametresi zorunludur."
                }
            # Bos string JSON olarak gecerli degil
            return {
                "basarili": False, "cikti": "",
                "hata": "Islem yapilacak JSON verisi bos."
            }

        if islem == "dogrula":
            return _dogrula(veri)
        elif islem == "formatla":
            return _formatla(veri, girinti, sirala)
        elif islem == "minify":
            return _minify(veri)
        else:
            return {
                "basarili": False, "cikti": "",
                "hata": f"Gecersiz islem: '{islem}'. Secenekler: dogrula, formatla, minify"
            }

    except Exception as e:
        logger.exception("JSON dogrusallik hatasi")
        return {
            "basarili": False, "cikti": "",
            "hata": f"Beklenmeyen hata: {str(e)}"
        }


def _parse_json(veri: str) -> tuple:
    """JSON string'i parse et.

    Returns:
        (parse_edildi: bool, sonuc: Any, hata: str)
    """
    try:
        sonuc = json.loads(veri)
        return True, sonuc, ""
    except json.JSONDecodeError as e:
        konum = f" (satir {e.lineno}, sutun {e.colno}, offset {e.pos})" if hasattr(e, 'lineno') else ""
        return False, None, f"JSON parse hatasi{konum}: {e.msg}"


def _dogrula(veri: str) -> dict:
    """JSON stringini dogrula, basariliysa tipini ve boyutunu goster."""
    basarili, sonuc, hata = _parse_json(veri)
    if basarili:
        tip = type(sonuc).__name__
        boyut = len(veri)
        return {
            "basarili": True,
            "cikti": {
                "durum": "Gecerli JSON",
                "tip": tip,
                "boyut": boyut,
                "karakter_sayisi": len(veri)
            },
            "hata": ""
        }
    else:
        return {"basarili": False, "cikti": "", "hata": hata}


def _formatla(veri: str, girinti: int = 2, sirala: bool = False) -> dict:
    """JSON stringini guzel yazdir."""
    basarili, sonuc, hata = _parse_json(veri)
    if not basarili:
        return {"basarili": False, "cikti": "", "hata": hata}

    try:
        # Unicode karakterleri koru (ensure_ascii=False)
        fmt = json.dumps(sonuc, indent=girinti, sort_keys=sirala, ensure_ascii=False)
        return {
            "basarili": True,
            "cikti": fmt,
            "hata": ""
        }
    except Exception as e:
        return {
            "basarili": False, "cikti": "",
            "hata": f"Formatlama hatasi: {str(e)}"
        }


def _minify(veri: str) -> dict:
    """JSON stringini kucult (gereksiz bosluklari kaldir)."""
    basarili, sonuc, hata = _parse_json(veri)
    if not basarili:
        return {"basarili": False, "cikti": "", "hata": hata}

    try:
        kucuk = json.dumps(sonuc, separators=(",", ":"), ensure_ascii=False)
        kazanc = len(veri) - len(kucuk)
        return {
            "basarili": True,
            "cikti": kucuk,
            "hata": "",
            "kazanc": kazanc,
            "kazanc_yuzde": round((kazanc / len(veri)) * 100, 1) if len(veri) > 0 else 0
        }
    except Exception as e:
        return {
            "basarili": False, "cikti": "",
            "hata": f"Minify hatasi: {str(e)}"
        }


if __name__ == "__main__":
    print("=== JSON DOGRULA ===")
    print(run(islem="dogrula", veri='{"ad": "Ali", "yas": 30}'))
    print("\n=== JSON FORMATLA ===")
    print(run(islem="formatla", veri='{"ad":"Ali","yas":30,"sehir":"Istanbul"}'))
    print("\n=== JSON MINIFY ===")
    print(run(islem="minify", veri='{"ad": "Ali", "yas": 30}'))
