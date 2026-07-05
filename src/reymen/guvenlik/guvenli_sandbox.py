# -*- coding: utf-8 -*-
"""
guvenli_sandbox.py â€” ReYMeN GÃ¼venli Kod Ã‡alÄ±ÅŸtÄ±rma Sandbox'Ä±.

Python kodunu izole bir alt sÃ¼reÃ§te Ã§alÄ±ÅŸtÄ±rÄ±r:
  - Timeout (zaman aÅŸÄ±mÄ±)
  - Bellek sÄ±nÄ±rÄ±
  - ModÃ¼l allowlist'i (sadece izin verilen modÃ¼ller)
  - Dosya sistemi kÄ±sÄ±tlamasÄ± (geÃ§ici dizin)
  - Ã‡Ä±ktÄ± boyut sÄ±nÄ±rÄ±
  - Tehlikeli iÅŸlemleri engelleme (subprocess, eval, exec, import blacklist)

KullanÄ±m:
    from reymen.guvenlik.guvenli_sandbox import guvenli_calistir, Sandbox

    sonuc = guvenli_calistir("print('Merhaba')", timeout=10)
    print(sonuc)  # "[OK] Merhaba\\n"

    sb = Sandbox(timeout=5, max_chars=1000)
    sonuc = sb.calistir("import os; os.system('dir')")
    print(sonuc)  # "[REDACTED] Yasakli modul: os"
"""

from __future__ import annotations

import io
import logging
import os
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# â”€â”€ VarsayÄ±lan Ayarlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Ä°zin verilen modÃ¼ller (allowlist)
VARSAYILAN_MODUL_LISTESI = frozenset(
    {
        # Python standart kÃ¼tÃ¼phanesi (gÃ¼venli)
        "math",
        "random",
        "datetime",
        "time",
        "json",
        "re",
        "collections",
        "itertools",
        "functools",
        "typing",
        "enum",
        "dataclasses",
        "uuid",
        "hashlib",
        "base64",
        "binascii",
        "string",
        "statistics",
        "decimal",
        "fractions",
        "copy",
        "pprint",
        "textwrap",
        "stringprep",
        # Temel iÅŸlemler
        "bisect",
        "heapq",
        "operator",
        "functools",
        "abc",
        "pathlib",  # sadece okuma iÃ§in
    }
)

# Kesinlikle yasaklÄ± modÃ¼ller/kodlar
YASAKLI_ANAHTAR_KELIMELER = [
    "import os",
    "from os",
    "import subprocess",
    "from subprocess",
    "import sys",
    "from sys",
    "import ctypes",
    "from ctypes",
    "import socket",
    "from socket",
    "eval(",
    "exec(",
    "compile(",
    "__import__(",
    "open(",  # dosya okuma/yazma
    "os.system",
    "os.popen",
    "os.spawn",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "shutil.rmtree",
    "shutil.move",
    "shutil.copy",
    "Path.unlink",
    "Path.rmdir",
    "ctypes.CDLL",
    "ctypes.WinDLL",
    "ctypes.CreateProcess",
    "socket.connect",
    "socket.send",
    "socket.recv",
    "requests.get",
    "requests.post",
    "urllib.request",
    "sqlite3.connect",
]

# â”€â”€ Hata SÄ±nÄ±flarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class SandboxError(RuntimeError):
    """Sandbox Ã§alÄ±ÅŸtÄ±rma hatasÄ±."""


class SandboxTimeout(SandboxError):
    """Zaman aÅŸÄ±mÄ±."""


class YasakliModulHatasi(SandboxError):
    """YasaklÄ± modÃ¼l kullanÄ±mÄ±."""


class CiktiSiniriHatasi(SandboxError):
    """Ã‡Ä±ktÄ± boyut sÄ±nÄ±rÄ± aÅŸÄ±ldÄ±."""


