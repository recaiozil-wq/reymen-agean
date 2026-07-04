# -*- coding: utf-8 -*-
"""Test: computer_use_tool.py — Shim for computer_use tool."""

from unittest.mock import patch, MagicMock
from tools import computer_use_tool


def test_module_imports():
    """Module should import without errors and have expected names."""
    assert hasattr(computer_use_tool, "registry")
    assert hasattr(computer_use_tool, "COMPUTER_USE_SCHEMA")
    assert hasattr(computer_use_tool, "handle_computer_use")
    assert hasattr(computer_use_tool, "check_computer_use_requirements")
    assert hasattr(computer_use_tool, "set_approval_callback")


def test_all_exports():
    expected = {
        "handle_computer_use",
        "set_approval_callback",
        "check_computer_use_requirements",
    }
    assert set(computer_use_tool.__all__) == expected


def test_registry_has_names():
    """The registry should have the computer_use name registered."""
    tools = computer_use_tool.registry.list_tools()
    names = [
        t.get("name", t.get("tool_name", "")) if isinstance(t, dict) else str(t)
        for t in tools
    ]
    assert "computer_use" in names or any("computer" in str(n) for n in names)
