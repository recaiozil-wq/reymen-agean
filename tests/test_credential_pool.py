# -*- coding: utf-8 -*-
"""test_credential_pool.py — CredentialPool testleri."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import sys
import os as _os

# Add project root to path
_proj = str(Path(__file__).resolve().parent.parent)
if _proj not in sys.path:
    sys.path.insert(0, _proj)

from reymen.sistem.credential_pool import (
    CredentialPool,
    _ANAHTAR_KAYNAKLARI,
    _platform_env_yolu,
    ReYMeN_ENV,
    anahtar_al,
)


class TestPlatformEnvYolu:
    def test_returns_path_object(self):
        result = _platform_env_yolu()
        assert isinstance(result, Path)

    def test_ends_with_env(self):
        result = _platform_env_yolu()
        assert result.name == ".env"

    def test_contains_reymen(self):
        result = _platform_env_yolu()
        assert "ReYMeN" in str(result) or "reymen" in str(result)


class TestCredentialPoolInit:
    def test_empty_cache(self):
        pool = CredentialPool()
        assert pool._cache == {}

    def test_kaynak_sirasi(self):
        pool = CredentialPool()
        assert "ReYMeN_env" in pool._kaynak_sirasi


class TestEnvOku:
    def test_valid_env(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DEEPSEEK_API_KEY=sk-test123\nOPENAI_API_KEY=sk-abc\n", encoding="utf-8"
        )
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert result["DEEPSEEK_API_KEY"] == "sk-test123"
        assert result["OPENAI_API_KEY"] == "sk-abc"

    def test_empty_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert result == {}

    def test_comments_skipped(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# yorum satiri\nDEEPSEEK_API_KEY=sk-test\n", encoding="utf-8"
        )
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert len(result) == 1
        assert result["DEEPSEEK_API_KEY"] == "sk-test"

    def test_missing_file(self, tmp_path):
        pool = CredentialPool()
        result = pool._env_oku(tmp_path / "nonexistent.env")
        assert result == {}

    def test_stars_masked(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=***REDACTED***\n", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert "KEY" not in result

    def test_quoted_values(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('KEY="value123"\n', encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert result["KEY"] == "value123"

    def test_single_quoted(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("KEY='hello'\n", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert result["KEY"] == "hello"

    def test_no_equals_skipped(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("BROKEN_LINE\nKEY=val\n", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert len(result) == 1

    def test_empty_values_skipped(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("EMPTY=\nKEY=val\n", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert "EMPTY" not in result

    def test_value_with_equals(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("URL=https://x.com?a=1&b=2\n", encoding="utf-8")
        pool = CredentialPool()
        result = pool._env_oku(env_file)
        assert result["URL"] == "https://x.com?a=1&b=2"


class TestAl:
    def test_cache_hit(self):
        pool = CredentialPool()
        pool._cache["TEST_KEY"] = "cached_val"
        assert pool.al("TEST_KEY") == "cached_val"

    def test_env_fallback(self):
        pool = CredentialPool()
        with patch.dict(os.environ, {"SOME_RARE_KEY_12345": "env_value"}):
            # Clear cache and _ANAHTAR_KAYNAKLARI doesn't have it, so returns env
            result = pool.al("SOME_RARE_KEY_12345")
            assert result == "env_value"

    def test_not_found_returns_empty(self):
        pool = CredentialPool()
        result = pool.al("NONEXISTENT_KEY_99999")
        assert result == ""

    def test_cache_populated_after_first_al(self):
        pool = CredentialPool()
        with patch.dict(os.environ, {"CACHE_TEST_KEY": "val"}):
            pool.al("CACHE_TEST_KEY")
            assert "CACHE_TEST_KEY" in pool._cache

    def test_masked_env_not_used(self):
        pool = CredentialPool()
        with patch.dict(os.environ, {"BAD_KEY": "***MASKED***"}):
            result = pool.al("BAD_KEY")
            assert result == ""


class TestTumAnahtarlar:
    def test_returns_dict(self):
        pool = CredentialPool()
        result = pool.tum_anahtarlar()
        assert isinstance(result, dict)

    def test_all_known_keys(self):
        pool = CredentialPool()
        result = pool.tum_anahtarlar()
        for key in _ANAHTAR_KAYNAKLARI:
            assert key in result

    def test_masked_values(self):
        pool = CredentialPool()
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-1234567890"}):
            pool._cache.clear()
            result = pool.tum_anahtarlar()
            assert (
                "***" in result["DEEPSEEK_API_KEY"]
                or result["DEEPSEEK_API_KEY"] == "YOK"
            )

    def test_short_values_not_masked(self):
        pool = CredentialPool()
        pool._cache["TELEGRAM_BOT_TOKEN"] = "abc"
        result = pool.tum_anahtarlar()
        # short value (< 6 chars) returned as-is
        assert result["TELEGRAM_BOT_TOKEN"] == "abc"


class TestDurum:
    def test_returns_string(self):
        pool = CredentialPool()
        result = pool.durum()
        assert isinstance(result, str)

    def test_contains_header(self):
        pool = CredentialPool()
        result = pool.durum()
        assert "CredentialPool" in result

    def test_shows_count(self):
        pool = CredentialPool()
        result = pool.durum()
        assert "/" in result  # format: X/Y anahtar


class TestTemizle:
    def test_clears_cache(self):
        pool = CredentialPool()
        pool._cache["foo"] = "bar"
        pool.temizle()
        assert pool._cache == {}


class TestAnahtarAl:
    def test_global_function(self):
        with patch.dict(os.environ, {"GLOBAL_TEST_KEY": "global_val"}):
            result = anahtar_al("GLOBAL_TEST_KEY")
            assert result == "global_val"

    def test_not_found(self):
        result = anahtar_al("NO_SUCH_KEY_XYZ")
        assert result == ""


class TestAnahtarKaynaklari:
    def test_has_deepseek(self):
        assert "DEEPSEEK_API_KEY" in _ANAHTAR_KAYNAKLARI

    def test_has_openai(self):
        assert "OPENAI_API_KEY" in _ANAHTAR_KAYNAKLARI

    def test_has_telegram(self):
        assert "TELEGRAM_BOT_TOKEN" in _ANAHTAR_KAYNAKLARI

    def test_all_values_are_lists(self):
        for key, sources in _ANAHTAR_KAYNAKLARI.items():
            assert isinstance(sources, list), f"{key} sources not a list"

    def test_all_sources_known(self):
        known = {"ReYMeN_env", "wcm"}
        for key, sources in _ANAHTAR_KAYNAKLARI.items():
            for src in sources:
                assert src in known, f"Unknown source {src} for {key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
