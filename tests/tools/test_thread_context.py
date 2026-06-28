# -*- coding: utf-8 -*-
"""Test: thread_context.py — Thread bağlam yönetimi."""

import json
from tools import thread_context


def test_run_kaydet():
    sonuc = thread_context.run("kaydet", "anahtar1", "deger1")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_kaydet_no_key():
    sonuc = thread_context.run("kaydet", "", "deger")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_oku():
    thread_context.run("kaydet", "test_key", "test_val")
    sonuc = thread_context.run("oku", "test_key")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"
    assert data.get("deger") == "test_val"


def test_run_oku_nonexistent():
    sonuc = thread_context.run("oku", "nonexistent_key")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_oku_no_key():
    sonuc = thread_context.run("oku", "")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_temizle_specific():
    thread_context.run("kaydet", "sil_key", "val")
    sonuc = thread_context.run("temizle", "sil_key")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_temizle_all():
    sonuc = thread_context.run("temizle", "")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_liste():
    sonuc = thread_context.run("liste")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"
    assert "veriler" in data


def test_run_invalid_islem():
    sonuc = thread_context.run("gecersiz")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_context_manager():
    ctx = thread_context.ThreadContext()
    with ctx as c:
        c.kaydet("ctx_key", "ctx_val")
        assert c.oku("ctx_key") == "ctx_val"
    assert c.listele() == {}


def test_propagate_context_to_thread():
    wrapper = thread_context.propagate_context_to_thread(lambda x: x + 1)
    assert wrapper(5) == 6
