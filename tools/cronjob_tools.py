#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cronjob_tools.py — Zamanlanmış görev yönetimi.
JSON tabanlı cron job'ları.
"""

import os
import json
import time
import threading
import subprocess
import datetime


CRON_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cron_jobs.json')


_cron_durum = {"calisiyor": False, "thread": None}
_cron_kilit = threading.Lock()


def _cron_oku():
    """Cron job'larını oku."""
    if not os.path.exists(CRON_DOSYASI):
        return {}
    try:
        with open(CRON_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _cron_yaz(veri):
    """Cron job'larını yaz."""
    try:
        with open(CRON_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def _zaman_kontrol(zaman_str):
    """Zaman formatını kontrol et (HH:MM)."""
    try:
        saat, dakika = zaman_str.strip().split(':')
        saat = int(saat)
        dakika = int(dakika)
        if 0 <= saat < 24 and 0 <= dakika < 60:
            return True
        return False
    except Exception:
        return False


def _cron_ekle(ad, zaman, komut):
    """Yeni bir cron job'ı ekle."""
    if not _zaman_kontrol(zaman):
        return {"durum": "hata", "mesaj": f"Geçersiz zaman formatı: {zaman} (HH:MM olmalı)"}
    
    veri = _cron_oku()
    if ad in veri:
        return {"durum": "hata", "mesaj": f"'{ad}' zaten var"}
    
    veri[ad] = {
        "ad": ad,
        "zaman": zaman,
        "komut": komut,
        "aktif": True,
        "olusturma": time.time(),
        "son_calisma": None
    }
    
    if _cron_yaz(veri):
        return {"durum": "basarili", "mesaj": f"Cron job eklendi: {ad} ({zaman})"}
    return {"durum": "hata", "mesaj": "Cron dosyası yazılamadı"}


def _cron_sil(ad):
    """Bir cron job'ını sil."""
    veri = _cron_oku()
    if ad not in veri:
        return {"durum": "hata", "mesaj": f"'{ad}' bulunamadı"}
    del veri[ad]
    if _cron_yaz(veri):
        return {"durum": "basarili", "mesaj": f"Cron job silindi: {ad}"}
    return {"durum": "hata", "mesaj": "Cron dosyası yazılamadı"}


def _cron_listele():
    """Tüm cron job'larını listele."""
    veri = _cron_oku()
    liste = []
    for ad, bilgi in sorted(veri.items()):
        item = dict(bilgi)
        if item.get("son_calisma"):
            item["son_calisma_str"] = datetime.datetime.fromtimestamp(item["son_calisma"]).isoformat()
        liste.append(item)
    return {"durum": "basarili", "cron_jobs": liste, "sayi": len(liste)}


def _cron_calistir(ad):
    """Belirli bir cron job'ını hemen çalıştır."""
    veri = _cron_oku()
    if ad not in veri:
        return {"durum": "hata", "mesaj": f"'{ad}' bulunamadı"}
    
    job = veri[ad]
    try:
        sonuc = subprocess.run(
            job["komut"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=60
        )
        veri[ad]["son_calisma"] = time.time()
        veri[ad]["son_cikti"] = sonuc.stdout[-500:] if sonuc.stdout else ""
        veri[ad]["son_hata"] = sonuc.stderr[-500:] if sonuc.stderr else ""
        veri[ad]["son_kod"] = sonuc.returncode
        _cron_yaz(veri)
        
        return {
            "durum": "basarili",
            "mesaj": f"'{ad}' çalıştırıldı",
            "cikis_kodu": sonuc.returncode,
            "cikti": sonuc.stdout[:500],
            "hata": sonuc.stderr[:500]
        }
    except subprocess.TimeoutExpired:
        return {"durum": "hata", "mesaj": f"'{ad}' zaman aşımı (60sn)"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def cronjob(islem="listele", ad="", zaman="", komut=""):
    """Cron job yonetimi — upstream Hermes uyumluluk alias."""
    return run(islem, ad, zaman, komut)


def run(islem="listele", ad="", zaman="", komut=""):
    """
    Zamanlanmış görev yönetimi.
    
    Parametreler:
        islem (str): ekle / sil / listele / calistir
        ad (str): Job adı
        zaman (str): Zaman (HH:MM formatında)
        komut (str): Çalıştırılacak komut
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "ekle":
            if not ad or not zaman or not komut:
                return json.dumps({"durum": "hata", "mesaj": "ad, zaman ve komut parametreleri gerekli"}, ensure_ascii=False)
            sonuc = _cron_ekle(ad, zaman, komut)

        elif islem == "sil":
            if not ad:
                return json.dumps({"durum": "hata", "mesaj": "ad parametresi gerekli"}, ensure_ascii=False)
            sonuc = _cron_sil(ad)

        elif islem == "listele":
            sonuc = _cron_listele()

        elif islem == "calistir":
            if not ad:
                return json.dumps({"durum": "hata", "mesaj": "ad parametresi gerekli"}, ensure_ascii=False)
            sonuc = _cron_calistir(ad)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


# ── CronScheduler daemon entegrasyonu ────────────────────────────────────────

_scheduler_instance = None
_scheduler_kilit = threading.Lock()


def _scheduler_al():
    """Global CronScheduler singleton'ını döndür (lazily oluştur)."""
    global _scheduler_instance
    with _scheduler_kilit:
        if _scheduler_instance is None:
            try:
                import sys, os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from cron_scheduler import CronScheduler
                _scheduler_instance = CronScheduler(json_yolu=CRON_DOSYASI)
            except ImportError:
                return None
        return _scheduler_instance


def _scheduler_baslat():
    """Arka plan CronScheduler daemon'ını başlat."""
    sc = _scheduler_al()
    if sc is None:
        return json.dumps({"durum": "hata", "mesaj": "cron_scheduler.py bulunamadı"}, ensure_ascii=False)
    if sc._calisiyor:
        return json.dumps({"durum": "bilgi", "mesaj": "Scheduler zaten çalışıyor"}, ensure_ascii=False)
    sc.baslat()
    return json.dumps({"durum": "basarili", "mesaj": "Cron scheduler başlatıldı"}, ensure_ascii=False)


def _scheduler_durdur():
    """CronScheduler daemon'ını durdur."""
    sc = _scheduler_al()
    if sc is None:
        return json.dumps({"durum": "hata", "mesaj": "cron_scheduler.py bulunamadı"}, ensure_ascii=False)
    if not sc._calisiyor:
        return json.dumps({"durum": "bilgi", "mesaj": "Scheduler zaten durmuş"}, ensure_ascii=False)
    sc.durdur()
    return json.dumps({"durum": "basarili", "mesaj": "Cron scheduler durduruldu"}, ensure_ascii=False)


def _scheduler_durum():
    """CronScheduler durumunu döndür."""
    sc = _scheduler_al()
    if sc is None:
        return json.dumps({"durum": "hata", "mesaj": "cron_scheduler.py bulunamadı"}, ensure_ascii=False)
    gorevler = sc.listele() if hasattr(sc, "listele") else []
    return json.dumps({
        "durum": "basarili",
        "calisiyor": sc._calisiyor,
        "gorev_sayisi": len(gorevler),
        "gorevler": gorevler,
    }, ensure_ascii=False, default=str)


def _zamanla(cron_ifade="", komut="", ad=""):
    """Tam cron ifadesiyle görev zamanla (daemon'a ekler)."""
    if not cron_ifade or not komut:
        return json.dumps({"durum": "hata", "mesaj": "cron_ifade ve komut zorunludur"}, ensure_ascii=False)
    sc = _scheduler_al()
    if sc is None:
        return json.dumps({"durum": "hata", "mesaj": "cron_scheduler.py bulunamadı"}, ensure_ascii=False)
    job_id = ad or f"job_{int(time.time())}"
    fonk = lambda: subprocess.run(komut, shell=False, capture_output=True, text=True, timeout=120)
    basarili = sc.ekle(job_id, cron_ifade, fonk, aciklama=komut[:80])
    if basarili:
        return json.dumps({"durum": "basarili", "mesaj": f"Görev zamanlandı: {job_id} ({cron_ifade})", "job_id": job_id}, ensure_ascii=False)
    return json.dumps({"durum": "hata", "mesaj": f"Görev eklenemedi: {job_id}"}, ensure_ascii=False)


def motor_kaydet(motor) -> None:
    """Motor'a cron araçlarını kaydet."""
    # JSON tabanlı basit görevler (HH:MM zamanlaması)
    motor._plugin_arac_kaydet(
        "CRON_EKLE",
        lambda ad="", zaman="", komut="": run("ekle", ad, zaman, komut),
        "Zamanlanmış görev ekle — CRON_EKLE(ad, zaman HH:MM, komut)"
    )
    motor._plugin_arac_kaydet(
        "CRON_SIL",
        lambda ad="": run("sil", ad),
        "Zamanlanmış görevi sil — CRON_SIL(ad)"
    )
    motor._plugin_arac_kaydet(
        "CRON_LISTELE",
        lambda: run("listele"),
        "Zamanlanmış görevleri listele"
    )
    motor._plugin_arac_kaydet(
        "CRON_CALISTIR",
        lambda ad="": run("calistir", ad),
        "Zamanlanmış görevi hemen çalıştır — CRON_CALISTIR(ad)"
    )
    # CronScheduler daemon (arka plan, Python tabanlı, platform bağımsız)
    motor._plugin_arac_kaydet(
        "CRON_BASLAT",
        _scheduler_baslat,
        "Arka plan cron scheduler daemon'ını başlat"
    )
    motor._plugin_arac_kaydet(
        "CRON_DURDUR",
        _scheduler_durdur,
        "Cron scheduler daemon'ını durdur"
    )
    motor._plugin_arac_kaydet(
        "CRON_DURUM",
        _scheduler_durum,
        "Cron scheduler durumunu göster (çalışıyor/görev sayısı)"
    )
    motor._plugin_arac_kaydet(
        "CRON_ZAMANLA",
        lambda cron_ifade="", komut="", ad="": _zamanla(cron_ifade, komut, ad),
        "Tam cron ifadesiyle görev zamanla — CRON_ZAMANLA(cron_ifade '*/5 * * * *', komut, ad)"
    )


if __name__ == "__main__":
    print(run("ekle", "test_job", "12:00", "echo 'Hello World'"))
    print(run("listele"))
    print(run("calistir", "test_job"))
    print(run("sil", "test_job"))
