"""
MiniMax model sağlayıcı.

MiniMax API üzerinden model çağrıları (MiniMax-Text-01, vb.).
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class MiniMaxProvider:
    """MiniMax API sağlayıcısı."""

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None, model: str = "MiniMax-Text-01"):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self.group_id = group_id or os.environ.get("MINIMAX_GROUP_ID", "")
        self.model = model
        self.base_url = "https://api.minimax.chat/v1"

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """MiniMax chat tamamlama."""
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
            logger.error("MiniMax chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "MiniMax: API anahtarı bulunamadı (MINIMAX_API_KEY)"
        return f"MiniMaxProvider hazır (model: {self.model})"
