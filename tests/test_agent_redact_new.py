# -*- coding: utf-8 -*-
"""tests/test_agent_redact.py --- Redact modulu testleri."""

import logging

from agent.redact import (
    redact_sensitive_text,
    mask_secret,
    _mask_token,
    RedactingFormatter,
    _redact_query_string,
    _redact_form_body,
)


class TestMaskSecret:
    """mask_secret() helper testleri."""

    def test_long_token_preserves_head_tail(self):
        assert mask_secret("sk-pro...7890") == "sk-p...7890"

    def test_short_token_fully_masked(self):
        assert mask_secret("short") == "***"

    def test_empty_returns_empty(self):
        assert mask_secret("") == ""

    def test_none_returns_empty(self):
        assert mask_secret(None) == ""

    def test_empty_override(self):
        assert mask_secret("", empty="(not set)") == "(not set)"

    def test_custom_head_tail_floor(self):
        assert mask_secret("long-token", head=6, tail=4, floor=18) == "***"
        assert mask_secret("this-is-a-long-enough-token", head=6, tail=4, floor=18) == "this-i...oken"

class TestMaskToken:
    def test_empty_returns_triple_asterisk(self):
        assert _mask_token("") == "***"

    def test_long_token_preserves_6_and_4(self):
        token = "sk-ABC...7890"
        result = _mask_token(token)
        assert result == "***"
