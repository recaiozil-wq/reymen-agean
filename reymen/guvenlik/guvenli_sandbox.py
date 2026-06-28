# -*- coding: utf-8 -*-
"""
guvenli_sandbox.py — FAZ 6: Cok katmanli guveli Python sandbox.

Katmanlar (en guvenilirden en az guvenilire):
  Mod 1: Docker    — izole_laboratuvar.py uzerinden (mevcutsa)
  Mod 2: Restricted — RestrictedPython ile builtin filtreleme (mevcutsa)
  Mod 3: TempDir  — ayri gecici dizin + subprocess (her zaman calısır)

Kullanim:
    from guvenli_sandbox import guvenli_calistir
import logging
logger = logging.getLogger(__name__)
    sonuc = guvenli_calistir("print('merhaba')", timeout=30)
"""

import os
import re
import subprocess
import sys
import tempfile
import textwrap
import uuid
from pathlib import Path

# ─── Tehlikeli kalip listesi ─────────────────────────────────────────────────

_TEHLIKELI_KALIPLAR = [
    r"\bos\.system\s*\(",
    r"\bsubprocess\s*\.",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\b__import__\s*\(",
    r"\bopen\s*\(.*['\"]w['\"]",          # yazma modunda dosya ac
    r"\bshutil\s*\.",
    r"\brmdir\b",
    r"\bunlink\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bsocket\s*\.",
    r"\burllib\s*\.",
    r"\brequests\s*\.",
    r"\bftplib\s*\.",
    r"\bsmtplib\s*\.",
    r"import\s+ctypes",
    r"import\s+winreg",
    r"import\s+win32",
]

_TEHLIKELI_RE = re.compile("|".join(_TEHLIKELI_KALIPLAR), re.IGNORECASE)


def _tehlikeli_mi(kod: str) -> tuple[bool, str]:
    """Kodu tehlikeli kaliplar icin tara. (tehlikeli_mi, kalip) doner."""
    eslesme = _TEHLIKELI_RE.search(kod)
    if eslesme:
        return True, eslesme.group()
    return False, ""


# ─── Mod 1: Docker (mevcut izole_laboratuvar.py uzerinden) ───────────────────

def _docker_ile_calistir(kod: str, timeout: int) -> str | None:
    """Docker mevcutsa izole_laboratuvar ile calistir, yoksa None don."""
    try:
        from reymen.cereyan.izole_laboratuvar import izole_python_calistir, DOCKER_AVAILABLE
        if not DOCKER_AVAILABLE:
            return None
        return izole_python_calistir(kod, timeout=timeout)
    except Exception:
        return None


# ─── Mod 2: RestrictedPython ─────────────────────────────────────────────────

def _restricted_ile_calistir(kod: str, timeout: int) -> str | None:
    """RestrictedPython ile sinirli ortamda calistir. Yuklu degilse None don."""
    try:
        from RestrictedPython import compile_restricted, safe_globals
        from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
    except ImportError:
        return None

    try:
        bytekod = compile_restricted(kod, "<sandbox>", "exec")
    except SyntaxError as e:
        return f"[Hata]: Sozdizimi hatasi — {e}"

    izinli_globals = dict(safe_globals)
    izinli_globals["__builtins__"] = dict(safe_builtins)
    izinli_globals["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence
    # print icin ciktiyi yakala
    cikti_satirlari: list[str] = []

    def _guveli_print(*args, **kwargs):
        cikti_satirlari.append(" ".join(str(a) for a in args))

    izinli_globals["__builtins__"]["print"] = _guveli_print

    try:
        import signal

        def _zaman_asimi(signum, frame):
            raise TimeoutError("Sandbox zaman asimi")

        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _zaman_asimi)
            signal.alarm(timeout)

        exec(bytekod, izinli_globals, {})

        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)

        return "[CIKTI]\n" + "\n".join(cikti_satirlari)
    except TimeoutError:
        return "[Hata]: Sandbox zaman asimi."
    except Exception as e:
        return f"[Hata]: {type(e).__name__}: {e}"


# ─── Mod 3: TempDir subprocess (her zaman calısır) ───────────────────────────

