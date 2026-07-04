# -*- coding: utf-8 -*-
"""Test: fal_common.py — Fal.ai ortak işlevler (requests mock)."""

from unittest.mock import patch, MagicMock
from tools import fal_common


def test_run_token_kontrol_no_key():
    with patch("tools.fal_common._FAL_TOKEN", ""):
        sonuc = fal_common.run(islem="token_kontrol")
        assert "bulunamadı" in sonuc


def test_run_token_kontrol_with_key():
    with patch("tools.fal_common._FAL_TOKEN", "test_key_1234567890"):
        sonuc = fal_common.run(islem="token_kontrol")
        assert "mevcut" in sonuc.lower()


def test_run_token_kontrol_short_key():
    with patch("tools.fal_common._FAL_TOKEN", "short"):
        sonuc = fal_common.run(islem="token_kontrol")
        assert "mevcut" in sonuc.lower()


def test_run_api_cagir_no_endpoint():
    with patch("tools.fal_common._FAL_TOKEN", "test_key"):
        sonuc = fal_common.run(islem="api_cagir")
        assert "Hata" in sonuc


def test_run_api_cagir_no_token():
    with patch("tools.fal_common._FAL_TOKEN", ""):
        sonuc = fal_common.run(islem="api_cagir", endpoint="/test")
        assert "Hata" in sonuc


def test_run_api_cagir_success():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"status": "ok"}'
        mock_post.return_value = mock_resp
        with patch("tools.fal_common._FAL_TOKEN", "test_key"):
            sonuc = fal_common.run(
                islem="api_cagir", endpoint="/test", parametreler={"key": "val"}
            )
            assert "200" in sonuc


def test_run_queue_bekle_no_request_id():
    sonuc = fal_common.run(islem="queue_bekle")
    assert "Hata" in sonuc


def test_run_queue_bekle():
    with patch("tools.fal_common.time.sleep", return_value=None):
        with patch("tools.fal_common.time.time", side_effect=[100.0, 102.0, 0.0]):
            sonuc = fal_common.run(
                islem="queue_bekle", request_id="abc123", max_bekle=1, aralik=1
            )
    assert "zaman aşımı" in sonuc


def test_run_invalid_islem():
    sonuc = fal_common.run(islem="gecersiz")
    assert "Geçersiz" in sonuc


def test_rate_limit_kontrol():
    fal_common._rate_limit_kontrol()
