#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
thread_context.py — Thread bağlam yönetimi.
Thread-safe veri saklama, context manager.
"""

import contextvars
import json
import threading


class ThreadContext:
    """Thread-safe bağlam yöneticisi."""
    
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
    
    def kaydet(self, anahtar, deger):
        """Thread-safe veri kaydet."""
        with self._lock:
            self._data[anahtar] = deger
        return True
    
    def oku(self, anahtar):
        """Thread-safe veri oku."""
        with self._lock:
            return self._data.get(anahtar)
    
    def temizle(self, anahtar=None):
        """Thread-safe veri temizle."""
        with self._lock:
            if anahtar is None:
                self._data.clear()
            elif anahtar in self._data:
                del self._data[anahtar]
        return True
    
    def listele(self):
        """Tüm verileri listele."""
        with self._lock:
            return dict(self._data)
    
    def __enter__(self):
        """Context manager giriş."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkış (otomatik temizlik)."""
        self.temizle()
        return False


# Varsayılan global context
_global_context = ThreadContext()


def run(islem="kaydet", anahtar="", deger=""):
    """
    Thread bağlam yönetimi.
    
    Parametreler:
        islem (str): kaydet / oku / temizle
        anahtar (str): Veri anahtarı
        deger (str): Veri değeri
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    global _global_context

    try:
        if islem == "kaydet":
            if not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "anahtar parametresi gerekli"}, ensure_ascii=False)
            try:
                deger_parsed = json.loads(deger) if deger and deger.startswith(('{', '[')) else deger
            except (json.JSONDecodeError, ValueError):
                deger_parsed = deger
            _global_context.kaydet(anahtar, deger_parsed)
            return json.dumps({"durum": "basarili", "mesaj": f"'{anahtar}' kaydedildi"}, ensure_ascii=False)

        elif islem == "oku":
            if not anahtar:
                return json.dumps({"durum": "hata", "mesaj": "anahtar parametresi gerekli"}, ensure_ascii=False)
            deger = _global_context.oku(anahtar)
            if deger is not None:
                return json.dumps({"durum": "basarili", "anahtar": anahtar, "deger": deger}, ensure_ascii=False, default=str)
            else:
                return json.dumps({"durum": "hata", "mesaj": f"'{anahtar}' bulunamadı"}, ensure_ascii=False)

        elif islem == "temizle":
            if anahtar:
                _global_context.temizle(anahtar)
                return json.dumps({"durum": "basarili", "mesaj": f"'{anahtar}' temizlendi"}, ensure_ascii=False)
            else:
                _global_context.temizle()
                return json.dumps({"durum": "basarili", "mesaj": "Tüm bağlam temizlendi"}, ensure_ascii=False)

        elif islem == "liste":
            veri = _global_context.listele()
            return json.dumps({"durum": "basarili", "veriler": veri, "sayi": len(veri)}, ensure_ascii=False, default=str)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


def propagate_context_to_thread(fn):
    """Mevcut contextvars baglami thread pool worker'ina tasir.

    ThreadPoolExecutor icinde calisan fonksiyonlar ContextVar'lari otomatik
    miras almaz. Bu wrapper, cagri anindaki snapshot'i yakalar ve worker
    thread'inde ayni context icinde calistirir.

    Kullanim: executor.submit(propagate_context_to_thread(fn), *args)
    """
    ctx = contextvars.copy_context()

    def _wrapper(*args, **kwargs):
        return ctx.run(fn, *args, **kwargs)

    return _wrapper


if __name__ == "__main__":
    print(run("kaydet", "test_key", "test_value"))
    print(run("oku", "test_key"))
    print(run("liste"))
    print(run("temizle", "test_key"))
