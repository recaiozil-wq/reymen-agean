# -*- coding: utf-8 -*-
"""ğŸ“¡ ACP (Agent Communication Protocol) + A2A GeniÅŸletmeleri

Agent Communication Protocol (JSON-RPC 2.0 tabanlÄ±) sunucu ve istemci.
A2A'nÄ±n eksik yeteneklerini tamamlar:

- **Agent Card**: Yetkinlik bildirimi, keÅŸif, durum (capabilities)
- **Skill Transfer**: Agent'lar arasÄ± yetenek/beceri aktarÄ±mÄ±
- **Task Delegation**: GÃ¶rev devretme protokolÃ¼

KullanÄ±m:
    # Sunucu
    from reymen.a2a_acp import ACPServer
    server = ACPServer()
    server.start()

    # Ä°stemci (uzak sunucuya baÄŸlan)
    from reymen.a2a_acp import ACPClient
    client = ACPClient("http://localhost:9200")
    client.initialize()
    tools = client.tools_list()
"""

from __future__ import annotations

import json
import logging
import os
import queue
import socket
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# â”€â”€ Versiyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ACP_PROTOCOL_VERSION = "2025-03-26"
ACP_SERVER_VERSION = "1.0.0"


# â”€â”€ JSON-RPC Hata KodlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class ACPErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    TOOL_NOT_FOUND = -32001
    TOOL_EXECUTION_ERROR = -32002
    SKILL_NOT_FOUND = -32003
    SERVER_NOT_INITIALIZED = -32000
    CARD_NOT_FOUND = -32010
    TRANSFER_FAILED = -32011
    DELEGATION_FAILED = -32012


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 1. VERÄ° MODELLERÄ°
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AgentCapability(str, Enum):
    """Agent yetkinlik tÃ¼rleri."""

    MESSAGING = "messaging"  # Temel mesajlaÅŸma
    TOOL_EXECUTION = "tool_execution"  # AraÃ§ Ã§alÄ±ÅŸtÄ±rma
    SKILL_TRANSFER = "skill_transfer"  # Beceri aktarÄ±mÄ±
    TASK_DELEGATION = "task_delegation"  # GÃ¶rev devretme
    STREAMING = "streaming"  # Stream yanÄ±t
    BROADCAST = "broadcast"  # Broadcast mesaj
    HEARTBEAT = "heartbeat"  # Periyodik sinyal
    FILE_TRANSFER = "file_transfer"  # Dosya aktarÄ±mÄ±


