#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_helpers.py — Debug yardımcıları.
İzleme, loglama, performans ölçümü.
"""

import json
import time
import traceback
import functools


_LOG_SEVIYELERI = {"DEBUG": 10, "INFO": 20, "UYARI": 30, "HATA": 40, "KRITIK": 50}


class Logger:
    """Basit loglama sınıfı."""
    
    def __init__(self, seviye="DEBUG"):
        self.seviye = seviye
        self.kayitlar = []
    
    def log(self, mesaj, seviye="DEBUG"):
        """Log kaydı ekle."""
        seviye_num = _LOG_SEVIYELERI.get(seviye, 0)
        min_seviye = _LOG_SEVIYELERI.get(self.seviye, 0)
        
        if seviye_num >= min_seviye:
            kayit = {
                "zaman": time.time(),
                "zaman_str": time.strftime("%Y-%m-%d %H:%M:%S"),
                "seviye": seviye,
                "mesaj": mesaj
            }
            self.kayitlar.append(kayit)
            return kayit
        return None
    
    def debug(self, mesaj):
        return self.log(mesaj, "DEBUG")
    
    def info(self, mesaj):
        return self.log(mesaj, "INFO")
    
    def uyari(self, mesaj):
        return self.log(mesaj, "UYARI")
    
    def hata(self, mesaj):
        return self.log(mesaj, "HATA")
    
    def kritik(self, mesaj):
        return self.log(mesaj, "KRITIK")
    
    def son_kayitlar(self, n=10):
        """Son N kaydı döndür."""
        return self.kayitlar[-n:]
    
    def temizle(self):
        """Tüm kayıtları temizle."""
        self.kayitlar = []


# Varsayılan logger
_logger = Logger()


def trace(islev=None, log_args=True, log_result=True):
    """
    Decorator: Fonksiyon çağrılarını izle.
    
    Kullanım:
        @trace
        def fonksiyonum():
            ...
        
        @trace(log_args=False)
        def fonksiyonum():
            ...
    """
    if islev is not None:
        @functools.wraps(islev)
        def sarmalayici(*args, **kwargs):
            baslangic = time.time()
            args_str = f"args={args}, kwargs={kwargs}" if log_args else "(gizli)"
            _logger.debug(f"→ {islev.__name__}({args_str})")
            try:
                sonuc = islev(*args, **kwargs)
                gecen = time.time() - baslangic
                sonuc_str = f" → {str(sonuc)[:100]}" if log_result else ""
                _logger.debug(f"← {islev.__name__} [{gecen:.3f}s]{sonuc_str}")
                return sonuc
            except Exception as e:
                gecen = time.time() - baslangic
                _logger.hata(f"✗ {islev.__name__} [{gecen:.3f}s] HATA: {e}")
                raise
        return sarmalayici
    
    def decorator(islev):
        @functools.wraps(islev)
        def sarmalayici(*args, **kwargs):
            baslangic = time.time()
            args_str = f"args={args}, kwargs={kwargs}" if log_args else "(gizli)"
            _logger.debug(f"→ {islev.__name__}({args_str})")
            try:
                sonuc = islev(*args, **kwargs)
                gecen = time.time() - baslangic
                sonuc_str = f" → {str(sonuc)[:100]}" if log_result else ""
                _logger.debug(f"← {islev.__name__} [{gecen:.3f}s]{sonuc_str}")
                return sonuc
            except Exception as e:
                gecen = time.time() - baslangic
                _logger.hata(f"✗ {islev.__name__} [{gecen:.3f}s] HATA: {e}")
                raise
        return sarmalayici
    return decorator


def profil(islev):
    """Decorator: Fonksiyon performans profilini çıkar."""
    @functools.wraps(islev)
    def sarmalayici(*args, **kwargs):
        baslangic = time.time()
        cagri_sayisi = [0]
        
        def sayac():
            cagri_sayisi[0] += 1
        
        try:
            sonuc = islev(*args, **kwargs)
            gecen = time.time() - baslangic
            return sonuc
        finally:
            gecen = time.time() - baslangic
            _logger.info(f"[PROFIL] {islev.__name__}: {gecen:.4f}s, {cagri_sayisi[0]} iç çağrı")
    return sarmalayici


def run(islem="log", mesaj="", seviye="DEBUG"):
    """
    Debug yardımcıları.
    
    Parametreler:
        islem (str): trace / log / profil
        mesaj (str): Log mesajı
        seviye (str): Log seviyesi (DEBUG/INFO/UYARI/HATA/KRITIK)
    
    Returns:
        str: Debug sonucu
    """
    global _logger

    try:
        if islem == "trace":
            return json.dumps({
                "durum": "basarili",
                "mesaj": "trace decorator'u fonksiyonlarda kullanılır",
                "kullanim": "@trace\\ndef fonksiyonum():\\n    ...",
                "mevcut_kayitlar": len(_logger.kayitlar)
            }, ensure_ascii=False)

        elif islem == "log":
            if not mesaj:
                return json.dumps({"durum": "hata", "mesaj": "mesaj parametresi gerekli"}, ensure_ascii=False)
            seviye = seviye.upper() if seviye else "DEBUG"
            if seviye not in _LOG_SEVIYELERI:
                return json.dumps({"durum": "hata", "mesaj": f"Geçersiz seviye: {seviye}"}, ensure_ascii=False)
            kayit = _logger.log(mesaj, seviye)
            return json.dumps({
                "durum": "basarili",
                "kayit": kayit,
                "toplam_kayit": len(_logger.kayitlar)
            }, ensure_ascii=False, default=str)

        elif islem == "profil":
            return json.dumps({
                "durum": "basarili",
                "mesaj": "profil decorator'u fonksiyonlarda kullanılır",
                "kullanim": "@profil\\ndef fonksiyonum():\\n    ..."
            }, ensure_ascii=False)

        elif islem == "kayitlar":
            n = 20
            try:
                n = int(mesaj) if mesaj else 20
            except ValueError:
                n = 20
            kayitlar = _logger.son_kayitlar(n)
            return json.dumps({
                "durum": "basarili",
                "kayitlar": kayitlar,
                "sayi": len(kayitlar)
            }, ensure_ascii=False, default=str)

        elif islem == "temizle":
            _logger.temizle()
            return json.dumps({
                "durum": "basarili",
                "mesaj": "Tüm kayıtlar temizlendi"
            }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("log", "Test mesajı", "INFO"))
    print(run("log", "Hata oluştu", "HATA"))
    print(run("kayitlar"))
