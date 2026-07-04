"""Auto-generated tests for reymen.sistem.cli_helpers."""

import pytest
from src.reymen.sistem.cli_helpers import (
    CanonicalUsage,
    estimate_usage_cost,
    format_duration_compact,
    format_token_count_compact,
    is_table_divider,
    looks_like_table_row,
    realign_markdown_tables,
    _strip_reasoning_tags,
    _assistant_content_as_text,
    _assistant_copy_text,
)


class TestHelpers:
    """Auto-generated tests — her fonksiyonun import + call edilebilirliğini kontrol eder."""

    def test_CanonicalUsage_importable(self):
        assert callable(CanonicalUsage)

    def test_estimate_usage_cost_importable(self):
        assert callable(estimate_usage_cost)

    def test_format_duration_compact_importable(self):
        assert callable(format_duration_compact)

    def test_format_token_count_compact_importable(self):
        assert callable(format_token_count_compact)

    def test_is_table_divider_importable(self):
        assert callable(is_table_divider)

    def test_looks_like_table_row_importable(self):
        assert callable(looks_like_table_row)

    def test_realign_markdown_tables_importable(self):
        assert callable(realign_markdown_tables)

    def test__strip_reasoning_tags_importable(self):
        assert callable(_strip_reasoning_tags)

    def test__assistant_content_as_text_importable(self):
        assert callable(_assistant_content_as_text)

    def test__assistant_copy_text_importable(self):
        assert callable(_assistant_copy_text)
