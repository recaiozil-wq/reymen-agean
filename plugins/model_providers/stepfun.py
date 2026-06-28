"""
StepFun (Step) model sağlayıcı.

StepFun API üzerinden Step-1/Step-2 modelleri.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class StepFunProvider:
    """StepFun API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "step-1-8k"):
        self.api_key = api_key or os.environ.get("STEPFUN_API_KEY", "")
        self.model = model
        self.base_url = "https://api.stepfun.com/v1"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """StepFun chat tamamlama (OpenAI uyumlu)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": mesajlar,
            **kwargs,
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("StepFun chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "StepFun: API anahtarı bulunamadı (STEPFUN_API_KEY)"
        return f"StepFunProvider hazır (model: {self.model})"
