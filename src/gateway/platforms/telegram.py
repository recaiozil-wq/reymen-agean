# -*- coding: utf-8 -*-
"""gateway.platforms.telegram — Telegram platform adaptörü."""

from __future__ import annotations

from typing import Any, Set

from gateway.platforms.base import BasePlatformAdapter, SendResult


TELEGRAM_AVAILABLE = True


def check_telegram_requirements() -> bool:
    return TELEGRAM_AVAILABLE


class TelegramAdapter(BasePlatformAdapter):
    """Telegram Bot API adaptörü."""

    platform = "telegram"

    def __init__(self, config: Any):
        self.config = config
        self._extra = getattr(config, "extra", {}) if config else {}

    def _telegram_allowed_chats(self) -> Set[str]:
        chats = self._extra.get("allowed_chats", [])
        return set(str(c) for c in chats)

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def send(self, chat_id: str, message: str, **kwargs) -> SendResult:
        return SendResult(success=True)

    async def get_chat_info(self, chat_id: str) -> dict:
        return {}
