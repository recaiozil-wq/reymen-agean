"""
Azure OpenAI model sağlayıcı.

Azure OpenAI Service üzerinden model çağrıları.
"""

import json
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class AzureProvider:
    """Azure OpenAI API sağlayıcısı."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
    ):
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY", "")
        self.endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        self.deployment = deployment or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
        self.api_version = api_version

    def chat(self, mesajlar: list[dict], **kwargs) -> dict[str, Any]:
        """Azure OpenAI chat tamamlama."""
        if not self.endpoint:
            return {"error": "Azure endpoint bulunamadı (AZURE_OPENAI_ENDPOINT)"}

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        payload = {"messages": mesajlar, **kwargs}

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Azure chat hatası: %s", e)
            return {"error": str(e)}

    def run(self, **kwargs) -> str:
        """Sağlayıcıyı test eder."""
        if not self.api_key:
            return "Azure: API anahtarı bulunamadı (AZURE_OPENAI_API_KEY)"
        if not self.endpoint:
            return "Azure: endpoint bulunamadı (AZURE_OPENAI_ENDPOINT)"
        return f"AzureProvider hazır (deployment: {self.deployment})"