@dataclass
class AgentCard:
    """ACP Agent KartÄ± â€” Bir agent'Ä±n yetkinlik bildirimi.

    Alanlar:
        agent_id: Benzersiz agent ID
        name: GÃ¶sterim adÄ±
        version: Agent versiyonu
        description: KÄ±sa aÃ§Ä±klama
        capabilities: Desteklenen yetenekler listesi
        skills: Agent'Ä±n sahip olduÄŸu beceriler
        transport: KullanÄ±lan taÅŸÄ±ma protokolÃ¼ (stdio/socket/http)
        endpoints: UlaÅŸÄ±m adresleri (Ã¶rn. http://host:port)
        metadata: Ek anahtar-deÄŸer Ã§iftleri
        public_key: Ä°steÄŸe baÄŸlÄ± imza anahtarÄ±
        last_seen: Son gÃ¶rÃ¼lme zamanÄ± (epoch)
    """

    agent_id: str
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    transport: str = "stdio"
    endpoints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    public_key: str = ""
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "skills": self.skills,
            "transport": self.transport,
            "endpoints": self.endpoints,
            "metadata": self.metadata,
            "public_key": self.public_key,
            "last_seen": self.last_seen,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AgentCard:
        return cls(
            agent_id=data.get("agent_id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            capabilities=data.get("capabilities", []),
            skills=data.get("skills", []),
            transport=data.get("transport", "stdio"),
            endpoints=data.get("endpoints", []),
            metadata=data.get("metadata", {}),
            public_key=data.get("public_key", ""),
            last_seen=data.get("last_seen", time.time()),
        )


@dataclass
class SkillPackage:
    """Skill Transfer Paketi â€” Agent'lar arasÄ± beceri aktarÄ±m formatÄ±.

    Alanlar:
        skill_id: Benzersiz beceri ID
        name: Beceri adÄ±
        description: AÃ§Ä±klama
        content: Beceri iÃ§eriÄŸi (markdown/metin/kod)
        source_agent: Kaynak agent ID
        target_agent: Hedef agent ID (isteÄŸe baÄŸlÄ±)
        version: Beceri versiyonu
        dependencies: BaÄŸÄ±mlÄ±lÄ±klar
        category: Kategori
        tags: Etiketler
        signature: Ä°mza (isteÄŸe baÄŸlÄ±)
        transferred_at: AktarÄ±m zamanÄ±
    """

    skill_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str = ""
    description: str = ""
    content: str = ""
    source_agent: str = ""
    target_agent: str = ""
    version: str = "1.0.0"
    dependencies: list[str] = field(default_factory=list)
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    signature: str = ""
    transferred_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "version": self.version,
            "dependencies": self.dependencies,
            "category": self.category,
            "tags": self.tags,
            "signature": self.signature,
            "transferred_at": self.transferred_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SkillPackage:
        return cls(
            skill_id=data.get("skill_id", uuid.uuid4().hex[:16]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            content=data.get("content", ""),
            source_agent=data.get("source_agent", ""),
            target_agent=data.get("target_agent", ""),
            version=data.get("version", "1.0.0"),
            dependencies=data.get("dependencies", []),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            signature=data.get("signature", ""),
            transferred_at=data.get("transferred_at", time.time()),
        )


@dataclass
class DelegationTask:
    """GÃ¶rev Devretme (Task Delegation) Paketi.

    Alanlar:
        task_id: Benzersiz gÃ¶rev ID
        source_agent: GÃ¶revi devreden agent
        target_agent: GÃ¶revi Ã¼stlenecek agent
        title: GÃ¶rev baÅŸlÄ±ÄŸÄ±
        description: GÃ¶rev aÃ§Ä±klamasÄ±
        context: BaÄŸlam/bilgi
        priority: Ã–ncelik (1-10)
        deadline: Son teslim (Unix epoch)
        status: Durum (pending/accepted/in_progress/completed/failed/rejected)
        result: GÃ¶rev sonucu
        error: Hata mesajÄ±
        metadata: Ek bilgiler
        created_at: OluÅŸturulma zamanÄ±
        completed_at: Tamamlanma zamanÄ±
    """

    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source_agent: str = ""
    target_agent: str = ""
    title: str = ""
    description: str = ""
    context: str = ""
    priority: int = 5
    deadline: float = 0.0
    status: str = "pending"
    result: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "priority": self.priority,
            "deadline": self.deadline,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DelegationTask:
        return cls(
            task_id=data.get("task_id", uuid.uuid4().hex[:16]),
            source_agent=data.get("source_agent", ""),
            target_agent=data.get("target_agent", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            context=data.get("context", ""),
            priority=data.get("priority", 5),
            deadline=data.get("deadline", 0.0),
            status=data.get("status", "pending"),
            result=data.get("result", ""),
            error=data.get("error", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            completed_at=data.get("completed_at", 0.0),
        )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 2. AGENT CARD REGISTRY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AgentCardRegistry:
    """Merkezi Agent Card kayÄ±t defteri.

    Agent'larÄ±n yetkinlik bildirimlerini tutar, keÅŸif ve doÄŸrulama saÄŸlar.
    """

    def __init__(self):
        self._cards: dict[str, AgentCard] = {}
        self._lock = threading.Lock()
        self._discovery_handlers: list[Callable[[AgentCard], None]] = []

    def register(self, card: AgentCard) -> None:
        """Bir Agent Card kaydeder (varsa gÃ¼nceller)."""
        card.last_seen = time.time()
        with self._lock:
            self._cards[card.agent_id] = card
        logger.info(
            "[ACP-CARD] Kaydedildi: %s (%d yetenek, %d beceri)",
            card.agent_id,
            len(card.capabilities),
            len(card.skills),
        )
        # KeÅŸif handler'larÄ±nÄ± uyar
        for handler in self._discovery_handlers:
            try:
                handler(card)
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

    def unregister(self, agent_id: str) -> bool:
        """Agent Card kaydÄ±nÄ± siler."""
        with self._lock:
            if agent_id in self._cards:
                del self._cards[agent_id]
                logger.info("[ACP-CARD] Silindi: %s", agent_id)
                return True
        return False

    def get(self, agent_id: str) -> AgentCard | None:
        """Bir agent'Ä±n kartÄ±nÄ± getirir."""
        with self._lock:
            return self._cards.get(agent_id)

    def list(self, capability: str | None = None) -> list[AgentCard]:
        """TÃ¼m kartlarÄ± (veya belirli yeteneÄŸe sahip olanlarÄ±) listeler."""
        with self._lock:
            cards = list(self._cards.values())
        if capability:
            cards = [c for c in cards if capability in c.capabilities]
        return cards

    def search_by_skill(self, skill_name: str) -> list[AgentCard]:
        """Belirli bir beceriye sahip agent'larÄ± arar."""
        with self._lock:
            return [
                c
                for c in self._cards.values()
                if any(skill_name.lower() in s.lower() for s in c.skills)
            ]

    def search_by_metadata(self, key: str, value: str) -> list[AgentCard]:
        """Metadata alanÄ±na gÃ¶re ara."""
        with self._lock:
            return [c for c in self._cards.values() if c.metadata.get(key) == value]

    def heartbeat(self, agent_id: str) -> bool:
        """Agent'Ä±n last_seen alanÄ±nÄ± gÃ¼nceller (heartbeat)."""
        with self._lock:
            card = self._cards.get(agent_id)
            if card:
                card.last_seen = time.time()
                return True
        return False

    def cleanup_stale(self, max_age: float = 300.0) -> int:
        """Belirli sÃ¼redir gÃ¶rÃ¼lmeyen agent'larÄ± temizler (varsayÄ±lan: 5 dk)."""
        now = time.time()
        stale = []
        with self._lock:
            for aid, card in list(self._cards.items()):
                if now - card.last_seen > max_age:
                    stale.append(aid)
            for aid in stale:
                del self._cards[aid]
        if stale:
            logger.info("[ACP-CARD] Temizlendi: %d eski kayit", len(stale))
        return len(stale)

    def count(self) -> int:
        """KayÄ±tlÄ± agent sayÄ±sÄ±."""
        with self._lock:
            return len(self._cards)

    def on_discovery(self, handler: Callable[[AgentCard], None]) -> None:
        """Yeni bir agent keÅŸfedildiÄŸinde Ã§aÄŸrÄ±lacak handler ekler."""
        self._discovery_handlers.append(handler)

    def to_dict(self) -> dict:
        """TÃ¼m kaydÄ± dict olarak dÃ¶ndÃ¼r."""
        with self._lock:
            return {
                "count": len(self._cards),
                "agents": {aid: card.to_dict() for aid, card in self._cards.items()},
            }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 3. SKILL TRANSFER PROTOCOL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class SkillTransferProtocol:
    """Skill Transfer ProtokolÃ¼ â€” Agent'lar arasÄ± beceri aktarÄ±mÄ±.

    Yetenekler:
        - Beceri paketleme ve gÃ¶nderme
        - Beceri alma ve kaydetme
        - Versiyon kontrolÃ¼
        - BaÄŸÄ±mlÄ±lÄ±k yÃ¶netimi
    """

    def __init__(self, skills_dir: str | Path | None = None):
        self._skills_dir = (
            Path(skills_dir) if skills_dir else Path.cwd() / "transferred_skills"
        )
        self._skills_dir.mkdir(parents=True, exist_ok=True)
        self._incoming: dict[str, SkillPackage] = {}
        self._lock = threading.Lock()

    def package_skill(
        self,
        name: str,
        content: str,
        source_agent: str,
        *,
        description: str = "",
        target_agent: str = "",
        category: str = "general",
        tags: list[str] | None = None,
        dependencies: list[str] | None = None,
    ) -> SkillPackage:
        """Bir beceriyi transfer paketine dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r."""
        return SkillPackage(
            name=name,
            description=description or f"Skill: {name}",
            content=content,
            source_agent=source_agent,
            target_agent=target_agent,
            category=category,
            tags=tags or [],
            dependencies=dependencies or [],
        )

    def receive_skill(self, pkg: SkillPackage) -> dict:
        """Bir skill paketini alÄ±r ve kaydeder.

        Returns:
            {"status": "ok/error", "path": "...", "message": "..."}
        """
        try:
            # Dosya adÄ± oluÅŸtur
            safe_name = "".join(
                c if c.isalnum() or c in "_-" else "_" for c in pkg.name
            )
            filename = f"{safe_name}__{pkg.skill_id[:8]}.md"
            filepath = self._skills_dir / filename

            # Ä°Ã§eriÄŸi yaz (frontmatter + body)
            frontmatter = {
                "skill_id": pkg.skill_id,
                "name": pkg.name,
                "description": pkg.description,
                "source_agent": pkg.source_agent,
                "target_agent": pkg.target_agent,
                "version": pkg.version,
                "category": pkg.category,
                "tags": pkg.tags,
                "dependencies": pkg.dependencies,
                "transferred_at": pkg.transferred_at,
            }
            content = f"""---
{json.dumps(frontmatter, ensure_ascii=False, indent=2)}
---

{pkg.content}
"""
            filepath.write_text(content, encoding="utf-8")

            with self._lock:
                self._incoming[pkg.skill_id] = pkg

            logger.info(
                "[ACP-TRANSFER] Beceri alindi: %s -> %s (%s)",
                pkg.source_agent,
                pkg.target_agent or "herkes",
                pkg.name,
            )

            return {
                "status": "ok",
                "path": str(filepath),
                "skill_id": pkg.skill_id,
                "message": f"Skill '{pkg.name}' alindi ve kaydedildi.",
            }
        except Exception as e:
            logger.exception("[ACP-TRANSFER] Beceri alma hatasi")
            return {"status": "error", "message": str(e)}

    def list_incoming(self) -> list[SkillPackage]:
        """AlÄ±nan becerileri listeler."""
        with self._lock:
            return list(self._incoming.values())

    def get_incoming(self, skill_id: str) -> SkillPackage | None:
        with self._lock:
            return self._incoming.get(skill_id)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 4. TASK DELEGATION PROTOCOL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TaskDelegationProtocol:
    """GÃ¶rev Devretme ProtokolÃ¼ (Task Delegation).

    Agent'larÄ±n birbirlerine gÃ¶rev devretmesini, takibini ve
    sonuÃ§landÄ±rmasÄ±nÄ± saÄŸlayan protokol.
    """

    def __init__(self):
        self._tasks: dict[str, DelegationTask] = {}
        self._lock = threading.Lock()
        self._handlers: dict[str, Callable[[DelegationTask], str]] = {}

    def delegate(
        self,
        source: str,
        target: str,
        title: str,
        description: str = "",
        context: str = "",
        priority: int = 5,
        deadline: float = 0.0,
        metadata: dict | None = None,
    ) -> DelegationTask:
        """Bir gÃ¶revi baÅŸka bir agent'a devreder.

        Returns:
            OluÅŸturulan DelegationTask objesi.
        """
        task = DelegationTask(
            source_agent=source,
            target_agent=target,
            title=title,
            description=description,
            context=context,
            priority=max(1, min(10, priority)),
            deadline=deadline,
            status="pending",
            metadata=metadata or {},
            created_at=time.time(),
        )

        with self._lock:
            self._tasks[task.task_id] = task

        logger.info(
            "[ACP-DELEGATE] Gorev devredildi: %s -> %s | %s", source, target, title[:60]
        )

        # Hedef handler varsa otomatik ilet
        handler = self._handlers.get(target)
        if handler:
            try:
                sonuc = handler(task)
                if sonuc:
                    self.update_status(task.task_id, "in_progress")
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        return task

    def accept(self, task_id: str) -> bool:
        """GÃ¶revi kabul eder."""
        return self.update_status(task_id, "accepted")

    def reject(self, task_id: str, reason: str = "") -> bool:
        """GÃ¶revi reddeder."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "rejected"
                task.error = reason
                return True
        return False

    def update_status(self, task_id: str, status: str, result: str = "") -> bool:
        """GÃ¶rev durumunu gÃ¼nceller."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = status
                if result:
                    task.result = result
                if status in ("completed", "failed"):
                    task.completed_at = time.time()
                return True
        return False

    def get_task(self, task_id: str) -> DelegationTask | None:
        """Bir gÃ¶revin detayÄ±nÄ± getirir."""
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(
        self,
        agent_id: str | None = None,
        status: str | None = None,
    ) -> list[DelegationTask]:
        """GÃ¶revleri listeler (filtreleme destekli)."""
        with self._lock:
            tasks = list(self._tasks.values())

        if agent_id:
            tasks = [
                t
                for t in tasks
                if t.source_agent == agent_id or t.target_agent == agent_id
            ]
        if status:
            tasks = [t for t in tasks if t.status == status]

        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def set_handler(
        self, agent_id: str, handler: Callable[[DelegationTask], str]
    ) -> None:
        """Bir agent iÃ§in delegasyon handler'Ä± ayarlar.

        Gelen gÃ¶revler otomatik olarak handler'a iletilir.
        Handler dÃ¶nen string task status mesajÄ± olarak kullanÄ±lÄ±r.
        """
        with self._lock:
            self._handlers[agent_id] = handler

    def remove_handler(self, agent_id: str) -> None:
        with self._lock:
            self._handlers.pop(agent_id, None)

    def stats(self) -> dict:
        """Delegasyon istatistikleri."""
        with self._lock:
            tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.status == "pending"),
            "accepted": sum(1 for t in tasks if t.status == "accepted"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
            "rejected": sum(1 for t in tasks if t.status == "rejected"),
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 5. ACP SUNUCU (JSON-RPC 2.0 over stdio/socket)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ACPServer:
    """ACP Sunucusu â€” JSON-RPC 2.0 protokolÃ¼ ile agent iletiÅŸimi.

    Desteklenen Metotlar:
        - initialize              : BaÄŸlantÄ± baÅŸlatma
        - tools/list              : AraÃ§ listesi
        - tools/call              : AraÃ§ Ã§aÄŸÄ±rma
        - skills/list             : Beceri listesi
        - skills/get              : Beceri detayÄ±
        - card/register           : Agent Card kaydetme
        - card/get                : Agent Card sorgulama
        - card/list               : Agent Card listesi
        - card/search             : Card arama
        - card/heartbeat          : Heartbeat sinyali
        - skill/transfer          : Beceri aktarÄ±mÄ±
        - skill/receive           : Beceri alma
        - task/delegate           : GÃ¶rev devretme
        - task/status             : GÃ¶rev durumu
        - task/list               : GÃ¶rev listesi
        - task/update             : GÃ¶rev gÃ¼ncelleme
        - ping                    : SaÄŸlÄ±k kontrolÃ¼
        - health                  : DetaylÄ± saÄŸlÄ±k
        - shutdown                : Kapatma
    """

    def __init__(
        self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 9200
    ):
        self.transport = transport
        self.host = host
        self.port = port
        self.running = False
        self.initialized = False
        self._card_registry = AgentCardRegistry()
        self._skill_protocol = SkillTransferProtocol()
        self._delegation = TaskDelegationProtocol()
        self._start_time = 0.0
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._client_info: dict = {}
        self._protocol_version = ACP_PROTOCOL_VERSION

        # Tool registry (plugin'ler tarafÄ±ndan ayarlanÄ±r)
        self._tool_registry = None
        self._tool_list_fn: Callable | None = None
        self._tool_call_fn: Callable | None = None
        self._skill_list_fn: Callable | None = None
        self._skill_get_fn: Callable | None = None

    # â”€â”€ Plugin API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def set_tool_registry(self, registry: Any) -> None:
        """ToolRegistry referansÄ±nÄ± ayarlar."""
        self._tool_registry = registry

    def set_tool_list_fn(self, fn: Callable[[], list[dict]]) -> None:
        """Tool listeleme fonksiyonunu ayarlar."""
        self._tool_list_fn = fn

    def set_tool_call_fn(self, fn: Callable[[str, dict], str]) -> None:
        """Tool Ã§aÄŸÄ±rma fonksiyonunu ayarlar."""
        self._tool_call_fn = fn

    def set_skill_list_fn(self, fn: Callable[[], list[dict]]) -> None:
        self._skill_list_fn = fn

    def set_skill_get_fn(self, fn: Callable[[str], dict | None]) -> None:
        self._skill_get_fn = fn

    @property
    def card_registry(self) -> AgentCardRegistry:
        return self._card_registry

    @property
    def skill_protocol(self) -> SkillTransferProtocol:
        return self._skill_protocol

    @property
    def delegation(self) -> TaskDelegationProtocol:
        return self._delegation

    # â”€â”€ JSON-RPC Ã‡ekirdek â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _json_safe(self, val: Any) -> Any:
        """JSON serialize edilemeyen deÄŸerleri str()'e Ã§evirir."""
        if val is None or isinstance(val, (str, int, float, bool)):
            return val
        if isinstance(val, (list, tuple)):
            return [self._json_safe(v) for v in val]
        if isinstance(val, dict):
            return {k: self._json_safe(v) for k, v in val.items()}
        if isinstance(val, set):
            return sorted(self._json_safe(v) for v in val)
        try:
            json.dumps(val)
            return val
        except (TypeError, ValueError):
            return str(val)

    def _error(self, code: int, msg: str, data: Any = None, req_id: Any = None) -> str:
        resp = {"jsonrpc": "2.0", "error": {"code": code, "message": msg}}
        if data is not None:
            resp["error"]["data"] = self._json_safe(data)
        resp["id"] = req_id if req_id is not None else None
        return json.dumps(resp, ensure_ascii=False)

    def _success(self, result: Any, req_id: Any) -> str:
        return json.dumps(
            {"jsonrpc": "2.0", "result": self._json_safe(result), "id": req_id},
            ensure_ascii=False,
        )

    def _timestamp(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    # â”€â”€ Ä°stek Ä°ÅŸleme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def handle(self, raw: str) -> str:
        """Tek bir JSON-RPC isteÄŸini iÅŸler, yanÄ±t dÃ¶ndÃ¼rÃ¼r."""
        raw = raw.strip()
        if not raw:
            return ""

        # JSON parse
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            return self._error(ACPErrorCode.PARSE_ERROR, f"JSON parse: {e}")

        if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
            rid = req.get("id") if isinstance(req, dict) else None
            return self._error(
                ACPErrorCode.INVALID_REQUEST, "jsonrpc: '2.0' olmali", req_id=rid
            )

        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id")

        # Metot dispatch
        handler_name = f"_method_{method.replace('/', '_')}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            return self._error(
                ACPErrorCode.METHOD_NOT_FOUND,
                f"Metot bulunamadi: '{method}'",
                data={"available": self._list_methods()},
                req_id=req_id,
            )

        try:
            if isinstance(params, dict):
                result = handler(**params)
            elif isinstance(params, list):
                result = handler(*params)
            else:
                result = handler(params) if params else handler()
            return self._success(result, req_id)
        except TypeError as e:
            return self._error(
                ACPErrorCode.INVALID_PARAMS, f"Parametre: {e}", req_id=req_id
            )
        except Exception as e:
            logger.exception("[ACP] Metot hatasi: %s", method)
            return self._error(
                ACPErrorCode.INTERNAL_ERROR, f"Ic hata: {e}", req_id=req_id
            )

    def _list_methods(self) -> list[str]:
        return sorted(
            name.replace("_method_", "").replace("_", "/", 1)
            for name in dir(self)
            if name.startswith("_method_")
        )

    # â”€â”€ JSON-RPC MetotlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _method_initialize(
        self, protocol_version: str = None, client_info: dict = None, **kw
    ) -> dict:
        """BaÄŸlantÄ± baÅŸlatma."""
        self.initialized = True
        self._client_info = client_info or {}
        if protocol_version:
            self._protocol_version = protocol_version
        return {
            "protocol_version": self._protocol_version,
            "server_info": {
                "name": "ReYMeN ACP Server",
                "version": ACP_SERVER_VERSION,
                "description": "ReYMeN ACP (Agent Communication Protocol) sunucusu",
                "transport": self.transport,
                "initialized_at": self._timestamp(),
                "capabilities": [c.value for c in AgentCapability],
            },
        }

    def _method_ping(self, **kw) -> dict:
        return {
            "pong": True,
            "timestamp": self._timestamp(),
            "initialized": self.initialized,
        }

    def _method_health(self, **kw) -> dict:
        return {
            "status": "ok" if self.running else "stopped",
            "initialized": self.initialized,
            "transport": self.transport,
            "uptime": time.time() - self._start_time if self._start_time else 0,
            "agents_count": self._card_registry.count(),
            "tools_count": len(self._list_tools()),
            "timestamp": self._timestamp(),
        }

    def _method_shutdown(self, **kw) -> dict:
        self.running = False
        self.initialized = False
        self._stop_event.set()
        return {"shutdown": True, "message": "ACP sunucusu kapatildi."}

    # â”€â”€ Tools â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _list_tools(self) -> list[dict]:
        if self._tool_list_fn:
            return self._tool_list_fn()
        if self._tool_registry:
            try:
                tools = []
                for ad, fonk in self._tool_registry._tools.items():
                    meta = self._tool_registry._meta.get(ad, {})
                    tools.append(
                        {
                            "name": ad,
                            "description": meta.get("aciklama", "") or f"Tool: {ad}",
                            "inputSchema": {"type": "object", "properties": {}},
                        }
                    )
                return tools
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
        return []

    def _method_tools_list(self, **kw) -> dict:
        return {"tools": self._list_tools()}

    def _method_tools_call(
        self, name: str = None, arguments: dict = None, **kw
    ) -> dict:
        if not name:
            return {
                "content": [{"type": "text", "text": "[Hata]: Arac adi gerekli"}],
                "isError": True,
            }
        args = arguments or {}
        if self._tool_call_fn:
            try:
                result = self._tool_call_fn(name, args)
                return {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False,
                }
            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"[Hata]: {e}"}],
                    "isError": True,
                }
        if self._tool_registry:
            try:
                params = list(args.values()) if args else []
                result = self._tool_registry.calistir(name, *params)
                return {
                    "content": [{"type": "text", "text": str(result)}],
                    "isError": False,
                }
            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"[Hata]: {e}"}],
                    "isError": True,
                }
        return {
            "content": [{"type": "text", "text": "[Hata]: ToolRegistry yuklu degil"}],
            "isError": True,
        }

    # â”€â”€ Skills â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _method_skills_list(self, **kw) -> dict:
        skills = []
        if self._skill_list_fn:
            skills = self._skill_list_fn()
        return {"skills": skills}

    def _method_skills_get(self, name: str = None, **kw) -> dict:
        if not name:
            return {"skill": None, "error": "Skill adi gerekli"}
        if self._skill_get_fn:
            skill = self._skill_get_fn(name)
            return (
                {"skill": skill}
                if skill
                else {"skill": None, "error": f"Skill bulunamadi: '{name}'"}
            )
        return {"skill": None, "error": "Skill get fonksiyonu yuklu degil"}

    # â”€â”€ Agent Card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _method_card_register(self, card: dict = None, **kw) -> dict:
        """Agent Card kaydeder."""
        if not card:
            return {"status": "error", "message": "Card bilgisi gerekli"}
        try:
            agent_card = AgentCard.from_dict(card)
            self._card_registry.register(agent_card)
            return {
                "status": "ok",
                "agent_id": agent_card.agent_id,
                "message": f"Agent '{agent_card.agent_id}' kaydedildi.",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _method_card_get(self, agent_id: str = None, **kw) -> dict:
        """Bir agent'Ä±n kartÄ±nÄ± getirir."""
        if not agent_id:
            return {"status": "error", "message": "agent_id gerekli"}
        card = self._card_registry.get(agent_id)
        if card:
            return {"status": "ok", "card": card.to_dict()}
        return {"status": "error", "message": f"Agent '{agent_id}' bulunamadi"}

    def _method_card_list(self, capability: str = None, **kw) -> dict:
        """TÃ¼m kartlarÄ± listeler."""
        cards = self._card_registry.list(capability)
        return {
            "count": len(cards),
            "cards": [c.to_dict() for c in cards],
        }

    def _method_card_search(
        self, skill: str = None, key: str = None, value: str = None, **kw
    ) -> dict:
        """Kartlarda arama yapar."""
        if skill:
            cards = self._card_registry.search_by_skill(skill)
        elif key and value:
            cards = self._card_registry.search_by_metadata(key, value)
        else:
            cards = self._card_registry.list()
        return {"count": len(cards), "cards": [c.to_dict() for c in cards]}

    def _method_card_heartbeat(self, agent_id: str = None, **kw) -> dict:
        """Heartbeat sinyali."""
        if not agent_id:
            return {"status": "error", "message": "agent_id gerekli"}
        ok = self._card_registry.heartbeat(agent_id)
        return {
            "status": "ok" if ok else "error",
            "message": "Heartbeat alindi" if ok else f"Agent '{agent_id}' bulunamadi",
        }

    # â”€â”€ Skill Transfer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _method_skill_transfer(self, **kw) -> dict:
        """Bir beceriyi baÅŸka bir agent'a aktarÄ±r (paket oluÅŸturur)."""
        name = kw.get("name", "")
        content = kw.get("content", "")
        source = kw.get("source_agent", kw.get("source", ""))
        target = kw.get("target_agent", kw.get("target", ""))
        desc = kw.get("description", "")
        category = kw.get("category", "general")

        if not name or not content or not source:
            return {"status": "error", "message": "name, content, source_agent gerekli"}

        pkg = self._skill_protocol.package_skill(
            name=name,
            content=content,
            source_agent=source,
            target_agent=target,
            description=desc,
            category=category,
            tags=kw.get("tags"),
            dependencies=kw.get("dependencies"),
        )
        return {
            "status": "ok",
            "package": pkg.to_dict(),
            "message": f"Skill paketi olusturuldu: {pkg.skill_id}",
        }

    def _method_skill_receive(self, package: dict = None, **kw) -> dict:
        """Bir skill paketini alÄ±r ve kaydeder."""
        if not package:
            return {"status": "error", "message": "Skill package gerekli"}
        pkg = SkillPackage.from_dict(package)
        result = self._skill_protocol.receive_skill(pkg)
        return result

    def _method_skill_list_incoming(self, **kw) -> dict:
        """AlÄ±nan becerileri listeler."""
        skills = self._skill_protocol.list_incoming()
        return {"count": len(skills), "skills": [s.to_dict() for s in skills]}

    # â”€â”€ Task Delegation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _method_task_delegate(self, **kw) -> dict:
        """Bir gÃ¶revi baÅŸka agent'a devreder."""
        source = kw.get("source_agent", kw.get("source", ""))
        target = kw.get("target_agent", kw.get("target", ""))
        title = kw.get("title", "")
        desc = kw.get("description", "")
        context = kw.get("context", "")

        if not source or not target or not title:
            return {
                "status": "error",
                "message": "source_agent, target_agent, title gerekli",
            }

        task = self._delegation.delegate(
            source=source,
            target=target,
            title=title,
            description=desc,
            context=context,
            priority=kw.get("priority", 5),
            deadline=kw.get("deadline", 0.0),
            metadata=kw.get("metadata"),
        )
        return {
            "status": "ok",
            "task": task.to_dict(),
            "message": f"Gorev devredildi: {task.task_id}",
        }

    def _method_task_status(self, task_id: str = None, **kw) -> dict:
        """Bir gÃ¶revin durumunu sorgular."""
        if not task_id:
            return {"status": "error", "message": "task_id gerekli"}
        task = self._delegation.get_task(task_id)
        if task:
            return {"status": "ok", "task": task.to_dict()}
        return {"status": "error", "message": f"Task '{task_id}' bulunamadi"}

    def _method_task_list(self, agent_id: str = None, status: str = None, **kw) -> dict:
        """GÃ¶revleri listeler."""
        tasks = self._delegation.list_tasks(agent_id, status)
        return {"count": len(tasks), "tasks": [t.to_dict() for t in tasks]}

    def _method_task_update(
        self, task_id: str = None, status: str = None, result: str = "", **kw
    ) -> dict:
        """GÃ¶rev durumunu gÃ¼nceller."""
        if not task_id or not status:
            return {"status": "error", "message": "task_id ve status gerekli"}
        ok = self._delegation.update_status(task_id, status, result)
        return {
            "status": "ok" if ok else "error",
            "message": "Gorev guncellendi" if ok else "Task bulunamadi",
        }

    def _method_task_accept(self, task_id: str = None, **kw) -> dict:
        if not task_id:
            return {"status": "error", "message": "task_id gerekli"}
        ok = self._delegation.accept(task_id)
        return {"status": "ok" if ok else "error"}

    def _method_task_reject(self, task_id: str = None, reason: str = "", **kw) -> dict:
        if not task_id:
            return {"status": "error", "message": "task_id gerekli"}
        ok = self._delegation.reject(task_id, reason)
        return {"status": "ok" if ok else "error"}

    def _method_task_stats(self, **kw) -> dict:
        return self._delegation.stats()

    # â”€â”€ YaÅŸam DÃ¶ngÃ¼sÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def start(self) -> None:
        """Sunucuyu baÅŸlatÄ±r (transport moduna gÃ¶re)."""
        self.running = True
        self.initialized = True
        self._start_time = time.time()

        if self.transport == "stdio":
            self._start_stdio()
        elif self.transport == "socket":
            self._start_socket()
        else:
            logger.error("[ACP] Bilinmeyen transport: %s", self.transport)

    def _start_stdio(self) -> None:
        """Stdio modunda Ã§alÄ±ÅŸtÄ±r (her satÄ±rda bir JSON mesajÄ±)."""
        logger.info("[ACP] Sunucu basladi (stdio)")
        try:
            for line in sys.stdin:
                if not self.running:
                    break
                line = line.strip()
                if not line:
                    continue
                response = self.handle(line)
                if response:
                    sys.stdout.write(response + "\n")
                    sys.stdout.flush()
        except (EOFError, KeyboardInterrupt):
            logger.warning("[fix_01_sessiz_except] Exception")
        finally:
            self.running = False
            logger.info("[ACP] Sunucu durduruldu (stdio)")

    def _start_socket(self) -> None:
        """Socket modunda Ã§alÄ±ÅŸtÄ±r."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.host, self.port))
            server.listen(5)
            server.settimeout(1.0)
            logger.info("[ACP] Sunucu basladi (socket) %s:%d", self.host, self.port)

            while self.running:
                try:
                    conn, addr = server.accept()
                    threading.Thread(
                        target=self._handle_socket_client,
                        args=(conn, addr),
                        daemon=True,
                    ).start()
                except socket.timeout:
                    continue
                except OSError:
                    break
        finally:
            server.close()
            logger.info("[ACP] Sunucu durduruldu (socket)")

    def _handle_socket_client(self, conn: socket.socket, addr: tuple) -> None:
        """Bir socket istemcisini iÅŸler."""
        logger.debug("[ACP] Baglanti: %s", addr)
        buffer = ""
        try:
            conn.settimeout(30.0)
            while self.running:
                data = conn.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    response = self.handle(line.strip())
                    if response:
                        conn.sendall((response + "\n").encode("utf-8"))
        except (socket.timeout, ConnectionResetError, OSError):
            logger.warning("[fix_01_sessiz_except] Exception")
        finally:
            conn.close()

    def start_threaded(self) -> threading.Thread:
        """Sunucuyu ayrÄ± bir thread'de baÅŸlatÄ±r."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        """Sunucuyu durdurur."""
        self.running = False
        self._stop_event.set()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 6. ACP Ä°STEMCÄ° (HTTP/Socket istemcisi)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ACPClient:
    """ACP Ä°stemcisi â€” Uzak bir ACP sunucusuna baÄŸlanmak iÃ§in.

    KullanÄ±m:
        client = ACPClient("http://localhost:9200")
        client.initialize()
        tools = client.tools_list()
        card = client.card_register(agent_card)
    """

    def __init__(self, endpoint: str = "stdio://"):
        self.endpoint = endpoint
        self._transport = "stdio" if endpoint.startswith("stdio") else "http"
        self._session = None
        self._initialized = False
        self._server_info: dict = {}
        self._protocol_version = ACP_PROTOCOL_VERSION
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _call(self, method: str, params: dict | None = None) -> dict:
        """JSON-RPC Ã§aÄŸrÄ±sÄ± yapar."""
        req_id = self._next_id()
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": req_id,
        }

        if self._transport == "http":
            return self._call_http(payload)
        else:
            return self._call_stdio(payload)

    def _call_http(self, payload: dict) -> dict:
        """HTTP Ã¼zerinden JSON-RPC Ã§aÄŸrÄ±sÄ±."""
        import httpx

        if self._session is None:
            self._session = httpx.Client(timeout=30.0)
        try:
            url = self.endpoint.rstrip("/")
            headers = {"Content-Type": "application/json"}
            r = self._session.post(url, json=payload, headers=headers, timeout=30.0)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": {"code": -1, "message": str(e)}, "id": payload["id"]}

    def _call_stdio(self, payload: dict) -> dict:
        """Stdio Ã¼zerinden JSON-RPC Ã§aÄŸrÄ±sÄ± (yerel process)."""
        # Stdio modu sadece sunucu iÃ§in; istemci genelde HTTP kullanÄ±r
        raise NotImplementedError(
            "Stdio istemci modu henuz desteklenmiyor. HTTP kullanin."
        )

    # â”€â”€ Ana Metotlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def initialize(self, client_info: dict | None = None) -> dict:
        """ACP baÄŸlantÄ±sÄ±nÄ± baÅŸlatÄ±r."""
        result = self._call(
            "initialize",
            {
                "protocol_version": self._protocol_version,
                "client_info": client_info or {},
            },
        )
        if "result" in result:
            self._initialized = True
            self._server_info = result["result"].get("server_info", {})
        return result.get("result", result)

    def ping(self) -> dict:
        return self._call("ping").get("result", {})

    def health(self) -> dict:
        return self._call("health").get("result", {})

    def tools_list(self) -> list[dict]:
        result = self._call("tools/list")
        return result.get("result", {}).get("tools", [])

    def tools_call(self, name: str, arguments: dict | None = None) -> dict:
        result = self._call("tools/call", {"name": name, "arguments": arguments or {}})
        return result.get("result", {})

    def skills_list(self) -> list[dict]:
        result = self._call("skills/list")
        return result.get("result", {}).get("skills", [])

    def skills_get(self, name: str) -> dict:
        result = self._call("skills/get", {"name": name})
        return result.get("result", {})

    def card_register(self, card: dict) -> dict:
        result = self._call("card/register", {"card": card})
        return result.get("result", {})

    def card_get(self, agent_id: str) -> dict:
        result = self._call("card/get", {"agent_id": agent_id})
        return result.get("result", {})

    def card_list(self, capability: str | None = None) -> dict:
        result = self._call(
            "card/list", {"capability": capability} if capability else {}
        )
        return result.get("result", {})

    def card_search(
        self, skill: str | None = None, key: str | None = None, value: str | None = None
    ) -> dict:
        params = {}
        if skill:
            params["skill"] = skill
        if key and value:
            params["key"] = key
            params["value"] = value
        result = self._call("card/search", params)
        return result.get("result", {})

    def card_heartbeat(self, agent_id: str) -> dict:
        result = self._call("card/heartbeat", {"agent_id": agent_id})
        return result.get("result", {})

    def skill_transfer(
        self, name: str, content: str, source_agent: str, target_agent: str = "", **kw
    ) -> dict:
        params = {
            "name": name,
            "content": content,
            "source_agent": source_agent,
            "target_agent": target_agent,
            **kw,
        }
        result = self._call("skill/transfer", params)
        return result.get("result", {})

    def skill_receive(self, package: dict) -> dict:
        result = self._call("skill/receive", {"package": package})
        return result.get("result", {})

    def task_delegate(self, source: str, target: str, title: str, **kw) -> dict:
        params = {"source_agent": source, "target_agent": target, "title": title, **kw}
        result = self._call("task/delegate", params)
        return result.get("result", {})

    def task_status(self, task_id: str) -> dict:
        result = self._call("task/status", {"task_id": task_id})
        return result.get("result", {})

    def task_list(self, agent_id: str | None = None, status: str | None = None) -> dict:
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        result = self._call("task/list", params)
        return result.get("result", {})

    def task_update(self, task_id: str, status: str, result: str = "") -> dict:
        result = self._call(
            "task/update",
            {
                "task_id": task_id,
                "status": status,
                "result": result,
            },
        )
        return result.get("result", {})

    def task_stats(self) -> dict:
        result = self._call("task/stats")
        return result.get("result", {})

    def shutdown(self) -> dict:
        result = self._call("shutdown")
        return result.get("result", {})

    def close(self) -> None:
        if self._session:
            try:
                self._session.close()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
            self._session = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 7. MOTOR ENTEGRASYONU
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# Global singleton
_ACP_SERVER_INSTANCE: ACPServer | None = None
_ACP_SERVER_LOCK = threading.Lock()


