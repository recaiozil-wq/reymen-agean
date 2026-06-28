# -*- coding: utf-8 -*-
"""python_exec modülü testleri."""
from unittest.mock import MagicMock, patch
from tools import python_exec


def test_run_kod_bos():
    """Boş kod ile hata mesajı döndürür."""
    sonuc = python_exec.run("")
    assert "gerekli" in sonuc


def test_run_success():
    """Başarılı Python çalıştırma (gerçek subprocess ile)."""
    sonuc = python_exec.run("print('Merhaba Dunya')")
    assert "Merhaba Dunya" in sonuc


def test_run_with_stderr():
    """Stderr çıktısı olan durum."""
    sonuc = python_exec.run("import sys; print('test', file=sys.stderr)")
    assert "test" in sonuc


def test_run_timeout():
    """Zaman aşımı durumu - kısa kod çalışır."""
    sonuc = python_exec.run("print('hizli')", timeout=5)
    assert "hizli" in sonuc
