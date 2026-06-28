# -*- coding: utf-8 -*-
"""ReYMeN bulgularini VS Code Claude Agent'a ileten kopru."""

import subprocess
import sys
import shlex

BAT_YOLU = r"C:\Users\marko\AppData\Local\hermes\scripts\vscode_yaz.bat"


def ilet(mesaj: str) -> int:
    """Mesaji vscode_yaz.bat araciligiyla VS Code Claude Agent'a gonder."""
    if not mesaj.strip():
        print("[kopru] Bos mesaj, atlanıyor.")
        return 1

    try:
        sonuc = subprocess.run([BAT_YOLU, mesaj], capture_output=True, text=True)
        if sonuc.returncode != 0:
            print(f"[kopru] BAT hatasi (kod {sonuc.returncode}): {sonuc.stderr.strip()}")
        else:
            print(f"[kopru] Gonderildi: {mesaj[:80]}{'...' if len(mesaj) > 80 else ''}")
        return sonuc.returncode
    except FileNotFoundError:
        print(f"[kopru] vscode_yaz.bat bulunamadı: {BAT_YOLU}")
        print("[kopru] Alternatif: claude --print ile dogrudan cagir.")
        return 2
    except Exception as hata:
        print(f"[kopru] Beklenmedik hata: {hata}")
        return 3


if __name__ == "__main__":
    mesaj = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    sys.exit(ilet(mesaj))
