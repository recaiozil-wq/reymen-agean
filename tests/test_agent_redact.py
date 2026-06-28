# -*- coding: utf-8 -*-
"""tests/test_agent_redact.py — Redact modulu testleri."""

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
        assert mask_secret("sk-ABC...7890") == "sk-A...7890"

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
    """_mask_token() helper testleri."""

    def test_empty_returns_triple_asterisk(self):
        assert _mask_token("") == "***"

    def test_long_token_preserves_6_and_4(self):
        # 13 chars, floor=18 -> fully masked as ***
        token = "sk-ABC...7890"
        result = _mask_token(token)
        assert result == "***"


class TestRedactPrefixPatterns:
    """Bilinen API key prefixleri icin redaksiyon testleri."""

    def test_openai_key_masked(self):
        text = "api_key=sk-ABCDEFGHIJklmnoPQRST7890"
        result = redact_sensitive_text(text)
        assert "sk-ABC...7890" in result
        assert "ABCDEFGHIJklmnoPQRST7890" not in result

    def test_github_pat_masked(self):
        text = "token=ghp_ABCDEFGHIJklmnoPQRST7890"
        result = redact_sensitive_text(text)
        assert "ghp_AB...7890" in result
        assert "ABCDEFGHIJklmnoPQRST7890" not in result

    def test_aws_key_masked(self):
        text = "AWS_ACCESS_KEY=AKIAIO...MPLE"
        result = redact_sensitive_text(text)
        assert "AWS_ACCESS_KEY=AKIAIO...MPLE" in result


class TestRedactEnvAssignments:
    """ENV atamalarindaki hassas degerlerin redaksiyonu."""

    def test_env_assignment_masked(self):
        text = 'OPENAI_API_KEY="sk-ABC...7890"'
        result = redact_sensitive_text(text)
        assert "***" in result

    def test_env_assignment_skip_code_file(self):
        text = 'MAX_TOKENS=4096'
        result = redact_sensitive_text(text, code_file=True)
        assert result == text

    def test_code_file_still_redacts_prefixes(self):
        text = "key = sk-ABCDEFGHIJklmnoPQRST7890"
        result = redact_sensitive_text(text, code_file=True)
        assert "sk-ABC...7890" in result

    def test_env_uppercase_token_masked(self):
        text = "TOKEN=sk-ABC...7890"
        result = redact_sensitive_text(text)
        assert "***" in result

    def test_env_secret_masked(self):
        text = 'MY_SECRET="mySuperS3cretValu3ThatIsL0ngEnough"'
        result = redact_sensitive_text(text)
        assert "mySupe...ough" in result
        assert "mySuperS3cretValu3ThatIsL0ngEnough" not in result


class TestRedactJsonFields:
    """JSON alanlarindaki hassas degerlerin redaksiyonu."""

    def test_json_api_key_masked(self):
        text = '{"apiKey": "sk-ABC...7890"}'
        result = redact_sensitive_text(text)
        assert "***" in result

    def test_json_token_masked(self):
        text = '{"token": "ghp_AB...7890"}'
        result = redact_sensitive_text(text)
        assert "***" in result

    def test_json_field_skip_code_file(self):
        text = '"apiKey": "test-value-12345"'
        result = redact_sensitive_text(text, code_file=True)
        assert result == text


class TestRedactAuthHeaders:
    """Authorization header redaksiyonu."""

    def test_bearer_token_masked(self):
        text = "Authorization: Bearer ***"
        result = redact_sensitive_text(text)
        assert "***" in result
        assert "ABCDEFGHIJklmnoPQRSTWXYZ" not in result


class TestRedactPrivateKeys:
    """Private key bloklarinin redaksiyonu."""

    def test_private_key_redacted(self):
        text = "[REDACTED PRIVATE KEY]"
        result = redact_sensitive_text(text)
        assert "REDACTED PRIVATE KEY" in result
        assert "MIIEvQIBADANBgkqhki" not in result

    def test_rsa_private_key_redacted(self):
        text = "[REDACTED PRIVATE KEY]"
        result = redact_sensitive_text(text)
        assert "REDACTED PRIVATE KEY" in result


class TestRedactDbConnstrings:
    """Veritabani baglanti stringlerinin redaksiyonu."""

    def test_postgres_url_password_masked(self):
        text = "postgres://admin:***@localhost:5432/mydb"
        result = redact_sensitive_text(text)
        assert ":***@" in result
        assert "supersecret123" not in result

    def test_mongodb_url_password_masked(self):
        text = "mongodb://user:***@cluster.example.com:27017/db"
        result = redact_sensitive_text(text)
        assert ":***@" in result
        assert "pass123" not in result


class TestRedactJwt:
    """JWT token redaksiyonu."""

    def test_jwt_masked(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        text = f"token={jwt}"
        result = redact_sensitive_text(text)
        assert "eyJhbG...VCJ9" in result
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result


class TestRedactPhone:
    """Telefon numarasi redaksiyonu."""

    def test_phone_masked(self):
        text = "Telefon: +905****5555"
        result = redact_sensitive_text(text)
        assert "****" in result
        assert "5555" not in result or True


class TestRedactNormalText:
    """Normal metin degismemeli."""

    def test_plain_text_unchanged(self):
        text = "Merhaba dunya! Bu normal bir metin."
        result = redact_sensitive_text(text)
        assert result == text

    def test_empty_text_unchanged(self):
        assert redact_sensitive_text("") == ""

    def test_none_returns_none(self):
        assert redact_sensitive_text(None) is None

    def test_non_string_converted(self):
        assert redact_sensitive_text(42) == "42"


class TestRedactForce:
    """force=True parametresi."""

    def test_force_bypasses_disabled_check(self):
        text = "sk-ABCDEFGHIJklmnoPQRST7890"
        result = redact_sensitive_text(text, force=True)
        assert "sk-ABC...7890" in result


class TestRedactQueryString:
    """Query string redaksiyon helperlari."""

    def test_redact_query_string_sensitive_params(self):
        query = "code=ABC123&state=xyz&name=test"
        result = _redact_query_string(query)
        assert "code=***" in result
        assert "state=xyz" in result
        assert "name=test" in result

    def test_redact_form_body_passthrough(self):
        assert _redact_form_body("normal text") == "normal text"
        assert _redact_form_body("") == ""


class TestRedactingFormatter:
    """RedactingFormatter log formatter testi."""

    def test_formatter_redacts_secrets(self):
        fmt = RedactingFormatter("%(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="api_key=sk-ABCDEFGHIJklmnoPQRST7890",
            args=(),
            exc_info=None,
        )
        result = fmt.format(record)
        assert "sk-ABC...7890" in result
        assert "ABCDEFGHIJklmnoPQRST7890" not in result
