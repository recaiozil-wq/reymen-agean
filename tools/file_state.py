#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file_state.py — Dosya durum izleyici.
Dosya boyutu, değişiklik zamanı, hash, lock durumu.
"""

import os
import json
import hashlib
import time
from datetime import datetime


def _dosya_hash(dosya_yolu, algoritma="sha256"):
    """Dosyanın hash değerini hesapla."""
    try:
        h = hashlib.new(algoritma)
        with open(dosya_yolu, 'rb') as f:
            for blok in iter(lambda: f.read(65536), b''):
                h.update(blok)
        return h.hexdigest()
    except Exception:
        return None


def _dosya_bilgisi(dosya_yolu):
    """Dosya hakkında detaylı bilgi döndür."""
    try:
        stat = os.stat(dosya_yolu)
        return {
            "boyut": stat.st_size,
            "boyut_str": _boyut_format(stat.st_size),
            "olusturma": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "degistirme": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "erisim": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "mod": oct(stat.st_mode),
            "dizin_mi": os.path.isdir(dosya_yolu),
            "okunabilir_mi": os.access(dosya_yolu, os.R_OK),
            "yazilabilir_mi": os.access(dosya_yolu, os.W_OK),
            "calistirilabilir_mi": os.access(dosya_yolu, os.X_OK),
            "hash_sha256": _dosya_hash(dosya_yolu, "sha256")
        }
    except Exception as e:
        return {"hata": str(e)}


def _boyut_format(bayt):
    """Bayt değerini insan okunabilir formata çevir."""
    for birim in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bayt < 1024:
            return f"{bayt:.2f} {birim}"
        bayt /= 1024
    return f"{bayt:.2f} PB"


def _kilit_kontrol(dosya_yolu):
    """Dosyanın kilitli olup olmadığını kontrol et."""
    try:
        if not os.path.exists(dosya_yolu):
            return {"kilitli": False, "mesaj": "Dosya mevcut değil"}
        if os.name == 'nt':
            try:
                with open(dosya_yolu, 'r+b') as f:
                    import msvcrt
                    try:
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                        return {"kilitli": False, "mesaj": "Kilitli değil (erişilebilir)"}
                    except (IOError, OSError):
                        return {"kilitli": True, "mesaj": "Kilitli (başka bir işlem tarafından)"}
            except (IOError, OSError):
                return {"kilitli": True, "mesaj": "Kilitli (erişilemez)"}
        else:
            return {"kilitli": False, "mesaj": "Unix'te kilit kontrolü sınırlı"}
    except Exception as e:
        return {"kilitli": None, "mesaj": str(e)}


def _karsilastir(dosya1, dosya2):
    """İki dosyayı karşılaştır."""
    sonuc = {}
    for i, yol in enumerate([dosya1, dosya2]):
        sonuc[f"dosya_{i+1}"] = _dosya_bilgisi(yol) if os.path.exists(yol) else {"hata": "Dosya mevcut değil"}

    if os.path.exists(dosya1) and os.path.exists(dosya2):
        h1 = _dosya_hash(dosya1)
        h2 = _dosya_hash(dosya2)
        sonuc["ayni_mi"] = h1 == h2 if h1 and h2 else None
        sonuc["hash_eslesmesi"] = h1 == h2 if h1 and h2 else False
        s1 = os.path.getsize(dosya1)
        s2 = os.path.getsize(dosya2)
        sonuc["boyut_farki"] = s1 - s2

    return sonuc


def run(islem="kontrol", dosya_yolu=""):
    """
    Dosya durum izleyici.
    
    Parametreler:
        islem (str): kontrol / izle / karsilastir
        dosya_yolu (str): Kontrol edilecek dosya yolu.
            'karsilastir' işleminde virgülle ayrılmış iki yol: "yol1,yol2"
    
    Returns:
        str: Durum bilgisi JSON formatında
    """
    try:
        if islem == "kontrol":
            if not dosya_yolu:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu parametresi gerekli"}, ensure_ascii=False)
            if not os.path.exists(dosya_yolu):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
            bilgi = _dosya_bilgisi(dosya_yolu)
            bilgi["kilit"] = _kilit_kontrol(dosya_yolu)
            return json.dumps({"durum": "basarili", "dosya": dosya_yolu, "bilgi": bilgi}, ensure_ascii=False, default=str)

        elif islem == "izle":
            if not dosya_yolu:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu parametresi gerekli"}, ensure_ascii=False)
            if not os.path.exists(dosya_yolu):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
            ilk_hash = _dosya_hash(dosya_yolu)
            ilk_boyut = os.path.getsize(dosya_yolu)
            ilk_zaman = os.path.getmtime(dosya_yolu)
            return json.dumps({
                "durum": "basarili",
                "mesaj": "İzleme başlatıldı",
                "dosya": dosya_yolu,
                "ilk_hash": ilk_hash,
                "ilk_boyut": ilk_boyut,
                "ilk_degistirme": datetime.fromtimestamp(ilk_zaman).isoformat()
            }, ensure_ascii=False, default=str)

        elif islem == "karsilastir":
            if not dosya_yolu or ',' not in dosya_yolu:
                return json.dumps({"durum": "hata", "mesaj": "dosya_yolu 'dosya1,dosya2' formatında olmalı"}, ensure_ascii=False)
            yollar = [y.strip() for y in dosya_yolu.split(',', 1)]
            sonuc = _karsilastir(yollar[0], yollar[1])
            return json.dumps({"durum": "basarili", "karsilastirma": sonuc}, ensure_ascii=False, default=str)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("kontrol", __file__))
