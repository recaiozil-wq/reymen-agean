# -*- coding: utf-8 -*-
"""Browser Provider ABC — Web tarayici saglayicilari.

Hermes agent/browser_provider.py'den adapte edilmistir.
"""
from __future__ import annotations
import abc
from typing import Any, Dict

class BrowserProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @abc.abstractmethod
    def is_available(self) -> bool: ...

    @abc.abstractmethod
    def create_session(self, task_id: str) -> Dict[str, object]:
        """Browser oturumu olustur."""

    @abc.abstractmethod
    def close_session(self, session_id: str) -> bool:
        """Oturumu kapat."""

    def get_setup_schema(self) -> Dict[str, Any]:
        return {"name": self.name, "badge": "", "tag": "", "env_vars": []}
