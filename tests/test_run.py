# -*- coding: utf-8 -*-
"""tests/test_run.py — GatewayRunner birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from unittest.mock import MagicMock, patch
from gateway.run import GatewayRunner, _logging_kur


class TestGatewayRunner:
    def test_init(self):
        runner = GatewayRunner(polling_interval=1.0)
        assert runner._calisiyor is False
        assert runner._polling_interval == 1.0
        assert runner._baslatilan_platform_sayisi == 0
        assert runner._hata_sayisi == 0

    @patch("gateway.run.GatewayRunner.platformlari_yukle", return_value={})
    def test_calistir_no_platforms(self, mock_yukle):
        runner = GatewayRunner()
        runner.calistir()
        assert runner._baslangic_zamani is not None

    def test_durdur_not_calisiyor(self):
        runner = GatewayRunner()
        runner.durdur()  # should not raise

    @patch("gateway.run.GatewayRunner.platformlari_yukle")
    @patch("gateway.run.GatewayRunner.tumunu_baslat")
    @patch("gateway.run.GatewayRunner.sinyal_yoneticisi_kur")
    def test_calistir_flow(self, mock_sinyal, mock_baslat, mock_yukle):
        mock_yukle.return_value = {"telegram": {}}
        runner = GatewayRunner()
        # will raise KeyboardInterrupt to exit loop
        import time as _time
        orig_sleep = _time.sleep
        def break_sleep(s):
            runner._calisiyor = False
        with patch("time.sleep", break_sleep):
            runner.calistir()
        assert runner._calisiyor is False

    def test_platformlari_yukle_no_gateway_platforms(self):
        runner = GatewayRunner()
        result = runner.platformlari_yukle()
        # should handle ImportError gracefully
        assert isinstance(result, dict)

    def test_durum_ozeti(self):
        runner = GatewayRunner()
        ozet = runner.durum_ozeti()
        assert ozet["calisiyor"] is False
        assert ozet["platform_sayisi"] == 0
        assert ozet["hata_sayisi"] == 0

    def test_logging_kur(self):
        _logging_kur()  # should not raise

    def test_sinyal_yoneticisi_kur_kaldir(self):
        runner = GatewayRunner()
        runner.sinyal_yoneticisi_kur()
        runner.sinyal_yoneticisi_kaldir()
        # should not raise and handlers should be cleared
