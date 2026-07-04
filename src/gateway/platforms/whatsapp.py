# -*- coding: utf-8 -*-
"""gateway.platforms.whatsapp — WhatsApp platform adaptörü."""

from __future__ import annotations

from typing import Any

from gateway.platforms.base import BasePlatformAdapter, SendResult
from gateway.platforms.whatsapp_common import WhatsAppBehaviorMixin


def check_whatsapp_requirements() -> bool:
    return True


class WhatsAppAdapter(WhatsAppBehaviorMixin, BasePlatformAdapter):
    """WhatsApp Business Cloud API adaptörü."""

    platform = "whatsapp"

    def __init__(self, config: Any):
        self.config = config
        self._extra = getattr(config, "extra", {}) if config else {}

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def send(self, chat_id: str, message: str, **kwargs) -> SendResult:
        return SendResult(success=True)

    async def get_chat_info(self, chat_id: str) -> dict:
        return {}
