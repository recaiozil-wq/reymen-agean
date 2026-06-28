"""
Novita AI model sağlayıcı.

Novita AI LLM API üzerinden model çağrıları.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class NovitaProvider:
    """Novita AI API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-7b-instruct"):
        self.api_key = api_key or os.environ.get("NOVITA_API_KEY", "")
        self.model = model
        self.base_url = "https://api.novita.ai/v3/openai"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """Novita AI chat tamamlama."""
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
            logger.error("Novita chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "Novita: API anahtarı bulunamadı (NOVITA_API_KEY)"
        return f"NovitaProvider hazır (model: {self.model})"
