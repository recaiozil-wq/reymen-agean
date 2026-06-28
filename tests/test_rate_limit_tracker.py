# -*- coding: utf-8 -*-
"""Tests for agent.rate_limit_tracker — header parsing, formatting, edge cases."""

import time
from unittest.mock import patch

import pytest

from agent.rate_limit_tracker import (
    RateLimitBucket,
    RateLimitState,
    _bar,
    _bucket_line,
    _fmt_count,
    _fmt_seconds,
    _safe_float,
    _safe_int,
    format_rate_limit_compact,
    format_rate_limit_display,
    parse_rate_limit_headers,
)


# ── _safe_int / _safe_float ──────────────────────────────────────────

class TestSafeConverters:
    def test_safe_int_normal(self):
        assert _safe_int("42") == 42

    def test_safe_int_float_string(self):
        assert _safe_int("3.9") == 3

    def test_safe_int_none(self):
        assert _safe_int(None) == 0

    def test_safe_int_garbage(self):
        assert _safe_int("abc", default=-1) == -1

    def test_safe_float_normal(self):
        assert _safe_float("2.5") == 2.5

    def test_safe_float_int_string(self):
        assert _safe_float("10") == 10.0

    def test_safe_float_none(self):
        assert _safe_float(None) == 0.0

    def test_safe_float_garbage(self):
        assert _safe_float("nope", default=-1.0) == -1.0


# ── RateLimitBucket ──────────────────────────────────────────────────

class TestRateLimitBucket:
    def test_used_property(self):
        b = RateLimitBucket(limit=100, remaining=35)
        assert b.used == 65

    def test_used_never_negative(self):
        b = RateLimitBucket(limit=10, remaining=15)
        assert b.used == 0

    def test_usage_pct_normal(self):
        b = RateLimitBucket(limit=200, remaining=100)
        assert b.usage_pct == pytest.approx(50.0)

    def test_usage_pct_zero_limit(self):
        b = RateLimitBucket(limit=0)
        assert b.usage_pct == 0.0

    def test_usage_pct_full(self):
        b = RateLimitBucket(limit=50, remaining=0)
        assert b.usage_pct == 100.0

    def test_remaining_seconds_now(self):
        now = time.time()
        b = RateLimitBucket(reset_seconds=60.0, captured_at=now - 10)
        remaining = b.remaining_seconds_now
        assert 49.0 < remaining < 51.0

    def test_remaining_seconds_now_expired(self):
        b = RateLimitBucket(reset_seconds=5.0, captured_at=time.time() - 100)
        assert b.remaining_seconds_now == 0.0


# ── RateLimitState ───────────────────────────────────────────────────

class TestRateLimitState:
    def test_has_data_false_default(self):
        s = RateLimitState()
        assert s.has_data is False

    def test_has_data_true(self):
        s = RateLimitState(captured_at=time.time())
        assert s.has_data is True

    def test_age_seconds_no_data(self):
        s = RateLimitState()
        assert s.age_seconds == float("inf")

    def test_age_seconds_fresh(self):
        now = time.time()
        s = RateLimitState(captured_at=now - 5)
        assert 4.0 < s.age_seconds < 6.0


# ── parse_rate_limit_headers ─────────────────────────────────────────

FULL_HEADERS = {
    "x-ratelimit-limit-requests": "60",
    "x-ratelimit-limit-requests-1h": "1000",
    "x-ratelimit-limit-tokens": "200000",
    "x-ratelimit-limit-tokens-1h": "5000000",
    "x-ratelimit-remaining-requests": "45",
    "x-ratelimit-remaining-requests-1h": "800",
    "x-ratelimit-remaining-tokens": "150000",
    "x-ratelimit-remaining-tokens-1h": "4000000",
    "x-ratelimit-reset-requests": "30",
    "x-ratelimit-reset-requests-1h": "1200",
    "x-ratelimit-reset-tokens": "15",
    "x-ratelimit-reset-tokens-1h": "900",
}


