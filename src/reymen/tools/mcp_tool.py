"""ReYMeN tools.mcp_tool shim â€” ReYMeN MCP tool fonksiyonlarÄ±nÄ± yönlendirir."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_servers: Dict[str, Any] = {}
_lock = None


def discover_mcp_tools(*args, **kwargs) -> List[Dict[str, Any]]:
    """ReYMeN discover_mcp_tools â€” ReYMeN stub."""
    return []


def shutdown_mcp_servers() -> None:
    """ReYMeN shutdown_mcp_servers â€” ReYMeN stub."""
    pass


def _kill_orphaned_mcp_children() -> None:
    """ReYMeN _kill_orphaned_mcp_children â€” ReYMeN stub."""
    pass
