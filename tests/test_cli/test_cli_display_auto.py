"""Auto-generated tests for reymen.sistem.cli_display."""
import pytest
from src.reymen.sistem.cli_display import (
    _detect_light_mode,
    _maybe_remap_for_light_mode,
    _accent_hex,
    _rich_text_from_ansi,
    _strip_markdown_syntax,
    _terminal_width_for_streaming,
    _render_final_assistant_content,
    _configure_output_history,
    _clear_output_history,
    _suspend_output_history,
    _record_output_history,
    _replay_output_history,
    _cprint,
    _hex_to_ansi,
    _luminance_from_hex,
)


class TestDisplay:
    """Auto-generated tests — her fonksiyonun import + call edilebilirliğini kontrol eder."""

    def test__detect_light_mode_importable(self):
        assert callable(_detect_light_mode)

    def test__maybe_remap_for_light_mode_importable(self):
        assert callable(_maybe_remap_for_light_mode)

    def test__accent_hex_importable(self):
        assert callable(_accent_hex)

    def test__rich_text_from_ansi_importable(self):
        assert callable(_rich_text_from_ansi)

    def test__strip_markdown_syntax_importable(self):
        assert callable(_strip_markdown_syntax)

    def test__terminal_width_for_streaming_importable(self):
        assert callable(_terminal_width_for_streaming)

    def test__render_final_assistant_content_importable(self):
        assert callable(_render_final_assistant_content)

    def test__configure_output_history_importable(self):
        assert callable(_configure_output_history)

    def test__clear_output_history_importable(self):
        assert callable(_clear_output_history)

    def test__suspend_output_history_importable(self):
        assert callable(_suspend_output_history)

    def test__record_output_history_importable(self):
        assert callable(_record_output_history)

    def test__replay_output_history_importable(self):
        assert callable(_replay_output_history)

    def test__cprint_importable(self):
        assert callable(_cprint)

    def test__hex_to_ansi_importable(self):
        assert callable(_hex_to_ansi)

    def test__luminance_from_hex_importable(self):
        assert callable(_luminance_from_hex)
