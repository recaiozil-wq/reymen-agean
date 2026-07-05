"""ReYMeN tools.schema_sanitizer shim â€” ReYMeN schema sanitizer'Ä±nÄ± yönlendirir."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def sanitize_tool_schemas(schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """ReYMeN sanitize_tool_schemas â€” ReYMeN'de olduÄŸu gibi geçir."""
    return schemas
