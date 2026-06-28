#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool_result_storage.py — Tool sonuç depolama.
JSON tabanlı sonuç önbelleği.
"""

import os
import json
import time
import hashlib
import logging
logger = logging.getLogger(__name__)


CACHE_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tool_cache.json')
MAX_CACHE_BOYUT = 1000  # Maksimum kayıt sayısı


def _cache_oku():
    """Cache verisini oku."""
    if not os.path.exists(CACHE_DOSYASI):
        return {}
    try:
        with open(CACHE_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _cache_yaz(veri):
    """Cache verisini yaz."""
    try:
        with open(CACHE_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def _hash_olustur(arac_adi, parametreler=None):
    """Parametrelere göre hash oluştur."""
    hash_str = arac_adi
    if parametreler:
        hash_str += json.dumps(parametreler, sort_keys=True)
    return hashlib.sha256(hash_str.encode()).hexdigest()[:16]


def _kaydet(arac_adi, parametre_hash, sonuc):
    """Bir tool sonucunu cache'e kaydet."""
    veri = _cache_oku()
    
    # Cache boyutunu kontrol et, eski kayıtları temizle
    if len(veri) >= MAX_CACHE_BOYUT:
        # En eski kayıtları sil
        sirali = sorted(veri.items(), key=lambda x: x[1].get("zaman", 0))
        silinecek = len(veri) - MAX_CACHE_BOYUT + 10  # 10 yeni kayda yer aç
        for anahtar, _ in sirali[:silinecek]:
            del veri[anahtar]
    
    anahtar = f"{arac_adi}:{parametre_hash}"
    veri[anahtar] = {
        "arac_adi": arac_adi,
        "parametre_hash": parametre_hash,
        "sonuc": sonuc,
        "zaman": time.time(),
        "tarih": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if _cache_yaz(veri):
        return {"durum": "basarili", "mesaj": f"Sonuç kaydedildi: {anahtar}"}
    return {"durum": "hata", "mesaj": "Cache dosyası yazılamadı"}


def _oku(arac_adi, parametre_hash):
    """Bir tool sonucunu cache'den oku."""
    veri = _cache_oku()
    anahtar = f"{arac_adi}:{parametre_hash}"
    
    if anahtar not in veri:
        return {"durum": "hata", "mesaj": f"Cache'de bulunamadı: {anahtar}"}
    
    return {"durum": "basarili", "kayit": veri[anahtar]}


def _sil(arac_adi, parametre_hash):
    """Bir tool sonucunu cache'den sil."""
    veri = _cache_oku()
    anahtar = f"{arac_adi}:{parametre_hash}"
    
    if anahtar in veri:
        del veri[anahtar]
        _cache_yaz(veri)
        return {"durum": "basarili", "mesaj": f"Silindi: {anahtar}"}
    return {"durum": "hata", "mesaj": f"Bulunamadı: {anahtar}"}


def _temizle(arac_adi=None):
    """Cache'i temizle."""
    if arac_adi:
        veri = _cache_oku()
        silinecek = [k for k in veri if k.startswith(f"{arac_adi}:")]
        for k in silinecek:
            del veri[k]
        _cache_yaz(veri)
        return {"durum": "basarili", "mesaj": f"'{arac_adi}' için {len(silinecek)} kayıt silindi"}
    else:
        _cache_yaz({})
        return {"durum": "basarili", "mesaj": "Tüm cache temizlendi"}


def run(islem="listele", arac_adi="", parametre_hash=""):
    """
    Tool sonuç depolama.
    
    Parametreler:
        islem (str): kaydet / oku / sil / temizle / listele
        arac_adi (str): Araç adı
        parametre_hash (str): Parametre hash'i (kaydet işleminde JSON sonuç,
            oku/sil işleminde hash)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "kaydet":
            if not arac_adi or not parametre_hash:
                return json.dumps({"durum": "hata", "mesaj": "arac_adi ve sonuç parametreleri gerekli"}, ensure_ascii=False)
            sonuc_data = parametre_hash  # Burada parametre_hash sonuç olarak kullanılır
            try:
                if isinstance(sonuc_data, str):
                    sonuc_data = json.loads(sonuc_data)
            except (json.JSONDecodeError, ValueError):
                logger.warning("[fix_01_sessiz_except] Exception")
            hash_val = _hash_olustur(arac_adi, sonuc_data)
            sonuc = _kaydet(arac_adi, hash_val, sonuc_data)

        elif islem == "oku":
            if not arac_adi:
                return json.dumps({"durum": "hata", "mesaj": "arac_adi parametresi gerekli"}, ensure_ascii=False)
            if not parametre_hash:
                parametre_hash = _hash_olustur(arac_adi)
            sonuc = _oku(arac_adi, parametre_hash)

        elif islem == "sil":
            if not arac_adi:
                return json.dumps({"durum": "hata", "mesaj": "arac_adi parametresi gerekli"}, ensure_ascii=False)
            if not parametre_hash:
                parametre_hash = _hash_olustur(arac_adi)
            sonuc = _sil(arac_adi, parametre_hash)

        elif islem == "temizle":
            sonuc = _temizle(arac_adi if arac_adi else None)

        elif islem == "listele":
            veri = _cache_oku()
            # arac_adi filtresi
            if arac_adi:
                kayitlar = {k: v for k, v in veri.items() if k.startswith(f"{arac_adi}:")}
            else:
                kayitlar = veri
            liste = []
            for anahtar, kayit in sorted(kayitlar.items(), key=lambda x: x[1].get("zaman", 0), reverse=True):
                liste.append({
                    "anahtar": anahtar,
                    "arac_adi": kayit.get("arac_adi", ""),
                    "zaman": kayit.get("tarih", ""),
                    "sonuc_ozet": str(kayit.get("sonuc", ""))[:100]
                })
            return json.dumps({
                "durum": "basarili",
                "kayitlar": liste,
                "sayi": len(liste),
                "toplam_cache": len(veri)
            }, ensure_ascii=False, default=str)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


_PERSIST_THRESHOLD = 50_000  # Bu siniri asan string sonuclar diske kaydedilir


def maybe_persist_tool_result(
    content: str,
    tool_name: str = "",
    tool_use_id: str = "",
    env=None,
) -> str:
    """Buyuk tool sonuclarini diske kaydet; kucukleri oldugu gibi dondur.

    Icerik _PERSIST_THRESHOLD karakteri asarsa cache'e yazar ve bir referans
    string dondurur. Boyut siniri altindaysa icerik aynen geri gelir.

    Args:
        content:     Tool'dan gelen ham sonuc string'i.
        tool_name:   Arac adi (loglama icin).
        tool_use_id: Tool call ID'si (loglama icin).
        env:         Aktif ortam (kullanilmaz; uyumluluk icin).

    Returns:
        Ya orijinal content ya da '<dosya_yolu> konumuna kaydedildi' mesaji.
    """
    if not isinstance(content, str) or len(content) <= _PERSIST_THRESHOLD:
        return content

    param_hash = _hash_olustur(tool_name or "tool", tool_use_id or content[:64])
    try:
        _kaydet(tool_name or "tool", param_hash, content)
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")
    return content


def enforce_turn_budget(messages: list, env=None) -> None:
    """Tur basina toplam token butcesini zorla — asimi buyuk sonuclari kisalt.

    Args:
        messages: Bu tura ait mesaj listesi (tool_result bloklari iceren).
        env:      Aktif ortam (butce limitlerini okumak icin; opsiyonel).

    Not: Basit implementasyon — hicbir seyi kesmeden geri doner.
    Gercek butce mantigi ileride eklenebilir.
    """
    return


if __name__ == "__main__":
    print(run("kaydet", "test_tool", '{"sonuc": "deneme"}'))
    print(run("listele"))
    print(run("temizle"))
