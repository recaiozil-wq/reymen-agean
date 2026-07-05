# -*- coding: utf-8 -*-
"""Kimlik bilgisi havuzu.

Hermes agent/credential_pool.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class CredentialPool:
    """API key havuzu - birden cok key arasinda gecis yapar."""
    def __init__(self):
        self._havuz = {}
    def ekle(self, anahtar, deger):
        self._havuz[anahtar] = deger
    def al(self, anahtar):
        return self._havuz.get(anahtar)
    def var_mi(self, anahtar):
        return anahtar in self._havuz
