"""Test: reymen/cost_tracker.py — CostTracker, CostRecord, singleton testleri"""
from __future__ import annotations

import sys
import time
import json
from pathlib import Path

import pytest

# Proje kokunu path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@pytest.fixture
def tracker(tmp_path):
    from reymen.cost_tracker import CostTracker
    db_path = tmp_path / "test_costs.db"
    t = CostTracker(db_path=db_path)
    yield t


# ── CostRecord ───────────────────────────────────────────────────────────

class TestCostRecord:
    def test_as_dict(self):
        from reymen.cost_tracker import CostRecord
        r = CostRecord(model="gpt-4o", prompt_tokens=100, completion_tokens=50, cost_usd=0.005)
        d = r.as_dict()
        assert d["model"] == "gpt-4o"
        assert d["prompt_tokens"] == 100
        assert d["completion_tokens"] == 50
        assert d["cost_usd"] == 0.005
        assert "timestamp" in d

    def test_default_values(self):
        from reymen.cost_tracker import CostRecord
        r = CostRecord(model="test", prompt_tokens=10, completion_tokens=5, cost_usd=0.001)
        assert r.provider == ""
        assert r.session_id is None
        assert r.metadata == {}


# ── Price computation ────────────────────────────────────────────────────

class TestPriceFor:
    def test_exact_model_match(self, tracker):
        price = tracker._price_for("gpt-4o")
        assert price["prompt"] == 5.0
        assert price["completion"] == 15.0

    def test_prefix_match(self, tracker):
        price = tracker._price_for("gpt-4o-2024-08-06")
        assert price["prompt"] == 5.0

    def test_default_fallback(self, tracker):
        price = tracker._price_for("unknown-model-v99")
        assert price["prompt"] == 1.0
        assert price["completion"] == 3.0

    def test_custom_price_table(self, tmp_path):
        from reymen.cost_tracker import CostTracker
        custom = {
            "my-model": {"prompt": 10.0, "completion": 20.0},
            "default": {"prompt": 1.0, "completion": 2.0},
        }
        t = CostTracker(db_path=tmp_path / "c.db", price_table=custom)
        assert t._price_for("my-model")["prompt"] == 10.0
        assert t._price_for("other")["prompt"] == 1.0


class TestComputeCost:
    def test_basic_computation(self, tracker):
        cost = tracker.compute_cost("gpt-4o", 1_000_000, 500_000)
        assert cost == 12.5

    def test_zero_tokens(self, tracker):
        cost = tracker.compute_cost("gpt-4o", 0, 0)
        assert cost == 0.0

    def test_rounding_precision(self, tracker):
        cost = tracker.compute_cost("gpt-4o-mini", 100, 50)
        assert cost == 0.000045

    def test_only_prompt_tokens(self, tracker):
        cost = tracker.compute_cost("gpt-4o", 1_000_000, 0)
        assert cost == 5.0

    def test_only_completion_tokens(self, tracker):
        cost = tracker.compute_cost("gpt-4o", 0, 1_000_000)
        assert cost == 15.0


# ── Record ───────────────────────────────────────────────────────────────

class TestRecord:
    def test_basic_record(self, tracker):
        rec = tracker.record("gpt-4o", 1000, 500)
        assert rec.model == "gpt-4o"
        assert rec.prompt_tokens == 1000
        assert rec.completion_tokens == 500
        assert rec.cost_usd > 0

    def test_record_with_provider_and_session(self, tracker):
        rec = tracker.record(
            "gpt-4o", 100, 50,
            provider="openai",
            session_id="sess-001",
            metadata={"test": True},
        )
        assert rec.provider == "openai"
        assert rec.session_id == "sess-001"
        assert rec.metadata["test"] is True

    def test_negative_tokens_raises(self, tracker):
        with pytest.raises(ValueError, match="negatif"):
            tracker.record("gpt-4o", -1, 50)

    def test_negative_completion_tokens_raises(self, tracker):
        with pytest.raises(ValueError, match="negatif"):
            tracker.record("gpt-4o", 100, -5)

    def test_multiple_records_persist(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 200, 100)
        s = tracker.summary()
        assert s["total_calls"] == 2
        assert s["total_prompt_tokens"] == 300


# ── Summary ──────────────────────────────────────────────────────────────

