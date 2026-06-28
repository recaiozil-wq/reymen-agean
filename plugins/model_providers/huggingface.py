"""
HuggingFace Inference API sağlayıcı.

HuggingFace Inference API üzerinden model çağrıları.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class HuggingFaceProvider:
    """HuggingFace Inference API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "HuggingFaceH4/zephyr-7b-beta"):
        self.api_key = api_key or os.environ.get("HF_API_KEY", "") or os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
        self.model = model
        self.base_url = "https://api-inference.huggingface.co/models"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """HuggingFace chat tamamlama."""
        try:
            # Son mesajı prompt olarak kullan
            prompt = mesajlar[-1]["content"] if mesajlar else ""
            return self.generate(prompt, **kwargs)
        except Exception as e:
            logger.error("HF chat hatası: %s", e)
            return {"error": str(e)}

    def generate(self, prompt: str, **kwargs) -> dict[str, Any]:
        """HuggingFace Inference API çağrısı."""
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        payload = {"inputs": prompt, "parameters": {**kwargs}}

        try:
            r = requests.post(f"{self.base_url}/{self.model}", json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("HF generate hatası (%s): %s", self.model, e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "HuggingFace: API anahtarı bulunamadı (HF_API_KEY veya HUGGINGFACEHUB_API_TOKEN)"
        return f"HuggingFaceProvider hazır (model: {self.model})"
