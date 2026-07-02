# -*- coding: utf-8 -*-
"""🚀 ReYMeN Telegram Bot'larini baslat — ReYMeN gateway olmadan.

2 bot ayri process'te BotProcess (ai_bot.py) ile calisir.
- @ReYMeN_ReYMeNbot: ReYMeN-Ajan/.env -> REYMEN_BOT_TOKEN
- @Kiral38bot: ReYMeN-Ajan/.env -> KIRAL38_BOT_TOKEN

Kullanim:
    python run_reymen_bots.py

Not: @Pasa_38_bot ReYMeN gateway'de kalir (dokunma).
"""

import os
import subprocess
import sys
from pathlib import Path

# Windows'ta pencere flaşını önle
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _env_oku():
    """ReYMeN-Ajan proje .env'sinden bot token'larini oku."""
    proje_env = Path(__file__).parent.resolve() / ".env"

    if not proje_env.exists():
        print(f"[HATA] {proje_env} bulunamadi!")
        return

    for line in proje_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            val = val.strip().strip("'\"")
            if val and not val.startswith("***"):
                os.environ[key] = val


def main():
    _env_oku()

    token_reymen = os.environ.get("REYMEN_BOT_TOKEN", "").strip()
    token_kiral38 = os.environ.get("KIRAL38_BOT_TOKEN", "").strip()

    if not token_reymen and not token_kiral38:
        print("Hicbir bot token bulunamadi.")
        sys.exit(1)

    proje_kok = Path(__file__).parent.resolve()
    ai_bot_py = str(proje_kok / "telegram_bot" / "ai_bot.py")
    processes = []

    # @ReYMeN_ReYMeNbot
    if token_reymen:
        env = {
            **os.environ,
            "BOT_TOKEN": token_reymen,
            "BOT_AD": "@ReYMeN_ReYMeNbot",
        }
        p = subprocess.Popen(
            [sys.executable, ai_bot_py],
            cwd=str(proje_kok),
            env=env,
            creationflags=_CREATE_NO_WINDOW,
        )
        processes.append(("@ReYMeN_ReYMeNbot", p))
        print(f"@ReYMeN_ReYMeNbot baslatildi (PID: {p.pid})")
    else:
        print("[UYARI] @ReYMeN_ReYMeNbot token bulunamadi!")

    # @Kiral38bot
    if token_kiral38:
        env = {
            **os.environ,
            "BOT_TOKEN": token_kiral38,
            "BOT_AD": "@Kiral38bot",
        }
        p = subprocess.Popen(
            [sys.executable, ai_bot_py],
            cwd=str(proje_kok),
            env=env,
            creationflags=_CREATE_NO_WINDOW,
        )
        processes.append(("@Kiral38bot", p))
        print(f"@Kiral38bot baslatildi (PID: {p.pid})")
    else:
        print("[UYARI] @Kiral38bot token bulunamadi!")

    if not processes:
        print("Hicbir bot baslatilamadi.")
        sys.exit(1)

    print(f"\n{len(processes)} bot calisiyor. Ctrl+C ile durdur.")
    try:
        for ad, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nDurduruluyor...")
        for ad, p in processes:
            p.terminate()
        print("Durduruldu.")


if __name__ == "__main__":
    main()
