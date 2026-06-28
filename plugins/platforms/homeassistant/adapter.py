# -*- coding: utf-8 -*-
"""plugins/platforms/homeassistant/adapter.py — Home Assistant adaptörü."""
from __future__ import annotations

import os

try:
    import aiohttp as _aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


def check_ha_requirements() -> bool:
    """Home Assistant gereksinimlerini kontrol et."""
    return bool(os.environ.get("HASS_TOKEN") and AIOHTTP_AVAILABLE)


class HomeAssistantAdapter:
    """Home Assistant platform adaptörü."""

    def __init__(self, config=None):
        self.platform = "homeassistant"
        self.config = config
        extra = getattr(config, "extra", {}) or {} if config else {}
        self._base_url = extra.get("base_url", os.environ.get("HASS_BASE_URL", ""))
        self._token = extra.get("token", os.environ.get("HASS_TOKEN", ""))

    async def connect(self) -> bool:
        if not check_ha_requirements():
            return False
        return bool(self._base_url and self._token)

    async def disconnect(self) -> None:
        pass

    async def send(self, chat_id: str, content: str, **kwargs):
        from gateway.platforms.base import SendResult
        if not self._token:
            return SendResult(success=False, error="HASS_TOKEN yapılandırılmamış")
        return SendResult(success=True, message_id="ha-1")


if __name__ == "__main__":
    print("HomeAssistantAdapter importlandı. Gereksinimler:", check_ha_requirements())
