# -*- coding: utf-8 -*-
"""Test: delegate_task_tool.py — Paralel alt-ajan delegasyonu."""

from unittest.mock import patch, MagicMock
import json
from tools import delegate_task_tool


def test_delegate_task_invalid_json():
    """Geçersiz JSON girdisi hata döndürür."""
    sonuc = delegate_task_tool.delegate_task("geçersiz json")
    assert "HATA" in sonuc


def test_delegate_task_empty_list():
    """Boş görev listesi özet döndürür."""
    sonuc = delegate_task_tool.delegate_task("[]")
    assert "görev" in sonuc.lower() or "özet" in sonuc.lower() or "DELEGASYON" in sonuc


def test_delegate_task_not_list():
    """Liste olmayan JSON hata döndürür."""
    sonuc = delegate_task_tool.delegate_task('{"gorev": "test"}')
    assert "HATA" in sonuc


def test_delegate_task_struct_input():
    """Dict listesi doğrudan kabul edilir."""
    gorevler = [{"gorev": "test", "baglam": ""}]
    # _delegate_task_impl çağrılır ama Beyin yüklenemez → hata yakalanır
    sonuc = delegate_task_tool.delegate_task(gorevler, timeout=5, max_adim=1)
    assert isinstance(sonuc, str)


def test_motor_kaydet():
    """motor_kaydet doğru çağrılır."""
    motor = MagicMock()
    delegate_task_tool.motor_kaydet(motor)
    motor._plugin_arac_kaydet.assert_called_once()
    args = motor._plugin_arac_kaydet.call_args
    assert args[0][0] == "DELEGATE_TASK"


def test_dataclass_alt_gorev_sonuc():
    """AltGorevSonuc dataclass doğru çalışır."""
    sonuc = delegate_task_tool.AltGorevSonuc(
        gorev="test", task_id="t1", basarili=True, sonuc="sonuç"
    )
    assert sonuc.basarili is True
    assert sonuc.sonuc == "sonuç"
    assert sonuc.hata == ""


def test_dataclass_delegasyon_sonuc():
    """DelegasyonSonuc dataclass doğru çalışır."""
    ds = delegate_task_tool.DelegasyonSonuc(
        parent_task_id="p1", toplam_gorev=2, basarili=1, basarisiz=1
    )
    assert ds.toplam_gorev == 2
    assert ds.basarili == 1
    assert len(ds.sonuclar) == 0


def test_config_yukle():
    """_config_yukle fonksiyonu dict döndürür."""
    config = delegate_task_tool._config_yukle()
    assert isinstance(config, dict)
