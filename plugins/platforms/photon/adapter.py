# -*- coding: utf-8 -*-
"""plugins/platforms/photon/adapter.py — Photon platform adaptörü."""
from __future__ import annotations

from typing import Any, List, Optional


class PhotonAdapter:
    """Photon (BlueBubbles/iMessage) platform adaptörü."""

    def __init__(self, config=None):
        self.platform = "photon"
        self.config = config
        extra = getattr(config, "extra", {}) or {} if config else {}
        self._server_url = extra.get("server_url", "")
        self._password = extra.get("password", "")
        self._events: List[Any] = []

    async def connect(self) -> bool:
        return bool(self._server_url and self._password)

    async def disconnect(self) -> None:
        pass

    async def send(self, chat_id: str, content: str, **kwargs) -> Any:
        from gateway.platforms.base import SendResult
        return SendResult(success=True, message_id="photon-1")

    def handle_inbound(self, data: dict) -> Optional[Any]:
        """Gelen webhook mesajını işle."""
        from gateway.platforms.base import MessageEvent, MessageType
        text = data.get("text", "")
        if not text:
            return None
        event = MessageEvent(
            message_id=str(data.get("id", "")),
            chat_id=str(data.get("chat_id", "")),
            user_id=str(data.get("from", "")),
            text=text,
            platform="photon",
            raw=data,
        )
        self._events.append(event)
        return event


if __name__ == "__main__":
    print("PhotonAdapter importlandı.")

def _env_enablement():
    import os as _os; return bool(_os.environ.get("BLUEBUBBLES_SERVER_URL") and _os.environ.get("BLUEBUBBLES_PASSWORD"))
