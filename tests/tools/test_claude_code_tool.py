# -*- coding: utf-8 -*-
"""Test: claude_code_tool.py — Claude Code işbirliği aracı."""

from unittest.mock import patch, MagicMock
from tools import claude_code_tool


def test_claude_yardim_no_gorev():
    sonuc = claude_code_tool.claude_yardim("")
    assert "boş" in sonuc


def test_claude_analiz_no_metin():
    sonuc = claude_code_tool.claude_analiz("")
    assert "gerekli" in sonuc


def test_claude_kod_yaz_no_aciklama():
    sonuc = claude_code_tool.claude_kod_yaz("")
    assert "boş" in sonuc


def test_claude_hata_ayikla_no_input():
    sonuc = claude_code_tool.claude_hata_ayikla("")
    assert "boş" in sonuc


def test_claude_plan_no_hedef():
    sonuc = claude_code_tool.claude_plan("")
    assert "boş" in sonuc


def test_claude_revize_no_input():
    sonuc = claude_code_tool.claude_revize("")
    assert "boş" in sonuc


def test_claude_durum_no_exe():
    with patch("tools.claude_code_tool._CLAUDE_EXE", None):
        sonuc = claude_code_tool.claude_durum()
        assert "bulunamadı" in sonuc


def test_claude_calistir_no_exe():
    with patch("tools.claude_code_tool._CLAUDE_EXE", None):
        sonuc = claude_code_tool.claude_yardim("test")
        assert "bulunamadı" in sonuc


def test_claude_calistir_exe_not_exists():
    with patch("tools.claude_code_tool._CLAUDE_EXE", "/nonexistent/claude.exe"):
        with patch("pathlib.Path.exists", return_value=False):
            sonuc = claude_code_tool.claude_yardim("test")
            assert "bulunamadı" in sonuc


@patch("tools.claude_code_tool.subprocess.run")
def test_claude_calistir_success(mock_run):
    with patch("tools.claude_code_tool._CLAUDE_EXE", "/usr/bin/claude"):
        with patch("pathlib.Path.exists", return_value=True):
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Merhaba dünya"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            sonuc = claude_code_tool.claude_yardim("test görev")
            assert "Merhaba" in sonuc


@patch("tools.claude_code_tool.subprocess.run")
def test_claude_calistir_nonzero(mock_run):
    with patch("tools.claude_code_tool._CLAUDE_EXE", "/usr/bin/claude"):
        with patch("pathlib.Path.exists", return_value=True):
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stdout = ""
            mock_proc.stderr = "hata mesajı"
            mock_run.return_value = mock_proc
            sonuc = claude_code_tool.claude_yardim("test")
            assert "Hata" in sonuc or "hata" in sonuc


@patch(
    "tools.claude_code_tool.subprocess.run", side_effect=Exception("Beklenmeyen hata")
)
def test_claude_calistir_exception(mock_run):
    with patch("tools.claude_code_tool._CLAUDE_EXE", "/usr/bin/claude"):
        with patch("pathlib.Path.exists", return_value=True):
            sonuc = claude_code_tool.claude_yardim("test")
            assert "Hata" in sonuc


def test_motor_kaydet():
    motor = MagicMock()
    claude_code_tool.motor_kaydet(motor)
    assert motor._plugin_arac_kaydet.call_count >= 7


@patch("tools.claude_code_tool.subprocess.run")
def test_claude_durum_with_version(mock_run):
    with patch("tools.claude_code_tool._CLAUDE_EXE", "/usr/bin/claude"):
        with patch("pathlib.Path.exists", return_value=True):
            mock_proc = MagicMock()
            mock_proc.stdout = "0.1.0"
            mock_proc.stderr = ""
            mock_run.return_value = mock_proc
            sonuc = claude_code_tool.claude_durum()
            assert "Hazır" in sonuc
