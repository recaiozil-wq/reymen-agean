#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
env_passthrough.py — Ortam değişkeni yönetimi.
.env dosyasından değişken okuma, yazma, silme, listeleme.
Python ile çalışır (PowerShell tırnak sorunu yok).
"""

import os
import json

ENV_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')


def _env_yolu():
    """.env dosyasının tam yolunu döndür."""
    return ENV_DOSYASI


def _env_oku_sozluk():
    """.env dosyasını oku, sözlük döndür."""
    yol = _env_yolu()
    if not os.path.exists(yol):
        return {}
    sozluk = {}
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            for satir in f:
                satir = satir.strip()
                if not satir or satir.startswith('#'):
                    continue
                if '=' in satir:
                    anahtar, _, deger = satir.partition('=')
                    anahtar = anahtar.strip()
                    deger = deger.strip().strip('"').strip("'")
                    if anahtar:
                        sozluk[anahtar] = deger
    except Exception:
        return {}
    return sozluk


def _env_yaz_sozluk(sozluk):
    """Sözlüğü .env dosyasına yaz."""
    yol = _env_yolu()
    try:
        with open(yol, 'w', encoding='utf-8') as f:
            for anahtar, deger in sorted(sozluk.items()):
                f.write(f"{anahtar}={deger}\n")
        return True
    except Exception:
        return False


def run(islem="liste", anahtar="", deger=""):
    """
    Ortam değişkeni yönetimi.
    
    Parametreler:
        islem (str): oku / yaz / sil / liste
        anahtar (str): Değişken adı
        deger (str): Değişken değeri (sadece yaz işleminde)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        sozluk = _env_oku_sozluk()

        if islem == "oku":
            if not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "anahtar parametresi gerekli"}, ensure_ascii=False)
            if anahtar in sozluk:
                return json.dumps({"durum": "basarili", "anahtar": anahtar, "deger": sozluk[anahtar]}, ensure_ascii=False)
            else:
                return json.dumps({"durum": "hata", "mesaj": f"'{anahtar}' bulunamadı"}, ensure_ascii=False)

        elif islem == "yaz":
            if not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "anahtar parametresi gerekli"}, ensure_ascii=False)
            sozluk[anahtar] = deger
            if _env_yaz_sozluk(sozluk):
                return json.dumps({"durum": "basarili", "mesaj": f"'{anahtar}' yazıldı"}, ensure_ascii=False)
            else:
                return json.dumps({"durum": "hata", "mesaj": ".env yazılamadı"}, ensure_ascii=False)

        elif islem == "sil":
            if not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "anahtar parametresi gerekli"}, ensure_ascii=False)
            if anahtar in sozluk:
                del sozluk[anahtar]
                if _env_yaz_sozluk(sozluk):
                    return json.dumps({"durum": "basarili", "mesaj": f"'{anahtar}' silindi"}, ensure_ascii=False)
                else:
                    return json.dumps({"durum": "hata", "mesaj": ".env yazılamadı"}, ensure_ascii=False)
            else:
                return json.dumps({"durum": "hata", "mesaj": f"'{anahtar}' bulunamadı"}, ensure_ascii=False)

        elif islem == "liste":
            liste = [{"anahtar": k, "deger": v} for k, v in sorted(sozluk.items())]
            return json.dumps({"durum": "basarili", "degiskenler": liste, "sayi": len(liste)}, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# ReYMeN referans API — skill & config env-var passthrough
# ---------------------------------------------------------------------------

import logging as _logging

_pt_logger = _logging.getLogger(__name__)

# Skill tarafindan kayit edilen izin listesi (module-level, clear/register ile yonetilir)
_passthrough_keys: set = set()
# Config'den yuklenen izin listesi (None = henuz yuklenmedi)
_config_passthrough = None


def _get_blocklist() -> frozenset:
    """Provider kimlik bilgisi engel listesini don."""
    try:
        from tools.environments.local import _ReYMeN_PROVIDER_ENV_BLOCKLIST
        return _ReYMeN_PROVIDER_ENV_BLOCKLIST
    except (ImportError, AttributeError):
        return frozenset()


def _load_config_passthrough() -> list:
    """config.yaml'dan env_passthrough listesini yukle (bir kez)."""
    global _config_passthrough
    if _config_passthrough is not None:
        return _config_passthrough
    try:
        import yaml
        home = os.environ.get("ReYMeN_HOME", os.path.join(os.path.expanduser("~"), ".ReYMeN"))
        cfg_path = os.path.join(home, "config.yaml")
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as _f:
                cfg = yaml.safe_load(_f) or {}
            _config_passthrough = list(cfg.get("terminal", {}).get("env_passthrough", []))
        else:
            _config_passthrough = []
    except Exception:
        _config_passthrough = []
    return _config_passthrough


def register_env_passthrough(keys: list) -> None:
    """Verilecek env degisken adlarini passthrough listesine ekle.

    Provider kimlik bilgileri (ANTHROPIC_API_KEY vb.) sessizce reddedilir.
    """
    blocklist = _get_blocklist()
    for k in keys:
        k = k.strip()
        if not k:
            continue
        if k in blocklist:
            _pt_logger.warning("register_env_passthrough: %r reddedildi (saglayici bloklisti)", k)
            continue
        _passthrough_keys.add(k)


def clear_env_passthrough() -> None:
    """Skill tarafindan kayit edilen tum passthrough anahtarlarini temizle."""
    _passthrough_keys.clear()


def is_env_passthrough(key: str) -> bool:
    """Verilen env degiskeni passthrough listesinde mi? Blokliste karsi korunur."""
    blocklist = _get_blocklist()
    if key in blocklist:
        return False
    if key in _passthrough_keys:
        return True
    cfg_pt = _load_config_passthrough()
    return key in cfg_pt


def get_all_passthrough() -> set:
    """Skill + config'den turetilen tum passthrough anahtarlarini dondur."""
    blocklist = _get_blocklist()
    result = set(_passthrough_keys)
    for k in _load_config_passthrough():
        if k not in blocklist:
            result.add(k)
    return result


if __name__ == "__main__":
    print(run("liste"))
