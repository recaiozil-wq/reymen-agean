# -*- coding: utf-8 -*-
"""Test: feishu_drive_tool.py — Feishu Drive yönetimi (urllib mock)."""

from unittest.mock import patch, MagicMock
from tools import feishu_drive_tool

_TOKEN_RESPONSE = b'{"tenant_access_token": "fake_token", "expire": 7200}'


def test_run_no_islem():
    sonuc = feishu_drive_tool.run()
    assert "Hata" in sonuc


def test_run_no_token():
    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", ""):
        with patch("tools.feishu_drive_tool.FEISHU_APP_SECRET", ""):
            sonuc = feishu_drive_tool.run(islem="listele")
            assert "Hata" in sonuc
            assert "token" in sonuc.lower()


@patch("tools.feishu_drive_tool.urllib.request.urlopen")
def test_run_listele(mock_urlopen):
    mock_resp_token = MagicMock()
    mock_resp_token.read.return_value = _TOKEN_RESPONSE
    mock_resp_files = MagicMock()
    mock_resp_files.read.return_value = b'{"data": {"files": []}}'
    mock_urlopen.return_value.__enter__.side_effect = [mock_resp_token, mock_resp_files]

    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_drive_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_drive_tool.run(islem="listele")
            assert isinstance(sonuc, str)


@patch("tools.feishu_drive_tool.urllib.request.urlopen")
def test_run_listele_with_files(mock_urlopen):
    mock_resp_token = MagicMock()
    mock_resp_token.read.return_value = _TOKEN_RESPONSE
    mock_resp_files = MagicMock()
    mock_resp_files.read.return_value = b'{"data": {"files": [{"token": "t1", "name": "file1", "type": "file", "size": 100}]}}'
    mock_urlopen.return_value.__enter__.side_effect = [mock_resp_token, mock_resp_files]

    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_drive_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_drive_tool.run(islem="listele")
            assert "file1" in sonuc


def test_run_indir_no_token():
    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", ""):
        sonuc = feishu_drive_tool.run(islem="indir")
        assert "Hata" in sonuc


def test_run_yukle_no_dosya():
    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", "test_id"):
        with patch("tools.feishu_drive_tool.FEISHU_APP_SECRET", "test_secret"):
            sonuc = feishu_drive_tool.run(islem="yukle")
            assert "Hata" in sonuc


def test_run_invalid_islem():
    sonuc = feishu_drive_tool.run(islem="gecersiz")
    assert "Hata" in sonuc


def test_tenant_access_token_al_no_creds():
    with patch("tools.feishu_drive_tool.FEISHU_APP_ID", ""):
        with patch("tools.feishu_drive_tool.FEISHU_APP_SECRET", ""):
            token = feishu_drive_tool._tenant_access_token_al()
            assert token == ""


def test_dosya_yukle_not_found():
    with patch("tools.feishu_drive_tool.os.path.exists", return_value=False):
        sonuc = feishu_drive_tool._dosya_yukle("/nonexistent", "", "token")
        assert "bulunamadi" in sonuc
