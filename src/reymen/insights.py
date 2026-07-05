# -*- coding: utf-8 -*-
"""Kullanim istatistigi ve icgoruleri.

Hermes agent/insights.py'den adapte edilmistir.
"""
from __future__ import annotations
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Insights:
    """Kullanim istatistigi toplayici."""

    def __init__(self, kayit_yolu: Optional[Path] = None):
        self.kayit_yolu = kayit_yolu or Path.cwd() / ".ReYMeN" / "insights.json"
        self.kayit_yolu.parent.mkdir(parents=True, exist_ok=True)
        self._veriler = self._yukle()

    def _yukle(self) -> Dict:
        try:
            if self.kayit_yolu.exists():
                return json.loads(self.kayit_yolu.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {"oturumlar": [], "toplam_soru": 0, "toplam_token": 0}

    def _kaydet(self) -> None:
        try:
            self.kayit_yolu.write_text(json.dumps(self._veriler, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.debug("Insights kayit hatasi: %s", e)

    def soru_kaydet(self, soru: str, provider: str, token_sayisi: int = 0) -> None:
        self._veriler["toplam_soru"] += 1
        self._veriler["toplam_token"] += token_sayisi
        self._veriler["oturumlar"].append({
            "zaman": datetime.now().isoformat(),
            "soru_uzunluk": len(soru),
            "provider": provider,
            "token": token_sayisi,
        })
        if len(self._veriler["oturumlar"]) > 1000:
            self._veriler["oturumlar"] = self._veriler["oturumlar"][-1000:]
        self._kaydet()

    def rapor(self) -> str:
        v = self._veriler
        return (
            f"Toplam soru: {v['toplam_soru']}\n"
            f"Toplam token: {v['toplam_token']}\n"
            f"Son oturum: {v['oturumlar'][-1]['zaman'] if v['oturumlar'] else 'YOK'}"
        )

_insights = Insights()

def insights_al() -> Insights:
    return _insights
