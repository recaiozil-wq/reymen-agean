"""TUI birim testleri."""

from __future__ import annotations

import io
import sys

import pytest

from reymen import tui
from reymen.tui import (
    RICH_AVAILABLE,
    StatusBar,
    with_spinner,
    progress_bar,
    info,
    success,
    warning,
    error,
    panel,
    table,
)


class TestStatusBar:
    def test_status_bar_context_manager(self):
        with StatusBar() as bar:
            bar.update("test message")
            assert bar._text == "test message"

    def test_status_bar_clear(self):
        bar = StatusBar()
        bar.update("hello")
        bar.clear()
        assert bar._text == ""

    def test_status_bar_stop(self):
        bar = StatusBar()
        bar.update("temp")
        bar.stop()


class TestSpinner:
    def test_with_spinner_executes_block(self):
        executed = []
        with with_spinner("working"):
            executed.append(True)
        assert executed == [True]

    def test_with_spinner_no_rich(self, monkeypatch):
        monkeypatch.setattr(tui, "RICH_AVAILABLE", False)
        monkeypatch.setattr(tui, "_console", None)
        with with_spinner("test"):
            pass


class TestProgressBar:
    def test_progress_bar_advances(self):
        with progress_bar(10, "test") as advance:
            for _ in range(10):
                advance(1)

    def test_progress_bar_no_rich(self, monkeypatch):
        monkeypatch.setattr(tui, "RICH_AVAILABLE", False)
        monkeypatch.setattr(tui, "_console", None)
        with progress_bar(5, "fallback") as advance:
            advance(2)
            advance(3)


class TestOutputHelpers:
    def test_info_prints(self, capsys):
        info("test info")
        captured = capsys.readouterr()
        assert "test info" in captured.out

    def test_success_prints(self, capsys):
        success("done")
        captured = capsys.readouterr()
        assert "done" in captured.out

    def test_warning_prints(self, capsys):
        warning("careful")
        captured = capsys.readouterr()
        assert "careful" in captured.out

    def test_error_prints(self, capsys):
        error("failed")
        captured = capsys.readouterr()
        assert "failed" in captured.out or "failed" in captured.err


class TestPanel:
    def test_panel_prints_content(self, capsys):
        panel("hello world", title="Test")
        captured = capsys.readouterr()
        assert "hello world" in captured.out


class TestTable:
    def test_table_prints_rows(self, capsys):
        table(["A", "B"], [[1, 2], [3, 4]], title="Data")
        captured = capsys.readouterr()
        assert "A" in captured.out
        assert "1" in captured.out


class TestRichAvailability:
    def test_rich_available_flag_is_bool(self):
        assert isinstance(RICH_AVAILABLE, bool)

    def test_get_console(self):
        console = tui.get_console()
        if RICH_AVAILABLE:
            assert console is not None
        else:
            assert console is None