#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool_output_limits.py — Tool çıktı limitleri.
Çıktı boyutu kontrolü, kesme, format.
"""

import json


def _kontrol(icerik, max_boyut=50000):
    """İçerik boyutunu kontrol et."""
    if icerik is None:
        icerik = ""
    if not isinstance(icerik, str):
        icerik = str(icerik)
    
    boyut = len(icerik)
    asim = boyut - max_boyut
    oran = round(boyut / max_boyut * 100, 1) if max_boyut > 0 else 100
    
    return {
        "durum": "basarili",
        "boyut": boyut,
        "max_boyut": max_boyut,
        "asim_mi": boyut > max_boyut,
        "asim_miktari": max(0, asim),
        "kullanim_orani": min(oran, 100),
        "guvenli_mi": boyut <= max_boyut
    }


def _kes(icerik, max_boyut=50000, kesme_str="\n...[KESILDI]"):
    """İçeriği belirtilen boyuta kadar kes."""
    if icerik is None:
        icerik = ""
    if not isinstance(icerik, str):
        icerik = str(icerik)
    
    if len(icerik) <= max_boyut:
        return {
            "durum": "basarili",
            "icerik": icerik,
            "kesildi_mi": False,
            "orijinal_boyut": len(icerik),
            "yeni_boyut": len(icerik)
        }
    
    kesilmis = icerik[:max_boyut - len(kesme_str)] + kesme_str
    return {
        "durum": "basarili",
        "icerik": kesilmis,
        "kesildi_mi": True,
        "orijinal_boyut": len(icerik),
        "yeni_boyut": len(kesilmis),
        "kayip_miktar": len(icerik) - len(kesilmis)
    }


def _formatla(icerik, max_boyut=50000):
    """İçeriği kontrol et ve gerekirse kes."""
    kontrol = _kontrol(icerik, max_boyut)
    if kontrol["guvenli_mi"]:
        return {
            "durum": "basarili",
            "icerik": icerik if isinstance(icerik, str) else str(icerik),
            "guvenli_mi": True,
            "boyut": kontrol["boyut"],
            "max_boyut": max_boyut
        }
    
    kesilmis = _kes(icerik, max_boyut)
    return {
        "durum": "basarili",
        "icerik": kesilmis["icerik"],
        "guvenli_mi": False,
        "boyut": kontrol["boyut"],
        "max_boyut": max_boyut,
        "kesme_bilgisi": {
            "orijinal_boyut": kesilmis["orijinal_boyut"],
            "yeni_boyut": kesilmis["yeni_boyut"],
            "kayip_miktar": kesilmis["kayip_miktar"]
        }
    }


def run(islem="kontrol", icerik="", max_boyut=50000):
    """
    Tool çıktı limitleri.
    
    Parametreler:
        islem (str): kontrol / kes / formatla
        icerik (str): Kontrol edilecek içerik
        max_boyut (int): Maksimum boyut (karakter)
    
    Returns:
        str: Limit kontrol sonucu JSON formatında
    """
    try:
        max_boyut = int(max_boyut)
        if max_boyut <= 0:
            return json.dumps({"durum": "hata", "mesaj": "max_boyut pozitif olmalı"}, ensure_ascii=False)

        if islem == "kontrol":
            sonuc = _kontrol(icerik, max_boyut)

        elif islem == "kes":
            sonuc = _kes(icerik, max_boyut)

        elif islem == "formatla":
            sonuc = _formatla(icerik, max_boyut)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("kontrol", "Kısa metin", 50000))
    print(run("kes", "Uzun metin " * 1000, 100))
    print(run("formatla", "Test " * 100, 50))