def _acp_baslat(**kw) -> str:
    """ACP sunucusunu baÅŸlatÄ±r.

    Parametreler:
        transport: "stdio" (varsayÄ±lan) veya "socket"
        port: Socket port (transport="socket" ise, varsayÄ±lan: 9200)
        host: Socket host (varsayÄ±lan: 127.0.0.1)

    Ã–rnek:
        ACP_BASLAT transport=socket port=9200 host=0.0.0.0
        ACP_BASLAT transport=stdio
    """
    global _ACP_SERVER_INSTANCE
    with _ACP_SERVER_LOCK:
        if _ACP_SERVER_INSTANCE and _ACP_SERVER_INSTANCE.running:
            return "[ACP] Sunucu zaten calisiyor."

        transport = kw.get("transport", "stdio")
        port = int(kw.get("port", 9200))
        host = kw.get("host", "127.0.0.1")

        _ACP_SERVER_INSTANCE = ACPServer(transport=transport, host=host, port=port)
        _ACP_SERVER_INSTANCE.start_threaded()
        time.sleep(0.1)  # Thread'in baÅŸlamasÄ±na izin ver

        ek = ""
        if transport == "socket":
            ek = f" ({host}:{port})"
        return f"[ACP] Sunucu baslatildi (transport={transport}{ek})"


