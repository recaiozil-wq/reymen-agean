from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model: str
    provider: str
    usage: dict = field(default_factory=dict)
    raw: Any = None
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def text(self) -> str:
        return self.content
