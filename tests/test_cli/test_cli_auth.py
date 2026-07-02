"""Tests for reymen.sistem.cli_auth."""
import pytest
from src.reymen.sistem.cli_auth import (
    set_sudo_password_callback,
    set_approval_callback,
)


class TestCallbacks:
    def test_set_sudo_password_callback_exists(self):
        assert callable(set_sudo_password_callback)

    def test_set_approval_callback_exists(self):
        assert callable(set_approval_callback)

    def test_module_imports(self):
        import reymen.sistem.cli_auth
        assert True
