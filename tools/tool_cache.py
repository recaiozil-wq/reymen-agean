# -*- coding: utf-8 -*-
"""tools/tool_cache.py — TTL tabanlı tool sonuç önbelleği.

Aynı (tool_adi + args) kombinasyonu tekrar çağrılırsa önbellekten döner;
API/işlem maliyetini ve gecikmeyi azaltır.
"""

import hashlib
import json
import time
import threading
from typing import Any

# ANSI renk kodları
_Y = "\033[92m"
_S = "\033[93m"
_M = "\033[94m"
_R = "\033[0m"

DEFAULT_TTL = 300  # 5 dakika


class ToolCache:
    """Thread-safe, TTL tabanlı bellek içi tool önbelleği.

    Kullanım::

        cache = ToolCache(ttl=60)
        k = cache.anahtar("shell", {"komut": "ls"})
        if cache.var_mi(k):
            return cache.al(k)
        sonuc = tool.run(...)
        cache.kaydet(k, sonuc)
    """

    def __init__(self, ttl: int = DEFAULT_TTL, max_boyut: int = 512):
        """
        Args:
            ttl: Saniye cinsinden yaşam süresi.
            max_boyut: Önbellekte tutulacak maksimum giriş sayısı.
        """
        self._ttl = ttl
        self._max = max_boyut
        self._depo: dict[str, tuple[Any, float]] = {}  # {anahtar: (deger, bitis)}
        self._kilit = threading.Lock()
        self._isabet = 0
        self._ıska = 0

    # --- Genel API ---

    def anahtar(self, tool_adi: str, args: dict) -> str:
        """Tool adı + sıralı args'tan deterministik SHA-256 önbellek anahtarı üret."""
        ham = json.dumps({"tool": tool_adi, "args": args}, sort_keys=True, default=str)
        return hashlib.sha256(ham.encode()).hexdigest()[:24]

    def var_mi(self, anahtar: str) -> bool:
        """Geçerli bir önbellek girdisi mevcut mu?"""
        with self._kilit:
            if anahtar not in self._depo:
                return False
            _, bitis = self._depo[anahtar]
            if time.monotonic() > bitis:
                del self._depo[anahtar]
                return False
            return True

    def al(self, anahtar: str) -> Any | None:
        """Önbellekteki değeri döndür (yoksa None)."""
        with self._kilit:
            girdi = self._depo.get(anahtar)
            if girdi is None:
                self._ıska += 1
                return None
            deger, bitis = girdi
            if time.monotonic() > bitis:
                del self._depo[anahtar]
                self._ıska += 1
                return None
            self._isabet += 1
            print(f"{_Y}[CACHE] HIT  {anahtar[:12]}…{_R}")
            return deger

    def kaydet(self, anahtar: str, deger: Any) -> None:
        """Değeri TTL ile önbelleğe yaz."""
        with self._kilit:
            # Kapasite aşımında en eski girdiyi sil
            if len(self._depo) >= self._max:
                en_eski = min(self._depo, key=lambda k: self._depo[k][1])
                del self._depo[en_eski]
            self._depo[anahtar] = (deger, time.monotonic() + self._ttl)
            print(f"{_M}[CACHE] SET  {anahtar[:12]}… (TTL={self._ttl}s){_R}")

    def sil(self, anahtar: str) -> bool:
        """Belirli bir girdiyi önbellekten çıkar."""
        with self._kilit:
            if anahtar in self._depo:
                del self._depo[anahtar]
                return True
            return False

    def temizle(self) -> int:
        """Süresi dolmuş tüm girdileri temizle. Silinen sayısını döndür."""
        simdi = time.monotonic()
        with self._kilit:
            eskiler = [k for k, (_, b) in self._depo.items() if simdi > b]
            for k in eskiler:
                del self._depo[k]
        if eskiler:
            print(f"{_S}[CACHE] {len(eskiler)} süresi dolmuş girdi temizlendi{_R}")
        return len(eskiler)

    def sifirla(self) -> None:
        """Tüm önbelleği temizle."""
        with self._kilit:
            self._depo.clear()
            self._isabet = 0
            self._ıska = 0

    def istatistik(self) -> dict:
        """Önbellek istatistiklerini döndür."""
        with self._kilit:
            toplam = self._isabet + self._ıska
            oran = round(self._isabet / toplam * 100, 1) if toplam else 0.0
            return {
                "boyut": len(self._depo),
                "maks_boyut": self._max,
                "ttl": self._ttl,
                "isabet": self._isabet,
                "ıska": self._ıska,
                "isabet_orani": oran,
            }

    # --- Dekoratör ---

    def onbellekle(self, tool_adi: str):
        """Fonksiyon dekoratörü: dönen değeri otomatik önbellekle.

        Kullanım::

            cache = ToolCache()

            @cache.onbellekle("shell")
            def shell_calistir(komut: str):
                ...
        """
        def sarmalayici(fonk):
            def ic(*args, **kwargs):
                anahtar = self.anahtar(tool_adi, {"args": args, "kwargs": kwargs})
                if self.var_mi(anahtar):
                    return self.al(anahtar)
                sonuc = fonk(*args, **kwargs)
                self.kaydet(anahtar, sonuc)
                return sonuc
            return ic
        return sarmalayici


def run(islem: str = "istatistik", anahtar: str = "", deger: str = "",
        tool_adi: str = "", args: str = "") -> str:
    """Tool cache harici arayüzü (tool_registry uyumu).

    Args:
        islem: 'istatistik' | 'temizle' | 'sifirla' | 'sil'
        anahtar: Belirli bir girdiyi silmek için önbellek anahtarı.
        tool_adi / args: 'anahtar_uret' işlemi için.

    Returns:
        str: JSON formatında sonuç.
    """
    import json as _json

    try:
        cache = global_cache()

        if islem == "istatistik":
            return _json.dumps(cache.istatistik(), ensure_ascii=False)

        elif islem == "temizle":
            silinen = cache.temizle()
            return _json.dumps({"silinen": silinen}, ensure_ascii=False)

        elif islem == "sifirla":
            cache.sifirla()
            return _json.dumps({"durum": "sıfırlandı"}, ensure_ascii=False)

        elif islem == "sil":
            basarili = cache.sil(anahtar)
            return _json.dumps({"basarili": basarili}, ensure_ascii=False)

        elif islem == "anahtar_uret":
            args_dict = _json.loads(args) if args else {}
            k = cache.anahtar(tool_adi, args_dict)
            return _json.dumps({"anahtar": k}, ensure_ascii=False)

        return _json.dumps({"durum": "hata", "mesaj": f"bilinmeyen islem: {islem}"}, ensure_ascii=False)

    except Exception as exc:
        import json as _j
        return _j.dumps({"durum": "hata", "mesaj": str(exc)}, ensure_ascii=False)


# Modül düzeyi singleton
_cache = ToolCache()


def global_cache() -> ToolCache:
    """Global singleton ToolCache döndür."""
    return _cache


if __name__ == "__main__":
    c = ToolCache(ttl=10)
    k = c.anahtar("shell", {"komut": "echo test"})
    c.kaydet(k, "test\n")
    print(c.al(k))
    print(c.istatistik())
