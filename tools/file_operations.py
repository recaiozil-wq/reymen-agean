#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file_operations.py — Gelişmiş dosya işlemleri.
Kopyalama, taşıma, yeniden adlandırma, silme, izin değiştirme.
file_safety.py entegrasyonu.
"""

import os
import sys
import json
import shutil
import stat

try:
    from tools import file_safety
    SAFETY_VAR = True
except ImportError:
    SAFETY_VAR = False


def _guvenli_mi(kaynak, hedef=""):
    """file_safety entegrasyonu: güvenlik kontrolü."""
    if not SAFETY_VAR:
        return True, ""
    try:
        if hasattr(file_safety, 'guvenli_mi'):
            return file_safety.guvenli_mi(kaynak, hedef)
        return True, ""
    except Exception:
        return True, ""


def _kopyala(kaynak, hedef):
    """Dosya veya dizin kopyala."""
    guvenli, mesaj = _guvenli_mi(kaynak, hedef)
    if not guvenli:
        return {"durum": "hata", "mesaj": f"Güvenlik engeli: {mesaj}"}

    try:
        if os.path.isdir(kaynak):
            shutil.copytree(kaynak, hedef, dirs_exist_ok=True)
        else:
            hedef_dir = os.path.dirname(hedef)
            if hedef_dir:
                os.makedirs(hedef_dir, exist_ok=True)
            shutil.copy2(kaynak, hedef)
        return {"durum": "basarili", "mesaj": f"'{kaynak}' -> '{hedef}' kopyalandı"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _tasi(kaynak, hedef):
    """Dosya veya dizin taşı."""
    guvenli, mesaj = _guvenli_mi(kaynak, hedef)
    if not guvenli:
        return {"durum": "hata", "mesaj": f"Güvenlik engeli: {mesaj}"}

    try:
        hedef_dir = os.path.dirname(hedef)
        if hedef_dir:
            os.makedirs(hedef_dir, exist_ok=True)
        shutil.move(kaynak, hedef)
        return {"durum": "basarili", "mesaj": f"'{kaynak}' -> '{hedef}' taşındı"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _sil(dosya_yolu):
    """Dosya veya dizin sil."""
    guvenli, mesaj = _guvenli_mi(dosya_yolu, "")
    if not guvenli:
        return {"durum": "hata", "mesaj": f"Güvenlik engeli: {mesaj}"}

    try:
        if os.path.isdir(dosya_yolu):
            shutil.rmtree(dosya_yolu)
        else:
            os.remove(dosya_yolu)
        return {"durum": "basarili", "mesaj": f"'{dosya_yolu}' silindi"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _yeniden_adlandir(kaynak, hedef):
    """Dosya yeniden adlandır."""
    guvenli, mesaj = _guvenli_mi(kaynak, hedef)
    if not guvenli:
        return {"durum": "hata", "mesaj": f"Güvenlik engeli: {mesaj}"}

    try:
        os.rename(kaynak, hedef)
        return {"durum": "basarili", "mesaj": f"'{kaynak}' -> '{hedef}' yeniden adlandırıldı"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _izin_degistir(dosya_yolu, mod):
    """Dosya izinlerini değiştir (Unix). Windows'ta no-op."""
    guvenli, mesaj = _guvenli_mi(dosya_yolu, "")
    if not guvenli:
        return {"durum": "hata", "mesaj": f"Güvenlik engeli: {mesaj}"}

    try:
        if os.name == 'nt':
            return {"durum": "basarili", "mesaj": f"Windows'ta izin değişikliği atlandı: {dosya_yolu}"}
        if isinstance(mod, str):
            mod = int(mod, 8)
        os.chmod(dosya_yolu, stat.S_IMODE(mod))
        return {"durum": "basarili", "mesaj": f"'{dosya_yolu}' izni {oct(mod)} olarak değiştirildi"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def run(islem="kopyala", kaynak="", hedef=""):
    """
    Gelişmiş dosya işlemleri.
    
    Parametreler:
        islem (str): kopyala / tasi / sil / yeniden_adlandir / izin
        kaynak (str): Kaynak dosya/dizin yolu
        hedef (str): Hedef dosya/dizin yolu (sil işleminde kullanılmaz)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kopyala":
            if not kaynak or not hedef:
                return json.dumps({"durum": "hata", "mesaj": "kaynak ve hedef parametreleri gerekli"}, ensure_ascii=False)
            if not os.path.exists(kaynak):
                return json.dumps({"durum": "hata", "mesaj": f"Kaynak bulunamadı: {kaynak}"}, ensure_ascii=False)
            sonuc = _kopyala(kaynak, hedef)

        elif islem == "tasi":
            if not kaynak or not hedef:
                return json.dumps({"durum": "hata", "mesaj": "kaynak ve hedef parametreleri gerekli"}, ensure_ascii=False)
            if not os.path.exists(kaynak):
                return json.dumps({"durum": "hata", "mesaj": f"Kaynak bulunamadı: {kaynak}"}, ensure_ascii=False)
            sonuc = _tasi(kaynak, hedef)

        elif islem == "sil":
            if not kaynak:
                return json.dumps({"durum": "hata", "mesaj": "kaynak parametresi gerekli"}, ensure_ascii=False)
            if not os.path.exists(kaynak):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {kaynak}"}, ensure_ascii=False)
            sonuc = _sil(kaynak)

        elif islem == "yeniden_adlandir":
            if not kaynak or not hedef:
                return json.dumps({"durum": "hata", "mesaj": "kaynak ve hedef parametreleri gerekli"}, ensure_ascii=False)
            if not os.path.exists(kaynak):
                return json.dumps({"durum": "hata", "mesaj": f"Kaynak bulunamadı: {kaynak}"}, ensure_ascii=False)
            sonuc = _yeniden_adlandir(kaynak, hedef)

        elif islem == "izin":
            if not kaynak:
                return json.dumps({"durum": "hata", "mesaj": "kaynak parametresi gerekli"}, ensure_ascii=False)
            if not os.path.exists(kaynak):
                return json.dumps({"durum": "hata", "mesaj": f"Dosya bulunamadı: {kaynak}"}, ensure_ascii=False)
            mod = hedef if hedef else "644"
            sonuc = _izin_degistir(kaynak, mod)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("list"))
