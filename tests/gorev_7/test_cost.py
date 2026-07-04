"""Cost tracker birim testleri."""

from __future__ import annotations

import os
import time

import pytest

from reymen import cost_tracker
from reymen.cost_tracker import CostTracker, CostRecord


@pytest.fixture
def tracker(tmp_path):
    """Her test için izole bir CostTracker."""
    db = tmp_path / "test_costs.db"
    return CostTracker(db_path=db)


class TestCostComputation:
    def test_known_model_price(self, tracker):
        cost = tracker.compute_cost(
            "gpt-4o", prompt_tokens=1_000_000, completion_tokens=0
        )
        assert cost == 5.0

    def test_completion_price(self, tracker):
        cost = tracker.compute_cost(
            "gpt-4o", prompt_tokens=0, completion_tokens=1_000_000
        )
        assert cost == 15.0

    def test_combined_tokens(self, tracker):
        cost = tracker.compute_cost(
            "gpt-4o", prompt_tokens=1_000_000, completion_tokens=1_000_000
        )
        assert cost == 20.0

    def test_unknown_model_uses_default(self, tracker):
        cost = tracker.compute_cost(
            "unknown-model", prompt_tokens=1_000_000, completion_tokens=0
        )
        assert cost == 1.0

    def test_prefix_matching(self, tracker):
        cost = tracker.compute_cost(
            "gpt-4o-2024-08-06", prompt_tokens=1_000_000, completion_tokens=0
        )
        assert cost == 5.0

    def test_custom_price_table(self, tmp_path):
        custom = {
            "my-model": {"prompt": 2.0, "completion": 6.0},
            "default": {"prompt": 1.0, "completion": 3.0},
        }
        t = CostTracker(db_path=tmp_path / "x.db", price_table=custom)
        assert t.compute_cost("my-model", 1_000_000, 0) == 2.0


class TestRecord:
    def test_record_returns_cost_record(self, tracker):
        rec = tracker.record("gpt-4o", 1000, 500)
        assert isinstance(rec, CostRecord)
        assert rec.model == "gpt-4o"
        assert rec.prompt_tokens == 1000
        assert rec.completion_tokens == 500
        assert rec.cost_usd > 0

    def test_record_with_metadata(self, tracker):
        rec = tracker.record(
            "gpt-4o", 100, 50, session_id="s1", metadata={"task": "test"}
        )
        assert rec.session_id == "s1"
        assert rec.metadata == {"task": "test"}

    def test_negative_tokens_raises(self, tracker):
        with pytest.raises(ValueError):
            tracker.record("gpt-4o", -1, 0)


class TestSummary:
    def test_empty_summary(self, tracker):
        s = tracker.summary()
        assert s["total_calls"] == 0
        assert s["total_cost_usd"] == 0.0
        assert s["by_model"] == {}

    def test_summary_after_records(self, tracker):
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("gpt-4o-mini", 2000, 1000)
        s = tracker.summary()
        assert s["total_calls"] == 2
        assert s["total_prompt_tokens"] == 3000
        assert s["total_completion_tokens"] == 1500
        assert s["total_tokens"] == 4500
        assert "gpt-4o" in s["by_model"]
        assert "gpt-4o-mini" in s["by_model"]
        assert s["total_cost_usd"] > 0

    def test_summary_filter_by_model(self, tracker):
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("gpt-4o-mini", 2000, 1000)
        s = tracker.summary(model="gpt-4o")
        assert s["total_calls"] == 1
        assert "gpt-4o-mini" not in s["by_model"]

    def test_summary_filter_by_session(self, tracker):
        tracker.record("gpt-4o", 1000, 500, session_id="s1")
        tracker.record("gpt-4o", 2000, 1000, session_id="s2")
        s = tracker.summary(session_id="s1")
        assert s["total_calls"] == 1


class TestDumpLog:
    def test_dump_log_returns_records(self, tracker):
        tracker.record("gpt-4o", 1000, 500)
        tracker.record("gpt-4o-mini", 2000, 1000)
        log = tracker.dump_log()
        assert len(log) == 2
        assert log[0]["model"] in ("gpt-4o", "gpt-4o-mini")

    def test_dump_log_limit(self, tracker):
        for i in range(10):
            tracker.record("gpt-4o", 100, 50)
        log = tracker.dump_log(limit=3)
        assert len(log) == 3

    def test_dump_log_filter_model(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 100, 50)
        log = tracker.dump_log(model="gpt-4o")
        assert all(r["model"] == "gpt-4o" for r in log)


class TestReset:
    def test_reset_clears_records(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        count = tracker.reset()
        assert count == 1
        assert tracker.summary()["total_calls"] == 0


class TestIterRecords:
    def test_iter_records(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 200, 100)
        records = list(tracker.iter_records())
        assert len(records) == 2
        assert all(isinstance(r, CostRecord) for r in records)


class TestModuleLevel:
    def test_module_singleton(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ReYMeN_HOME", str(tmp_path))
        cost_tracker.set_db_path(tmp_path / "module.db")
        cost_tracker.record_usage("gpt-4o", 100, 50)
        s = cost_tracker.summary()
        assert s["total_calls"] == 1
        cost_tracker.reset()
