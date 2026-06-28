"""Resolve ReYMeN_HOME for standalone skill scripts.

Skill scripts may run outside the ReYMeN process (e.g. system Python,
nix env, CI) where ``ReYMeN_constants`` is not importable.  This module
provides the same ``get_ReYMeN_home()`` and ``display_ReYMeN_home()``
contracts as ``ReYMeN_constants`` without requiring it on ``sys.path``.

When ``ReYMeN_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``ReYMeN_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``ReYMeN_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from ReYMeN_constants import display_ReYMeN_home as display_ReYMeN_home
    from ReYMeN_constants import get_ReYMeN_home as get_ReYMeN_home
except (ModuleNotFoundError, ImportError):

    def get_ReYMeN_home() -> Path:
        """Return the ReYMeN home directory (default: ~/.ReYMeN).

        Mirrors ``ReYMeN_constants.get_ReYMeN_home()``."""
        val = os.environ.get("ReYMeN_HOME", "").strip()
        return Path(val) if val else Path.home() / ".ReYMeN"

    def display_ReYMeN_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``ReYMeN_constants.display_ReYMeN_home()``."""
        home = get_ReYMeN_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
