# -*- coding: utf-8 -*-
"""Xiaomi MiMo (MiniMax) API adapteri — api.minimax.chat/v1/text/chatcompletion_v2."""

import httpx
import logging
from typing import Optional

log = logging.getLogger(__name__)

BASE_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

class XiaomiAdapter:
    def __init__(self, api_key: str, model: str = "mimo-v2.5-pro",
                 group_id: Optional[str] = None, timeout: int = 120):
        self.api_key = api_key
        self.model = model
        self.group_id = group_id
        self.timeout = timeout

    def cagri_yap(self, messages: list, temperature: float = 0.7,
                  max_tokens: int = 4096) -> dict:
        """MiniMax API'ye istek gonder."""
        # MiniMax /v2 endpoint'te model query param'da gider
        params = {"ModelId": self.model}
        if self.group_id:
            params["GroupId"] = self.group_id

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(BASE_URL, headers=headers, json=payload, params=params)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"basarili": True, "yanit": content, "ham": data}
            else:
                log.warning("Xiaomi HTTP %s: %s", resp.status_code, resp.text[:200])
                return {"basarili": False, "hata": f"HTTP {resp.status_code}", "kod": resp.status_code}
        except Exception as e:
            log.error("Xiaomi hatasi: %s", e)
            return {"basarili": False, "hata": str(e)}

    def kontrol(self) -> bool:
        """Basit saglik kontrolu."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get("https://api.minimax.chat/v1/status")
            return resp.status_code == 200
        except Exception:
            return False
