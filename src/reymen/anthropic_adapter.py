# -*- coding: utf-8 -*-
"""Anthropic Claude API adapter.

Hermes agent/anthropic_adapter.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class AnthropicAdapter:
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.aktif = bool(self.api_key)

    def is_available(self) -> bool:
        return self.aktif

    def uret(self, mesajlar: list, model: str = "claude-sonnet-4") -> Optional[dict]:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            r = client.messages.create(model=model, max_tokens=4096, messages=mesajlar)
            return {"choices": [{"message": {"role": "assistant", "content": r.content[0].text}}]}
        except Exception as e:
            logger.debug("Anthropic hatasi: %s", e)
            return None