class TestParseRateLimitHeaders:
    def test_no_rate_limit_headers(self):
        assert parse_rate_limit_headers({"content-type": "application/json"}) is None

    def test_empty_headers(self):
        assert parse_rate_limit_headers({}) is None

    def test_full_headers(self):
        state = parse_rate_limit_headers(FULL_HEADERS, provider="openai")
        assert state is not None
        assert state.provider == "openai"
        assert state.has_data is True
        assert state.requests_min.limit == 60
        assert state.requests_min.remaining == 45
        assert state.requests_hour.limit == 1000
        assert state.tokens_min.limit == 200000
        assert state.tokens_hour.limit == 5000000

    def test_case_insensitive_headers(self):
        mixed = {k.upper(): v for k, v in FULL_HEADERS.items()}
        state = parse_rate_limit_headers(mixed)
        assert state is not None
        assert state.requests_min.limit == 60

    def test_partial_headers(self):
        partial = {
            "x-ratelimit-limit-requests": "100",
            "x-ratelimit-remaining-requests": "50",
        }
        state = parse_rate_limit_headers(partial)
        assert state is not None
        assert state.requests_min.limit == 100
        assert state.requests_min.remaining == 50
        # Other buckets default to 0
        assert state.tokens_min.limit == 0


# ── Formatting helpers ───────────────────────────────────────────────

class TestFmtCount:
    def test_small_number(self):
        assert _fmt_count(42) == "42"

    def test_thousands(self):
        assert _fmt_count(1500) == "1.5K"

    def test_ten_thousands(self):
        assert _fmt_count(33599) == "33.6K"

    def test_millions(self):
        assert _fmt_count(7999856) == "8.0M"

    def test_exact_boundary_10k(self):
        assert _fmt_count(10000) == "10.0K"


class TestFmtSeconds:
    def test_seconds(self):
        assert _fmt_seconds(45) == "45s"

    def test_minutes(self):
        assert _fmt_seconds(120) == "2m"

    def test_minutes_and_seconds(self):
        assert _fmt_seconds(134) == "2m 14s"

    def test_hours(self):
        assert _fmt_seconds(3600) == "1h"

    def test_hours_and_minutes(self):
        assert _fmt_seconds(3660) == "1h 1m"

    def test_zero(self):
        assert _fmt_seconds(0) == "0s"

    def test_negative_clamps_to_zero(self):
        assert _fmt_seconds(-10) == "0s"


class TestBar:
    def test_empty(self):
        assert _bar(0) == "[░░░░░░░░░░░░░░░░░░░░]"

    def test_full(self):
        assert _bar(100) == "[████████████████████]"

    def test_half(self):
        bar = _bar(50)
        assert bar.count("█") == 10
        assert bar.count("░") == 10

    def test_custom_width(self):
        bar = _bar(75, width=4)
        assert bar.count("█") == 3
        assert bar.count("░") == 1

    def test_over_100_clamps(self):
        bar = _bar(150, width=10)
        assert bar.count("█") == 10


# ── format_rate_limit_display ────────────────────────────────────────

class TestFormatDisplay:
    def test_no_data(self):
        s = RateLimitState()
        assert "No rate limit data" in format_rate_limit_display(s)

    def test_with_data(self):
        s = RateLimitState(
            requests_min=RateLimitBucket(limit=60, remaining=45, reset_seconds=30, captured_at=time.time()),
            tokens_min=RateLimitBucket(limit=200000, remaining=150000, reset_seconds=15, captured_at=time.time()),
            captured_at=time.time(),
            provider="deepseek",
        )
        output = format_rate_limit_display(s)
        assert "Deepseek" in output
        assert "Requests/min" in output
        assert "Tokens/min" in output

    def test_high_usage_warning(self):
        s = RateLimitState(
            requests_min=RateLimitBucket(limit=60, remaining=5, reset_seconds=10, captured_at=time.time()),
            captured_at=time.time(),
        )
        output = format_rate_limit_display(s)
        assert "⚠" in output
        assert "requests/min" in output


# ── format_rate_limit_compact ────────────────────────────────────────

class TestFormatCompact:
    def test_no_data(self):
        s = RateLimitState()
        assert format_rate_limit_compact(s) == "No rate limit data."

    def test_with_data(self):
        s = RateLimitState(
            requests_min=RateLimitBucket(limit=60, remaining=45, reset_seconds=30, captured_at=time.time()),
            tokens_min=RateLimitBucket(limit=200000, remaining=150000, reset_seconds=15, captured_at=time.time()),
            captured_at=time.time(),
        )
        output = format_rate_limit_compact(s)
        assert "RPM: 45/60" in output
        assert "TPM:" in output
