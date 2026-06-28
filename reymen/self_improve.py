"""🔄 Self-improvement — Kalite metrikleri + otomatik iyileştirme.

Çözüm adımlarının kalitesini ölçer ve düşük kaliteli adımlar için
iyileştirme önerileri üretir. Metrikler: başarı, hata sayısı, yeniden
deneme sayısı, süre. Kalite skoru 0.0–1.0 arasındadır.

Örnek::

    from ReYMeN.self_improve import QualityMetric, evaluate, suggest_fix

    metric = QualityMetric(success=True, errors=0, retries=1, duration=2.5)
    score = evaluate(metric)
    print(score, suggest_fix(metric))
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "QualityMetric",
    "QualityReport",
    "evaluate",
    "suggest_fix",
    "SelfImprover",
    "record_step",
    "record_step_with_cost",
    "report",
    "reset_history",
]


# ---------------------------------------------------------------------------
# QualityMetric
# ---------------------------------------------------------------------------
@dataclass
class QualityMetric:
    """Tek bir çözüm adımının kalite metrikleri."""

    success: bool
    errors: int = 0
    retries: int = 0
    duration: float = 0.0
    tokens_used: int = 0
    step_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "errors": self.errors,
            "retries": self.retries,
            "duration": self.duration,
            "tokens_used": self.tokens_used,
            "step_name": self.step_name,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# QualityReport
# ---------------------------------------------------------------------------
@dataclass
class QualityReport:
    """Kalite değerlendirme raporu."""

    score: float  # 0.0 – 1.0
    grade: str  # "A" | "B" | "C" | "D" | "F"
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Skor 0.6 üstüyse geçer."""
        return self.score >= 0.6

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 3),
            "grade": self.grade,
            "passed": self.passed,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


# ---------------------------------------------------------------------------
# Değerlendirme
# ---------------------------------------------------------------------------
def _grade_for(score: float) -> str:
    if score >= 0.9:
        return "A"
    if score >= 0.8:
        return "B"
    if score >= 0.7:
        return "C"
    if score >= 0.6:
        return "D"
    return "F"


def evaluate(metric: QualityMetric) -> QualityReport:
    """Kalite metriklerini değerlendirip rapor döndürür.

    Skor hesaplama:
    - Başarı: +0.5
    - Hata yoksa: +0.2 (her hata -0.05, min 0)
    - Yeniden deneme yoksa: +0.15 (her retry -0.05, min 0)
    - Süre < 5sn: +0.15 (5–30sn: +0.10, >30sn: +0.0)
    """
    score = 0.0
    issues: list[str] = []

    # Başarı
    if metric.success:
        score += 0.5
    else:
        issues.append("adım başarısız")

    # Hata sayısı
    if metric.errors == 0:
        score += 0.2
    else:
        penalty = min(0.2, metric.errors * 0.05)
        score += 0.2 - penalty
        if metric.errors >= 3:
            issues.append(f"yüksek hata sayısı ({metric.errors})")

    # Yeniden deneme
    if metric.retries == 0:
        score += 0.15
    else:
        penalty = min(0.15, metric.retries * 0.05)
        score += 0.15 - penalty
        if metric.retries >= 3:
            issues.append(f"çok fazla yeniden deneme ({metric.retries})")

    # Süre
    if metric.duration <= 0:
        score += 0.0
    elif metric.duration < 5.0:
        score += 0.15
    elif metric.duration < 30.0:
        score += 0.10
    else:
        issues.append(f"uzun süre ({metric.duration:.1f}s)")
        score += 0.0

    score = max(0.0, min(1.0, score))
    return QualityReport(
        score=score,
        grade=_grade_for(score),
        issues=issues,
        suggestions=[],
    )


def suggest_fix(metric: QualityMetric) -> list[str]:
    """Düşük kaliteli adımlar için iyileştirme önerileri üretir."""
    suggestions: list[str] = []

    if not metric.success:
        suggestions.append("Adım başarısız — hata loglarını inceleyip kök nedeni bul.")

    if metric.errors >= 3:
        suggestions.append(
            "Çok hata var — input validasyonu ve hata yakalama (try/except) ekle."
        )

    if metric.retries >= 3:
        suggestions.append(
            "Çok yeniden deneme — backoff stratejisi veya farklı yaklaşım dene."
        )

    if metric.duration > 30.0:
        suggestions.append(
            "Yavaş adım — paralelleştirme, önbellekleme veya batch işlem düşün."
        )

    if metric.tokens_used > 10_000:
        suggestions.append(
            "Yüksek token kullanımı — prompt'u kısalt veya özetle."
        )

    if not suggestions:
        suggestions.append("İyi performans — iyileştirme gerekmiyor.")

    return suggestions


