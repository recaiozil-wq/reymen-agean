# -*- coding: utf-8 -*-
"""Test: lsp_tool.py — LSP (Language Server Protocol) entegrasyonu."""

from unittest.mock import patch, MagicMock
from tools import lsp_tool


def test_dil_bul_python():
    assert lsp_tool._dil_bul("/path/test.py") == "python"


def test_dil_bul_javascript():
    assert lsp_tool._dil_bul("/path/test.js") == "javascript"


def test_dil_bul_typescript():
    assert lsp_tool._dil_bul("/path/test.ts") == "typescript"


def test_dil_bul_json():
    assert lsp_tool._dil_bul("/path/test.json") == "json"


def test_dil_bul_unknown():
    assert lsp_tool._dil_bul("/path/test.xyz") == "python"


def test_lsp_client_init():
    client = lsp_tool.LspClient(root_uri="file:///test")
    assert client.hazir is False
    assert client._root_uri == "file:///test"


def test_lsp_client_diagnostik_al_not_ready():
    client = lsp_tool.LspClient()
    result = client.diagnostik_al("test.py", "content")
    assert len(result) == 1
    assert "hazir degil" in result[0]["mesaj"]


def test_lsp_client_tamamlama_al_not_ready():
    client = lsp_tool.LspClient()
    result = client.tamamlama_al("test.py", "content", 1, 1)
    assert result == []


def test_lsp_client_hover_al_not_ready():
    client = lsp_tool.LspClient()
    result = client.hover_al("test.py", "content", 1, 1)
    assert result == ""


def test_lsp_client_tanima_git_not_ready():
    client = lsp_tool.LspClient()
    result = client.tanima_git("test.py", "content", 1, 1)
    assert result == []


def test_lsp_client_formatla_not_ready():
    client = lsp_tool.LspClient()
    result = client.formatla("test.py", "content")
    assert result == "content"


def test_lsp_client_referanslari_bul_not_ready():
    client = lsp_tool.LspClient()
    result = client.referanslari_bul("test.py", "content", 1, 1)
    assert result == []


@patch("tools.lsp_tool.subprocess.Popen")
def test_lsp_client_baslat_no_server(mock_popen):
    """pylsp yoksa FileNotFoundError döner."""
    mock_popen.side_effect = FileNotFoundError("pylsp not found")
    client = lsp_tool.LspClient()
    result = client.baslat("python")
    assert result is False


def test_lsp_client_durdur_not_started():
    client = lsp_tool.LspClient()
    client.durdur()  # should not raise


def test_lsp_client_context_manager():
    with lsp_tool.LspClient() as client:
        assert client is not None


def test_lsp_servers_config():
    assert "python" in lsp_tool.LSP_SERVERS
    assert "javascript" in lsp_tool.LSP_SERVERS
    assert "default" in lsp_tool.LSP_SERVERS
    assert lsp_tool.LSP_SERVERS["default"]["language_id"] == "python"
