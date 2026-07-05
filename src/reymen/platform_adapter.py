"""ğŸŒ Ã‡apraz platform â€” WSL/Kali adapter + path çevirici.

Windows â†” WSL/Kali arasÄ±nda yol çevirisi ve komut çalÄ±ÅŸtÄ±rma saÄŸlar.
WSL kurulu deÄŸilse veya Windows dÄ±ÅŸÄ± platformdaysa ``NativeAdapter``
kullanÄ±lÄ±r; tüm metotlar graceful fallback yapar.

Ã–rnek::

    from ReYMeN.platform_adapter import detect, translate_path, run

    adapter = detect()
    linux_path = translate_path(r"C:\\Users\\marko\\proj")
    result = run(["ls", "-la", linux_path])
"""

from __future__ import annotations

import os
import platform
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Sequence

__all__ = [
    "PlatformAdapter",
    "NativeAdapter",
    "WSLAdapter",
    "KaliAdapter",
    "PlatformInfo",
    "detect",
    "translate_path",
    "run",
    "is_wsl_available",
    "list_wsl_distros",
]


# ---------------------------------------------------------------------------
# YardÄ±mcÄ±: WSL varlÄ±k kontrolü
# ---------------------------------------------------------------------------
def is_wsl_available() -> bool:
    """``wsl.exe`` bulunuyorsa ve en az bir daÄŸÄ±tÄ±m kuruluysa ``True``."""
    if not shutil.which("wsl.exe"):
        return False
    try:
        result = subprocess.run(
            ["wsl.exe", "--list", "--quiet"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    # WSL çÄ±ktÄ±sÄ± UTF-16 LE olabilir; güvenli temizle
    out = result.stdout.replace("\x00", "").strip()
    return bool(out)


def list_wsl_distros() -> list[str]:
    """Kurulu WSL daÄŸÄ±tÄ±mlarÄ±nÄ±n isim listesini döndürür."""
    if not shutil.which("wsl.exe"):
        return []
    try:
        result = subprocess.run(
            ["wsl.exe", "--list", "--quiet"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    out = result.stdout.replace("\x00", "")
    return [line.strip() for line in out.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# PlatformInfo
# ---------------------------------------------------------------------------
@dataclass
class PlatformInfo:
    """Tespit edilen platform bilgisi."""

    kind: str  # "native" | "wsl" | "kali"
    distro: str | None = None
    wsl_available: bool = False
    host_os: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "distro": self.distro,
            "wsl_available": self.wsl_available,
            "host_os": self.host_os,
        }


# ---------------------------------------------------------------------------
# Adapter arayüzü
# ---------------------------------------------------------------------------
class PlatformAdapter:
    """Platform adapter temel sÄ±nÄ±fÄ±."""

    kind = "native"

    def info(self) -> PlatformInfo:
        return PlatformInfo(kind=self.kind, host_os=platform.system())

    # -- Path çeviri --------------------------------------------------------
    def translate_path(self, path: str | Path) -> str:
        """Verilen yolu hedef platformun formatÄ±na çevirir."""
        raise NotImplementedError

    def translate_path_back(self, path: str | Path) -> str:
        """Hedef platformdan host platforma yol çevirir."""
        raise NotImplementedError

    # -- Komut çalÄ±ÅŸtÄ±r -----------------------------------------------------
    def run(
        self,
        cmd: Sequence[str] | str,
        *,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Komutu hedef platformda çalÄ±ÅŸtÄ±rÄ±r."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Native adapter (Windows üzerinde Windows, Linux üzerinde Linux)
# ---------------------------------------------------------------------------
class NativeAdapter(PlatformAdapter):
    """AynÄ± iÅŸletim sisteminde çalÄ±ÅŸan yerel adapter."""

    kind = "native"

    def translate_path(self, path: str | Path) -> str:
        return str(path)

    def translate_path_back(self, path: str | Path) -> str:
        return str(path)

    def run(
        self,
        cmd: Sequence[str] | str,
        *,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        shell = isinstance(cmd, str)
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            timeout=timeout,
            check=check,
            capture_output=True,
            text=True,
            shell=shell,
        )


# ---------------------------------------------------------------------------
# WSL adapter
# ---------------------------------------------------------------------------
class WSLAdapter(PlatformAdapter):
    """Windows üzerinden WSL'de komut çalÄ±ÅŸtÄ±ran adapter.

    ``distro`` belirtilmezse varsayÄ±lan WSL daÄŸÄ±tÄ±mÄ± kullanÄ±lÄ±r.
    """

    kind = "wsl"

    def __init__(self, distro: str | None = None) -> None:
        self.distro = distro

    def info(self) -> PlatformInfo:
        return PlatformInfo(
            kind=self.kind,
            distro=self.distro,
            wsl_available=is_wsl_available(),
            host_os=platform.system(),
        )

    # -- Path çeviri --------------------------------------------------------
    def translate_path(self, path: str | Path) -> str:
        """Windows yolunu WSL (Linux) yoluna çevirir.

        - ``C:\\Users\\foo`` -> ``/mnt/c/Users/foo``
        - ``\\\\wsl$\\Ubuntu\\home\\user`` -> ``/home/user``
        - Zaten Linux yoluysa olduÄŸu gibi bÄ±rakilir.
        """
        s = str(path)
        if s.startswith("/") or s.startswith("~"):
            return s

        # \\wsl$\Distro\path  veya  \\wsl.localhost\Distro\path
        low = s.lower()
        if low.startswith("\\\\wsl$\\") or low.startswith("\\\\wsl.localhost\\"):
            parts = s.split(
                "\\", 4
            )  # ['', '', 'wsl$'/'wsl.localhost', 'Distro', 'path']
            if len(parts) == 5:
                return "/" + parts[4].replace("\\", "/")
            elif len(parts) == 4:
                # Sadece \\wsl$\Distro â€” kök
                return "/"

        # Sürücü harfi: C:\Users\foo
        if len(s) >= 2 and s[1] == ":":
            drive = s[0].lower()
            rest = s[2:].replace("\\", "/")
            if rest.startswith("/"):
                rest = rest[1:]
            return f"/mnt/{drive}/{rest}"

        return s.replace("\\", "/")

    def translate_path_back(self, path: str | Path) -> str:
        """WSL (Linux) yolunu Windows yoluna çevirir.

        - ``/mnt/c/Users/foo`` -> ``C:\\Users\\foo``
        - ``/home/user`` -> ``\\\\wsl$\\<distro>\\home\\user``
        """
        s = str(path)
        # /mnt/x/... -> X:\...
        if s.startswith("/mnt/"):
            parts = s.split("/", 3)  # ['', 'mnt', 'x', 'rest']
            if len(parts) >= 3:
                drive = parts[2].upper()
                rest = parts[3].replace("/", "\\") if len(parts) == 4 else ""
                return f"{drive}:\\" + rest

        # DiÄŸer Linux yollarÄ± \\wsl$\<distro>\... olarak
        distro = self.distro or _default_wsl_distro() or "Ubuntu"
        clean = s.lstrip("/").replace("/", "\\")
        return "\\\\wsl$\\" + distro + "\\" + clean

    # -- Komut çalÄ±ÅŸtÄ±r -----------------------------------------------------
    def _wsl_prefix(self) -> list[str]:
        prefix = ["wsl.exe"]
        if self.distro:
            prefix += ["-d", self.distro]
        return prefix

    def run(
        self,
        cmd: Sequence[str] | str,
        *,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        if isinstance(cmd, str):
            shell_cmd = cmd
        else:
            shell_cmd = " ".join(shlex.quote(str(c)) for c in cmd)

        full_cmd = self._wsl_prefix()
        if cwd:
            full_cmd += ["--cd", self.translate_path(cwd)]
        full_cmd += ["--", shell_cmd]

        # WSL env deÄŸiÅŸkenleri: -- bash -c 'export X=Y; ...'
        if env:
            env_prefix = " ".join(
                f"export {k}={shlex.quote(v)}" for k, v in env.items()
            )
            shell_cmd = f"{env_prefix}; {shell_cmd}"
            full_cmd = self._wsl_prefix()
            if cwd:
                full_cmd += ["--cd", self.translate_path(cwd)]
            full_cmd += ["--", "bash", "-c", shell_cmd]

        return subprocess.run(
            full_cmd,
            timeout=timeout,
            check=check,
            capture_output=True,
            text=True,
        )


# ---------------------------------------------------------------------------
# Kali adapter (WSL üzerinden kali-linux daÄŸÄ±tÄ±mÄ±)
# ---------------------------------------------------------------------------
class KaliAdapter(WSLAdapter):
    """Kali Linux (WSL) adapter."""

    kind = "kali"

    def __init__(self, distro: str = "kali-linux") -> None:
        super().__init__(distro=distro)


# ---------------------------------------------------------------------------
# Tespit ve singleton
# ---------------------------------------------------------------------------
def _default_wsl_distro() -> str | None:
    distros = list_wsl_distros()
    return distros[0] if distros else None


def detect(prefer_kali: bool = False) -> PlatformAdapter:
    """Ã‡alÄ±ÅŸma ortamÄ±na göre uygun adapter döndürür.

    - Windows + WSL varsa ``WSLAdapter`` (veya ``prefer_kali`` ise
      ``KaliAdapter`` eÄŸer kali-linux kuruluysa)
    - DiÄŸer durumda ``NativeAdapter``
    """
    if sys.platform != "win32":
        return NativeAdapter()

    if not is_wsl_available():
        return NativeAdapter()

    distros = list_wsl_distros()
    if prefer_kali and any("kali" in d.lower() for d in distros):
        return KaliAdapter()

    return WSLAdapter(distro=None)


# ---------------------------------------------------------------------------
# Modül-seviyesi singleton + kolaylÄ±k fonksiyonlarÄ±
# ---------------------------------------------------------------------------
_singleton: PlatformAdapter | None = None


def _get_adapter() -> PlatformAdapter:
    global _singleton
    if _singleton is None:
        _singleton = detect()
    return _singleton


def set_adapter(adapter: PlatformAdapter) -> None:
    """Singleton adapter'Ä± deÄŸiÅŸtirir (testler için)."""
    global _singleton
    _singleton = adapter


def translate_path(path: str | Path) -> str:
    """Global adapter üzerinden yol çevirisi."""
    return _get_adapter().translate_path(path)


def run(
    cmd: Sequence[str] | str,
    *,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Global adapter üzerinden komut çalÄ±ÅŸtÄ±rÄ±r."""
    return _get_adapter().run(cmd, cwd=cwd, env=env, timeout=timeout, check=check)
