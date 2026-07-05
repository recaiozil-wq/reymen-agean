"""ğŸ“¡ A2A prototip â€” Basit agent mesajlaÅŸma.

Agent'lar arasÄ± mesajlaÅŸma prototipi. Bellek içi kuyruk tabanlÄ± basit
bir protokol saÄŸlar. Her agent bir inbox'a sahiptir; ``Broker`` mesajlarÄ±
hedef agent'a iletir. Thread-safe'dir.

Ã–rnek::

    from ReYMeN.a2a import Agent, Broker, Message

    broker = Broker()
    alice = Agent("alice", broker)
    bob = Agent("bob", broker)

    alice.send("bob", "Merhaba Bob!")
    msg = bob.receive()
    print(msg.content)
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

__all__ = [
    "MessageType",
    "Message",
    "Agent",
    "Broker",
    "A2AError",
]


# ---------------------------------------------------------------------------
# Hatalar
# ---------------------------------------------------------------------------
class A2AError(RuntimeError):
    """A2A mesajlaÅŸma hatasÄ±."""


# ---------------------------------------------------------------------------
# MessageType
# ---------------------------------------------------------------------------
class MessageType(str, Enum):
    """Mesaj tipleri."""

    TEXT = "text"
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------
@dataclass
class Message:
    """A2A mesajÄ±."""

    sender: str
    receiver: str
    content: Any
    type: MessageType = MessageType.TEXT
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    reply_to: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.type.value,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def reply(self, content: Any, *, msg_type: MessageType | None = None) -> "Message":
        """Bu mesaja yanÄ±t oluÅŸturur (sender/receiver ters çevrilir)."""
        return Message(
            sender=self.receiver,
            receiver=self.sender,
            content=content,
            type=msg_type or MessageType.RESPONSE,
            reply_to=self.id,
        )


# ---------------------------------------------------------------------------
# Broker
# ---------------------------------------------------------------------------
class Broker:
    """Merkezi mesaj broker'Ä±.

    Her agent için bir inbox (kuyruk) tutar. Thread-safe'dir. Mesajlar
    hedef agent kayÄ±tlÄ±ysa iletilir; deÄŸilse ``A2AError`` fÄ±rlatÄ±lÄ±r.
    """

    def __init__(self) -> None:
        self._inboxes: dict[str, deque[Message]] = {}
        self._conditions: dict[str, threading.Condition] = {}
        self._global_lock = threading.Lock()
        self._handlers: dict[str, Callable[[Message], None]] = {}
        self._log: list[Message] = []

    # -- KayÄ±t --------------------------------------------------------------
    def register(self, agent_id: str) -> None:
        """Agent'Ä± broker'a kaydeder."""
        with self._global_lock:
            if agent_id not in self._inboxes:
                self._inboxes[agent_id] = deque()
                self._conditions[agent_id] = threading.Condition()

    def unregister(self, agent_id: str) -> None:
        """Agent kaydÄ±nÄ± siler."""
        with self._global_lock:
            self._inboxes.pop(agent_id, None)
            self._conditions.pop(agent_id, None)
            self._handlers.pop(agent_id, None)

    def is_registered(self, agent_id: str) -> bool:
        return agent_id in self._inboxes

    # -- Gönderim -----------------------------------------------------------
    def send(self, message: Message) -> None:
        """MesajÄ± hedef agent'Ä±n inbox'Ä±na bÄ±rakÄ±r."""
        with self._global_lock:
            if message.receiver not in self._inboxes:
                raise A2AError(f"AlÄ±cÄ± '{message.receiver}' kayÄ±tlÄ± deÄŸil")
            inbox = self._inboxes[message.receiver]
            condition = self._conditions[message.receiver]

        with condition:
            inbox.append(message)
            condition.notify_all()

        self._log.append(message)

        # Handler varsa çaÄŸÄ±r
        handler = self._handlers.get(message.receiver)
        if handler is not None:
            try:
                handler(message)
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )  # Handler hatasÄ± mesaj akÄ±ÅŸÄ±nÄ± bozmamalÄ±

    def broadcast(
        self, sender: str, content: Any, *, exclude: set[str] | None = None
    ) -> list[str]:
        """Tüm kayÄ±tlÄ± agent'lara broadcast mesaj gönderir.

        Returns:
            MesajÄ±n iletildiÄŸi agent ID'leri.
        """
        exclude = exclude or set()
        exclude.add(sender)
        sent_to: list[str] = []
        with self._global_lock:
            targets = [aid for aid in self._inboxes if aid not in exclude]
        for aid in targets:
            msg = Message(
                sender=sender,
                receiver=aid,
                content=content,
                type=MessageType.BROADCAST,
            )
            self.send(msg)
            sent_to.append(aid)
        return sent_to

    # -- Alma ---------------------------------------------------------------
    def receive(
        self,
        agent_id: str,
        *,
        timeout: float | None = None,
        block: bool = True,
    ) -> Message | None:
        """Agent'Ä±n inbox'Ä±ndan mesaj alÄ±r.

        Args:
            agent_id: Agent ID.
            timeout: Saniye cinsinden bekleme süresi (None = sonsuz).
            block: ``False`` ise boÅŸ inbox'ta hemen None döner.

        Returns:
            ``Message`` veya inbox boÅŸsa ``None``.
        """
        with self._global_lock:
            if agent_id not in self._inboxes:
                raise A2AError(f"Agent '{agent_id}' kayÄ±tlÄ± deÄŸil")
            inbox = self._inboxes[agent_id]
            condition = self._conditions[agent_id]

        with condition:
            if block and not inbox:
                condition.wait(timeout=timeout)
            if inbox:
                return inbox.popleft()
            return None

    def peek(self, agent_id: str) -> Message | None:
        """Inbox'tan mesajÄ± silmeden okur."""
        with self._global_lock:
            if agent_id not in self._inboxes:
                raise A2AError(f"Agent '{agent_id}' kayÄ±tlÄ± deÄŸil")
            inbox = self._inboxes[agent_id]
            condition = self._conditions[agent_id]

        with condition:
            return inbox[0] if inbox else None

    def inbox_size(self, agent_id: str) -> int:
        """Agent'Ä±n inbox'undaki mesaj sayÄ±sÄ±."""
        with self._global_lock:
            if agent_id not in self._inboxes:
                raise A2AError(f"Agent '{agent_id}' kayÄ±tlÄ± deÄŸil")
            return len(self._inboxes[agent_id])

    # -- Handler ------------------------------------------------------------
    def set_handler(self, agent_id: str, handler: Callable[[Message], None]) -> None:
        """Agent için mesaj handler'Ä± ayarlar (mesaj geldiÄŸinde çaÄŸrÄ±lÄ±r)."""
        with self._global_lock:
            if agent_id not in self._inboxes:
                raise A2AError(f"Agent '{agent_id}' kayÄ±tlÄ± deÄŸil")
            self._handlers[agent_id] = handler

    def clear_handler(self, agent_id: str) -> None:
        """Agent'Ä±n handler'Ä±nÄ± temizler."""
        with self._global_lock:
            self._handlers.pop(agent_id, None)

    # -- Log / istatistik ---------------------------------------------------
    def message_log(self) -> list[Message]:
        """Tüm iletilen mesajlarÄ±n kopyasÄ±."""
        return list(self._log)

    def stats(self) -> dict[str, Any]:
        """Broker istatistikleri."""
        with self._global_lock:
            return {
                "agents": len(self._inboxes),
                "total_messages": len(self._log),
                "pending": {aid: len(inbox) for aid, inbox in self._inboxes.items()},
            }

    def reset(self) -> None:
        """Tüm inbox'larÄ± ve log'u temizler."""
        with self._global_lock:
            for inbox in self._inboxes.values():
                inbox.clear()
            for condition in self._conditions.values():
                with condition:
                    condition.notify_all()
            self._log.clear()


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class Agent:
    """A2A agent'Ä±.

    Bir ``Broker`` üzerinden mesaj gönderir/alÄ±r. ``on_message`` callback'i
    ile asenkron mesaj iÅŸleme yapÄ±labilir.
    """

    def __init__(
        self,
        agent_id: str,
        broker: Broker,
        *,
        on_message: Callable[[Message], None] | None = None,
    ) -> None:
        self.id = agent_id
        self.broker = broker
        self.broker.register(agent_id)
        if on_message is not None:
            self.broker.set_handler(agent_id, on_message)

    # -- Gönderim -----------------------------------------------------------
    def send(
        self,
        receiver: str,
        content: Any,
        *,
        msg_type: MessageType = MessageType.TEXT,
        reply_to: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """BaÅŸka bir agent'a mesaj gönderir."""
        msg = Message(
            sender=self.id,
            receiver=receiver,
            content=content,
            type=msg_type,
            reply_to=reply_to,
            metadata=metadata or {},
        )
        self.broker.send(msg)
        return msg

    def broadcast(self, content: Any, *, exclude: set[str] | None = None) -> list[str]:
        """Tüm agent'lara broadcast."""
        return self.broker.broadcast(self.id, content, exclude=exclude)

    def reply(self, original: Message, content: Any) -> Message:
        """Bir mesaja yanÄ±t verir."""
        msg = original.reply(content)
        self.broker.send(msg)
        return msg

    # -- Alma ---------------------------------------------------------------
    def receive(
        self,
        *,
        timeout: float | None = None,
        block: bool = True,
    ) -> Message | None:
        """Inbox'tan mesaj alÄ±r."""
        return self.broker.receive(self.id, timeout=timeout, block=block)

    def peek(self) -> Message | None:
        """Inbox'tan mesajÄ± silmeden okur."""
        return self.broker.peek(self.id)

    @property
    def inbox_size(self) -> int:
        """Bekleyen mesaj sayÄ±sÄ±."""
        return self.broker.inbox_size(self.id)

    # -- Handler ------------------------------------------------------------
    def set_handler(self, handler: Callable[[Message], None]) -> None:
        """Mesaj handler'Ä± ayarlar."""
        self.broker.set_handler(self.id, handler)

    def clear_handler(self) -> None:
        """Handler'Ä± temizler."""
        self.broker.clear_handler(self.id)

    # -- Temizlik -----------------------------------------------------------
    def close(self) -> None:
        """Agent'Ä± broker'dan kaydÄ±nÄ± siler."""
        self.broker.unregister(self.id)

    def __repr__(self) -> str:
        return f"Agent(id={self.id!r}, pending={self.inbox_size})"