def _tempdir_ile_calistir(kod: str, timeout: int) -> str:
    """Gecici dizinde izole subprocess ile calistir."""
    with tempfile.TemporaryDirectory(prefix="reymen_sb_") as tmpdir:
        dosya = os.path.join(tmpdir, f"sb_{uuid.uuid4().hex[:8]}.py")
        try:
            with open(dosya, "w", encoding="utf-8") as f:
                f.write(kod)
        except OSError as e:
            return f"[Hata]: Gecici dosya yazılamadi — {e}"

        try:
            proc = subprocess.run(
                [sys.executable, dosya],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
                encoding="utf-8",
                errors="replace",
            )
            cikti = proc.stdout.strip()
            hata = proc.stderr.strip()
            parcalar = []
            if cikti:
                parcalar.append(f"[CIKTI]\n{cikti}")
            if hata:
                parcalar.append(f"[HATA]\n{hata}")
            return "\n".join(parcalar) if parcalar else "[Cikti yok]"
        except subprocess.TimeoutExpired:
            return "[Hata]: Sandbox zaman asimi."
        except Exception as e:
            return f"[Hata]: {e}"


# ─── Ana API ──────────────────────────────────────────────────────────────────

def guvenli_calistir(
    kod: str,
    timeout: int = 30,
    mod: str = "oto",
    tehlike_kontrolu: bool = True,
) -> str:
    """Python kodunu en guvenli mevcut modda calistir.

    Args:
        kod:              Calistirilacak Python kodu.
        timeout:          Saniye cinsinden zaman siniri (varsayilan: 30).
        mod:              "oto" | "docker" | "restricted" | "tempdir"
        tehlike_kontrolu: True ise tehlikeli kaliplarda hemen reddet.

    Returns:
        Cikti veya hata mesaji (string).
    """
    if not kod or not kod.strip():
        return "[Hata]: Bos kod."

    # Tehlike taramasi
    if tehlike_kontrolu:
        tehlikeli, kalip = _tehlikeli_mi(kod)
        if tehlikeli:
            return f"[Guvenlik Reddi]: Tehlikeli kalip tespit edildi — '{kalip}'"

    if mod == "docker":
        sonuc = _docker_ile_calistir(kod, timeout)
        return sonuc if sonuc is not None else "[Hata]: Docker mevcut degil."

    if mod == "restricted":
        sonuc = _restricted_ile_calistir(kod, timeout)
        return sonuc if sonuc is not None else "[Hata]: RestrictedPython yuklu degil."

    if mod == "tempdir":
        return _tempdir_ile_calistir(kod, timeout)

    # oto: en guvenli mevcut moda dusme
    sonuc = _docker_ile_calistir(kod, timeout)
    if sonuc is not None:
        return sonuc

    sonuc = _restricted_ile_calistir(kod, timeout)
    if sonuc is not None:
        return sonuc

    return _tempdir_ile_calistir(kod, timeout)


def sandbox_modu_raporu() -> str:
    """Hangi sandbox modlarinin kullanilabildigini raporla."""
    modlar = []
    try:
        from reymen.cereyan.izole_laboratuvar import DOCKER_AVAILABLE
        modlar.append(f"Docker: {'HAZIR' if DOCKER_AVAILABLE else 'yok'}")
    except ImportError:
        modlar.append("Docker: modul yok")

    try:
        import RestrictedPython  # noqa: F401
        modlar.append("RestrictedPython: HAZIR")
    except ImportError:
        modlar.append("RestrictedPython: yuklu degil")

    modlar.append("TempDir subprocess: HAZIR (her zaman)")
    return " | ".join(modlar)


# ─── Test ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== guvenli_sandbox.py Test ===")
    print(f"[Mod raporu] {sandbox_modu_raporu()}\n")

    testler = [
        ("Basit print", "print('Merhaba ReYMeN FAZ6')"),
        ("Matematik", "x = 2 ** 10\nprint(f'2^10 = {x}')"),
        ("Tehlike: os.system", "import os\nos.system('echo kotu')"),
        ("Tehlike: subprocess", "import subprocess\nsubprocess.run(['dir'])"),
        ("Syntax hatasi", "def eksik(\nprint('bozuk')"),
        ("Zaman asimi", "while True: pass"),
    ]

    for ad, kod in testler:
        print(f"--- Test: {ad} ---")
        sonuc = guvenli_calistir(kod, timeout=3)
        print(sonuc)
        print()
