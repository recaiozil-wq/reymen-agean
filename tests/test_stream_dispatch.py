# -*- coding: utf-8 -*-
"""tests/test_stream_dispatch.py — GatewayEventDispatcher birim testleri."""

import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from unittest.mock import MagicMock, ANY

from gateway.stream_dispatch import GatewayEventDispatcher
from gateway.stream_events import (
    MessageChunk,
    MessageStop,
    Commentary,
    ToolCallChunk,
    ToolCallFinished,
    LongToolHint,
    GatewayNotice,
)


class _FakeAdapter:
    """Minimal adapter stub for testing dispatch routing."""

    def render_message_event(self, event, sink):
        sink.append(event)

    def format_tool_event(self, event, mode="all", preview_max_len=40):
        return f"[{event.tool_name}]"


class TestGatewayEventDispatcher:
    def test_init_defaults(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter)
        assert d.adapter is adapter
        assert d.sink is None
        assert d.tool_mode == "all"

    def test_dispatch_message_chunk_with_sink(self):
        sink = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, sink=sink)
        event = MessageChunk(text="hello")
        d.dispatch(event)
        assert len(sink) == 1

    def test_dispatch_message_chunk_no_sink(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, sink=None)
        event = MessageChunk(text="hello")
        d.dispatch(event)  # should not raise

    def test_dispatch_message_stop(self):
        sink = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, sink=sink)
        event = MessageStop(final=False)
        d.dispatch(event)
        assert len(sink) == 1

    def test_dispatch_commentary(self):
        sink = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, sink=sink)
        event = Commentary(text="note")
        d.dispatch(event)
        assert len(sink) == 1

    def test_dispatch_tool_call_chunk(self):
        lines = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, enqueue_tool_line=lines.append)
        event = ToolCallChunk(tool_name="search", preview="query", args={})
        d.dispatch(event)
        assert len(lines) == 1
        assert "[search]" in lines[0]

    def test_dispatch_tool_call_chunk_off_mode(self):
        lines = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(
            adapter, enqueue_tool_line=lines.append, tool_mode="off"
        )
        event = ToolCallChunk(tool_name="search", preview="query", args={})
        d.dispatch(event)
        assert len(lines) == 0

    def test_dispatch_tool_call_chunk_new_mode(self):
        lines = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(
            adapter, enqueue_tool_line=lines.append, tool_mode="new"
        )
        event1 = ToolCallChunk(tool_name="search", preview="query", args={})
        event2 = ToolCallChunk(
            tool_name="search", preview="query", args={}
        )  # same tool, dedup
        event3 = ToolCallChunk(
            tool_name="read", preview="file", args={}
        )  # different tool
        d.dispatch(event1)
        d.dispatch(event2)
        d.dispatch(event3)
        assert len(lines) == 2

    def test_dispatch_tool_call_finished(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter)
        event = ToolCallFinished(tool_name="search", duration=1.5, ok=True)
        d.dispatch(event)  # should not raise, does nothing by default

    def test_dispatch_long_tool_hint(self):
        hints = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, on_long_tool=hints.append)
        event = LongToolHint(tool_name="search", duration=30.0)
        d.dispatch(event)
        assert len(hints) == 1

    def test_dispatch_long_tool_hint_no_handler(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, on_long_tool=None)
        event = LongToolHint(tool_name="search", duration=30.0)
        d.dispatch(event)  # should not raise

    def test_dispatch_gateway_notice(self):
        notices = []
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, on_notice=notices.append)
        event = GatewayNotice(kind="online", text="test notice")
        d.dispatch(event)
        assert len(notices) == 1

    def test_dispatch_gateway_notice_no_handler(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, on_notice=None)
        event = GatewayNotice(kind="online", text="test notice")
        d.dispatch(event)  # should not raise

    def test_dispatch_never_raises(self):
        """dispatch() catches exceptions internally."""

        class CrashAdapter:
            def render_message_event(self, event, sink):
                raise RuntimeError("crash")

            def format_tool_event(self, event, **kwargs):
                raise RuntimeError("crash")

        adapter = CrashAdapter()
        d = GatewayEventDispatcher(adapter, sink=[])
        event = MessageChunk(text="x")
        d.dispatch(event)  # should not raise

    def test_dispatch_unknown_event(self):
        """Unknown event types are silently ignored."""
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter)

        class UnknownEvent:
            pass

        event = UnknownEvent()
        d.dispatch(event)  # should not raise

    def test_preview_max_len(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, preview_max_len=80)
        assert d.preview_max_len == 80

    def test_tool_mode_none_fallback(self):
        adapter = _FakeAdapter()
        d = GatewayEventDispatcher(adapter, tool_mode=None)
        assert d.tool_mode == "all"
