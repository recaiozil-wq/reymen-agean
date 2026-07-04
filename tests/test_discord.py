# -*- coding: utf-8 -*-
"""gateway/platforms/discord.py testleri — actual API.

Discord modulu bu projede mevcut degil.
Tum testler modulun mevcut olmadigini dogruluyor.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestDiscordModule:
    def test_discord_module_not_exists(self):
        """Discord modulu su an mevcut degil."""
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from gateway.platforms import discord

    def test_discord_import_error(self):
        """gateway.platforms.discord import edilemez."""
        with pytest.raises((ImportError, ModuleNotFoundError)):
            __import__("gateway.platforms.discord")
