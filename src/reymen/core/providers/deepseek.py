# -*- coding: utf-8 -*-
"""DeepSeek API adapteri — api.deepseek.com/v1/chat/completions."""

import httpx
import logging
from typing import Optional

log = logging.getLogger(__name__)

BASE_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekAdapter:
    def __init__(self, api_key: str, model: str = "deepseek-chat", timeout: int = 120):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def cagri_yap(self, messages: list, temperature: float = 0.7,
                  max_tokens: int = 4096, frequency_penalty: float = 0.0) -> dict:
        """DeepSeek API'ye istek gonder."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(BASE_URL, headers=self.headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"basarili": True, "yanit": content, "ham": data}
            else:
                log.warning("DeepSeek HTTP %s: %s", resp.status_code, resp.text[:200])
                return {"basarili": False, "hata": f"HTTP {resp.status_code}", "kod": resp.status_code}
        except Exception as e:
            log.error("DeepSeek hatasi: %s", e)
            return {"basarili": False, "hata": str(e)}

    def kontrol(self) -> bool:
        """API key gecerli mi? GET /v1/models ile test et."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    "https://api.deepseek.com/v1/models",
                    headers=self.headers,
                )
            return resp.status_code == 200
        except Exception:
            return False
