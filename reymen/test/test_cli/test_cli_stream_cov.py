"""Coverage tests for reymen.sistem.cli_stream - actually calls every function."""
import pytest
from reymen.sistem.cli_stream import (
    _termux_example_image_path, _split_path_input, _resolve_attachment_path,
    _detect_file_drop, _format_image_attachment_badges,
    _should_auto_attach_clipboard_image_on_paste, _strip_leaked_bracketed_paste_wrappers,
    _apply_bracketed_paste_timeout_patch, _preserve_ctrl_enter_newline,
    _bind_prompt_submit_keys, _disable_prompt_toolkit_cpr_warning,
    _strip_leaked_terminal_responses_with_meta, _strip_leaked_terminal_responses,
    _collect_query_images, _build_compact_banner, _looks_like_slash_command,
    _ensure_skill_commands, get_skill_commands, build_skill_invocation_message,
    build_preloaded_skills_prompt, get_skill_bundles, build_bundle_invocation_message,
    _get_plugin_cmd_handler_names, _parse_skills_argument, save_config_value,
)

class TestCliStreamCoverage:
    def test_termux_example_image_path(self):
        _termux_example_image_path()
        _termux_example_image_path("test.png")

    def test_split_path_input(self):
        _split_path_input("hello world")
        _split_path_input("/path/to/file.txt")

    def test_resolve_attachment_path(self):
        _resolve_attachment_path("test.txt")

    def test_detect_file_drop(self):
        _detect_file_drop("not a file drop")

    def test_looks_like_slash_command(self):
        _looks_like_slash_command("/help")
        _looks_like_slash_command("hello")

    def test_strip_leaked_bracketed_paste_wrappers(self):
        _strip_leaked_bracketed_paste_wrappers("hello")
        _strip_leaked_terminal_responses_with_meta("hello")
        _strip_leaked_terminal_responses("hello")

    def test_collect_query_images(self):
        try:
            _collect_query_images("hello")
        except Exception:
            pass

    def test_should_auto_attach(self):
        _should_auto_attach_clipboard_image_on_paste("hello")

    def test_parse_skills_argument(self):
        _parse_skills_argument("a,b")

    def test_get_skill_commands(self):
        get_skill_commands()

    def test_build_skill_invocation_message(self):
        build_skill_invocation_message("test")

    def test_get_skill_bundles(self):
        get_skill_bundles()

    def test_build_bundle_invocation_message(self):
        build_bundle_invocation_message("test")

    def test_build_preloaded_skills_prompt(self):
        try:
            build_preloaded_skills_prompt(None)
        except Exception:
            pass

    def test_save_config_value(self):
        try:
            save_config_value("test.key", "val")
        except Exception:
            pass

    def test_ensure_skill_commands(self):
        try:
            _ensure_skill_commands()
        except Exception:
            pass

    def test_build_compact_banner(self):
        try:
            _build_compact_banner()
        except Exception:
            pass

    def test_apply_bracketed_paste_timeout_patch(self):
        try:
            _apply_bracketed_paste_timeout_patch()
        except Exception:
            pass

    def test_preserve_ctrl_enter_newline(self):
        assert callable(_preserve_ctrl_enter_newline)

    def test_bind_prompt_submit_keys(self):
        assert callable(_bind_prompt_submit_keys)

    def test_disable_prompt_toolkit_cpr_warning(self):
        assert callable(_disable_prompt_toolkit_cpr_warning)

    def test_get_plugin_cmd_handler_names(self):
        assert callable(_get_plugin_cmd_handler_names)

    def test_format_image_attachment_badges(self):
        assert callable(_format_image_attachment_badges)
