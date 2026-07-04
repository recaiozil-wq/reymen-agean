# -*- coding: utf-8 -*-
"""Test: read_terminal_tool.py — Terminal buffer okuma aracı."""

from unittest.mock import patch
from tools import read_terminal_tool


def setup_function():
    """Her test öncesi buffer'ı temizle."""
    read_terminal_tool._TERMINAL_BUFFER.clear()


def test_buffer_baslangic_bos():
    """Başlangıçta buffer boştur."""
    assert len(read_terminal_tool._TERMINAL_BUFFER) == 0


def test_buffer_ekle():
    """_buffer_ekle satır ekler."""
    read_terminal_tool._buffer_ekle("test satir")
    assert len(read_terminal_tool._TERMINAL_BUFFER) == 1
    assert read_terminal_tool._TERMINAL_BUFFER[0] == "test satir"


def test_run_tumu():
    """run(islem='tumu') tüm buffer'ı döndürür."""
    read_terminal_tool._buffer_ekle("satir 1")
    read_terminal_tool._buffer_ekle("satir 2")
    sonuc = read_terminal_tool.run(islem="tumu")
    assert "satir 1" in sonuc
    assert "satir 2" in sonuc


def test_run_son_n():
    """run(islem='son_n') son n satırı döndürür."""
    for i in range(10):
        read_terminal_tool._buffer_ekle(f"satir {i}")
    sonuc = read_terminal_tool.run(islem="son_n", n=3)
    assert "satir 7" in sonuc
    assert "satir 9" in sonuc


def test_run_ara():
    """run(islem='ara') regex ile arar."""
    read_terminal_tool._buffer_ekle("hata: dosya bulunamadi")
    read_terminal_tool._buffer_ekle("bilgi: islem tamam")
    sonuc = read_terminal_tool.run(islem="ara", desen="hata")
    assert "hata" in sonuc


def test_run_ara_no_desen():
    """ara işlemi desen olmadan hata döndürür."""
    sonuc = read_terminal_tool.run(islem="ara")
    assert "desen" in sonuc


def test_run_bos_buffer():
    """Boş buffer'da run çalışır."""
    sonuc = read_terminal_tool.run(islem="tumu")
    assert "boş" in sonuc or "bos" in sonuc.lower()


def test_run_gecersiz_islem():
    """Geçersiz işlem hata döndürür."""
    sonuc = read_terminal_tool.run(islem="bilinmeyen")
    assert "Hata" in sonuc


def test_buffer_max_10000():
    """Buffer maksimum 10000 satır tutar."""
    for i in range(10050):
        read_terminal_tool._buffer_ekle(f"line {i}")
    assert len(read_terminal_tool._TERMINAL_BUFFER) <= 10000
