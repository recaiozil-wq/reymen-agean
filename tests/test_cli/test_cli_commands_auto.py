"""Auto-generated tests for reymen.sistem.cli_commands."""
import pytest
from src.reymen.sistem.cli_commands import (
    load_cli_config,
    _load_prefill_messages,
    _parse_reasoning_config,
    _parse_service_tier_config,
)


class TestCommands:
    """Auto-generated tests — her fonksiyonun import + call edilebilirliğini kontrol eder."""

    def test_load_cli_config_importable(self):
        assert callable(load_cli_config)

    def test__load_prefill_messages_importable(self):
        assert callable(_load_prefill_messages)

    def test__parse_reasoning_config_importable(self):
        assert callable(_parse_reasoning_config)

    def test__parse_service_tier_config_importable(self):
        assert callable(_parse_service_tier_config)