def _acp_durum(**kw) -> str:
    """ACP sunucu durumunu gÃ¶sterir."""
    global _ACP_SERVER_INSTANCE
    if _ACP_SERVER_INSTANCE is None:
        return "[ACP] Sunucu baslatilmadi. (ACP_BASLAT ile baslat)"
    s = _ACP_SERVER_INSTANCE
    return (
        f"[ACP] Sunucu Durumu:\n"
        f"  Durum: {'ğŸŸ¢ AKTIF' if s.running else 'ğŸ”´ DURDURULDU'}\n"
        f"  Transport: {s.transport}\n"
        f"  Agent Sayisi: {s._card_registry.count()}\n"
        f"  Calisma: {time.time() - s._start_time:.0f}s"
    )


def _acp_durdur(**kw) -> str:
    """ACP sunucusunu durdurur."""
    global _ACP_SERVER_INSTANCE
    if _ACP_SERVER_INSTANCE and _ACP_SERVER_INSTANCE.running:
        _ACP_SERVER_INSTANCE.stop()
        _ACP_SERVER_INSTANCE = None
        return "[ACP] Sunucu durduruldu."
    return "[ACP] Sunucu zaten kapali."


def _acp_card_liste(**kw) -> str:
    """KayÄ±tlÄ± Agent Card'larÄ± listeler."""
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."
    cards = _ACP_SERVER_INSTANCE._card_registry.list()
    if not cards:
        return "[ACP] Kayitli agent yok."
    satirlar = [f"[ACP] Kayitli Agent'lar ({len(cards)}):"]
    for c in cards:
        yetenek = ", ".join(c.capabilities[:4])
        satirlar.append(
            f"  ğŸ†” {c.agent_id}\n"
            f"     Ä°sim: {c.name or '-'}\n"
            f"     Yetenek: {yetenek or '-'}\n"
            f"     Beceri: {len(c.skills)} adet\n"
            f"     Son: {time.time() - c.last_seen:.0f}s once"
        )
    return "\n".join(satirlar)


