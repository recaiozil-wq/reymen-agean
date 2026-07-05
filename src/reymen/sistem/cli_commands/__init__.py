"""cli_commands â€” MixinCommands modüler yapÄ±sÄ±.

Bu paket, cli_mixin_commands.py'nin modüler versiyonudur.
Tüm alt modüllerden MixinCommands sÄ±nÄ±fÄ±nÄ± birleÅŸtirir.
"""

# Tüm alt modülleri import et (metotlar MixinCommands'a eklenir)
from .base import MixinCommands as _BaseMixin
from .edit_commands import MixinCommands as _EditMixin
from .tool_commands import MixinCommands as _ToolMixin
from .session_commands import MixinCommands as _SessionMixin
from .config_commands import MixinCommands as _ConfigMixin
from .system_commands import MixinCommands as _SystemMixin

# load_cli_config â€” eski cli_commands.py'den buraya tasindi
from reymen.sistem.cli_commands_flat import (
    load_cli_config,
    _load_prefill_messages,
    _parse_reasoning_config,
    _parse_service_tier_config,
)


class MixinCommands(
    _BaseMixin,
    _EditMixin,
    _ToolMixin,
    _SessionMixin,
    _ConfigMixin,
    _SystemMixin,
):
    """BirleÅŸtirilmiÅŸ MixinCommands â€” tüm komut metotlarÄ±nÄ± içerir."""

    pass


__all__ = ["MixinCommands"]
