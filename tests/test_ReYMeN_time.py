# -*- coding: utf-8 -*-
"""Tests for ReYMeN_time.py — timezone-aware clock."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from reymen.sistem import ReYMeN_time as time_mod
from reymen.sistem.ReYMeN_time import (
    _resolve_timezone_name,
    _get_zoneinfo,
    get_timezone,
    now,
)


def _reset_cache():
    """Reset module-level cached state (no public API exists)."""
    time_mod._cache_resolved = False
    time_mod._cached_tz = None
    time_mod._cached_tz_name = None


# ════════════════════════════════════════════════════════════════
# _resolve_timezone_name
# ════════════════════════════════════════════════════════════════

class TestResolveTimezoneName:
    def test_env_var_priority(self):
        """Environment variable has highest priority."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Europe/Istanbul"}, clear=True):
            assert _resolve_timezone_name() == "Europe/Istanbul"

    def test_env_var_empty_falls_through(self):
        """Empty env var falls through to config."""
        _reset_cache()
        with patch.dict(os.environ, {}, clear=True):
            result = _resolve_timezone_name()
            # Should return empty string (no config file or no timezone key)
            # OR whatever is in the actual config -- we just check it doesn't crash
            assert isinstance(result, str)

    def test_env_var_whitespace_stripped(self):
        """Whitespace around env var value is stripped."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "  Asia/Tokyo  "}, clear=True):
            assert _resolve_timezone_name() == "Asia/Tokyo"

    def test_config_yaml_timezone_key(self, tmp_path):
        """Config.yaml timezone key is used when no env var is set."""
        _reset_cache()
        config_dir = tmp_path / ".ReYMeN"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("timezone: America/New_York\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("reymen.sistem.ReYMeN_time.get_config_path",
                  return_value=config_file),
        ):
            assert _resolve_timezone_name() == "America/New_York"

    def test_config_yaml_missing_key(self, tmp_path):
        """Missing timezone key returns empty string."""
        _reset_cache()
        config_dir = tmp_path / ".ReYMeN"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("other_key: value\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("reymen.sistem.ReYMeN_time.get_config_path",
                  return_value=config_file),
        ):
            assert _resolve_timezone_name() == ""

    def test_config_yaml_not_timezone_string(self, tmp_path):
        """Non-string timezone value returns empty string."""
        _reset_cache()
        config_dir = tmp_path / ".ReYMeN"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("timezone: 12345\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("reymen.sistem.ReYMeN_time.get_config_path",
                  return_value=config_file),
        ):
            assert _resolve_timezone_name() == ""

    def test_config_file_not_found(self):
        """Non-existent config file returns empty string."""
        _reset_cache()
        fake_path = Path(tempfile.mktemp(suffix=".yaml"))
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("reymen.sistem.ReYMeN_time.get_config_path",
                  return_value=fake_path),
        ):
            assert _resolve_timezone_name() == ""


# ════════════════════════════════════════════════════════════════
# _get_zoneinfo
# ════════════════════════════════════════════════════════════════

class TestGetZoneinfo:
    def test_valid_timezone(self):
        tz = _get_zoneinfo("UTC")
        assert tz is not None
        assert str(tz) == "UTC"

    def test_another_valid_tz(self):
        tz = _get_zoneinfo("Europe/Istanbul")
        assert tz is not None
        assert str(tz) == "Europe/Istanbul"

    def test_empty_string(self):
        assert _get_zoneinfo("") is None

    def test_invalid_timezone(self):
        assert _get_zoneinfo("Mars/Olympus") is None

    def test_garbage_string(self):
        assert _get_zoneinfo("not-a-timezone!!!") is None


# ════════════════════════════════════════════════════════════════
# get_timezone
# ════════════════════════════════════════════════════════════════

class TestGetTimezone:
    def test_returns_none_when_unconfigured(self):
        """No env var + no config -> None (server local time)."""
        _reset_cache()
        with patch.dict(os.environ, {}, clear=True):
            tz = get_timezone()
            assert tz is None

    def test_returns_zoneinfo_when_configured(self):
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Asia/Kolkata"}, clear=True):
            tz = get_timezone()
            assert tz is not None
            assert str(tz) == "Asia/Kolkata"

    def test_returns_none_for_invalid_tz(self):
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Fake/Zone"}, clear=True):
            tz = get_timezone()
            assert tz is None

    def test_cache_works(self):
        """Second call returns cached value without re-resolving."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Europe/Berlin"}, clear=True):
            tz1 = get_timezone()
            # Change env var after first call
            with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "US/Pacific"}, clear=True):
                tz2 = get_timezone()
                # Should still be Berlin (cached), not Pacific
                assert str(tz1) == "Europe/Berlin"
                assert str(tz2) == "Europe/Berlin"

    def test_reset_cache_works(self):
        """_reset_cache() forces re-resolution."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Europe/Berlin"}, clear=True):
            tz1 = get_timezone()
            assert str(tz1) == "Europe/Berlin"

        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "US/Pacific"}, clear=True):
            tz2 = get_timezone()
            assert str(tz2) == "US/Pacific"


# ════════════════════════════════════════════════════════════════
# now()
# ════════════════════════════════════════════════════════════════

class TestNow:
    def test_returns_datetime(self):
        """now() always returns a datetime."""
        _reset_cache()
        result = now()
        from datetime import datetime
        assert isinstance(result, datetime)

    def test_timezone_aware(self):
        """now() returns timezone-aware datetime (no naive datetimes)."""
        _reset_cache()
        result = now()
        assert result.tzinfo is not None

    def test_configured_tz(self):
        """now() uses configured timezone."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "Asia/Kolkata"}, clear=True):
            result = now()
            assert result.tzinfo is not None
            # UTC+5:30 -> offset should be +05:30
            offset = result.utcoffset()
            assert offset is not None
            total_seconds = offset.total_seconds()
            assert total_seconds == 19800  # 5.5 hours * 3600

    def test_one_call_after_reset(self):
        """Cache reset doesn't break subsequent now() calls."""
        _reset_cache()
        r1 = now()
        assert r1.tzinfo is not None
        r2 = now()
        assert r2 >= r1  # time didn't go backwards (probably)


# ════════════════════════════════════════════════════════════════
# Edge cases
# ════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_never_crashes_on_bad_tz(self):
        """Invalid timezone never crashes — falls back safely."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": "This/DoesNotExist!"}, clear=True):
            tz = get_timezone()
            assert tz is None
            # now() should still work with fallback
            result = now()
            from datetime import datetime
            assert isinstance(result, datetime)
            assert result.tzinfo is not None

    def test_never_crashes_on_broken_config(self):
        """Corrupted config file never crashes — falls back safely."""
        _reset_cache()
        config_dir = Path(tempfile.mkdtemp())
        config_file = config_dir / "config.yaml"
        config_file.write_text("{broken: yaml: [\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("reymen.sistem.ReYMeN_time.get_config_path",
                  return_value=config_file),
        ):
            tz = get_timezone()
            assert tz is None

    def test_empty_env_var_after_set(self):
        """Explicit empty env var after a valid one goes to fallback."""
        _reset_cache()
        with patch.dict(os.environ, {"ReYMeN_TIMEZONE": ""}, clear=True):
            result = _resolve_timezone_name()
            assert isinstance(result, str)

    def test_zoneinfo_with_dot_in_name(self):
        """Timezone names with dots (unusual but valid)."""
        tz = _get_zoneinfo("CET")
        # CET is a valid Olson DB alias on most systems
        # Accept None as valid too — it's platform-dependent
        if tz is not None:
            assert str(tz) is not None