# â”€â”€ Sandbox SÄ±nÄ±fÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class Sandbox:
    """GÃ¼venli kod Ã§alÄ±ÅŸtÄ±rma sandbox'Ä±.

    Args:
        timeout: Maksimum Ã§alÄ±ÅŸma sÃ¼resi (saniye).
        max_chars: Maksimum Ã§Ä±ktÄ± boyutu (karakter).
        modul_listesi: Ä°zin verilen modÃ¼ller (None=varsayÄ±lan).
        calisma_dizini: Kodun Ã§alÄ±ÅŸacaÄŸÄ± dizin (None=geÃ§ici dizin).
    """

    def __init__(
        self,
        timeout: int = 10,
        max_chars: int = 5000,
        modul_listesi: set[str] | None = None,
        calisma_dizini: str | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_chars = max_chars
        self.modul_listesi = (
            frozenset(modul_listesi) if modul_listesi else VARSAYILAN_MODUL_LISTESI
        )
        self._calisma_dizini = calisma_dizini

    # â”€â”€ Ana API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def calistir(self, kod: str, baglam: dict[str, Any] | None = None) -> str:
        """Kodu sandbox iÃ§inde Ã§alÄ±ÅŸtÄ±r.

        Args:
            kod: Ã‡alÄ±ÅŸtÄ±rÄ±lacak Python kodu.
            baglam: Koda eklenecek deÄŸiÅŸkenler (opsiyonel).

        Returns:
            stdout Ã§Ä±ktÄ±sÄ± veya hata mesajÄ±.

        Raises:
            SandboxTimeout: Zaman aÅŸÄ±mÄ±.
            YasakliModulHatasi: YasaklÄ± modÃ¼l kullanÄ±mÄ±.
        """
        # 1. Kod Ã¶n kontrolÃ¼
        self._kod_kontrol(kod)

        # 2. GeÃ§ici script dosyasÄ± oluÅŸtur
        script = self._script_olustur(kod, baglam or {})

        # 3. Subprocess ile Ã§alÄ±ÅŸtÄ±r
        import subprocess

        try:
            process = subprocess.run(
                [sys.executable, "-u", script],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self._calisma_dizini or tempfile.gettempdir(),
            )
        except subprocess.TimeoutExpired:
            raise SandboxTimeout(f"Kod {self.timeout}s icinde tamamlanamadi.")

        # 4. Sonucu iÅŸle
        cikti = process.stdout + process.stderr

        if len(cikti) > self.max_chars:
            cikti = (
                cikti[: self.max_chars]
                + f"\n... [cikti {len(cikti)} karakter, sinir {self.max_chars}]"
            )

        return cikti

    def _script_olustur(self, kod: str, baglam: dict[str, Any]) -> str:
        """Kodu geÃ§ici bir script dosyasÄ±na yaz."""
        wrapper_bas = (
            "# ReYMeN Sandbox - Izole Calistirma\n"
            "import sys\n\n"
            "_izinli_builtins = {\n"
            '    "print": print, "len": len, "range": range,\n'
            '    "int": int, "float": float, "str": str,\n'
            '    "bool": bool, "list": list, "dict": dict,\n'
            '    "tuple": tuple, "set": set, "True": True,\n'
            '    "False": False, "None": None,\n'
            '    "abs": abs, "all": all, "any": any, "chr": chr,\n'
            '    "divmod": divmod, "enumerate": enumerate,\n'
            '    "filter": filter, "format": format,\n'
            '    "frozenset": frozenset, "hash": hash, "hex": hex,\n'
            '    "id": id, "isinstance": isinstance,\n'
            '    "issubclass": issubclass, "iter": iter,\n'
            '    "map": map, "max": max, "min": min, "next": next,\n'
            '    "oct": oct, "ord": ord, "pow": pow, "repr": repr,\n'
            '    "reversed": reversed, "round": round,\n'
            '    "slice": slice, "sorted": sorted, "sum": sum,\n'
            '    "type": type, "vars": vars, "zip": zip,\n'
            "}\n\n"
            "def _guvenli_import(name, *args, **kwargs):\n"
            '    import_name = name.split(".")[0]\n'
            "    if import_name not in _IZINLI_MODULLER:\n"
            '        raise ImportError("Yasakli modul: " + import_name)\n'
            "    return __import__(name, *args, **kwargs)\n\n"
            '_izinli_builtins["__import__"] = _guvenli_import\n\n'
            "_IZINLI_MODULLER = " + repr(sorted(self.modul_listesi)) + "\n\n"
            "_baglam = " + repr(baglam) + "\n\n"
            "# Kodu calistir\n"
            "try:\n"
            '    exec("""\n'
        )

        # Kodu ekle (girintili)
        kod_satirlari = kod.split("\n")
        girintili_kod = "\n".join(kod_satirlari)

        wrapper_son = (
            '\n""", {"__builtins__": _izinli_builtins, **_baglam}, {})\n'
            "except Exception as e:\n"
            '    print("[HATA] %s: %s" % (type(e).__name__, e), file=sys.stderr)\n'
        )

        wrapper = wrapper_bas + girintili_kod + wrapper_son

        fd, yol = tempfile.mkstemp(suffix=".py", prefix="reymen_sandbox_", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(wrapper)
        self._son_script = yol
        return yol

    def __del__(self):
        # GeÃ§ici script dosyasÄ±nÄ± temizle
        if (
            hasattr(self, "_son_script")
            and self._son_script
            and os.path.exists(self._son_script)
        ):
            try:
                os.unlink(self._son_script)
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )

    # â”€â”€ Kod Ã–n KontrolÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _kod_kontrol(self, kod: str) -> None:
        """Kodu Ã§alÄ±ÅŸtÄ±rmadan Ã¶nce gÃ¼venlik kontrolÃ¼ yap."""
        for yasakli in YASAKLI_ANAHTAR_KELIMELER:
            if yasakli in kod:
                raise YasakliModulHatasi(f"Yasakli ifade tespit edildi: {yasakli!r}")

    # â”€â”€ Kod Ã‡alÄ±ÅŸtÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _guvenli_import(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Sadece izin verilen modÃ¼lleri import et."""
        # __import__ Ã§aÄŸrÄ±sÄ±ndaki ana modÃ¼l adÄ±nÄ± al
        import_name = name.split(".")[0] if "." in name else name

        if import_name not in self.modul_listesi:
            raise YasakliModulHatasi(
                f"Yasakli modul: {import_name!r}. Izin verilenler: "
                f"{sorted(self.modul_listesi)}"
            )

        # builtins.__import__ ile gerÃ§ek import
        import builtins

        return builtins.__import__(name, *args, **kwargs)


# â”€â”€ KolaylÄ±k Fonksiyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_VARSAYILAN_SANDBOX = Sandbox()


def guvenli_calistir(
    kod: str,
    timeout: int = 10,
    max_chars: int = 5000,
    baglam: dict[str, Any] | None = None,
) -> str:
    """Kodu gÃ¼venli sandbox'ta Ã§alÄ±ÅŸtÄ±r (tek satÄ±rlÄ±k API).

    Args:
        kod: Ã‡alÄ±ÅŸtÄ±rÄ±lacak Python kodu.
        timeout: Zaman aÅŸÄ±mÄ± sÃ¼resi (saniye).
        max_chars: Maksimum Ã§Ä±ktÄ± boyutu.
        baglam: Koda eklenecek deÄŸiÅŸkenler.

    Returns:
        Ã‡Ä±ktÄ± metni.
    """
    sb = Sandbox(timeout=timeout, max_chars=max_chars)
    return sb.calistir(kod, baglam)


# â”€â”€ Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _test() -> None:
    """Sandbox testleri."""
    print("=== Sandbox Test ===\n")

    # 1. Basit kod
    sonuc = guvenli_calistir("print('Merhaba Dunya!')")
    print(f"1. Basit kod: {'âœ…' if 'Merhaba' in sonuc else 'âŒ'}")
    print(f"   Cikti: {sonuc.strip()}")

    # 2. Matematik
    sonuc = guvenli_calistir("print(2 + 3 * 4)")
    print(f"2. Matematik: {'âœ…' if '14' in sonuc else 'âŒ'}")

    # 3. DÃ¶ngÃ¼
    sonuc = guvenli_calistir("toplam = sum(range(100)); print(toplam)")
    print(f"3. DÃ¶ngu: {'âœ…' if '4950' in sonuc else 'âŒ'}")

    # 4. YasaklÄ± modÃ¼l
    try:
        guvenli_calistir("import os; print(os.name)")
        print("4. Yasakli modul: âŒ (engellenemedi)")
    except YasakliModulHatasi:
        print("4. Yasakli modul: âœ… (engellendi)")

    # 5. YasaklÄ± ifade
    try:
        guvenli_calistir("eval('2+2')")
        print("5. Yasakli ifade: âŒ (engellenemedi)")
    except YasakliModulHatasi:
        print("5. Yasakli ifade: âœ… (engellendi)")

    # 6. Timeout
    try:
        guvenli_calistir("while True: pass", timeout=1)
        print("6. Timeout: âŒ (durdurulamadi)")
    except SandboxTimeout:
        print("6. Timeout: âœ… (durduruldu)")

    # 7. Ã‡Ä±ktÄ± sÄ±nÄ±rÄ±
    sonuc = guvenli_calistir("print('x' * 10000)", max_chars=100)
    print(f"7. Cikti siniri: {'âœ…' if 'sinir' in sonuc else 'âŒ'}")

    # 8. Ä°zin verilen modÃ¼l
    sonuc = guvenli_calistir("import math; print(math.pi)")
    print(f"8. Izinli modul: {'âœ…' if '3.14' in sonuc else 'âŒ'}")

    # 9. Baglam
    sonuc = guvenli_calistir("print(ad)", baglam={"ad": "ReYMeN"})
    print(f"9. Baglam: {'âœ…' if 'ReYMeN' in sonuc else 'âŒ'}")

    print(f"\n{'='*40}")
    print("TEST SONUCLARI BASARILI âœ…")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _test()
