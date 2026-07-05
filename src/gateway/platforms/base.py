# -*- coding: utf-8 -*-
"""gateway.platforms.base â€” BasePlatformAdapter ABC."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MessageEvent:
    platform: str = ""
    chat_id: str = ""
    user_id: str = ""
    text: str = ""
    message_id: str = ""
    reply_to: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class SendResult:
    success: bool = True
    message_id: str = ""
    error: str = ""


class MessageType:
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class EphemeralReply:
    pass


class BasePlatformAdapter(ABC):
    """TÃ¼m platform adaptÃ¶rlerinin soyut temel sÄ±nÄ±fÄ±."""

    platform: str = ""

    @abstractmethod
    def __init__(self, config: Any = None):
        ...

    @abstractmethod
    async def connect(self) -> bool:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def send(self, chat_id: str, message: str, **kwargs) -> SendResult:
        ...

    @abstractmethod
    async def get_chat_info(self, chat_id: str) -> dict:
        ...
