#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_provenance.py — Skill kaynak takibi.
Skill'lerin nereden geldiğini, hangi versiyonda olduğunu takip etme.
"""

import os
import json
import time
import hashlib


PROVENANCE_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skill_provenance.json')


def _prov_oku():
    """Provenance verisini oku."""
    if not os.path.exists(PROVENANCE_DOSYASI):
        return {}
    try:
        with open(PROVENANCE_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _prov_yaz(veri):
    """Provenance verisini yaz."""
    try:
        with open(PROVENANCE_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def _kaydet(skill_adi, kaynak="", versiyon="1.0.0", metadata=None):
    """Bir skill'in kaynağını kaydet."""
    veri = _prov_oku()
    veri[skill_adi] = {
        "skill_adi": skill_adi,
        "kaynak": kaynak,
        "versiyon": versiyon,
        "kayit_zamani": time.time(),
        "kayit_tarihi": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata or {},
        "hash": hashlib.sha256(skill_adi.encode()).hexdigest()[:12]
    }
    if _prov_yaz(veri):
        return {"durum": "basarili", "mesaj": f"'{skill_adi}' kaynağı kaydedildi"}
    return {"durum": "hata", "mesaj": "Provenance dosyası yazılamadı"}


def _kontrol(skill_adi):
    """Bir skill'in kaynağını kontrol et."""
    veri = _prov_oku()
    if skill_adi not in veri:
        return {"durum": "hata", "mesaj": f"'{skill_adi}' bulunamadı"}
    return {"durum": "basarili", "skill": veri[skill_adi]}


def _listele():
    """Tüm skill kaynaklarını listele."""
    veri = _prov_oku()
    liste = []
    for ad, bilgi in sorted(veri.items()):
        item = dict(bilgi)
        liste.append(item)
    return {"durum": "basarili", "skilller": liste, "sayi": len(liste)}


def run(islem="listele", skill_adi="", kaynak="", versiyon="1.0.0"):
    """
    Skill kaynak takibi.
    
    Parametreler:
        islem (str): kaydet / kontrol / listele
        skill_adi (str): Skill adı
        kaynak (str): Kaynak (örn: "github/user/repo", "local", "marketplace")
        versiyon (str): Versyon numarası
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not skill_adi:
                return json.dumps({"durum": "hata", "mesaj": "skill_adi parametresi gerekli"}, ensure_ascii=False)
            sonuc = _kaydet(skill_adi, kaynak, versiyon)

        elif islem == "kontrol":
            if not skill_adi:
                return json.dumps({"durum": "hata", "mesaj": "skill_adi parametresi gerekli"}, ensure_ascii=False)
            sonuc = _kontrol(skill_adi)

        elif islem == "listele":
            sonuc = _listele()

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# ReYMeN uyumluluk fonksiyonlari
_write_origin = None

def set_current_write_origin(origin: str) -> None:
    """ReYMeN uyumluluk: mevcut yazma kaynagini ayarla."""
    global _write_origin
    _write_origin = origin

def get_current_write_origin() -> str:
    """ReYMeN uyumluluk: mevcut yazma kaynagini getir."""
    return _write_origin


if __name__ == "__main__":
    print(run("kaydet", "test_skill", "local", "1.0.0"))
    print(run("listele"))
