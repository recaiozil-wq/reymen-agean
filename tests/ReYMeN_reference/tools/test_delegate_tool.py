# -*- coding: utf-8 -*-
"""Test: delegate_tool.py — Alt-Ajan delegasyon aracı."""

from unittest.mock import patch, MagicMock
from tools import delegate_tool


def test_run_no_goal():
    sonuc = delegate_tool.run()
    assert "goal" in sonuc


def test_run_no_motor_fallback():
    """Motor import edilemezse fallback subprocess çalışır."""
    with patch("tools.delegate_tool.Motor", None):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "merhaba"
            mock_run.return_value = mock_proc
            sonuc = delegate_tool.run(goal="selam")
            assert "tamamlandi" in sonuc


def test_run_no_motor_fallback_exception():
    with patch("tools.delegate_tool.Motor", None):
        with patch("subprocess.run", side_effect=Exception("hata")):
            sonuc = delegate_tool.run(goal="selam")
            assert "Hata" in sonuc


def test_ping():
    assert delegate_tool.ping() is True


def test_delegate_event():
    event = delegate_tool.DelegateEvent(event_type="test", payload={"key": "val"})
    assert event.event_type == "test"
    assert event.payload == {"key": "val"}


def test_strip_blocked_tools():
    tools_list = ["delegate", "read_file", "rm", "write_file"]
    result = delegate_tool._strip_blocked_tools(tools_list)
    assert "delegate" not in result
    assert "rm" not in result
    assert "read_file" in result


def test_expand_parent_toolsets():
    result = delegate_tool._expand_parent_toolsets(["a", "b"])
    assert result == ["a", "b"]


def test_get_max_concurrent_children():
    assert delegate_tool._get_max_concurrent_children() == 5


def test_build_child_progress_callback():
    cb = delegate_tool._build_child_progress_callback(lambda x: x)
    assert cb is not None
