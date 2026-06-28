"""
NVIDIA NIM model sağlayıcı.

NVIDIA NIM Inference API üzerinden model çağrıları.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class NvidiaProvider:
    """NVIDIA NIM API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "meta/llama-3.1-8b-instruct"):
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY", "")
        self.model = model
        self.base_url = "https://api.nvcf.nvidia.com/v2/nvcf"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """NVIDIA NIM chat tamamlama."""
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
            logger.error("NVIDIA chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "NVIDIA: API anahtarı bulunamadı (NVIDIA_API_KEY)"
        return f"NvidiaProvider hazır (model: {self.model})"
