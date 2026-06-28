#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fuzzy_match.py — Bulanık eşleştirme.
Levenshtein mesafesi, kısmi eşleşme, en iyi N sonucu.
"""

import json


def _levenshtein(s1, s2):
    """Levenshtein mesafesini hesapla."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if len(s2) == 0:
        return len(s1)
    onceki = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        guncel = [i + 1]
        for j, c2 in enumerate(s2):
            ekle = onceki[j + 1] + 1
            sil = guncel[j] + 1
            degistir = onceki[j] + (c1 != c2)
            guncel.append(min(ekle, sil, degistir))
        onceki = guncel
    return onceki[-1]


def _benzerlik_orani(s1, s2):
    """İki string arasındaki benzerlik oranı (0-1)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    mesafe = _levenshtein(s1.lower(), s2.lower())
    max_uzunluk = max(len(s1), len(s2))
    if max_uzunluk == 0:
        return 1.0
    return 1 - (mesafe / max_uzunluk)


def _kismi_eslesme(sorgu, hedef):
    """Kısmi eşleşme skoru (hedef içinde sorgu geçiyor mu)."""
    sorgu_lower = sorgu.lower()
    hedef_lower = hedef.lower()
    if sorgu_lower in hedef_lower:
        return 1.0
    # Alt dize benzerliği
    for i in range(len(sorgu_lower)):
        for j in range(i + 1, len(sorgu_lower) + 1):
            alt = sorgu_lower[i:j]
            if len(alt) >= 3 and alt in hedef_lower:
                return 0.7 + (len(alt) / len(sorgu)) * 0.3
    return _benzerlik_orani(sorgu, hedef)


def _en_iyi_n(sorgu, hedefler, limit, esik):
    """En iyi N eşleşmeyi döndür."""
    sonuclar = []
    for hedef in hedefler:
        tam_skor = _benzerlik_orani(sorgu, hedef)
        kismi_skor = _kismi_eslesme(sorgu, hedef)
        skor = max(tam_skor, kismi_skor)
        if skor >= esik:
            sonuclar.append({
                "hedef": hedef,
                "skor": round(skor, 4),
                "levenshtein": _levenshtein(sorgu, hedef),
                "kismi_eslesme": kismi_skor > tam_skor
            })
    sonuclar.sort(key=lambda x: x["skor"], reverse=True)
    return sonuclar[:limit]


def run(sorgu="", hedefler=None, limit=5, esik=0.6):
    """
    Bulanık eşleştirme.
    
    Parametreler:
        sorgu (str): Aranacak metin
        hedefler (list): Hedef metin listesi
        limit (int): Döndürülecek maksimum sonuç sayısı
        esik (float): Minimum benzerlik eşiği (0-1)
    
    Returns:
        str: Eşleşme sonuçları JSON formatında
    """
    try:
        if not sorgu:
            return json.dumps({"durum": "hata", "mesaj": "sorgu parametresi gerekli"}, ensure_ascii=False)

        if hedefler is None:
            hedefler = []
        if isinstance(hedefler, str):
            try:
                hedefler = json.loads(hedefler)
            except json.JSONDecodeError:
                hedefler = [hedefler]
        if not isinstance(hedefler, list):
            hedefler = [hedefler]

        if not hedefler:
            return json.dumps({"durum": "hata", "mesaj": "hedefler listesi boş"}, ensure_ascii=False)

        esik = float(esik)
        limit = int(limit)

        sonuclar = _en_iyi_n(sorgu, hedefler, limit, esik)

        return json.dumps({
            "durum": "basarili",
            "sorgu": sorgu,
            "toplam_hedef": len(hedefler),
            "esik": esik,
            "limit": limit,
            "eslesme_sayisi": len(sonuclar),
            "sonuclar": sonuclar
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("merhaba", ["merhaba dunya", "hello world", "merhaba", "test"], limit=5, esik=0.5))
