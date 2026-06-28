#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interrupt.py — Döngü kesme mekanizması.
Sonsuz döngü tespiti, timeout yönetimi, kullanıcı iptali.
"""

import json
import time
import threading
import signal
import logging
logger = logging.getLogger(__name__)


_aktif_islemler = {}
_islem_kilit = threading.Lock()

# --- ReYMeN uyumlu thread-scoped interrupt API ---
_interrupted_threads: set = set()
_interrupt_lock = threading.Lock()


def is_interrupted() -> bool:
    """Mevcut thread için kesme sinyali var mı kontrol et."""
    tid = threading.current_thread().ident
    with _interrupt_lock:
        return tid in _interrupted_threads


def set_interrupt(active: bool, thread_id=None) -> None:
    """Thread için kesme sinyali ayarla veya temizle."""
    tid = thread_id if thread_id is not None else threading.current_thread().ident
    with _interrupt_lock:
        if active:
            _interrupted_threads.add(tid)
        else:
            _interrupted_threads.discard(tid)


def clear_interrupt(thread_id=None) -> None:
    """Thread kesme sinyalini temizle."""
    set_interrupt(False, thread_id)


class _ThreadAwareEventProxy:
    """threading.Event uyumlu proxy — eski kod tabanı için."""

    def is_set(self) -> bool:
        return is_interrupted()

    def set(self) -> None:
        set_interrupt(True)

    def clear(self) -> None:
        set_interrupt(False)


_interrupt_event = _ThreadAwareEventProxy()
# --- ReYMeN uyumlu API sonu ---


def _zamanlayici_baslat(islem_id, sure, callback=None):
    """Belirtilen süre sonra işlemi iptal et."""
    def _zaman_doldu():
        with _islem_kilit:
            if islem_id in _aktif_islemler:
                _aktif_islemler[islem_id]["zaman_doldu"] = True
                _aktif_islemler[islem_id]["durum"] = "zaman_doldu"
        if callback:
            try:
                callback(islem_id)
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

    timer = threading.Timer(sure, _zaman_doldu)
    timer.daemon = True
    timer.start()
    return timer


def _baslat(islem_id, sure=30, callback=None):
    """Bir işlemi izlemeye başla."""
    with _islem_kilit:
        if islem_id in _aktif_islemler:
            return {"durum": "hata", "mesaj": f"İşlem zaten aktif: {islem_id}"}
        _aktif_islemler[islem_id] = {
            "baslangic": time.time(),
            "durum": "calisiyor",
            "sure": sure,
            "zaman_doldu": False,
            "iptal_edildi": False,
            "adim_sayisi": 0,
            "son_adim": time.time()
        }
    timer = _zamanlayici_baslat(islem_id, sure, callback)
    _aktif_islemler[islem_id]["timer"] = timer
    return {"durum": "basarili", "mesaj": f"İşlem başlatıldı: {islem_id}", "sure": sure}


def _durdur(islem_id):
    """Bir işlemi durdur/iptal et."""
    with _islem_kilit:
        if islem_id not in _aktif_islemler:
            return {"durum": "hata", "mesaj": f"İşlem bulunamadı: {islem_id}"}
        islem = _aktif_islemler[islem_id]
        islem["durum"] = "iptal_edildi"
        islem["iptal_edildi"] = True
        islem["bitis"] = time.time()
        if "timer" in islem:
            islem["timer"].cancel()
        gecen = islem["bitis"] - islem["baslangic"]
        del _aktif_islemler[islem_id]
    return {"durum": "basarili", "mesaj": f"İşlem durduruldu: {islem_id}", "gecen_sure": round(gecen, 2)}


def _kontrol(islem_id):
    """Bir işlemin durumunu kontrol et."""
    with _islem_kilit:
        if islem_id not in _aktif_islemler:
            return {"durum": "hata", "mesaj": f"İşlem bulunamadı: {islem_id}"}
        islem = _aktif_islemler[islem_id]
        gecen = time.time() - islem["baslangic"]
        kalan = max(0, islem["sure"] - gecen)

        if islem.get("zaman_doldu"):
            islem["durum"] = "zaman_doldu"
            islem["bitis"] = time.time()
            return {
                "durum": "basarili",
                "islem_durumu": "zaman_doldu",
                "gecen_sure": round(gecen, 2),
                "mesaj": f"İşlem zaman aşımına uğradı ({islem['sure']}sn)"
            }
        if islem.get("iptal_edildi"):
            return {
                "durum": "basarili",
                "islem_durumu": "iptal_edildi",
                "gecen_sure": round(gecen, 2),
                "mesaj": "İşlem kullanıcı tarafından iptal edildi"
            }

        return {
            "durum": "basarili",
            "islem_durumu": "calisiyor",
            "gecen_sure": round(gecen, 2),
            "kalan_sure": round(kalan, 2),
            "adim_sayisi": islem["adim_sayisi"]
        }


def run(islem="baslat", sure=30, islem_id="default"):
    """
    Döngü kesme mekanizması.
    
    Parametreler:
        islem (str): baslat / durdur / kontrol
        sure (int): Timeout süresi (saniye)
        islem_id (str): İşlem tanımlayıcı
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "baslat":
            sonuc = _baslat(islem_id, int(sure))
        elif islem == "durdur":
            sonuc = _durdur(islem_id)
        elif islem == "kontrol":
            sonuc = _kontrol(islem_id)
        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("baslat", 30, "test"))
    print(run("kontrol", islem_id="test"))
    print(run("durdur", islem_id="test"))
