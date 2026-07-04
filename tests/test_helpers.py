# -*- coding: utf-8 -*-
"""gateway/platforms/helpers.py testleri — actual API."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

# Skip if gateway module can't be properly imported
try:
    from gateway.platforms.helpers import MessageDeduplicator
    _GATEWAY_AVAILABLE = True
except (ImportError, TypeError, AttributeError):
    _GATEWAY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _GATEWAY_AVAILABLE,
    reason="gateway.platforms.helpers not importable (shim stub active or missing hermes_cli)"
)


class TestMessageDeduplicator:
    def test_deduplicator(self):
        from gateway.platforms.helpers import MessageDeduplicator

        md = MessageDeduplicator()
        assert md.is_duplicate("a") is False
        assert md.is_duplicate("a") is True
        assert md.is_duplicate("b") is False
        assert md.is_duplicate("b") is True

    def test_deduplicator_custom_size(self):
        from gateway.platforms.helpers import MessageDeduplicator

        md = MessageDeduplicator(max_size=10)
        for i in range(15):
            md.is_duplicate(f"msg_{i}")
        assert md.is_duplicate("msg_0") is False

    def test_deduplicator_ttl(self):
        from gateway.platforms.helpers import MessageDeduplicator

        md = MessageDeduplicator(ttl_seconds=0.01)
        md.is_duplicate("test")
        import time
        time.sleep(0.02)
        assert md.is_duplicate("test") is False


class TestThreadParticipationTracker:
    def test_init(self):
        from gateway.platforms.helpers import ThreadParticipationTracker

        tracker = ThreadParticipationTracker(platform_name="test")
        assert tracker._platform == "test"

    def test_mark_and_contains(self):
        from gateway.platforms.helpers import ThreadParticipationTracker

        tracker = ThreadParticipationTracker(platform_name="test")
        tracker.mark("thread_1")
        assert "thread_1" in tracker

    def test_mark_multiple(self):
        from gateway.platforms.helpers import ThreadParticipationTracker

        tracker = ThreadParticipationTracker(platform_name="test")
        tracker.mark("t1")
        tracker.mark("t2")
        assert "t1" in tracker
        assert "t2" in tracker


class TestStripMarkdown:
    def test_strip_markdown_bold(self):
        from gateway.platforms.helpers import strip_markdown

        result = strip_markdown("**bold** text")
        assert "bold" in result

    def test_strip_markdown_links(self):
        from gateway.platforms.helpers import strip_markdown

        result = strip_markdown("[link](http://example.com)")
        assert "link" in result

    def test_strip_markdown_headers(self):
        from gateway.platforms.helpers import strip_markdown

        result = strip_markdown("# Baslik\n## Alt")
        assert "Baslik" in result

    def test_strip_markdown_empty(self):
        from gateway.platforms.helpers import strip_markdown

        assert strip_markdown("") == ""

    def test_strip_markdown_code_block(self):
        from gateway.platforms.helpers import strip_markdown

        result = strip_markdown("```\nkod\n```")
        assert "kod" in result


class TestAtomicJsonWrite:
    def test_atomic_json_write(self, tmp_path):
        from gateway.platforms.helpers import atomic_json_write

        dosya = tmp_path / "test.json"
        atomic_json_write(dosya, {"key": "value"})
        import json
        data = json.loads(dosya.read_text(encoding="utf-8"))
        assert data["key"] == "value"


class TestRedactPhone:
    def test_redact_phone(self):
        from gateway.platforms.helpers import redact_phone

        result = redact_phone("+905551234567")
        assert isinstance(result, str)

    def test_redact_phone_short(self):
        from gateway.platforms.helpers import redact_phone

        result = redact_phone("123")
        assert isinstance(result, str)


class TestTextBatchAggregator:
    def test_init(self):
        from gateway.platforms.helpers import TextBatchAggregator

        handler = lambda text: None
        agg = TextBatchAggregator(handler=handler)
        assert agg is not None
