"""
Cohere model sağlayıcı.

Cohere API üzerinden chat/generate.
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CohereProvider:
    """Cohere API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "command-r-plus"):
        self.api_key = api_key or os.environ.get("COHERE_API_KEY", "")
        self.model = model
        self.base_url = "https://api.cohere.ai/v1"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """Cohere chat tamamlama."""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "message": mesajlar[-1]["content"] if mesajlar else "",
            "chat_history": [
                {"role": m["role"], "message": m["content"]}
                for m in mesajlar[:-1]
            ],
            **kwargs,
        }
        try:
            r = requests.post(f"{self.base_url}/chat", json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Cohere chat hatası: %s", e)
            return {"error": str(e)}

    def generate(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Cohere generate (eski API)."""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "prompt": prompt, **kwargs}
        try:
            r = requests.post(f"{self.base_url}/generate", json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Cohere generate hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "Cohere: API anahtarı bulunamadı (COHERE_API_KEY)"
        return f"CohereProvider hazır (model: {self.model})"
