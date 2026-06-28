"""Tests for reymen.sistem.cli_helpers."""
import pytest
from reymen.sistem.cli_helpers import (
    format_duration_compact,
    format_token_count_compact,
    is_table_divider,
    looks_like_table_row,
    realign_markdown_tables,
)


class TestFormatDurationCompact:
    def test_zero(self):
        r = format_duration_compact(0)
        assert isinstance(r, str)

    def test_seconds(self):
        r = format_duration_compact(30)
        assert isinstance(r, str)

    def test_minutes(self):
        r = format_duration_compact(120)
        assert isinstance(r, str)

    def test_hours(self):
        r = format_duration_compact(3600)
        assert isinstance(r, str)

    def test_large(self):
        r = format_duration_compact(99999)
        assert isinstance(r, str)


class TestFormatTokenCountCompact:
    def test_zero(self):
        assert isinstance(format_token_count_compact(0), str)

    def test_small(self):
        assert isinstance(format_token_count_compact(500), str)

    def test_thousands(self):
        assert isinstance(format_token_count_compact(5000), str)

    def test_millions(self):
        assert isinstance(format_token_count_compact(2000000), str)


class TestIsTableDivider:
    def test_table_divider(self):
        assert is_table_divider("|---|---|---|") == True

    def test_table_divider_colons(self):
        assert is_table_divider("|:---|:---:|") == True

    def test_not_table(self):
        assert is_table_divider("hello") == False

    def test_empty(self):
        assert is_table_divider("") == False


class TestLooksLikeTableRow:
    def test_table_row(self):
        assert looks_like_table_row("| a | b |") == True

    def test_not_table_row(self):
        assert looks_like_table_row("hello") == False

    def test_empty(self):
        assert looks_like_table_row("") == False


class TestRealignMarkdownTables:
    def test_simple_table(self):
        lines = ["| a | b |", "|---|---|", "| 1 | 2 |"]
        result = realign_markdown_tables(lines)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_no_table(self):
        lines = ["hello", "world"]
        result = realign_markdown_tables(lines)
        assert result == lines

    def test_empty_list(self):
        result = realign_markdown_tables([])
        assert result == []

    def test_mixed(self):
        lines = ["text", "| a |", "|---|---|", "| 1 |"]
        result = realign_markdown_tables(lines)
        assert isinstance(result, list)
