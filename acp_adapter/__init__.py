# -*- coding: utf-8 -*-
"""acp_adapter/__init__.py — Agent Communication Protocol.

Ajanlar arasi JSON-RPC 2.0 iletisim protokolu.
ReYMeN'in diger ajanlarla (Claude Code, ReYMeN, Codex) konusmasini saglar.
"""

from .server import ACPServer
from .client import ACPClient

__all__ = ["ACPServer", "ACPClient"]
