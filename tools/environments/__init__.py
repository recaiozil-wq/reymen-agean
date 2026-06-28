"""
tools.environments — Terminal arka uç ortamları.

Kullanılabilir ortamlar:
- local: Yerel Windows/POSIX
- ssh: Uzak sunucu (paramiko)
- docker: Docker konteyner (SDK/CLI)
- wsl: WSL Linux (Windows)
"""

from tools.environments.base import BaseEnvironment
from tools.environments.local import LocalEnvironment
from tools.environments.ssh import SSHEnvironment
from tools.environments.docker import DockerEnvironment

try:
    from tools.environments.wsl import WSLEnvironment
    HAS_WSL = True
except ImportError:
    HAS_WSL = False

__all__ = [
    "BaseEnvironment",
    "LocalEnvironment",
    "SSHEnvironment",
    "DockerEnvironment",
]
if HAS_WSL:
    __all__.append("WSLEnvironment")
