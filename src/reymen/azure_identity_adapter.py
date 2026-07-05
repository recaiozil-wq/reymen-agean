# -*- coding: utf-8 -*-
"""Azure Identity adapter.

Hermes agent/azure_identity_adapter.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class AzureIdentityAdapter:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
    def get_token(self) -> str:
        return ""
