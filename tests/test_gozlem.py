# -*- coding: utf-8 -*-
"""gozlem.py icin pytest testleri."""

import os
import sys
import time

import pytest

sys.path.insert(0, ".")

from gozlem import Gozlemci, gozlemci, GOZLEM_DIZINI


class TestGozlemci:
    """Gozlemci birim testleri."""

    def setup_method(self):
        self.gz = Gozlemci()

    def test_kaydet_basit(self):
        """Basit kayit calismali."""
        self.gz.kaydet("t001", 1.5, "test yanit")
        ozet = self.gz.task_ozet("t001")
        assert ozet["cagri_sayisi"] == 1
        assert ozet["toplam_sure_sn"] == 1.5

    def test_coklu_kayit(self):
        """Ayni task'a birden cok kayit eklenebilmeli."""
        self.gz.kaydet("t002", 0.5, "a")
        self.gz.kaydet("t002", 1.0, "b")
        self.gz.kaydet("t002", 2.0, "c")
        ozet = self.gz.task_ozet("t002")
        assert ozet["cagri_sayisi"] == 3
        assert ozet["ortalama_sure_sn"] == pytest.approx(1.166, 0.1)

    def test_basarisiz_kayit(self):
        """Basarisiz (timeout) kaydi."""
        self.gz.kaydet("t003", 25.0, "", basarili=False, notlar="TIMEOUT")
        ozet = self.gz.task_ozet("t003")
        assert ozet["cagri_sayisi"] == 1
        assert ozet["basarisiz"] == 1
        assert ozet["basarili"] == 0

    def test_genel_ozet(self):
        """Genel ozet dogru calismali."""
        self.gz.kaydet("t004", 1.0, "x")
        self.gz.kaydet("t005", 2.0, "y")
        genel = self.gz.genel_ozet()
        assert genel["toplam_cagri"] == 2
        assert genel["aktif_task"] == 2

    def test_token_sayisi(self):
        """Token sayisi dogru hesaplanmali (4chr ≈ 1 token)."""
        self.gz.kaydet("t006", 0.5, "Merhaba dunya!")  # 14 chars → 3 token
        ozet = self.gz.task_ozet("t006")
        assert ozet["toplam_cikti_token"] == 3

    def test_girdi_token_manuel(self):
        """Girdi token manuel verilebilmeli."""
        self.gz.kaydet("t007", 0.5, "cevap", girdi_token=100, cikti_token=50)
        ozet = self.gz.task_ozet("t007")
        assert ozet["toplam_girdi_token"] == 100
        assert ozet["toplam_cikti_token"] == 50

    def test_maliyet_hesaplama(self):
        """Maliet sifirdan buyuk olmali (varsayilan fiyatla)."""
        self.gz.kaydet("t008", 1.0, "x" * 400)  # ~100 token
        ozet = self.gz.task_ozet("t008")
        assert ozet["tahmini_maliyet_usd"] > 0

    def test_farkli_task_ozetleri(self):
        """Farkli task'lar ayri ozetlere sahip."""
        self.gz.kaydet("t009", 1.0, "a")
        self.gz.kaydet("t010", 2.0, "b")
        assert self.gz.task_ozet("t009")["cagri_sayisi"] == 1
        assert self.gz.task_ozet("t010")["cagri_sayisi"] == 1

    def test_temizle(self):
        """Temizleme sonrasi genel ozet sifirlanmali."""
        self.gz.kaydet("t011", 0.5, "x")
        self.gz.temizle()
        genel = self.gz.genel_ozet()
        assert genel["toplam_cagri"] == 0

    def test_bos_genel_ozet(self):
        """Hic kayit yokken genel_ozet calismali."""
        gz2 = Gozlemci()
        genel = gz2.genel_ozet()
        assert genel["toplam_cagri"] == 0
        assert genel["aktif_task"] == 0

    def test_disk_log_var(self):
        """Disk log dosyasi olusmali."""
        self.gz.kaydet("t012", 0.5, "disk log test")
        log_path = GOZLEM_DIZINI / "gozlem_log.txt"
        assert log_path.exists()
        assert log_path.stat().st_size > 0
