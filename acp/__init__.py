# -*- coding: utf-8 -*-
"""acp — Agent Communication Protocol paketi (stub).

Bu modül, gerçek ACP SDK'sının (agent-client-protocol) yüzeyini
yansıtan bir stub'tir. acp_adapter/ içindeki kodun import ve
fonksiyon çağrılarının çalışması için yeterli tanımları sağlar.
Gerçek ACP SDK kurulduğunda bu dosya gölgelenir.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Re-export everything from schema
# ---------------------------------------------------------------------------
from .schema import (
    Agent,
    AgentCapabilities,
    AgentMessageChunk,
    AgentPlanUpdate,
    AgentThoughtChunk,
    AllowedOutcome,
    AuthenticateResponse,
    AvailableCommandsUpdate,
    BlobResourceContents,
    ContentToolCallContent,
    DeniedOutcome,
    EmbeddedResourceContentBlock,
    EnvVariable,
    FileEditToolCallContent,
    HttpHeader,
    Implementation,
    InitializeResponse,
    LoadSessionResponse,
    McpServerHttp,
    McpServerStdio,
    NewSessionResponse,
    PermissionOption,
    PlanEntry,
    PromptResponse,
    ResumeSessionResponse,
    SessionInfo,
    SessionInfoUpdate,
    SessionModelState,
    SessionModeState,
    SetSessionConfigOptionResponse,
    SetSessionModelResponse,
    SetSessionModeResponse,
    TextContentBlock,
    ToolCallEnd,
    ToolCallLocation,
    ToolCallProgress,
    ToolCallStart,
    ToolKind,
    ToolResultContentBlock,
    ToolUseContentBlock,
)

from .exceptions import (
    ACPAuthError,
    ACPConnectionError,
    ACPError,
    ACPPermissionError,
    ACPSessionError,
    ACPTimeoutError,
    RequestError,
    ResponseError,
)

__all__ = [
    # Schema classes
    "Agent", "AgentCapabilities", "AgentMessageChunk", "AgentPlanUpdate",
    "AgentThoughtChunk", "AllowedOutcome", "AuthenticateResponse",
    "AvailableCommandsUpdate", "BlobResourceContents", "ContentToolCallContent",
    "DeniedOutcome", "EmbeddedResourceContentBlock", "EnvVariable",
    "FileEditToolCallContent", "HttpHeader", "Implementation",
    "InitializeResponse", "LoadSessionResponse", "McpServerHttp",
    "McpServerStdio", "NewSessionResponse", "PermissionOption", "PlanEntry",
    "PromptResponse", "ResumeSessionResponse", "SessionInfo",
    "SessionInfoUpdate", "SessionModelState", "SessionModeState",
    "SetSessionConfigOptionResponse", "SetSessionModelResponse",
    "SetSessionModeResponse", "TextContentBlock", "ToolCallEnd",
    "ToolCallLocation", "ToolCallProgress", "ToolCallStart", "ToolKind",
    "ToolResultContentBlock", "ToolUseContentBlock",
    # Exceptions
    "ACPError", "ACPConnectionError", "ACPAuthError", "ACPSessionError",
    "ACPPermissionError", "ACPTimeoutError", "RequestError", "ResponseError",
    # Functions
    "start_tool_call", "update_tool_call", "run_agent",
    "tool_content", "text_block", "tool_diff_content",
    "update_agent_thought_text", "update_agent_message_text",
    # Client
    "Client",
]


# ---------------------------------------------------------------------------
# Client — minimal stub
# ---------------------------------------------------------------------------

class Client:
    """ACP istemci bağlantısı (stub).

    Gerçek ACP SDK'sı bu sınıfı JSON-RPC 2.0 taşıyıcısı ile doldurur.
    """
    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    async def session_update(self, session_id: str, update: Any) -> Any:
        """Oturum güncellemesi gönder."""
        return {"success": True}


# ---------------------------------------------------------------------------
# Tool call helpers
# ---------------------------------------------------------------------------

def start_tool_call(
    tool_call_id: str,
    title: str,
    kind: str = "other",
    content: Any = None,
    locations: Any = None,
    raw_input: Any = None,
) -> ToolCallStart:
    """Create a ToolCallStart notification payload.

    Args:
        tool_call_id: Benzersiz araç çağrısı ID'si.
        title: İnsan tarafından okunabilir başlık.
        kind: ToolKind değeri (örn. 'read', 'edit', 'execute').
        content: İçerik blokları listesi (``tool_content`` / ``text_block``).
        locations: ``ToolCallLocation`` nesneleri listesi.
        raw_input: Ham girdi verisi.
    """
    return ToolCallStart(
        tool_id=tool_call_id,
        tool_name=title,
        input_preview=str(content) if content else "",
    )


def update_tool_call(
    tool_call_id: str,
    title: str | None = None,
    kind: str = "other",
    status: str = "completed",
    content: Any = None,
    raw_input: Any = None,
    raw_output: Any = None,
) -> ToolCallProgress:
    """Create a ToolCallProgress (update) notification payload.

    Args:
        tool_call_id: Araç çağrısı ID'si.
        title: Güncellenmiş başlık (opsiyonel).
        kind: ToolKind değeri.
        status: 'pending', 'completed', veya 'failed'.
        content: İçerik blokları listesi.
        raw_input: Ham girdi (opsiyonel).
        raw_output: Ham çıktı (opsiyonel).
    """
    return ToolCallProgress(
        tool_id=tool_call_id,
        tool_name=title or "",
        progress=1.0 if status == "completed" else 0.0,
        message=str(content) if content else "",
    )


# ---------------------------------------------------------------------------
# Content-block helpers
# ---------------------------------------------------------------------------


def tool_content(*blocks: Any) -> List[Any]:
    """Wrap content blocks into a list of tool-content items.

    Each block is typically a ``TextContentBlock``, ``ToolUseContentBlock``,
    ``ToolResultContentBlock``, or a diff block.
    """
    return list(blocks)


def text_block(text: str) -> TextContentBlock:
    """Create a ``TextContentBlock`` for ACP tool content."""
    return TextContentBlock(text=text, block_type="text")


def tool_diff_content(
    path: str,
    old_text: str | None = None,
    new_text: str | None = None,
) -> Dict[str, Any]:
    """Create a diff content block for ACP tool calls.

    Args:
        path: Değiştirilen dosyanın yolu.
        old_text: Eski metin (None = yeni dosya).
        new_text: Yeni metin (None = dosya silindi).
    """
    block: Dict[str, Any] = {"type": "diff", "path": path}
    if old_text is not None:
        block["old_text"] = old_text
    if new_text is not None:
        block["new_text"] = new_text
    return block


# ---------------------------------------------------------------------------
# Agent-message helpers
# ---------------------------------------------------------------------------


def update_agent_thought_text(text: str) -> AgentThoughtChunk:
    """Create an agent thought update.

    Args:
        text: Düşünce metni.
    """
    return AgentThoughtChunk(thought=text)


def update_agent_message_text(text: str) -> AgentMessageChunk:
    """Create an agent message update.

    Args:
        text: Mesaj metni.
    """
    return AgentMessageChunk(content=text, chunk_type="message")


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------


async def run_agent(
    agent: Any,
    *,
    use_unstable_protocol: bool = False,
) -> None:
    """Run an ACP agent over stdio.

    This is a stub; the real ACP SDK implements the JSON-RPC 2.0
    transport loop.  For now it simply awaits forever or until the
    agent signals completion.

    Args:
        agent: ACPAgent uyumlu ajan nesnesi.
        use_unstable_protocol: Deneysel protokol özelliklerini etkinleştir.
    """
    import asyncio

    # In the real SDK this starts a JSON-RPC loop over stdin/stdout.
    # For the stub we just simulate readiness and block.
    if hasattr(agent, "initialize"):
        await agent.initialize()
    # Sleep forever — real ACP will handle this with a transport loop.
    # Using an extremely long sleep that can be interrupted by signals.
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        if hasattr(agent, "close"):
            await agent.close()
