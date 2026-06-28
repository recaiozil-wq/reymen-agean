# -*- coding: utf-8 -*-
"""acp/agent.py — ACP ajan arayüzü."""

__all__ = ['ACPAgent', 'Any', 'AsyncIterator', 'Dict', 'List', 'Optional', 'annotations', 'close', 'prompt']
from __future__ import annotations
from typing import Any, AsyncIterator, Dict, List, Optional


class ACPAgent:
    """ACP protokolü üzerinden çalışan ajan arayüzü."""

    def __init__(self, session_id: str = '', config: dict = None):
        self.session_id = session_id
        self.config = config or {}

    async def prompt(self, text: str, **kwargs) -> AsyncIterator:
        """Ajana prompt gönder."""
        if False:
            yield

    async def close(self) -> None:
        """Bağlantıyı kapat."""
        pass


if __name__ == '__main__':
    print('acp.agent importlandı.')
