# -*- coding: utf-8 -*-
"""Gemini API schema donusumleri.

Hermes agent/gemini_schema.py'den adapte edilmistir.
"""
from __future__ import annotations

GEMINI_SCHEMA = {"type": "object", "properties": {}}

def geminiye_cevir(mesajlar: list) -> list:
    return [{"role": m.get("role","user"), "parts": [{"text": str(m.get("content",""))}]} for m in mesajlar]
