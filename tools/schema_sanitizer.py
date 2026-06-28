#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_sanitizer.py — JSON şema doğrulayıcı.
Girdi/çıktı şema kontrolü, tip dönüşümü.
"""

import json
import datetime
import logging
logger = logging.getLogger(__name__)


def _tip_kontrol(deger, beklenen_tip):
    """Değerin tipini kontrol et ve dönüştürmeyi dene."""
    tip_haritasi = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "none": type(None),
        "any": object
    }
    
    hedef_tip = tip_haritasi.get(beklenen_tip)
    if hedef_tip is None:
        return False, None, f"Bilinmeyen tip: {beklenen_tip}"
    
    if isinstance(deger, hedef_tip):
        return True, deger, None
    
    # Dönüştürmeyi dene
    try:
        if beklenen_tip == "str":
            donusen = str(deger)
        elif beklenen_tip == "int":
            donusen = int(deger)
        elif beklenen_tip == "float":
            donusen = float(deger)
        elif beklenen_tip == "bool":
            if isinstance(deger, str):
                donusen = deger.lower() in ("true", "1", "yes", "evet")
            else:
                donusen = bool(deger)
        elif beklenen_tip == "list":
            if isinstance(deger, str):
                donusen = [deger]
            else:
                donusen = list(deger)
        elif beklenen_tip == "dict":
            if isinstance(deger, str):
                donusen = json.loads(deger)
            else:
                return False, None, f"'{type(deger).__name__}' -> dict dönüşümü başarısız"
        else:
            return False, None, f"'{type(deger).__name__}' -> {beklenen_tip} dönüşümü desteklenmiyor"
        return True, donusen, f"'{type(deger).__name__}' -> {beklenen_tip} dönüştürüldü"
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return False, None, f"Dönüşüm başarısız: {e}"


def _dogrula(veri, sema):
    """Veriyi şemaya göre doğrula."""
    if not isinstance(sema, dict):
        # Basit tip kontrolü
        basarili, donusen, mesaj = _tip_kontrol(veri, sema)
        if basarili:
            return {"basarili": True, "veri": donusen, "uyarilar": [mesaj] if mesaj else []}
        return {"basarili": False, "hata": mesaj}
    
    hatalar = []
    uyarilar = []
    sonuc = {}
    
    for alan, alan_sema in sema.items():
        if alan not in veri:
            zorunlu = alan_sema.get("zorunlu", True) if isinstance(alan_sema, dict) else True
            if zorunlu:
                hatalar.append(f"Eksik alan: {alan}")
            continue
        
        deger = veri[alan]
        
        if isinstance(alan_sema, dict):
            beklenen_tip = alan_sema.get("tip", "any")
            basarili, donusen, mesaj = _tip_kontrol(deger, beklenen_tip)
            if not basarili:
                hatalar.append(f"{alan}: {mesaj}")
                continue
            if mesaj:
                uyarilar.append(f"{alan}: {mesaj}")
            
            # Alt şema kontrolü
            alt_sema = alan_sema.get("ozellikler")
            if alt_sema and isinstance(donusen, dict):
                alt_sonuc = _dogrula(donusen, alt_sema)
                if not alt_sonuc["basarili"]:
                    hatalar.extend([f"{alan}.{h}" for h in alt_sonuc.get("hatalar", [])])
            
            sonuc[alan] = donusen
        else:
            basarili, donusen, mesaj = _tip_kontrol(deger, alan_sema)
            if not basarili:
                hatalar.append(f"{alan}: {mesaj}")
                continue
            if mesaj:
                uyarilar.append(f"{alan}: {mesaj}")
            sonuc[alan] = donusen
    
    if hatalar:
        return {"basarili": False, "hatalar": hatalar, "uyarilar": uyarilar}
    return {"basarili": True, "veri": sonuc, "uyarilar": uyarilar}


def _temizle(veri, sema):
    """Veriyi şemaya göre temizle (gereksiz alanları kaldır)."""
    if not isinstance(sema, dict):
        basarili, donusen, _ = _tip_kontrol(veri, sema)
        return donusen if basarili else veri
    
    sonuc = {}
    for alan, alan_sema in sema.items():
        if alan in veri:
            deger = veri[alan]
            if isinstance(alan_sema, dict):
                beklenen_tip = alan_sema.get("tip", "any")
                basarili, donusen, _ = _tip_kontrol(deger, beklenen_tip)
                if basarili:
                    alt_sema = alan_sema.get("ozellikler")
                    if alt_sema and isinstance(donusen, dict):
                        sonuc[alan] = _temizle(donusen, alt_sema)
                    else:
                        sonuc[alan] = donusen
            else:
                basarili, donusen, _ = _tip_kontrol(deger, alan_sema)
                if basarili:
                    sonuc[alan] = donusen
    return sonuc


def _donustur(veri, sema):
    """Veriyi şemaya göre dönüştür (tip dönüşümü yap)."""
    sonuc = _dogrula(veri, sema)
    if sonuc["basarili"]:
        return sonuc
    # Hatalı alanları dönüştürmeyi dene
    duzeltilmis = {}
    for alan, deger in veri.items():
        if alan in sema:
            alan_sema = sema[alan]
            beklenen_tip = alan_sema.get("tip", "any") if isinstance(alan_sema, dict) else alan_sema
            basarili, donusen, _ = _tip_kontrol(deger, beklenen_tip)
            duzeltilmis[alan] = donusen if basarili else deger
        else:
            duzeltilmis[alan] = deger
    return _dogrula(duzeltilmis, sema)


def run(islem="dogrula", veri="{}", sema="{}"):
    """
    JSON şema doğrulayıcı.
    
    Parametreler:
        islem (str): dogrula / temizle / donustur
        veri (str): Doğrulanacak JSON verisi
        sema (str): Şema tanımı (JSON)
    
    Returns:
        str: Doğrulama sonucu JSON formatında
    """
    try:
        # String'leri parse et
        if isinstance(veri, str):
            try:
                veri = json.loads(veri)
            except json.JSONDecodeError:
                # Düz string olabilir
                logger.warning("[fix_01_sessiz_except] JSONDecodeError")
        if isinstance(sema, str):
            try:
                sema = json.loads(sema)
            except json.JSONDecodeError:
                sema = "str"  # Varsayılan

        if islem == "dogrula":
            sonuc = _dogrula(veri, sema)
        elif islem == "temizle":
            temiz = _temizle(veri, sema)
            sonuc = {"basarili": True, "veri": temiz}
        elif islem == "donustur":
            sonuc = _donustur(veri, sema)
        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        sonuc["durum"] = "basarili" if sonuc.get("basarili") else "hata"
        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    sema = '{"adi": {"tip": "str"}, "yas": {"tip": "int"}, "aktif": {"tip": "bool"}}'
    veri = '{"adi": "Ahmet", "yas": "25", "aktif": "true"}'
    print(run("dogrula", veri, sema))
    print(run("donustur", veri, sema))
