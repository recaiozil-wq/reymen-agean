"""cli_commands — MixinCommands modüler yapısı.

Bu paket, cli_mixin_commands.py'nin modüler versiyonudur.
Tüm alt modüllerden MixinCommands sınıfını birleştirir.
"""

# Tüm alt modülleri import et (metotlar MixinCommands'a eklenir)
from .base import MixinCommands as _BaseMixin
from .edit_commands import MixinCommands as _EditMixin
from .tool_commands import MixinCommands as _ToolMixin
from .session_commands import MixinCommands as _SessionMixin
from .config_commands import MixinCommands as _ConfigMixin
from .system_commands import MixinCommands as _SystemMixin


class MixinCommands(
    _BaseMixin,
    _EditMixin,
    _ToolMixin,
    _SessionMixin,
    _ConfigMixin,
    _SystemMixin,
):
    """Birleştirilmiş MixinCommands — tüm komut metotlarını içerir."""
    pass


__all__ = ["MixinCommands"]
