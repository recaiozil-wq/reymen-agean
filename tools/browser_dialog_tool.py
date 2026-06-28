#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_dialog_tool.py — Tarayıcı dialog yönetimi.
JavaScript alert/confirm/prompt yakalama.
"""

import json
import time
import uuid


# Dialog kuyruğu (browser_tool.py ile entegre)
_bekleyen_dialoglar = {}
_dialog_cevaplari = {}


def _dialog_kaydet(dialog_id, dialog_turu, mesaj):
    """Bir dialogu kaydet."""
    _bekleyen_dialoglar[dialog_id] = {
        "id": dialog_id,
        "tur": dialog_turu,
        "mesaj": mesaj,
        "zaman": time.time(),
        "cevaplandi": False
    }
    return dialog_id


def _dialog_bekle(dialog_turu=None, timeout=30):
    """Bir dialogu bekle."""
    baslangic = time.time()
    while time.time() - baslangic < timeout:
        for dialog_id, dialog in list(_bekleyen_dialoglar.items()):
            if dialog["cevaplandi"]:
                continue
            if dialog_turu is None or dialog["tur"] == dialog_turu:
                return dialog
        time.sleep(0.1)
    return None


def _dialog_cevapla(dialog_id, cevap):
    """Bir dialogu cevapla."""
    if dialog_id in _bekleyen_dialoglar:
        _bekleyen_dialoglar[dialog_id]["cevaplandi"] = True
        _bekleyen_dialoglar[dialog_id]["cevap"] = cevap
        _dialog_cevaplari[dialog_id] = cevap
        return True
    return False


def _dialog_gec(dialog_id):
    """Bir dialogu geç/iptal et."""
    if dialog_id in _bekleyen_dialoglar:
        _bekleyen_dialoglar[dialog_id]["cevaplandi"] = True
        _bekleyen_dialoglar[dialog_id]["cevap"] = None
        _bekleyen_dialoglar[dialog_id]["gecildi"] = True
        return True
    return False


def run(islem="bekle", dialog_turu="", cevap=""):
    """
    Tarayıcı dialog yönetimi.
    
    Parametreler:
        islem (str): bekle / cevapla / gec
        dialog_turu (str): alert / confirm / prompt (bekle işleminde filtre)
        cevap (str): Dialog cevabı (cevapla işleminde)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "bekle":
            tur = dialog_turu if dialog_turu else None
            sure = 30
            dialog = _dialog_bekle(tur, sure)
            if dialog:
                return json.dumps({
                    "durum": "basarili",
                    "dialog": dialog,
                    "mesaj": f"{dialog['tur']} dialogu bulundu"
                }, ensure_ascii=False, default=str)
            else:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"{sure}s içinde dialog bulunamadı"
                }, ensure_ascii=False)

        elif islem == "cevapla":
            if not dialog_turu:
                return json.dumps({"durum": "hata", "mesaj": "dialog_turu (dialog ID) parametresi gerekli"}, ensure_ascii=False)
            dialog_id = dialog_turu
            if _dialog_cevapla(dialog_id, cevap):
                return json.dumps({
                    "durum": "basarili",
                    "mesaj": f"Dialog '{dialog_id}' cevaplandı"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Dialog bulunamadı: {dialog_id}"
                }, ensure_ascii=False)

        elif islem == "gec":
            if not dialog_turu:
                return json.dumps({"durum": "hata", "mesaj": "dialog_turu (dialog ID) parametresi gerekli"}, ensure_ascii=False)
            dialog_id = dialog_turu
            if _dialog_gec(dialog_id):
                return json.dumps({
                    "durum": "basarili",
                    "mesaj": f"Dialog '{dialog_id}' geçildi"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Dialog bulunamadı: {dialog_id}"
                }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    # Test
    print(run("bekle"))
