# -*- coding: utf-8 -*-
"""OpenRouter API adapteri — openrouter.ai/api/v1/chat/completions."""

import httpx
import logging
from typing import Optional

log = logging.getLogger(__name__)

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterAdapter:
    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini",
                 timeout: int = 120, extra_headers: Optional[dict] = None):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.extra_headers = extra_headers or {}

    def cagri_yap(self, messages: list, temperature: float = 0.7,
                  max_tokens: int = 4096) -> dict:
        """OpenRouter API'ye istek gonder."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(BASE_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"basarili": True, "yanit": content, "ham": data}
            else:
                log.warning("OpenRouter HTTP %s: %s", resp.status_code, resp.text[:200])
                return {"basarili": False, "hata": f"HTTP {resp.status_code}", "kod": resp.status_code}
        except Exception as e:
            log.error("OpenRouter hatasi: %s", e)
            return {"basarili": False, "hata": str(e)}

    def kontrol(self) -> bool:
        """API key gecerli mi? /auth/key ile test."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
            return resp.status_code == 200
        except Exception:
            return False
