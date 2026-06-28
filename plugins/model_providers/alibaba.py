"""
Alibaba Cloud (Qwen) model sağlayıcı.

Alibaba Cloud DashScope API üzerinden Qwen modelleri.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class AlibabaProvider:
    """Alibaba Cloud (Qwen) API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-plus"):
        self.api_key = api_key or os.environ.get("ALIBABA_API_KEY", "") or os.environ.get("DASHSCOPE_API_KEY", "")
        self.model = model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """Qwen chat tamamlama."""
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
            r = requests.post(f"{self.base_url}/services/aigc/text-generation/generation", json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Alibaba chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "Alibaba: API anahtarı bulunamadı (ALIBABA_API_KEY veya DASHSCOPE_API_KEY)"
        return f"AlibabaProvider hazır (model: {self.model})"
