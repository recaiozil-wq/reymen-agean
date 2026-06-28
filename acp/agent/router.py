# -*- coding: utf-8 -*-
"""acp/agent/router.py — ACP ajan yönlendirici."""
from __future__ import annotations
from typing import Any, Callable, Dict, List


class AgentRouter:
    """ACP mesajlarını uygun ajana yönlendir."""

    def __init__(self):
        self._routes: Dict[str, Callable] = {}

    def register(self, pattern: str, handler: Callable) -> None:
        self._routes[pattern] = handler

    async def dispatch(self, message: Any) -> Any:
        for pattern, handler in self._routes.items():
            if pattern in str(message):
                return await handler(message)
        return None


if __name__ == '__main__':
    print('acp.agent.router importlandı.')

def build_agent_router(): return AgentRouter()
