"""ReYMeN tools.cronjob_tools shim â€” ReYMeN cronjob araçlarÄ±nÄ± yönlendirir."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _scan_cron_prompt(prompt: str) -> dict:
    """ReYMeN _scan_cron_prompt â€” cron prompt'unu tarar."""
    return {"prompt": prompt, "schedule": None}


def _scan_cron_skill_assembled(skills: list) -> list:
    """ReYMeN _scan_cron_skill_assembled â€” skill listesini tarar."""
    return skills


def cronjob(*args, **kwargs) -> str:
    """ReYMeN cronjob â€” cronjob tool'una yönlendirir."""
    import json

    try:
        from reymen.cron.cronjob_tool import cronjob as _cronjob

        return _cronjob(*args, **kwargs)
    except Exception as e:
        return json.dumps({"success": False, "error": f"Cronjob unavailable: {e}"})
