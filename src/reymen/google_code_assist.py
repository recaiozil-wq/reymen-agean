# -*- coding: utf-8 -*-
"""Google Code Assist entegrasyonu — Gemini tabanli kod yardimi.

Hermes agent/google_code_assist.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GoogleCodeAssist:
    """Google Code Assist API'sine baglan."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""

    def is_available(self) -> bool:
        return bool(self.api_key)

    def complete(self, code: str, context: str = "") -> Optional[str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"{context}\n\n{code}" if context else code
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.debug("Google Code Assist hatasi: %s", e)
            return None