def _acp_card_kaydet(**kw) -> str:
    """Bir Agent Card kaydeder.

    Parametreler:
        agent_id: Benzersiz ID (zorunlu)
        name: GÃ¶sterim adÄ±
        capabilities: Yetenek listesi (virgÃ¼lle ayrÄ±lmÄ±ÅŸ)
        skills: Beceri listesi (virgÃ¼lle ayrÄ±lmÄ±ÅŸ)
    """
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."

    agent_id = kw.get("agent_id", kw.get("args", [None])[0] if kw.get("args") else None)
    if not agent_id:
        return "[ACP] agent_id zorunlu. Orn: ACP_CARD_KAYDET agent_id=my_agent"

    caps_str = kw.get("capabilities", "")
    skills_str = kw.get("skills", "")
    capabilities = [c.strip() for c in caps_str.split(",") if c.strip()]
    skills = [s.strip() for s in skills_str.split(",") if s.strip()]

    card = AgentCard(
        agent_id=agent_id,
        name=kw.get("name", agent_id),
        version=kw.get("version", "1.0.0"),
        description=kw.get("description", ""),
        capabilities=capabilities or [AgentCapability.MESSAGING.value],
        skills=skills,
        transport=_ACP_SERVER_INSTANCE.transport,
    )
    _ACP_SERVER_INSTANCE._card_registry.register(card)
    return f"[ACP] Card kaydedildi: {agent_id} ({len(capabilities)} yetenek, {len(skills)} beceri)"


