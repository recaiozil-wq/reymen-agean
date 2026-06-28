# -*- coding: utf-8 -*-
"""tools/shell.py — Shell Komut Calistirma Araci.

KOMUT_CALISTIR icin terminal_backends uzerinden shell komutu calistirir.
"""

from pathlib import Path

try:
    from terminal_backends import TerminalBackendDispatcher
except ImportError:
    TerminalBackendDispatcher = None


def run(komut: str, timeout: int = 60) -> str:
    """Shell komutu calistir.

    Args:
        komut: Calistirilacak komut
        timeout: Zaman asimi (saniye)

    Returns:
        Cikti metni
    """
    if not komut:
        return "[Shell]: Komut gerekli."
    if TerminalBackendDispatcher:
        t = TerminalBackendDispatcher(mode="local")
        return t.calistir(komut, timeout=timeout)
    import subprocess
    try:
        r = subprocess.run(komut, shell=False, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + ("\n" + r.stderr if r.stderr else "")
    except subprocess.TimeoutExpired:
        return "[Shell]: Zaman asimi."
    except Exception as e:
        return f"[Shell]: Hata: {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run("echo test"))
