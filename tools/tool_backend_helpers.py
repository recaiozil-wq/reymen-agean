#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool_backend_helpers.py â€” Tool arka plan yardÄ±mcÄ±larÄ±.
Ortak tool fonksiyonlarÄ±: format_sonuc(), hata_yakala(), sure_olc().
"""

import json
import time
import traceback
import functools


def format_sonuc(durum="basarili", data=None, mesaj="", ekstra=None):
    """
    Standart sonuÃ§ formatÄ±.
    
    Parametreler:
        durum (str): "basarili" veya "hata"
        data (dict): SonuÃ§ verisi
        mesaj (str): AÃ§Ä±klama mesajÄ±
        ekstra (dict): Ekstra alanlar
    
    Returns:
        str: JSON formatÄ±nda sonuÃ§
    """
    sonuc = {"durum": durum}
    if data:
        sonuc["data"] = data
    if mesaj:
        sonuc["mesaj"] = mesaj
    if ekstra:
        sonuc.update(ekstra)
    return json.dumps(sonuc, ensure_ascii=False, default=str)


def hata_yakala(islev):
    """
    Decorator: Fonksiyon hatalarÄ±nÄ± yakala ve JSON formatÄ±nda dÃ¶ndÃ¼r.
    
    KullanÄ±m:
        @hata_yakala
        def benim_fonksiyonum():
            ...
    """
    @functools.wraps(islev)
    def sarmalayici(*args, **kwargs):
        try:
            return islev(*args, **kwargs)
        except Exception as e:
            hata_detay = {
                "hata": str(e),
                "tip": type(e).__name__,
                "izleme": traceback.format_exc()
            }
            return json.dumps({
                "durum": "hata",
                "mesaj": str(e),
                "hata_detay": hata_detay
            }, ensure_ascii=False)
    return sarmalayici


def sure_olc(islev=None, birim="sn"):
    """
    Decorator veya context: Ä°ÅŸlem sÃ¼resini Ã¶lÃ§.
    
    Decorator olarak:
        @sure_olc
        def benim_fonksiyonum():
            ...
    
    @sure_olc(birim="ms")
    def benim_fonksiyonum():
        ...
    
    Manuel kullanÄ±m:
        basla = sure_olc.baslat()
        ... islem ...
        gecen = sure_olc.bitir(basla)
    """
    if islev is not None:
        # Direkt decorator kullanÄ±mÄ±: @sure_olc
        @functools.wraps(islev)
        def sarmalayici(*args, **kwargs):
            baslangic = time.time()
            try:
                sonuc = islev(*args, **kwargs)
                return sonuc
            finally:
                gecen = time.time() - baslangic
                if birim == "ms":
                    gecen *= 1000
        return sarmalayici
    
    # Parametreli decorator: @sure_olc(birim="ms")
    def decorator(islev):
        @functools.wraps(islev)
        def sarmalayici(*args, **kwargs):
            baslangic = time.time()
            try:
                return islev(*args, **kwargs)
            finally:
                gecen = time.time() - baslangic
                if birim == "ms":
                    gecen *= 1000
        return sarmalayici
    return decorator


# Manuel sÃ¼re Ã¶lÃ§Ã¼mÃ¼ iÃ§in yardÄ±mcÄ±lar
def baslat():
    """SÃ¼re Ã¶lÃ§Ã¼mÃ¼ baÅŸlat."""
    return time.time()


def bitir(baslangic, birim="sn"):
    """SÃ¼re Ã¶lÃ§Ã¼mÃ¼ bitir ve geÃ§en sÃ¼reyi dÃ¶ndÃ¼r."""
    gecen = time.time() - baslangic
    if birim == "ms":
        gecen *= 1000
    return round(gecen, 4)


def run(islem="format_sonuc", durum="basarili", mesaj="", data=None):
    """
    Tool arka plan yardÄ±mcÄ±larÄ±.
    
    Parametreler:
        islem (str): format_sonuc / hata_yakala / sure_olc
        durum (str): Ä°ÅŸlem durumu
        mesaj (str): AÃ§Ä±klama mesajÄ±
        data (str): JSON veri
    
    Returns:
        str: YardÄ±mcÄ± fonksiyon sonucu
    """
    try:
        if islem == "format_sonuc":
            parsed_data = None
            if data:
                try:
                    parsed_data = json.loads(data) if isinstance(data, str) else data
                except json.JSONDecodeError:
                    parsed_data = data
            return format_sonuc(durum, parsed_data, mesaj)

        elif islem == "hata_yakala":
            return json.dumps({
                "durum": "basarili",
                "mesaj": "hata_yakala decorator'u fonksiyonlarda kullanÄ±lÄ±r: @hata_yakala",
                "kullanim": "@hata_yakala\\ndef fonksiyonum():\\n    ..."
            }, ensure_ascii=False)

        elif islem == "sure_olc":
            ornek_basla = baslat()
            time.sleep(0.01)  # 10ms bekle
            gecen = bitir(ornek_basla, "ms")
            return json.dumps({
                "durum": "basarili",
                "mesaj": "sure_olc decorator veya manuel kullanÄ±labilir",
                "ornek_sure_ms": gecen,
                "kullanim": "@sure_olc\\nveya\\nbasla = baslat(); ...; gecen = bitir(basla)"
            }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen iÅŸlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# --- ReYMeN uyumlu stubs ---

_VALID_MODAL_MODES = {"default", "auto", "native", "fallback"}


def managed_nous_tools_enabled() -> bool:
    """Nous yonetimli araclari etkinlestir â€” ReYMeN uyumluluÄŸu."""
    import os
    return os.getenv("NOUS_MANAGED_TOOLS", "0").lower() in ("1", "true", "yes")


def has_direct_modal_credentials() -> bool:
    """Modal kimlik bilgileri mevcut mu kontrol et â€” ReYMeN uyumluluÄŸu."""
    import os
    from pathlib import Path
    try:
        modal_file = (Path.home() / ".modal.toml").exists()
    except (PermissionError, OSError):
        modal_file = False
    return bool(
        (os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"))
        or modal_file
    )


def coerce_modal_mode(value=None) -> str:
    """Modal mod deÄŸerini doÄŸrula ve dÃ¶ndÃ¼r â€” ReYMeN uyumluluÄŸu."""
    if value is None:
        return "default"
    if isinstance(value, str) and value.lower() in _VALID_MODAL_MODES:
        return value.lower()
    return "default"

# --- ReYMeN stubs sonu ---


if __name__ == "__main__":
    print(run("format_sonuc", "basarili", "Test mesajÄ±"))
    print(run("sure_olc"))

def nous_tool_gateway_unavailable_message(tool_name: str = "") -> str:
    """Nous arac gecidi kullanilamaz mesaji — ReYMeN uyumluluk stubu."""
    return f"[Nous Gateway] '{tool_name}' araci gecici olarak kullanilamiyor."

def resolve_modal_backend_state(modal_mode=None):
    """Modal arka plan durumunu coz - ReYMeN uyumluluk stubu."""
    return {"mode": coerce_modal_mode(modal_mode), "available": has_direct_modal_credentials()}