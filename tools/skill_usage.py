#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_usage.py — Skill kullanım istatistikleri.
Hangi skill ne sıklıkta kullanılıyor, başarı oranı.
"""

import os
import json
import time
from collections import defaultdict


USAGE_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skill_usage.json')


def _usage_oku():
    """Kullanım verisini oku."""
    if not os.path.exists(USAGE_DOSYASI):
        return {}
    try:
        with open(USAGE_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _usage_yaz(veri):
    """Kullanım verisini yaz."""
    try:
        with open(USAGE_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def _kaydet(skill_adi, basarili=True, sure=0.0):
    """Bir skill kullanımını kaydet."""
    veri = _usage_oku()
    if skill_adi not in veri:
        veri[skill_adi] = {
            "skill_adi": skill_adi,
            "toplam_kullanim": 0,
            "basarili_sayi": 0,
            "basarisiz_sayi": 0,
            "toplam_sure": 0.0,
            "ilk_kullanim": time.time(),
            "son_kullanim": time.time(),
            "kullanim_gecmisi": []
        }
    
    kayit = veri[skill_adi]
    kayit["toplam_kullanim"] += 1
    if basarili:
        kayit["basarili_sayi"] += 1
    else:
        kayit["basarisiz_sayi"] += 1
    kayit["toplam_sure"] += sure
    kayit["son_kullanim"] = time.time()
    
    # Son 100 kaydı tut
    kayit["kullanim_gecmisi"].append({
        "zaman": time.time(),
        "basarili": basarili,
        "sure": sure
    })
    if len(kayit["kullanim_gecmisi"]) > 100:
        kayit["kullanim_gecmisi"] = kayit["kullanim_gecmisi"][-100:]
    
    basari_orani = kayit["basarili_sayi"] / max(kayit["toplam_kullanim"], 1)
    kayit["basari_orani"] = round(basari_orani, 4)
    
    if _usage_yaz(veri):
        return {"durum": "basarili", "mesaj": f"'{skill_adi}' kullanımı kaydedildi"}
    return {"durum": "hata", "mesaj": "Usage dosyası yazılamadı"}


def _raporla(skill_adi=None):
    """Kullanım raporu üret."""
    veri = _usage_oku()
    if skill_adi:
        if skill_adi not in veri:
            return {"durum": "hata", "mesaj": f"'{skill_adi}' bulunamadı"}
        return {"durum": "basarili", "rapor": veri[skill_adi]}
    
    rapor = {
        "toplam_skill": len(veri),
        "genel_toplam": sum(v["toplam_kullanim"] for v in veri.values()),
        "genel_basari": sum(v["basarili_sayi"] for v in veri.values()),
        "skill_raporlari": list(veri.values())
    }
    # Başarı oranına göre sırala
    rapor["skill_raporlari"].sort(key=lambda x: x["basari_orani"], reverse=True)
    return {"durum": "basarili", "rapor": rapor}


def _istatistik(skill_adi=None):
    """Detaylı istatistik üret."""
    return _raporla(skill_adi)


def run(islem="raporla", skill_adi="", basarili=True):
    """
    Skill kullanım istatistikleri.
    
    Parametreler:
        islem (str): kaydet / raporla / istatistik
        skill_adi (str): Skill adı
        basarili (bool): İşlem başarılı mı
    
    Returns:
        str: İstatistik sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not skill_adi:
                return json.dumps({"durum": "hata", "mesaj": "skill_adi parametresi gerekli"}, ensure_ascii=False)
            sonuc = _kaydet(skill_adi, bool(basarili))

        elif islem == "raporla":
            sonuc = _raporla(skill_adi if skill_adi else None)

        elif islem == "istatistik":
            sonuc = _istatistik(skill_adi if skill_adi else None)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("kaydet", "test_skill", True))
    print(run("raporla"))
