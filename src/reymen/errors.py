# -*- coding: utf-8 -*-
"""Hata siniflari.

Hermes agent/errors.py'den adapte edilmistir.
"""
from __future__ import annotations

class ReYMeNError(Exception):
    """Temel ReYMeN hatasi."""
    def __init__(self, mesaj: str = "", kod: int = 0):
        self.mesaj = mesaj
        self.kod = kod
        super().__init__(mesaj)

class ProviderError(ReYMeNError):
    """Provider kaynakli hata."""

class ToolError(ReYMeNError):
    """Tool kaynakli hata."""

class ConfigError(ReYMeNError):
    """Config kaynakli hata."""
