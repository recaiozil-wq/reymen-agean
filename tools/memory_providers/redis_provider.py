# -*- coding: utf-8 -*-
"""memory_providers/redis_provider.py — Redis bellek."""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from .base import BellekSaglayici
import logging
logger = logging.getLogger(__name__)


class RedisBellek(BellekSaglayici):
    """Redis ile hızlı anahtar-değer bellek (TTL destekli)."""

    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, ttl: Optional[int] = None,
                 sifre: Optional[str] = None):
        self._host  = host
        self._port  = port
        self._db    = db
        self._ttl   = ttl       # None = süresiz
        self._r     = None
        self._aktif = False
        self._hata_msg = ""
        self._init(sifre)

    def _init(self, sifre: Optional[str]) -> None:
        try:
            import redis  # type: ignore
            self._r = redis.Redis(
                host=self._host, port=self._port,
                db=self._db, password=sifre,
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True,      # bytes değil str
            )
            self._r.ping()                  # Bağlantı testi
            self._aktif = True
        except ImportError:
            self._hata_msg = "redis kurulu değil (pip install redis)"
        except Exception as e:
            self._hata_msg = str(e)

    def _guard(self) -> Optional[str]:
        if not self._aktif:
            return f"[Hata]: Redis kullanılamıyor — {self._hata_msg}"
        return None

    @staticmethod
    def _anahtar(namespace: str, anahtar: str) -> str:
        """Redis key: namespace:anahtar"""
        return f"{namespace}:{anahtar}"

    # ── Interface ─────────────────────────────────────────────
    def kaydet(self, anahtar: str, deger: Any,
               namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        if not anahtar:
            return "[Hata]: anahtar boş olamaz."
        deger_str = json.dumps(deger, ensure_ascii=False) \
                    if not isinstance(deger, str) else deger
        try:
            key = self._anahtar(namespace, anahtar)
            if self._ttl:
                self._r.setex(key, self._ttl, deger_str)
            else:
                self._r.set(key, deger_str)
            # Namespace index: sadd ile namespace altındaki key'leri tut
            self._r.sadd(f"ns:{namespace}", anahtar)
        except Exception as e:
            return f"[Hata]: Redis kayıt — {e}"
        return f"[Tamam] Redis: '{anahtar}' → '{namespace}' kaydedildi."

    def oku(self, anahtar: str,
            namespace: str = "default") -> Optional[Any]:
        if self._guard():
            return None
        try:
            deger = self._r.get(self._anahtar(namespace, anahtar))
            if deger is None:
                return None
            try:
                return json.loads(deger)
            except (json.JSONDecodeError, TypeError):
                return deger
        except Exception:
            return None

    def ara(self, sorgu: str, limit: int = 5) -> List[Dict]:
        """Redis'te FTS yok; SCAN + substring match (küçük veri setleri için)."""
        if self._guard():
            return []
        sorgu_kucuk = sorgu.lower()
        sonuc: List[Dict] = []
        try:
            # SCAN: tüm key'leri tek seferde yüklemez; iterator
            for key in self._r.scan_iter(match="*:*", count=100):
                if len(sonuc) >= limit:
                    break
                if sorgu_kucuk not in key.lower():
                    deger = self._r.get(key)
                    if not deger or sorgu_kucuk not in deger.lower():
                        continue
                deger = self._r.get(key)
                sonuc.append({
                    "id":     key,
                    "icerik": self._sinirla(deger or ""),
                })
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return sonuc

    def sil(self, anahtar: str, namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        try:
            key     = self._anahtar(namespace, anahtar)
            silindi = self._r.delete(key)
            self._r.srem(f"ns:{namespace}", anahtar)
        except Exception as e:
            return f"[Hata]: Redis silme — {e}"
        if silindi == 0:
            return f"[Hata]: '{anahtar}' → '{namespace}' bulunamadı."
        return f"[Tamam] Redis: '{anahtar}' silindi."

    def durum(self) -> Dict:
        if not self._aktif:
            return {"tur": "redis", "aktif": False, "hata": self._hata_msg}
        try:
            bilgi   = self._r.info("server")
            db_bilgi = self._r.info("keyspace")
            versiyon = bilgi.get("redis_version", "?")
            toplam   = sum(
                v.get("keys", 0)
                for v in db_bilgi.values()
                if isinstance(v, dict)
            )
        except Exception:
            versiyon = "?"
            toplam   = -1
        return {
            "tur":      "redis",
            "aktif":    True,
            "versiyon": versiyon,
            "kayit":    toplam,
            "ttl":      self._ttl,
            "host":     f"{self._host}:{self._port}",
        }
