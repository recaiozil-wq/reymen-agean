# -*- coding: utf-8 -*-
"""ReYMeN Multi-Bot Launcher — 3 botu ayri process'lerde baslatir."""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

PROJE_KOK = Path(__file__).resolve().parent
VENV_PYTHON = PROJE_KOK / "venv" / "Scripts" / "python.exe"

BOTLAR = [
    {"adi": "Kral_38", "token_env": "BOT_TOKEN_KRAL"},
    {"adi": "Pasa_38", "token_env": "BOT_TOKEN_PASA"},
    {"adi": "ReYMeN_¥_♤", "token_env": "BOT_TOKEN_REYMEN"},
]


def _env_yukle():
    """.env dosyasini oku, ortam degiskenlerine ekle."""
    env_dosyasi = PROJE_KOK / ".env"
    if env_dosyasi.exists():
        with open(env_dosyasi, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())


def bot_baslat(bot_adi: str, token_env: str):
    """Bir botu ayri process'te baslat."""
    token = os.environ.get(token_env, "").strip()
    if not token:
        print(f"[{bot_adi}] ❌ Token bulunamadi ({token_env})")
        return None

    env = os.environ.copy()
    env["BOT_TOKEN"] = token
    env["BOT_AD"] = bot_adi

    proc = subprocess.Popen(
        [str(VENV_PYTHON), "-m", "reymen.telegram_bot"],
        cwd=str(PROJE_KOK),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    )
    print(f"[{bot_adi}] ✅ Baslatildi (PID: {proc.pid})", flush=True)
    return proc


def main():
    print("╔══════════════════════════════════════╗")
    print("║   ReYMeN Multi-Bot Launcher          ║")
    print("╚══════════════════════════════════════╝")
    print()

    _env_yukle()
    processler = []

    for bot in BOTLAR:
        proc = bot_baslat(bot["adi"], bot["token_env"])
        if proc:
            processler.append(proc)
        time.sleep(1)

    print(f"\n{len(processler)}/{len(BOTLAR)} bot calisiyor.")
    print("Ctrl+C ile tumunu durdurun.")
    print()

    try:
        while True:
            time.sleep(1)
            for p in processler:
                if p.poll() is not None:
                    print(f"[!] Bir bot kapandi (PID: {p.pid})")
    except KeyboardInterrupt:
        print("\nDurduruluyor...")
        for p in processler:
            p.terminate()
        print("Tum botlar durduruldu.")


if __name__ == "__main__":
    main()
