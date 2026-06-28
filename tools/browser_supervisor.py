#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_supervisor.py — Tarayıcı denetleyici.
Çoklu sekme yönetimi, kaynak kullanımı, timeout.
"""

import json
import time
import uuid


_sekmeler = {}
_sekme_sayaci = {}


def _sektor_kaydet(url):
    """Yeni bir sekme kaydet."""
    sekme_id = str(uuid.uuid4())[:8]
    _sekmeler[sekme_id] = {
        "id": sekme_id,
        "url": url,
        "baslangic": time.time(),
        "durum": "acik",
        "son_aktivite": time.time(),
        "yuk_sayisi": 0
    }
    return sekme_id


def _sektor_kapat(sekme_id):
    """Bir sekmeyi kapat."""
    if sekme_id in _sekmeler:
        _sekmeler[sekme_id]["durum"] = "kapali"
        _sekmeler[sekme_id]["bitis"] = time.time()
        return True
    return False


def _sektor_listele():
    """Tüm sekmeleri listele."""
    liste = []
    for sekme_id, bilgi in sorted(_sekmeler.items()):
        item = dict(bilgi)
        if bilgi["durum"] == "acik":
            item["acik_kalma_suresi"] = round(time.time() - bilgi["baslangic"], 2)
        liste.append(item)
    return liste


def _durum():
    """Tarayıcı durumunu döndür."""
    toplam = len(_sekmeler)
    acik = sum(1 for s in _sekmeler.values() if s["durum"] == "acik")
    kapali = toplam - acik
    return {
        "toplam_sekme": toplam,
        "acik_sekme": acik,
        "kapali_sekme": kapali
    }


def run(islem="listele", url="", sekme_id=""):
    """
    Tarayıcı denetleyici.
    
    Parametreler:
        islem (str): ac / kapat / listele / durum
        url (str): Açılacak URL
        sekme_id (str): Sekme ID'si (kapat işleminde)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "ac":
            if not url:
                return json.dumps({"durum": "hata", "mesaj": "url parametresi gerekli"}, ensure_ascii=False)
            yeni_id = _sektor_kaydet(url)
            return json.dumps({
                "durum": "basarili",
                "sekme_id": yeni_id,
                "url": url,
                "mesaj": f"Sekme açıldı: {yeni_id}"
            }, ensure_ascii=False)

        elif islem == "kapat":
            if not sekme_id:
                return json.dumps({"durum": "hata", "mesaj": "sekme_id parametresi gerekli"}, ensure_ascii=False)
            if _sektor_kapat(sekme_id):
                return json.dumps({
                    "durum": "basarili",
                    "mesaj": f"Sekme kapatıldı: {sekme_id}"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Sekme bulunamadı: {sekme_id}"
                }, ensure_ascii=False)

        elif islem == "listele":
            sekmeler = _sektor_listele()
            return json.dumps({
                "durum": "basarili",
                "sekmeler": sekmeler,
                "sayi": len(sekmeler)
            }, ensure_ascii=False, default=str)

        elif islem == "durum":
            durum = _durum()
            return json.dumps({
                "durum": "basarili",
                "tarayici_durumu": durum
            }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("ac", "https://example.com"))
    print(run("listele"))
    print(run("durum"))