def _acp_delege(**kw) -> str:
    """Bir gÃ¶revi baÅŸka bir agent'a devreder.

    Parametreler:
        source: Kaynak agent ID
        target: Hedef agent ID
        title: GÃ¶rev baÅŸlÄ±ÄŸÄ±
        description: GÃ¶rev aÃ§Ä±klamasÄ±
        context: BaÄŸlam bilgisi
        priority: Ã–ncelik (1-10)
    """
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."

    source = kw.get("source", kw.get("source_agent", ""))
    target = kw.get("target", kw.get("target_agent", ""))
    title = kw.get("title", "")

    if not source or not target or not title:
        return "[ACP] source, target ve title zorunlu."

    task = _ACP_SERVER_INSTANCE._delegation.delegate(
        source=source,
        target=target,
        title=title,
        description=kw.get("description", ""),
        context=kw.get("context", ""),
        priority=int(kw.get("priority", 5)),
    )
    return (
        f"[ACP] Gorev devredildi:\n"
        f"  ID: {task.task_id}\n"
        f"  Kaynak: {source} -> Hedef: {target}\n"
        f"  Baslik: {title}\n"
        f"  Durum: {task.status}"
    )


def _acp_gorev_liste(**kw) -> str:
    """GÃ¶revleri listeler.

    Parametreler:
        agent_id: Sadece bu agent'Ä±n gÃ¶revleri
        status: Durum filtresi (pending/accepted/completed/failed)
    """
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."

    tasks = _ACP_SERVER_INSTANCE._delegation.list_tasks(
        agent_id=kw.get("agent_id"),
        status=kw.get("status"),
    )
    if not tasks:
        return "[ACP] Gorev yok."
    satirlar = [f"[ACP] Gorevler ({len(tasks)}):"]
    for t in tasks:
        satirlar.append(
            f"  ğŸ“‹ {t.task_id[:12]} | {t.title[:40]:<42} | {t.status:<12} | "
            f"{t.source_agent} -> {t.target_agent}"
        )
    return "\n".join(satirlar)