class TestSummary:
    def test_empty_summary(self, tracker):
        s = tracker.summary()
        assert s["total_calls"] == 0
        assert s["total_cost_usd"] == 0.0
        assert s["by_model"] == {}

    def test_summary_with_data(self, tracker):
        tracker.record("gpt-4o", 1_000_000, 500_000)
        s = tracker.summary()
        assert s["total_calls"] == 1
        assert s["total_cost_usd"] == 12.5

    def test_summary_by_model(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 200, 100)
        s = tracker.summary()
        assert "gpt-4o" in s["by_model"]
        assert "gpt-4o-mini" in s["by_model"]

    def test_summary_by_provider(self, tracker):
        tracker.record("gpt-4o", 100, 50, provider="openai")
        tracker.record("claude-3-5-sonnet", 200, 100, provider="anthropic")
        s = tracker.summary()
        assert "openai" in s["by_provider"]
        assert "anthropic" in s["by_provider"]

    def test_summary_filter_by_model(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 200, 100)
        s = tracker.summary(model="gpt-4o")
        assert s["total_calls"] == 1
        assert "gpt-4o-mini" not in s["by_model"]

    def test_summary_filter_by_session(self, tracker):
        tracker.record("gpt-4o", 100, 50, session_id="s1")
        tracker.record("gpt-4o", 200, 100, session_id="s2")
        s = tracker.summary(session_id="s1")
        assert s["total_calls"] == 1

    def test_summary_since_timestamp(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        now = time.time()
        tracker.record("gpt-4o-mini", 200, 100)
        s = tracker.summary(since=now)
        assert s["total_calls"] == 1


# ── DumpLog ──────────────────────────────────────────────────────────────

class TestDumpLog:
    def test_dump_empty(self, tracker):
        logs = tracker.dump_log()
        assert logs == []

    def test_dump_with_data(self, tracker):
        tracker.record("gpt-4o", 100, 50, metadata={"test": True})
        logs = tracker.dump_log()
        assert len(logs) == 1
        assert logs[0]["model"] == "gpt-4o"
        assert logs[0]["metadata"]["test"] is True

    def test_dump_limit(self, tracker):
        for i in range(5):
            tracker.record(f"model-{i}", 10, 5)
        logs = tracker.dump_log(limit=2)
        assert len(logs) == 2

    def test_dump_filter_model(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("claude-3-5-sonnet", 200, 100)
        logs = tracker.dump_log(model="gpt-4o")
        assert len(logs) == 1
        assert logs[0]["model"] == "gpt-4o"


# ── Reset ────────────────────────────────────────────────────────────────

class TestReset:
    def test_reset_clears_records(self, tracker):
        tracker.record("gpt-4o", 100, 50)
        tracker.record("gpt-4o-mini", 200, 100)
        deleted = tracker.reset()
        assert deleted == 2
        s = tracker.summary()
        assert s["total_calls"] == 0

    def test_reset_empty(self, tracker):
        deleted = tracker.reset()
        assert deleted == 0


# ── IterRecords ──────────────────────────────────────────────────────────

class TestIterRecords:
    def test_iter_returns_records(self, tracker):
        from reymen.cost_tracker import CostRecord
        tracker.record("gpt-4o", 100, 50)
        tracker.record("claude-3-5-sonnet", 200, 100)
        records = list(tracker.iter_records())
        assert len(records) == 2
        assert all(isinstance(r, CostRecord) for r in records)

    def test_iter_empty(self, tracker):
        records = list(tracker.iter_records())
        assert records == []


# ── Module-level functions ───────────────────────────────────────────────

class TestModuleFunctions:
    def test_record_usage_and_summary(self, tmp_path, monkeypatch):
        from reymen import cost_tracker
        monkeypatch.setenv("ReYMeN_HOME", str(tmp_path))
        cost_tracker.set_db_path(tmp_path / "mod.db")
        rec = cost_tracker.record_usage("gpt-4o", 1000, 500, provider="openai")
        assert rec.model == "gpt-4o"
        s = cost_tracker.summary()
        assert s["total_calls"] == 1
        assert s["total_cost_usd"] > 0
        cost_tracker.reset()

    def test_dump_log_module(self, tmp_path, monkeypatch):
        from reymen import cost_tracker
        monkeypatch.setenv("ReYMeN_HOME", str(tmp_path))
        cost_tracker.set_db_path(tmp_path / "mod2.db")
        cost_tracker.record_usage("gpt-4o", 100, 50)
        logs = cost_tracker.dump_log()
        assert len(logs) == 1
        cost_tracker.reset()

    def test_set_price_table_module(self, tmp_path, monkeypatch):
        from reymen import cost_tracker
        monkeypatch.setenv("ReYMeN_HOME", str(tmp_path))
        cost_tracker.set_db_path(tmp_path / "mod3.db")
        custom = {"my-model": {"prompt": 99.0, "completion": 199.0}, "default": {"prompt": 1.0, "completion": 2.0}}
        cost_tracker.set_price_table(custom)
        rec = cost_tracker.record_usage("my-model", 1_000_000, 0)
        assert rec.cost_usd == 99.0
        cost_tracker.reset()
