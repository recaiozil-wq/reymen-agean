#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process_registry.py — Süreç kayıt defteri.
Arka plan süreçlerini takip etme, PID yönetimi, durum kontrolü.
"""

import json
import os
import time
import threading


_surecler = {}
_surec_kilit = threading.Lock()


def _kaydet(ad, pid, metadata=None):
    """Bir süreci kaydet."""
    with _surec_kilit:
        _surecler[ad] = {
            "pid": pid,
            "ad": ad,
            "baslangic": time.time(),
            "durum": "calisiyor",
            "metadata": metadata or {}
        }
    return {"durum": "basarili", "mesaj": f"Süreç kaydedildi: {ad} (PID: {pid})"}


def _sil(ad):
    """Bir süreç kaydını sil."""
    with _surec_kilit:
        if ad in _surecler:
            del _surecler[ad]
            return {"durum": "basarili", "mesaj": f"Süreç silindi: {ad}"}
        return {"durum": "hata", "mesaj": f"Süreç bulunamadı: {ad}"}


def _listele():
    """Tüm kayıtlı süreçleri listele."""
    with _surec_kilit:
        liste = []
        for ad, bilgi in sorted(_surecler.items()):
            item = dict(bilgi)
            item["gecen_sure"] = round(time.time() - bilgi["baslangic"], 2)
            liste.append(item)
        return {"durum": "basarili", "surecler": liste, "sayi": len(liste)}


def _durum(ad):
    """Bir sürecin durumunu kontrol et."""
    with _surec_kilit:
        if ad not in _surecler:
            return {"durum": "hata", "mesaj": f"Süreç bulunamadı: {ad}"}
        bilgi = _surecler[ad]
        pid = bilgi["pid"]
        # PID hala çalışıyor mu?
        pid_aktif = _pid_kontrol(pid)
        sonuc = dict(bilgi)
        sonuc["pid_aktif"] = pid_aktif
        sonuc["gecen_sure"] = round(time.time() - bilgi["baslangic"], 2)
        if not pid_aktif:
            sonuc["durum"] = "sonlandi"
        return {"durum": "basarili", "surec": sonuc}


def _pid_kontrol(pid):
    """PID'in çalışıp çalışmadığını kontrol et."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
    except Exception:
        # Windows'ta os.kill farklı çalışabilir
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            HANDLE = kernel32.OpenProcess(0x0400, False, pid)
            if HANDLE:
                kernel32.CloseHandle(HANDLE)
                return True
            return False
        except Exception:
            return None


def run(islem="listele", pid=None, ad=""):
    """
    Süreç kayıt defteri.
    
    Parametreler:
        islem (str): kaydet / sil / listele / durum
        pid (int): Süreç ID'si
        ad (str): Süreç adı
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not ad or pid is None:
                return json.dumps({"durum": "hata", "mesaj": "ad ve pid parametreleri gerekli"}, ensure_ascii=False)
            pid = int(pid)
            sonuc = _kaydet(ad, pid)

        elif islem == "sil":
            if not ad:
                return json.dumps({"durum": "hata", "mesaj": "ad parametresi gerekli"}, ensure_ascii=False)
            sonuc = _sil(ad)

        elif islem == "listele":
            sonuc = _listele()

        elif islem == "durum":
            if not ad:
                return json.dumps({"durum": "hata", "mesaj": "ad parametresi gerekli"}, ensure_ascii=False)
            sonuc = _durum(ad)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("listele"))
    print(run("kaydet", 12345, "test_process"))
    print(run("listele"))
    print(run("sil", ad="test_process"))



class _ProcessRegistry:
    """Singleton wrapper for process_registry — matches GatewayRunner API."""
    def has_active_for_session(self, session_key: str) -> bool:
        with _surec_kilit:
            return any(
                v.get("session_key") == session_key
                for v in _surecler.values()
                if isinstance(v, dict)
            )

    def kaydet(self, ad, pid, metadata=None):
        return _kaydet(ad, pid, metadata)

    def sil(self, ad):
        return _sil(ad)

    def listele(self):
        return _listele()


process_registry = _ProcessRegistry()
