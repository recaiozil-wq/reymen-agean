# -*- coding: utf-8 -*-
"""Test: code_execution_tool.py — Kod çalıştırma sandbox."""

from unittest.mock import patch, MagicMock
import json
from tools import code_execution_tool


def test_run_no_kod():
    sonuc = code_execution_tool.run()
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"
    assert "kod" in data["hata"]


def test_run_basic():
    sonuc = code_execution_tool.run(kod="print('merhaba'); x = 2 + 2")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"
    assert "merhaba" in data.get("cikti", "")


def test_run_syntax_error():
    sonuc = code_execution_tool.run(kod="if True print('hata')")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_timeout():
    """Timeout test: Windows'ta SIGALRM yok, mock ile test edilir."""
    with patch("tools.code_execution_tool._guvenli_calistir") as mock_guvenli:
        mock_guvenli.return_value = '{"durum": "zaman_asimi", "hata": "Kod 1 saniyede tamamlanamadi.", "cikti": "", "hata_metni": "Zaman asimi"}'
        sonuc = code_execution_tool.run(kod="while True: pass", timeout=1)
        assert "zaman" in sonuc.lower()


def test_run_guvensiz():
    """_guvensiz_calistir mock ile test edilir."""
    with patch("tools.code_execution_tool._guvensiz_calistir") as mock_guvensiz:
        mock_guvensiz.return_value = '{"durum": "basarili", "cikti": "guvensiz", "hata_metni": ""}'
        sonuc = code_execution_tool.run(kod="print('guvensiz')", guvenli=False)
        data = json.loads(sonuc)
        assert data.get("durum") == "basarili"


def test_run_guvenli_string():
    sonuc = code_execution_tool.run(kod="print('test')", guvenli="true")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_timeout_clamp():
    sonuc = code_execution_tool.run(kod="print('a')", timeout=999)
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_ping():
    assert code_execution_tool.ping() is True


def test_execute_code():
    sonuc = code_execution_tool.execute_code("print('test')")
    data = json.loads(sonuc)
    assert "output" in data


def test_generate_ReYMeN_tools_module():
    result = code_execution_tool.generate_ReYMeN_tools_module()
    assert isinstance(result, str)


def test_sandbox_allowed_tools():
    assert "read_file" in code_execution_tool.SANDBOX_ALLOWED_TOOLS
