"""Self-improvement birim testleri."""

from __future__ import annotations

import pytest

from ReYMeN import self_improve
from ReYMeN.self_improve import (
    QualityMetric,
    QualityReport,
    SelfImprover,
    evaluate,
    suggest_fix,
    record_step,
    report,
    reset_history,
)


class TestEvaluate:
    def test_perfect_score(self):
        metric = QualityMetric(success=True, errors=0, retries=0, duration=1.0)
        report = evaluate(metric)
        assert report.score == 1.0
        assert report.grade == "A"
        assert report.passed is True
        assert report.issues == []

    def test_failed_step(self):
        metric = QualityMetric(success=False, errors=0, retries=0, duration=1.0)
        report = evaluate(metric)
        assert report.score < 0.6
        assert report.grade == "F"
        assert report.passed is False
        assert "adım başarısız" in report.issues

    def test_high_errors(self):
        metric = QualityMetric(success=True, errors=5, retries=0, duration=1.0)
        report = evaluate(metric)
        assert report.score < 1.0
        assert any("hata" in i for i in report.issues)

    def test_many_retries(self):
        metric = QualityMetric(success=True, errors=0, retries=5, duration=1.0)
        report = evaluate(metric)
        assert report.score < 1.0
        assert any("yeniden deneme" in i for i in report.issues)

    def test_slow_duration(self):
        metric = QualityMetric(success=True, errors=0, retries=0, duration=60.0)
        report = evaluate(metric)
        assert report.score < 1.0
        assert any("süre" in i for i in report.issues)

    def test_score_clamped_to_range(self):
        metric = QualityMetric(success=False, errors=100, retries=100, duration=100.0)
        report = evaluate(metric)
        assert 0.0 <= report.score <= 1.0

    def test_grade_thresholds(self):
        # A: mükemmel (success + 0 hata + 0 retry + hızlı)
        assert evaluate(QualityMetric(True, 0, 0, 1.0)).grade == "A"
        # B: 0.8-0.9 arası — 1 retry, orta süre
        assert evaluate(QualityMetric(True, 0, 1, 10.0)).grade == "B"
        # C: 0.7-0.8 arası — 2 hata + 2 retry, orta süre = 0.75
        assert evaluate(QualityMetric(True, 2, 2, 10.0)).grade == "C"
        # D: 0.6-0.7 arası — 3 hata + 3 retry, orta süre = 0.65
        assert evaluate(QualityMetric(True, 3, 3, 10.0)).grade == "D"
        # F: başarısız
        assert evaluate(QualityMetric(False, 0, 0, 1.0)).grade == "F"


class TestSuggestFix:
    def test_no_suggestions_for_good_metric(self):
        metric = QualityMetric(success=True, errors=0, retries=0, duration=1.0)
        suggestions = suggest_fix(metric)
        assert any("iyileştirme gerekmiyor" in s.lower() for s in suggestions)

    def test_suggestion_for_failure(self):
        metric = QualityMetric(success=False, errors=0, retries=0, duration=1.0)
        suggestions = suggest_fix(metric)
        assert any("başarısız" in s.lower() for s in suggestions)

    def test_suggestion_for_high_errors(self):
        metric = QualityMetric(success=True, errors=5, retries=0, duration=1.0)
        suggestions = suggest_fix(metric)
        assert any("hata" in s.lower() for s in suggestions)

    def test_suggestion_for_many_retries(self):
        metric = QualityMetric(success=True, errors=0, retries=5, duration=1.0)
        suggestions = suggest_fix(metric)
        assert any("yeniden deneme" in s.lower() for s in suggestions)

    def test_suggestion_for_slow(self):
        metric = QualityMetric(success=True, errors=0, retries=0, duration=60.0)
        suggestions = suggest_fix(metric)
        assert any("yavaş" in s.lower() for s in suggestions)

    def test_suggestion_for_high_tokens(self):
        metric = QualityMetric(success=True, errors=0, retries=0, duration=1.0, tokens_used=20_000)
        suggestions = suggest_fix(metric)
        assert any("token" in s.lower() for s in suggestions)


class TestSelfImprover:
    def test_record_returns_report(self):
        improver = SelfImprover()
        metric = QualityMetric(success=True, errors=0, retries=0, duration=1.0)
        report = improver.record(metric)
        assert isinstance(report, QualityReport)
        assert report.score == 1.0

    def test_history_tracking(self):
        improver = SelfImprover()
        improver.record(QualityMetric(True, 0, 0, 1.0))
        improver.record(QualityMetric(False, 0, 0, 1.0))
        assert len(improver.history()) == 2

    def test_trend_empty(self):
        improver = SelfImprover()
        trend = improver.trend()
        assert trend["total_steps"] == 0
        assert trend["avg_score"] == 0.0

    def test_trend_after_records(self):
        improver = SelfImprover()
        improver.record(QualityMetric(True, 0, 0, 1.0))
        improver.record(QualityMetric(False, 0, 0, 1.0))
        trend = improver.trend()
        assert trend["total_steps"] == 2
        assert 0.0 < trend["avg_score"] < 1.0
        assert trend["pass_rate"] == 0.5
        assert trend["low_quality_steps"] == 1

    def test_low_quality_steps(self):
        improver = SelfImprover()
        improver.record(QualityMetric(True, 0, 0, 1.0))
        improver.record(QualityMetric(False, 0, 0, 1.0))
        low = improver.low_quality_steps()
        assert len(low) == 1

    def test_auto_improve_returns_suggestions(self):
        improver = SelfImprover()
        improver.record(QualityMetric(False, 5, 5, 60.0))
        suggestions = improver.auto_improve()
        assert len(suggestions) > 0

    def test_auto_improve_deduplicates(self):
        improver = SelfImprover()
        improver.record(QualityMetric(False, 5, 0, 1.0))
        improver.record(QualityMetric(False, 5, 0, 1.0))
        suggestions = improver.auto_improve()
        # Aynı öneri iki kez çıkmamalı
        assert len(suggestions) == len(set(suggestions))

    def test_reset(self):
        improver = SelfImprover()
        improver.record(QualityMetric(True, 0, 0, 1.0))
        improver.reset()
        assert len(improver.history()) == 0


class TestModuleLevel:
    def test_record_step_and_report(self):
        reset_history()
        record_step(QualityMetric(True, 0, 0, 1.0))
        r = report()
        assert r["total_steps"] == 1
        reset_history()