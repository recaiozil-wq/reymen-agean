# -*- coding: utf-8 -*-
"""GitHub Copilot ACP client.

Hermes agent/copilot_acp_client.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class CopilotACPClient:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
