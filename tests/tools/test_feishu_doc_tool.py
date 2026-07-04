# -*- coding: utf-8 -*-
"""Test: feishu_doc_tool.py — Feishu dokuman yönetimi (urllib mock)."""

from unittest.mock import patch, MagicMock
from tools import feishu_doc_tool

# Tenant access token response
_TOKEN_RESPONSE = b'{"tenant_access_token": "fake_token", "expire": 7200}'


def test_run_no_islem():
    sonuc = feishu_doc_tool.run()
    assert "Hata" in sonuc


def test_run_no_token():
    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", ""):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", ""):
            sonuc = feishu_doc_tool.run(islem="listele")
            assert "Hata" in sonuc
            assert "token" in sonuc.lower()


@patch("tools.feishu_doc_tool.urllib.request.urlopen")
def test_run_listele(mock_urlopen):
    # First call (token): return token response
    # Second call (list): return empty files
    mock_resp_token = MagicMock()
    mock_resp_token.read.return_value = _TOKEN_RESPONSE
    mock_resp_files = MagicMock()
    mock_resp_files.read.return_value = b'{"data": {"files": []}}'
    mock_urlopen.return_value.__enter__.side_effect = [mock_resp_token, mock_resp_files]

    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_doc_tool.run(islem="listele")
            assert isinstance(sonuc, str)


@patch("tools.feishu_doc_tool.urllib.request.urlopen")
def test_run_listele_with_files(mock_urlopen):
    mock_resp_token = MagicMock()
    mock_resp_token.read.return_value = _TOKEN_RESPONSE
    mock_resp_files = MagicMock()
    mock_resp_files.read.return_value = (
        b'{"data": {"files": [{"token": "t1", "name": "doc1", "type": "doc"}]}}'
    )
    mock_urlopen.return_value.__enter__.side_effect = [mock_resp_token, mock_resp_files]

    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_doc_tool.run(islem="listele")
            assert "doc1" in sonuc


def test_run_oku_no_doc_token():
    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_doc_tool.run(islem="oku")
            assert "Hata" in sonuc


def test_run_yaz_no_icerik():
    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_doc_tool.run(islem="yaz")
            assert "Hata" in sonuc


def test_run_ara_no_sorgu():
    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_doc_tool.run(islem="ara")
            assert "Hata" in sonuc


def test_run_invalid_islem():
    sonuc = feishu_doc_tool.run(islem="gecersiz")
    assert "Hata" in sonuc


def test_tenant_access_token_al_no_creds():
    with patch("tools.feishu_doc_tool.FEISHU_APP_ID", ""):
        with patch("tools.feishu_doc_tool.FEISHU_APP_SECRET", ""):
            token = feishu_doc_tool._tenant_access_token_al()
            assert token == ""
