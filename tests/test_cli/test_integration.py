"""Integration tests for reymen.sistem.cli."""

import pytest


class TestReYMeNCLIImport:
    """Verify the CLI class can be imported and has expected structure."""

    def test_cli_import(self):
        from reymen.sistem.cli import ReYMeNCLI

        assert ReYMeNCLI is not None

    def test_cli_main_import(self):
        from reymen.sistem.cli_main import ReYMeNCLI as MainCLI

        assert MainCLI is not None

    def test_mixin_inheritance(self):
        from reymen.sistem.cli_main import ReYMeNCLI

        mro = [c.__name__ for c in ReYMeNCLI.__mro__]
        assert "MixinDisplay" in mro
        assert "MixinStream" in mro
        assert "MixinCommands" in mro
        assert "MixinCore" in mro

    def test_voice_methods_available(self):
        from reymen.sistem.cli_main import ReYMeNCLI

        for m in [
            "_voice_start_recording",
            "_voice_stop_and_transcribe",
            "_voice_speak_response_async",
        ]:
            assert hasattr(ReYMeNCLI, m), f"Missing: {m}"

    def test_split_modules_importable(self):
        import reymen.sistem.cli_helpers
        import reymen.sistem.cli_display
        import reymen.sistem.cli_commands
        import reymen.sistem.cli_auth
        import reymen.sistem.cli_maintenance
        import reymen.sistem.cli_stream

        assert True

    def test_wrapper_cli_import(self):
        from reymen.sistem import cli

        assert hasattr(cli, "ReYMeNCLI")
