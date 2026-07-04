# -*- coding: utf-8 -*-
"""Test: computer_use_tool.py — Approval callback shim."""

from unittest.mock import MagicMock
from tools import computer_use_tool


def test_set_approval_callback():
    """Approval callback ayarlanabilir."""
    cb = MagicMock()
    computer_use_tool.set_approval_callback(cb)
    assert computer_use_tool._approval_callback is cb


def test_set_approval_callback_none():
    """Approval callback None yapılabilir."""
    computer_use_tool.set_approval_callback(None)
    assert computer_use_tool._approval_callback is None


def test_module_has_expected_names():
    """Modül beklenen isimleri içermeli."""
    assert hasattr(computer_use_tool, "set_approval_callback")
    assert hasattr(computer_use_tool, "_approval_callback")
    assert hasattr(computer_use_tool, "logger")