def _acp_beceri_aktar(**kw) -> str:
    """Bir beceriyi paketler (skill transfer).

    Parametreler:
        name: Beceri adÄ±
        source: Kaynak agent ID
        content: Beceri iÃ§eriÄŸi
        description: AÃ§Ä±klama
    """
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."

    name = kw.get("name", "")
    source = kw.get("source", kw.get("source_agent", ""))
    content = kw.get("content", "")

    if not name or not content or not source:
        return "[ACP] name, source ve content zorunlu."

    pkg = _ACP_SERVER_INSTANCE._skill_protocol.package_skill(
        name=name,
        content=content,
        source_agent=source,
        description=kw.get("description", ""),
        category=kw.get("category", "general"),
    )
    return (
        f"[ACP] Skill paketi olusturuldu:\n"
        f"  ID: {pkg.skill_id}\n"
        f"  Ad: {pkg.name}\n"
        f"  Kaynak: {pkg.source_agent}\n"
        f"  Boyut: {len(pkg.content)} karakter"
    )


def _acp_istatistik(**kw) -> str:
    """ACP istatistiklerini gÃ¶sterir."""
    global _ACP_SERVER_INSTANCE
    if not _ACP_SERVER_INSTANCE or not _ACP_SERVER_INSTANCE.running:
        return "[ACP] Sunucu calismiyor."

    cards = _ACP_SERVER_INSTANCE._card_registry.count()
    card_list = _ACP_SERVER_INSTANCE._card_registry.list()
    top_yetenek = {}
    for c in card_list:
        for cap in c.capabilities:
            top_yetenek[cap] = top_yetenek.get(cap, 0) + 1

    del_stats = _ACP_SERVER_INSTANCE._delegation.stats()
    yetenek_str = ", ".join(
        f"{k}: {v}" for k, v in sorted(top_yetenek.items(), key=lambda x: -x[1])[:5]
    )

    return (
        f"[ACP] Istatistikler:\n"
        f"  Agent Sayisi: {cards}\n"
        f"  Yetenek Dagilimi: {yetenek_str or '-'}\n"
        f"  Gorevler: {del_stats['total']} (tamamlanan: {del_stats['completed']}, "
        f"bekleyen: {del_stats['pending']})\n"
        f"  Transport: {_ACP_SERVER_INSTANCE.transport}\n"
        f"  Calisma: {time.time() - _ACP_SERVER_INSTANCE._start_time:.0f}s"
    )


