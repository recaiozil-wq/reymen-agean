#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file_tools.py — Dosya araçları birleşik arayüz.
Okuma, yazma, arama, patch işlemleri.
"""

import os
import json
import re


def _oku(dosya_yolu):
    """Dosyayı oku, içeriğini döndür."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        return {"durum": "basarili", "icerik": icerik, "boyut": len(icerik)}
    except UnicodeDecodeError:
        try:
            with open(dosya_yolu, 'r', encoding='latin-1') as f:
                icerik = f.read()
            return {"durum": "basarili", "icerik": icerik, "boyut": len(icerik), "not": "latin-1 encoding kullanıldı"}
        except Exception as e:
            return {"durum": "hata", "mesaj": str(e)}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _yaz(dosya_yolu, icerik):
    """Dosyaya yaz."""
    try:
        dizin = os.path.dirname(dosya_yolu)
        if dizin:
            os.makedirs(dizin, exist_ok=True)
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(icerik)
        return {"durum": "basarili", "mesaj": f"'{dosya_yolu}' yazıldı", "boyut": len(icerik)}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _ara(dosya_yolu, desen):
    """Dosyada regex araması yap."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            satirlar = f.readlines()
        eslesmeler = []
        for i, satir in enumerate(satirlar, 1):
            for eslesme in re.finditer(desen, satir):
                eslesmeler.append({
                    "satir": i,
                    "konum": eslesme.start(),
                    "eslesen": eslesme.group(),
                    "icerik": satir.rstrip('\n')
                })
        return {"durum": "basarili", "eslesme_sayisi": len(eslesmeler), "eslesmeler": eslesmeler}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _patch(dosya_yolu, eski_metin, yeni_metin):
    """Dosyada find-and-replace yap."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        if eski_metin not in icerik:
            return {"durum": "hata", "mesaj": "Eski metin dosyada bulunamadı"}
        sayi = icerik.count(eski_metin)
        yeni_icerik = icerik.replace(eski_metin, yeni_metin)
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(yeni_icerik)
        return {"durum": "basarili", "degisiklik_sayisi": sayi, "mesaj": f"{sayi} değişiklik yapıldı"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def run(islem="oku", dosya_yolu="", icerik=""):
    """
    Dosya araçları birleşik arayüz.
    
    Parametreler:
        islem (str): oku / yaz / ara / patch
        dosya_yolu (str): İşlem yapılacak dosya
        icerik (str): Yazma işlemi için içerik.
            Patch işlemi için "ESKI::YENI" formatında.
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "oku":
            if not dosya_yolu:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu parametresi gerekli"}, ensure_ascii=False)
            if not os.path.exists(dosya_yolu):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
            sonuc = _oku(dosya_yolu)

        elif islem == "yaz":
            if not dosya_yolu:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu parametresi gerekli"}, ensure_ascii=False)
            sonuc = _yaz(dosya_yolu, icerik)

        elif islem == "ara":
            if not dosya_yolu or not icerik:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu ve icerik (desen) parametreleri gerekli"}, ensure_ascii=False)
            if not os.path.exists(dosya_yolu):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
            sonuc = _ara(dosya_yolu, icerik)

        elif islem == "patch":
            if not dosya_yolu or not icerik:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu ve icerik (eski::yeni) parametreleri gerekli"}, ensure_ascii=False)
            if not os.path.exists(dosya_yolu):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
            if "::" not in icerik:
                return json.dumps({"durum": "hata", "mesaj": "icerik 'ESKI_METIN::YENI_METIN' formatında olmalı"}, ensure_ascii=False)
            eski, yeni = icerik.split("::", 1)
            sonuc = _patch(dosya_yolu, eski, yeni)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("oku", __file__))
