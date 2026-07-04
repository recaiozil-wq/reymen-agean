"""Test: reymen/telegram_bot/__init__.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestTelegramBot:
    def test_bot_class_import(self):
        from reymen.telegram_bot import ReYMeNTelegramBot

        assert ReYMeNTelegramBot is not None

    def test_bot_create(self):
        from reymen.telegram_bot import ReYMeNTelegramBot

        bot = ReYMeNTelegramBot(token="test:token", bot_ad="test_bot")
        assert bot is not None
        assert bot.bot_ad == "test_bot"

    def test_main_function(self):
        from reymen.telegram_bot import main

        assert callable(main)
