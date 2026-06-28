#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
registry.py — Genel kayıt defteri.
Servis, eylem, callback kaydı. ToolRegistry'in tamamlayıcısı.
"""

import importlib
import json
import time
import threading
from pathlib import Path
from typing import List
import logging
logger = logging.getLogger(__name__)


_kayitlar = {"servis": {}, "eylem": {}, "callback": {}}
_kayit_kilit = threading.Lock()


def _kaydet(tur, ad, deger):
    """Bir kaydı ekle/güncelle."""
    with _kayit_kilit:
        if tur not in _kayitlar:
            _kayitlar[tur] = {}
        _kayitlar[tur][ad] = {
            "deger": deger,
            "kayit_zamani": time.time(),
            "tur": tur
        }
    return {"durum": "basarili", "mesaj": f"'{tur}/{ad}' kaydedildi"}


def _sil(tur, ad):
    """Bir kaydı sil."""
    with _kayit_kilit:
        if tur in _kayitlar and ad in _kayitlar[tur]:
            del _kayitlar[tur][ad]
            return {"durum": "basarili", "mesaj": f"'{tur}/{ad}' silindi"}
        return {"durum": "hata", "mesaj": f"'{tur}/{ad}' bulunamadı"}


def _listele(tur=None):
    """Kayıtları listele."""
    with _kayit_kilit:
        if tur:
            if tur not in _kayitlar:
                return {"durum": "basarili", "kayitlar": [], "sayi": 0, "tur": tur}
            liste = [{"ad": k, **v} for k, v in _kayitlar[tur].items()]
            return {"durum": "basarili", "kayitlar": liste, "sayi": len(liste), "tur": tur}
        else:
            toplam = {}
            toplam_sayi = 0
            for t, kayit in _kayitlar.items():
                toplam[t] = {k: v for k, v in kayit.items()}
                toplam_sayi += len(kayit)
            return {"durum": "basarili", "kayitlar": toplam, "sayi": toplam_sayi}


def _ara(anahtar):
    """Kayıtlarda ara."""
    with _kayit_kilit:
        sonuclar = []
        for tur, kayit in _kayitlar.items():
            for ad, deger in kayit.items():
                if anahtar.lower() in ad.lower() or anahtar.lower() in str(deger.get("deger", "")).lower():
                    sonuclar.append({"tur": tur, "ad": ad, **deger})
        return {"durum": "basarili", "sonuclar": sonuclar, "sayi": len(sonuclar)}


def run(islem="listele", tur="", ad="", deger=""):
    """
    Genel kayıt defteri.
    
    Parametreler:
        islem (str): kaydet / sil / listele / ara
        tur (str): Kayıt türü (servis / eylem / callback)
        ad (str): Kayıt adı
        deger (str): Kayıt değeri (JSON string olabilir)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not tur or not ad:
                return json.dumps({"durum": "hata", "mesaj": "tur ve ad parametreleri gerekli"}, ensure_ascii=False)
            try:
                deger_parsed = json.loads(deger) if deger and deger.startswith(('{', '[')) else deger
            except (json.JSONDecodeError, ValueError):
                deger_parsed = deger
            sonuc = _kaydet(tur, ad, deger_parsed)

        elif islem == "sil":
            if not tur or not ad:
                return json.dumps({"durum": "hata", "mesaj": "tur ve ad parametreleri gerekli"}, ensure_ascii=False)
            sonuc = _sil(tur, ad)

        elif islem == "listele":
            sonuc = _listele(tur if tur else None)

        elif islem == "ara":
            if not ad:
                return json.dumps({"durum": "hata", "mesaj": "ad (aranacak) parametresi gerekli"}, ensure_ascii=False)
            sonuc = _ara(ad)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# --- ReYMeN ToolRegistry uyumluluğu ---

class ToolRegistry:
    """ReYMeN tool kaydı için uyumlu sınıf."""

    def __init__(self):
        self._tools = {}

    def register(self, name, handler=None, schema=None, toolset=None, **kwargs):
        """Araç kaydet."""
        self._tools[name] = {"handler": handler, "schema": schema, "toolset": toolset, **kwargs}

    def get(self, name):
        return self._tools.get(name)

    def list_tools(self, toolset=None):
        if toolset:
            return [k for k, v in self._tools.items() if v.get("toolset") == toolset]
        return list(self._tools.keys())

    def __contains__(self, name):
        return name in self._tools

    def get_definitions(self):
        """Tool definition'larini dict olarak dondur (model_tools.py icin)."""
        return {name: info.get("schema", {}) for name, info in self._tools.items()}

    def get_tool_to_toolset_map(self) -> dict:
        """Her tool adi -> toolset eslemesini dondur."""
        return {name: info.get("toolset", "default") for name, info in self._tools.items()}

    def get_toolset_requirements(self) -> dict:
        """Her toolset icin gereksinimleri dondur (opsiyonel)."""
        return {}


def tool_error(message, success=False):
    """Tool hata mesaji formatla (ReYMeN uyumlulugu)."""
    return json.dumps({"success": success, "error": message}, ensure_ascii=False)


def tool_result(data, success=True):
    """Tool başarılı sonuç formatla (ReYMeN uyumluluğu)."""
    if isinstance(data, str):
        return data
    result = dict(data) if data else {}
    result.setdefault("success", success)
    return json.dumps(result, ensure_ascii=False)


registry = ToolRegistry()
# --- ReYMeN ToolRegistry uyumluluğu sonu ---


def discover_builtin_tools(tools_dir=None) -> List[str]:
    """Scan the tools/ directory, import each .py file (except __init__.py,
    registry.py, mcp_tool.py), and return a list of imported module names.

    Args:
        tools_dir: Optional path to the tools directory. If None, uses the
                   directory containing this file (registry.py).

    Returns:
        List[str]: Names of successfully imported tool modules.
    """
    if tools_dir is None:
        tools_dir = Path(__file__).resolve().parent

    tools_path = Path(tools_dir).resolve()
    imported = []

    for py_file in sorted(tools_path.glob("*.py")):
        name = py_file.stem
        # Skip special files
        if name in ("__init__", "registry", "mcp_tool"):
            continue

        mod_name = f"tools.{name}"
        try:
            importlib.import_module(mod_name)
            imported.append(mod_name)
        except Exception:
            pass  # Silently skip modules that fail to import

    return imported


if __name__ == "__main__":
    print(run("kaydet", "servis", "test_servis", '{"url": "http://test"}'))
    print(run("listele"))
    print(run("ara", ad="test"))
    print(run("sil", "servis", "test_servis"))
