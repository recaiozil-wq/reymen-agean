# -*- coding: utf-8 -*-
"""LM Studio local API adapteri — localhost:1234/v1/chat/completions."""

import httpx
import logging
from typing import Optional

log = logging.getLogger(__name__)

DEFAULT_URL = "http://localhost:1234/v1/chat/completions"

class LMStudioAdapter:
    def __init__(self, base_url: str = DEFAULT_URL, model: str = "",
                 timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/chat/completions"):
            self.base_url += "/v1/chat/completions" if "/v1" not in self.base_url else ""
        self.model = model
        self.timeout = timeout

    def cagri_yap(self, messages: list, temperature: float = 0.7,
                  max_tokens: int = 4096) -> dict:
        """LM Studio'ya istek gonder."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if self.model:
            payload["model"] = self.model
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.base_url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {"basarili": True, "yanit": content, "ham": data}
            else:
                log.warning("LM Studio HTTP %s: %s", resp.status_code, resp.text[:200])
                return {"basarili": False, "hata": f"HTTP {resp.status_code}", "kod": resp.status_code}
        except httpx.ConnectError:
            log.warning("LM Studio calismiyor (baglanti reddedildi)")
            return {"basarili": False, "hata": "baglanti_reddedildi"}
        except Exception as e:
            log.error("LM Studio hatasi: %s", e)
            return {"basarili": False, "hata": str(e)}

    def kontrol(self) -> bool:
        """LM Studio calisiyor mu?"""
        try:
            hedef = self.base_url.replace("/chat/completions", "/models")
            with httpx.Client(timeout=5) as client:
                resp = client.get(hedef)
            return resp.status_code == 200
        except Exception:
            return False
