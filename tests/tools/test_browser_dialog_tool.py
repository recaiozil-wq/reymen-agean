# -*- coding: utf-8 -*-
"""Test: browser_dialog_tool.py — Tarayıcı dialog yönetimi."""

import json
from tools import browser_dialog_tool


def test_run_bekle_timeout():
    """Hiç dialog kaydedilmemişken bekle timeout döner."""
    browser_dialog_tool._bekleyen_dialoglar.clear()
    sonuc = browser_dialog_tool.run(islem="bekle")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"
    assert "bulunamadı" in data["mesaj"]


def test_dialog_kaydet_ve_cevapla():
    browser_dialog_tool._bekleyen_dialoglar.clear()
    browser_dialog_tool._dialog_cevaplari.clear()
    dialog_id = browser_dialog_tool._dialog_kaydet(
        "test_dialog", "alert", "Test mesajı"
    )
    assert dialog_id == "test_dialog"
    assert browser_dialog_tool._dialog_cevapla(dialog_id, "OK") is True
    assert browser_dialog_tool._bekleyen_dialoglar[dialog_id]["cevaplandi"] is True


def test_dialog_cevapla_nonexistent():
    assert browser_dialog_tool._dialog_cevapla("yok", "cevap") is False


def test_dialog_gec():
    browser_dialog_tool._bekleyen_dialoglar.clear()
    browser_dialog_tool._dialog_kaydet("dialog2", "confirm", "Emin misiniz?")
    assert browser_dialog_tool._dialog_gec("dialog2") is True
    assert browser_dialog_tool._bekleyen_dialoglar["dialog2"]["gecildi"] is True


def test_dialog_gec_nonexistent():
    assert browser_dialog_tool._dialog_gec("yok") is False


def test_run_cevapla():
    browser_dialog_tool._bekleyen_dialoglar.clear()
    browser_dialog_tool._dialog_kaydet("d1", "prompt", "Adınız?")
    sonuc = browser_dialog_tool.run(islem="cevapla", dialog_turu="d1", cevap="Ahmet")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_cevapla_nonexistent():
    sonuc = browser_dialog_tool.run(islem="cevapla", dialog_turu="yok", cevap="x")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_cevapla_no_id():
    sonuc = browser_dialog_tool.run(islem="cevapla", cevap="x")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_gec():
    browser_dialog_tool._bekleyen_dialoglar.clear()
    browser_dialog_tool._dialog_kaydet("d2", "confirm", "Onaylıyor musun?")
    sonuc = browser_dialog_tool.run(islem="gec", dialog_turu="d2")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_gec_nonexistent():
    sonuc = browser_dialog_tool.run(islem="gec", dialog_turu="yok")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_gec_no_id():
    sonuc = browser_dialog_tool.run(islem="gec")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_invalid_islem():
    sonuc = browser_dialog_tool.run(islem="gecersiz")
    data = json.loads(sonuc)
    assert "bilinmeyen" in str(data)


def test_dialog_bekle_with_filter():
    browser_dialog_tool._bekleyen_dialoglar.clear()
    browser_dialog_tool._dialog_kaydet("alert1", "alert", "Uyarı!")
    # Direct test of the _dialog_bekle with filter
    dialog = browser_dialog_tool._dialog_bekle(dialog_turu="alert", timeout=1)
    # Should find it since it's unresponded
    assert dialog is not None
    assert dialog["tur"] == "alert"
