#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
credential_files.py — Kimlik dosyası yönetimi.
API anahtarlarını güvenli JSON dosyasında saklama.
"""

import os
import json
from contextvars import ContextVar
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


CREDENTIAL_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'credentials.json')


def _cred_yolu():
    return CREDENTIAL_DOSYASI


def _cred_oku():
    """Credentials dosyasını oku."""
    yol = _cred_yolu()
    if not os.path.exists(yol):
        return {}
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def _cred_yaz(veri):
    """Credentials dosyasına yaz."""
    yol = _cred_yolu()
    try:
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        # Sadece Unix'te izinleri kısıtla
        try:
            os.chmod(yol, 0o600)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return True
    except Exception:
        return False


def _kaydet(servis, anahtar, deger):
    """Bir servis için kimlik bilgisi kaydet."""
    veri = _cred_oku()
    if servis not in veri:
        veri[servis] = {}
    veri[servis][anahtar] = deger
    if _cred_yaz(veri):
        return {"durum": "basarili", "mesaj": f"'{servis}/{anahtar}' kaydedildi"}
    return {"durum": "hata", "mesaj": "Credentials dosyası yazılamadı"}


def _oku(servis, anahtar):
    """Bir servis için kimlik bilgisi oku."""
    veri = _cred_oku()
    if servis not in veri:
        return {"durum": "hata", "mesaj": f"Servis bulunamadı: {servis}"}
    if anahtar not in veri[servis]:
        return {"durum": "hata", "mesaj": f"Anahtar bulunamadı: {servis}/{anahtar}"}
    return {"durum": "basarili", "servis": servis, "anahtar": anahtar, "deger": veri[servis][anahtar]}


def _sil(servis, anahtar=None):
    """Bir servis/anahtar kimlik bilgisini sil."""
    veri = _cred_oku()
    if servis not in veri:
        return {"durum": "hata", "mesaj": f"Servis bulunamadı: {servis}"}
    if anahtar is None:
        del veri[servis]
        mesaj = f"Tüm '{servis}' bilgileri silindi"
    else:
        if anahtar not in veri[servis]:
            return {"durum": "hata", "mesaj": f"Anahtar bulunamadı: {servis}/{anahtar}"}
        del veri[servis][anahtar]
        mesaj = f"'{servis}/{anahtar}' silindi"
    if _cred_yaz(veri):
        return {"durum": "basarili", "mesaj": mesaj}
    return {"durum": "hata", "mesaj": "Credentials dosyası yazılamadı"}


def _listele():
    """Tüm servisleri ve anahtarları listele (değerleri gizle)."""
    veri = _cred_oku()
    liste = {}
    for servis, anahtarlar in veri.items():
        liste[servis] = {k: "***" for k in anahtarlar}
    return {"durum": "basarili", "servisler": liste, "sayi": len(liste)}


def run(islem="listele", servis="", anahtar="", deger=""):
    """
    Kimlik dosyası yönetimi.
    
    Parametreler:
        islem (str): kaydet / oku / sil / listele
        servis (str): Servis adı (örn: openai, github)
        anahtar (str): Anahtar adı (örn: api_key, secret)
        deger (str): Değer (sadece kaydet işleminde)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not servis or not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "servis ve anahtar parametreleri gerekli"}, ensure_ascii=False)
            sonuc = _kaydet(servis, anahtar, deger)

        elif islem == "oku":
            if not servis or not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "servis ve anahtar parametreleri gerekli"}, ensure_ascii=False)
            sonuc = _oku(servis, anahtar)

        elif islem == "sil":
            if not servis:
                return json.dumps({"durum": "hata", "mesaj": "servis parametresi gerekli"}, ensure_ascii=False)
            sonuc = _sil(servis, anahtar if anahtar else None)

        elif islem == "listele":
            sonuc = _listele()

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# ReYMeN referans API — ContextVar tabanli kimlik dosyasi yonetimi
# ---------------------------------------------------------------------------

# ContextVar: copy_context() ile is parcaciklarina kopyalanir
_registered_cv: ContextVar[dict] = ContextVar("credential_files_registered", default=None)


def _resolve_ReYMeN_home() -> Path:
    """ReYMeN ev dizinini dondur."""
    home = os.environ.get("ReYMeN_HOME", str(Path.home() / ".ReYMeN"))
    return Path(home)


def _get_registered() -> dict:
    """Kayitli kimlik dosyalarini dondur {dosya_adi: tam_yol}."""
    v = _registered_cv.get()
    return dict(v) if v is not None else {}


def register_credential_file(path: str) -> None:
    """Bir kimlik dosyasini kaydeder (ContextVar'a yazar).

    Args:
        path: ReYMeN ev dizinine goreceli dosya yolu (ornek: credentials/token.json)
    """
    current = _get_registered()
    key = os.path.basename(path)
    full = str(_resolve_ReYMeN_home() / path)
    current[key] = full
    _registered_cv.set(current)


def clear_credential_files() -> None:
    """Tum kayitli kimlik dosyalarini temizle."""
    _registered_cv.set({})


def to_agent_visible_cache_path(path: str) -> str:
    """Kimlik dosyasi yolunu ajan gorunur tam yola donustur."""
    return str(_resolve_ReYMeN_home() / path)


if __name__ == "__main__":
    print(run("listele"))
