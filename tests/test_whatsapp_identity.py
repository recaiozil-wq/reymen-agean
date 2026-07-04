# -*- coding: utf-8 -*-
"""tests/test_whatsapp_identity.py — WhatsApp identity helpers birim testleri."""

import json
import sys
import tempfile
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from unittest.mock import patch, MagicMock
from gateway.whatsapp_identity import (
    normalize_whatsapp_identifier,
    expand_whatsapp_aliases,
    canonical_whatsapp_identifier,
)


class TestNormalizeWhatsAppIdentifier:
    def test_full_jid(self):
        assert (
            normalize_whatsapp_identifier("60123456789@s.whatsapp.net") == "60123456789"
        )

    def test_lid(self):
        assert normalize_whatsapp_identifier("999999999999999@lid") == "999999999999999"

    def test_with_device(self):
        assert (
            normalize_whatsapp_identifier("60123456789:47@s.whatsapp.net")
            == "60123456789"
        )

    def test_plus_prefix(self):
        assert normalize_whatsapp_identifier("+60123456789") == "60123456789"

    def test_bare_number(self):
        assert normalize_whatsapp_identifier("60123456789") == "60123456789"

    def test_empty(self):
        assert normalize_whatsapp_identifier("") == ""

    def test_none(self):
        assert normalize_whatsapp_identifier(None) == ""

    def test_whitespace(self):
        assert normalize_whatsapp_identifier("  60123456789  ") == "60123456789"

    def test_no_mutation(self):
        assert (
            normalize_whatsapp_identifier("15551234567@s.whatsapp.net") == "15551234567"
        )


class TestExpandWhatsAppAliases:
    def test_empty_identifier(self):
        assert expand_whatsapp_aliases("") == set()

    def test_no_mapping_files(self, tmp_path):
        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = expand_whatsapp_aliases("60123456789")
            assert result == {"60123456789"}

    def test_with_mapping(self, tmp_path):
        session_dir = tmp_path / "whatsapp" / "session"
        session_dir.mkdir(parents=True)
        # Create a mapping file
        mapping = session_dir / "lid-mapping-60123456789.json"
        mapping.write_text('"70123456789"', encoding="utf-8")
        # Also create reverse mapping
        rev = session_dir / "lid-mapping-70123456789.json"
        rev.write_text('"60123456789"', encoding="utf-8")

        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = expand_whatsapp_aliases("60123456789")
            assert "60123456789" in result
            assert "70123456789" in result

    def test_broken_mapping(self, tmp_path):
        session_dir = tmp_path / "whatsapp" / "session"
        session_dir.mkdir(parents=True)
        mapping = session_dir / "lid-mapping-60123456789.json"
        mapping.write_text("not valid json", encoding="utf-8")

        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = expand_whatsapp_aliases("60123456789")
            assert result == {"60123456789"}

    def test_unsafe_identifier_skipped(self, tmp_path):
        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = expand_whatsapp_aliases("../../etc/passwd")
            assert result == set()

    def test_transitive_resolution(self, tmp_path):
        session_dir = tmp_path / "whatsapp" / "session"
        session_dir.mkdir(parents=True)
        (session_dir / "lid-mapping-100.json").write_text('"200"', encoding="utf-8")
        (session_dir / "lid-mapping-200.json").write_text('"300"', encoding="utf-8")
        (session_dir / "lid-mapping-300.json").write_text('"100"', encoding="utf-8")

        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = expand_whatsapp_aliases("100")
            assert result == {"100", "200", "300"}


class TestCanonicalWhatsAppIdentifier:
    def test_normalizes(self):
        with patch(
            "gateway.whatsapp_identity.get_hermes_home",
            return_value=Path(tempfile.mkdtemp()),
        ):
            result = canonical_whatsapp_identifier("60123456789@s.whatsapp.net")
            assert result == "60123456789"

    def test_empty(self):
        assert canonical_whatsapp_identifier("") == ""

    def test_prefers_shortest(self, tmp_path):
        session_dir = tmp_path / "whatsapp" / "session"
        session_dir.mkdir(parents=True)
        # 100 maps to 200
        (session_dir / "lid-mapping-100.json").write_text('"200"', encoding="utf-8")

        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            # both have same length, min picks "100" alphabetically
            result = canonical_whatsapp_identifier("100")
            # "100" < "200" lexicographically
            assert result in ("100", "200")

    def test_no_mapping_fresh_install(self, tmp_path):
        with patch("gateway.whatsapp_identity.get_hermes_home", return_value=tmp_path):
            result = canonical_whatsapp_identifier("+15551234567")
            assert result == "15551234567"
