# -*- coding: utf-8 -*-
"""acp/schema.py — Agent Communication Protocol şema sınıfları (stub)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentCapabilities:
    streaming: bool = True
    tools: bool = True
    plans: bool = True


@dataclass
class AgentMessageChunk:
    content: str = ""
    chunk_type: str = "message"


@dataclass
class AgentPlanUpdate:
    plan: str = ""
    status: str = "pending"


@dataclass
class AgentThoughtChunk:
    thought: str = ""


@dataclass
class AuthenticateResponse:
    success: bool = True
    token: str = ""


@dataclass
class AvailableCommandsUpdate:
    commands: List[str] = field(default_factory=list)


@dataclass
class Implementation:
    name: str = ""
    version: str = "0.0.1"


@dataclass
class InitializeResponse:
    capabilities: Optional[AgentCapabilities] = None
    implementation: Optional[Implementation] = None
    protocol_version: str = "1.0"


@dataclass
class LoadSessionResponse:
    session_id: str = ""
    success: bool = True


@dataclass
class NewSessionResponse:
    session_id: str = ""


@dataclass
class PromptResponse:
    content: str = ""
    done: bool = True


@dataclass
class ResumeSessionResponse:
    session_id: str = ""
    success: bool = True


@dataclass
class SessionModelState:
    model: str = ""


@dataclass
class SessionModeState:
    mode: str = "default"


@dataclass
class SetSessionConfigOptionResponse:
    success: bool = True


@dataclass
class SetSessionModelResponse:
    model: str = ""
    success: bool = True


@dataclass
class SetSessionModeResponse:
    mode: str = ""
    success: bool = True


@dataclass
class SessionInfo:
    session_id: str = ""
    model: str = ""
    mode: str = "default"


@dataclass
class McpServerStdio:
    command: str = ""
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None


@dataclass
class McpServerHttp:
    url: str = ""
    headers: Optional[Dict[str, str]] = None


@dataclass
class EnvVariable:
    name: str = ""
    value: str = ""


@dataclass
class HttpHeader:
    name: str = ""
    value: str = ""


@dataclass
class TextContentBlock:
    """Metin içerik bloğu."""
    text: str = ""
    block_type: str = "text"


@dataclass
class ToolUseContentBlock:
    """Araç kullanım içerik bloğu."""
    tool_id: str = ""
    tool_name: str = ""
    input: dict = field(default_factory=dict)
    block_type: str = "tool_use"


@dataclass
class ToolResultContentBlock:
    """Araç sonuç içerik bloğu."""
    tool_id: str = ""
    content: str = ""
    is_error: bool = False
    block_type: str = "tool_result"


if __name__ == "__main__":
    print("acp.schema importlandı.")


@dataclass
class ToolCallLocation:
    """Araç çağrısı konumu."""
    path: str = ''
    line: int = 0
    column: int = 0


# Backward-compat: tools.py references `ToolCallLocation(path=...)` with 'path'
ToolCallLocation.file_path = ToolCallLocation.path  # type: ignore[attr-defined]


@dataclass
class ToolCallProgress:
    """Araç çağrısı ilerleme bilgisi."""
    tool_id: str = ''
    tool_name: str = ''
    progress: float = 0.0
    message: str = ''
    location: ToolCallLocation = None

    def __post_init__(self):
        if self.location is None:
            self.location = ToolCallLocation()


@dataclass
class ToolCallStart:
    """Araç çağrısı başlangıcı."""
    tool_id: str = ''
    tool_name: str = ''
    input_preview: str = ''


@dataclass
class UsageUpdate:
    """Token kullanım güncellemesi."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0


@dataclass
class UserMessageChunk:
    """Kullanıcı mesaj parçası."""
    content: str = ""
    chunk_type: str = "user_message"


@dataclass
class ToolCallEnd:
    """Araç çağrısı bitişi."""
    tool_id: str = ''
    tool_name: str = ''
    success: bool = True
    error: str = ''


from enum import Enum as _ToolKindEnum

class ToolKind(_ToolKindEnum):
    """Araç türü."""
    BASH = 'bash'
    FILE = 'file'
    WEB = 'web'
    MEMORY = 'memory'
    CUSTOM = 'custom'
    INTERNAL = 'internal'


@dataclass
class PlanEntry:
    """Plan girişi."""
    step: int = 0
    action: str = ''
    status: str = 'pending'
    result: str = ''
    content: str = ''
    priority: str = 'medium'

@dataclass
class FileEditToolCallContent:
    path: str=""
    old_string: str=""
    new_string: str=""
    block_type: str="file_edit"

@dataclass
class AllowedOutcome:
    action: str = ""
    description: str = ""
@dataclass
class BlobResourceContents:
    uri: str = ""
    mime_type: str = ""
    data: bytes = None
@dataclass
class ContentToolCallContent:
    tool_id: str = ""
    content: str = ""
    block_type: str = "content_tool_call"

@dataclass
class SessionInfoUpdate:
    session_id: str = ""
    status: str = ""
    metadata: dict = None
    def __post_init__(self):
        if self.metadata is None: self.metadata = {}


@dataclass
class EmbeddedResourceContentBlock:
    resource_id: str = ""
    mime_type: str = ""
    block_type: str = "embedded_resource"


@dataclass
class DeniedOutcome:
    action: str = ""
    reason: str = ""


@dataclass
class PermissionOption:
    """ACP izin seçeneği."""
    option_id: str = ''
    kind: str = 'allow_once'
    name: str = ''


@dataclass
class Agent:
    """ACP ajan tanımı."""
    name: str = ''
    version: str = '1.0'
    capabilities: Optional[AgentCapabilities] = None