# ---------------------------------------------------------------------------
# SelfImprover — geçmiş takibi + otomatik iyileştirme
# ---------------------------------------------------------------------------
class SelfImprover:
    """Adım geçmişini tutar ve kalite trendini izler.

    Düşük kaliteli adımları tespit edip otomatik öneri üretir.
    """

    def __init__(self, threshold: float = 0.6) -> None:
        self.threshold = threshold
        self._history: list[tuple[QualityMetric, QualityReport]] = []

    def record(self, metric: QualityMetric) -> QualityReport:
        """Adımı değerlendirir ve geçmişe ekler."""
        report = evaluate(metric)
        if not report.passed:
            report.suggestions = suggest_fix(metric)
        self._history.append((metric, report))
        return report

    def history(self) -> list[tuple[QualityMetric, QualityReport]]:
        """Tüm geçmişi döndürür."""
        return list(self._history)

    def trend(self) -> dict[str, Any]:
        """Kalite trend özeti."""
        if not self._history:
            return {
                "total_steps": 0,
                "avg_score": 0.0,
                "pass_rate": 0.0,
                "low_quality_steps": 0,
            }
        scores = [r.score for _, r in self._history]
        passed = sum(1 for r in scores if r >= self.threshold)
        return {
            "total_steps": len(self._history),
            "avg_score": round(sum(scores) / len(scores), 3),
            "pass_rate": round(passed / len(self._history), 3),
            "low_quality_steps": len(self._history) - passed,
        }

    def low_quality_steps(self) -> list[tuple[QualityMetric, QualityReport]]:
        """Eşik altındaki adımları döndürür."""
        return [(m, r) for m, r in self._history if not r.passed]

    def auto_improve(self) -> list[str]:
        """Düşük kaliteli adımlar için toplu öneri üretir."""
        all_suggestions: list[str] = []
        for metric, report in self.low_quality_steps():
            all_suggestions.extend(report.suggestions)
        # Tekrarları kaldır, sırayı koru
        seen: set[str] = set()
        unique: list[str] = []
        for s in all_suggestions:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique

    def reset(self) -> None:
        """Geçmişi temizler."""
        self._history.clear()


# ---------------------------------------------------------------------------
# Modül-seviyesi singleton + kolaylık fonksiyonları
# ---------------------------------------------------------------------------
_singleton = SelfImprover()


def record_step(metric: QualityMetric) -> QualityReport:
    """Global improver üzerinden adım kaydı."""
    return _singleton.record(metric)


def report() -> dict[str, Any]:
    """Global improver trend raporu."""
    return _singleton.trend()


def reset_history() -> None:
    """Global improver geçmişini temizler."""
    _singleton.reset()


def record_step_with_cost(
    *,
    success: bool,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    errors: int = 0,
    retries: int = 0,
    duration: float = 0.0,
    step_name: str = "",
) -> QualityReport:
    """Maliyet ve kalite metriklerini birlikte kaydeder.

    ``cost_tracker`` ve ``self_improve`` modülleri arasında köprü kurar:
    API kullanımını maliyet veritabanına kaydeder ve aynı zamanda kalite
    olarak değerlendirir.

    Args:
        success: Adım başarılı mı?
        model: Kullanılan model adı.
        prompt_tokens: Prompt token sayısı.
        completion_tokens: Completion token sayısı.
        errors: Hata sayısı.
        retries: Yeniden deneme sayısı.
        duration: Süre (saniye).
        step_name: Adım adı.

    Returns:
        ``QualityReport``.
    """
    from . import cost_tracker

    # Maliyet kaydı
    cost_tracker.record_usage(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        metadata={"step_name": step_name} if step_name else None,
    )

    # Kalite kaydı
    metric = QualityMetric(
        success=success,
        errors=errors,
        retries=retries,
        duration=duration,
        tokens_used=prompt_tokens + completion_tokens,
        step_name=step_name,
    )
    return _singleton.record(metric)
