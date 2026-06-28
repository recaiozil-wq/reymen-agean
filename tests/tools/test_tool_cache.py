# -*- coding: utf-8 -*-
"""Test: tool_cache.py — TTL tabanlı tool sonuç önbelleği."""

import json
import time
from tools import tool_cache


def test_toolcache_anahtar():
    c = tool_cache.ToolCache(ttl=10)
    k = c.anahtar("shell", {"komut": "ls"})
    assert isinstance(k, str)
    assert len(k) == 24


def test_toolcache_kaydet_al():
    c = tool_cache.ToolCache(ttl=10)
    k = c.anahtar("test", {"x": 1})
    c.kaydet(k, "sonuc")
    assert c.var_mi(k) is True
    assert c.al(k) == "sonuc"


def test_toolcache_var_mi_expired():
    c = tool_cache.ToolCache(ttl=-1)  # expired immediately
    k = c.anahtar("test", {"x": 1})
    c.kaydet(k, "sonuc")
    assert c.var_mi(k) is False


def test_toolcache_sil():
    c = tool_cache.ToolCache(ttl=10)
    k = c.anahtar("test", {"x": 1})
    c.kaydet(k, "val")
    assert c.sil(k) is True
    assert c.var_mi(k) is False
    assert c.sil("nonexistent") is False


def test_toolcache_temizle():
    c = tool_cache.ToolCache(ttl=10)
    k1 = c.anahtar("a", {"x": 1})
    k2 = c.anahtar("b", {"x": 2})
    c.kaydet(k1, "v1")
    c.kaydet(k2, "v2")
    assert c.temizle() >= 0


def test_toolcache_sifirla():
    c = tool_cache.ToolCache(ttl=10)
    k = c.anahtar("test", {"x": 1})
    c.kaydet(k, "val")
    c.sifirla()
    assert c.var_mi(k) is False
    stats = c.istatistik()
    assert stats["boyut"] == 0


def test_toolcache_istatistik():
    c = tool_cache.ToolCache(ttl=10, max_boyut=100)
    stats = c.istatistik()
    assert stats["ttl"] == 10
    assert stats["maks_boyut"] == 100
    assert stats["isabet"] == 0
    assert stats["ıska"] == 0


def test_toolcache_max_boyut():
    c = tool_cache.ToolCache(ttl=10, max_boyut=2)
    k1 = c.anahtar("a", {"x": 1})
    k2 = c.anahtar("b", {"x": 2})
    k3 = c.anahtar("c", {"x": 3})
    c.kaydet(k1, "v1")
    c.kaydet(k2, "v2")
    c.kaydet(k3, "v3")  # should evict oldest
    assert c.istatistik()["boyut"] <= 2


def test_toolcache_onbellekle():
    c = tool_cache.ToolCache(ttl=10)

    @c.onbellekle("test_tool")
    def toplama(a, b):
        return a + b

    assert toplama(2, 3) == 5


def test_run_istatistik():
    sonuc = tool_cache.run("istatistik")
    data = json.loads(sonuc)
    assert "boyut" in data


def test_run_temizle():
    sonuc = tool_cache.run("temizle")
    data = json.loads(sonuc)
    assert "silinen" in data


def test_run_sifirla():
    sonuc = tool_cache.run("sifirla")
    data = json.loads(sonuc)
    assert data.get("durum") == "sıfırlandı"


def test_run_sil_nonexistent():
    sonuc = tool_cache.run("sil", anahtar="nonexistent")
    data = json.loads(sonuc)
    assert data.get("basarili") is False


def test_run_anahtar_uret():
    sonuc = tool_cache.run("anahtar_uret", tool_adi="shell", args='{"komut":"ls"}')
    data = json.loads(sonuc)
    assert "anahtar" in data
    assert len(data["anahtar"]) == 24


def test_run_unknown_islem():
    sonuc = tool_cache.run("bilinmeyen")
    data = json.loads(sonuc)
    assert "hata" in data.get("durum", "") or "hata" in str(data)


def test_global_cache():
    c = tool_cache.global_cache()
    assert isinstance(c, tool_cache.ToolCache)
