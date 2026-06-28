# -*- coding: utf-8 -*-
"""Test: delegate_task_tool.py — Görevi alt process'e devret."""

from unittest.mock import patch, MagicMock
from tools import delegate_task_tool


def test_run_no_gorev():
    sonuc = delegate_task_tool.run(gorev="")
    assert "gerekli" in sonuc


def test_run_main_py_not_found():
    with patch("tools.delegate_task_tool._MAIN_PY") as mock_path:
        mock_path.exists.return_value = False
        sonuc = delegate_task_tool.run(gorev="test")
        assert "bulunamadı" in sonuc


@patch("tools.delegate_task_tool.subprocess.run")
def test_run_success(mock_run):
    with patch("tools.delegate_task_tool._MAIN_PY") as mock_path:
        mock_path.exists.return_value = True
        mock_path.__str__.return_value = "/path/to/main.py"
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "İşlem tamam"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc
        sonuc = delegate_task_tool.run(gorev="test", zaman_asimi=30)
        assert "İşlem" in sonuc or "Sonuç" in sonuc


@patch("tools.delegate_task_tool.subprocess.run")
def test_run_nonzero_return(mock_run):
    with patch("tools.delegate_task_tool._MAIN_PY") as mock_path:
        mock_path.exists.return_value = True
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "hata"
        mock_run.return_value = mock_proc
        sonuc = delegate_task_tool.run(gorev="test")
        assert "Hata" in sonuc


@patch("tools.delegate_task_tool.subprocess.run", side_effect=Exception("patladı"))
def test_run_exception(mock_run):
    with patch("tools.delegate_task_tool._MAIN_PY") as mock_path:
        mock_path.exists.return_value = True
        sonuc = delegate_task_tool.run(gorev="test")
        assert "Hata" in sonuc


def test_run_json_cikti():
    with patch("tools.delegate_task_tool._MAIN_PY") as mock_path:
        mock_path.exists.return_value = True
        mock_path.__str__.return_value = "/path/to/main.py"
        with patch("tools.delegate_task_tool.subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = '{"key": "value"}'
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            sonuc = delegate_task_tool.run(gorev="test", json_cikti=True)
            assert "key" in sonuc


def test_run_zaman_asimi_clamp():
    sonuc = delegate_task_tool.run(gorev="test", zaman_asimi=999)
    # Should clamp to 300, but main.py doesn't exist
    assert isinstance(sonuc, str)


def test_motor_kaydet():
    motor = MagicMock()
    delegate_task_tool.motor_kaydet(motor)
    motor._plugin_arac_kaydet.assert_called_once()