def motor_kaydet(motor: Any) -> None:
    """Motor'a ACP araÃ§larÄ±nÄ± kaydeder.

    Args:
        motor: Motor instance (_plugin_arac_kaydet metoduna sahip)
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    tools = [
        (
            "ACP_BASLAT",
            _acp_baslat,
            "ACP sunucusunu baslatir. Parametreler: transport=(stdio|socket), "
            "port=(varsayilan 9200), host=(varsayilan 127.0.0.1). "
            "Agent'lar arasi JSON-RPC 2.0 protokolu.",
        ),
        (
            "ACP_DURUM",
            _acp_durum,
            "ACP sunucu durumunu gosterir: calisiyor/durduruldu, transport, agent sayisi.",
        ),
        ("ACP_DURDUR", _acp_durdur, "ACP sunucusunu durdurur."),
        (
            "ACP_CARD_LISTE",
            _acp_card_liste,
            "Kayitli tum Agent Card'lari (yetkinlik bildirimleri) listeler.",
        ),
        (
            "ACP_CARD_KAYDET",
            _acp_card_kaydet,
            "Bir Agent Card kaydeder. Parametreler: agent_id (zorunlu), name, "
            "capabilities (virgulle), skills (virgulle). "
            'Orn: ACP_CARD_KAYDET agent_id=asistan_1 name="Asistan 1" capabilities=messaging,tool_execution',
        ),
        (
            "ACP_DELEGE",
            _acp_delege,
            "Bir gorevi baska bir agent'a devreder. Parametreler: source, target, "
            "title (zorunlu), description, context, priority=(1-10). "
            'Orn: ACP_DELEGE source=reymen target=asistan_2 title="API dokumantasyonu hazirla"',
        ),
        (
            "ACP_GOREV_LISTE",
            _acp_gorev_liste,
            "Devredilen gorevleri listeler. Parametreler: agent_id (filtre), "
            "status=(pending/accepted/completed/failed).",
        ),
        (
            "ACP_BECERI_AKTAR",
            _acp_beceri_aktar,
            "Bir beceriyi skill transfer paketi olarak hazirlar. "
            "Parametreler: name, source, content (zorunlu), description.",
        ),
        (
            "ACP_ISTATISTIK",
            _acp_istatistik,
            "ACP istatistiklerini gosterir: agent sayisi, yetenek dagilimi, "
            "gorev durumu, calisma suresi.",
        ),
    ]

    for ad, fonk, aciklama in tools:
        motor._plugin_arac_kaydet(ad, fonk, aciklama)

    logger.info("[ACP-MOTOR] 9 arac kaydedildi")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 8. TEST / DOÄRUDAN Ã‡ALIÅTIRMA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _test() -> None:
    """Basit entegrasyon testi."""
    print("=== ACP Server Test ===\n")

    # 1. Sunucu oluÅŸtur
    server = ACPServer()
    print("[Test 1] Sunucu olusturuldu.")

    # 2. tools/list
    resp = server.handle('{"jsonrpc":"2.0","method":"tools/list","id":1}')
    data = json.loads(resp)
    tools = data.get("result", {}).get("tools", [])
    print(f"[Test 2] tools/list: {len(tools)} arac")

    # 3. ping
    resp = server.handle('{"jsonrpc":"2.0","method":"ping","id":2}')
    data = json.loads(resp)
    assert data.get("result", {}).get("pong"), f"ping basarisiz: {data}"
    print(f"[Test 3] ping: OK")

    # 4. health
    resp = server.handle('{"jsonrpc":"2.0","method":"health","id":3}')
    data = json.loads(resp)
    assert "status" in data.get("result", {})
    print(f"[Test 4] health: {data['result']['status']}")

    # 5. Agent Card register
    card = {
        "agent_id": "test_agent_1",
        "name": "Test Agent",
        "capabilities": ["messaging", "tool_execution"],
        "skills": ["python", "api"],
    }
    resp = server.handle(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "card/register",
                "params": {"card": card},
                "id": 4,
            }
        )
    )
    data = json.loads(resp)
    assert data.get("result", {}).get("status") == "ok"
    print(f"[Test 5] card/register: {data['result']['agent_id']}")

    # 6. Agent Card list
    resp = server.handle('{"jsonrpc":"2.0","method":"card/list","id":5}')
    data = json.loads(resp)
    cards = data.get("result", {}).get("cards", [])
    print(f"[Test 6] card/list: {len(cards)} card")

    # 7. Task delegation
    resp = server.handle(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "task/delegate",
                "params": {
                    "source_agent": "reymen",
                    "target_agent": "test_agent_1",
                    "title": "Dosya analizi yap",
                    "description": "Verilen dosyayi analiz et",
                },
                "id": 6,
            }
        )
    )
    data = json.loads(resp)
    assert data.get("result", {}).get("status") == "ok"
    task_id = data["result"].get("task", {}).get("task_id", "?")
    print(f"[Test 7] task/delegate: {task_id}")

    # 8. Task status
    resp = server.handle(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "task/status",
                "params": {"task_id": task_id},
                "id": 7,
            }
        )
    )
    data = json.loads(resp)
    print(f"[Test 8] task/status: {data['result']['task']['status']}")

    # 9. Skill transfer
    resp = server.handle(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "skill/transfer",
                "params": {
                    "name": "Python_API_Skill",
                    "content": "# Python API Kullanimi\n...",
                    "source_agent": "reymen",
                    "target_agent": "test_agent_1",
                    "description": "Python API becerisi",
                },
                "id": 8,
            }
        )
    )
    data = json.loads(resp)
    assert data.get("result", {}).get("status") == "ok"
    print(f"[Test 9] skill/transfer: {data['result']['package']['skill_id']}")

    # 10. Bilinmeyen metot
    resp = server.handle('{"jsonrpc":"2.0","method":"bilinmeyen","id":9}')
    data = json.loads(resp)
    assert "error" in data
    print(f"[Test 10] Bilinmeyen metot: {data['error']['code']}")

    # 11. Gecersiz JSON
    resp = server.handle("bu gecerli bir json degil")
    data = json.loads(resp)
    assert "error" in data
    print(f"[Test 11] Gecersiz JSON: {data['error']['code']}")

    # 12. motor_kaydet test
    class MockMotor:
        def __init__(self):
            self._tools = {}

        def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
            self._tools[ad] = (fonk, aciklama)

    mm = MockMotor()
    motor_kaydet(mm)
    print(f"[Test 12] motor_kaydet: {len(mm._tools)} arac kaydedildi")
    for ad in mm._tools:
        print(f"  - {ad}")

    print(f"\n[OK] Tum testler gecti!")
    return 0


if __name__ == "__main__":
    sys.exit(_test())
