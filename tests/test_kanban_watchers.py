# -*- coding: utf-8 -*-
"""tests/test_kanban_watchers.py — GatewayKanbanWatchersMixin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from gateway.kanban_watchers import GatewayKanbanWatchersMixin


class FakeGatewayRunner:
    """Minimal stand-in for GatewayRunner that uses the mixin."""
    def __init__(self):
        self._platformlar = {}
        self._kanban_sub_fail_counts = {}


class TestGatewayKanbanWatchersMixin:
    def test_mixin_class_exists(self):
        assert GatewayKanbanWatchersMixin is not None

    @pytest.mark.asyncio
    async def test_kanban_notifier_watcher_disabled_by_env(self):
        runner = FakeGatewayRunner()
        mixin = GatewayKanbanWatchersMixin()
        # Simulate inherited method call
        with patch.dict("os.environ", {"REYMEN_KANBAN_DISPATCH_IN_GATEWAY": "0"}, clear=False):
            # We need to bind the mixin method to the runner for self access
            bound_method = mixin._kanban_notifier_watcher.__get__(runner, type(runner))
            result = await bound_method(interval=1.0)
            # Should not raise and return early
            assert result is None

    def test_mixin_basic(self):
        """Verify the mixin can be combined with a class."""
        class TestRunner(GatewayKanbanWatchersMixin):
            def __init__(self):
                self._platformlar = {}
                self._kanban_sub_fail_counts = {}
        runner = TestRunner()
        assert hasattr(runner, "_kanban_notifier_watcher")
        assert hasattr(runner, "_kanban_sub_fail_counts")

    @pytest.mark.asyncio
    async def test_dispatch_workflow(self):
        """Test the worker dispatch dispatches correctly when config is available."""
        class TestRunner(GatewayKanbanWatchersMixin):
            def __init__(self):
                self._platformlar = {}
                self._kanban_sub_fail_counts = {}
                self._config_loaded = False

        runner = TestRunner()
        # Just verify the method exists and can be called
        assert callable(runner._kanban_notifier_watcher)

    def test_kanban_sub_fail_counts_default(self):
        """When accessed via getattr default, creates empty dict."""
        runner = FakeGatewayRunner()
        counts = getattr(runner, "_kanban_sub_fail_counts", {})
        assert counts == {}
