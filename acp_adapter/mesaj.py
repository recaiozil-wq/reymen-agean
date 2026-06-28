# -*- coding: utf-8 -*-
"""acp_adapter/mesaj.py — ACP mesaj ve olay veri yapilari."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AcpMesaj:
    session_id: str
    icerik: str
    tip: str = "user"
    zaman: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AcpOlay:
    tip: str
    session_id: str
    veri: dict = field(default_factory=dict)
    zaman: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {"tip": self.tip, "session_id": self.session_id,
                "veri": self.veri, "zaman": self.zaman}
