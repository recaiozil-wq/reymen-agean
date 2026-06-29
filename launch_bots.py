# -*- coding: utf-8 -*-
"""ReYMeN bot'larini arka planda baslatir ve cikar.

run_reymen_bots.py'den farki: child process'leri beklemez, hemen cikar.
ScheduledTask / VBS / baslangic icin uygundur.
"""
import os
import subprocess
import sys
from pathlib import Path


def main():
    proje_kok = Path(__file__).parent.resolve()
    ai_bot_py = str(proje_kok / "telegram_bot" / "ai_bot.py")
    env_file = proje_kok / ".env"

    # .env'den token'lari oku
    tokens = {}
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            val = val.strip().strip("'\"")
            if val and not val.startswith("***"):
                tokens[key] = val

    botlar = [
        ("@ReYMeN_ReYMeNbot", tokens.get("REYMEN_BOT_TOKEN", "")),
        ("@Kiral38bot", tokens.get("KIRAL38_BOT_TOKEN", "")),
    ]

    for ad, token in botlar:
        if not token:
            print(f"[UYARI] {ad} token bulunamadi, atlaniyor.")
            continue
        env = os.environ.copy()
        env["BOT_TOKEN"] = token
        env["BOT_AD"] = ad
        env["PYTHONUNBUFFERED"] = "1"
        logfile = proje_kok / ".ReYMeN" / f"{ad.replace('@','')}_bot.log"
        subprocess.Popen(
            [sys.executable, ai_bot_py],
            cwd=str(proje_kok),
            env=env,
            stdout=open(str(logfile), "w"),
            stderr=subprocess.STDOUT,
        )
        print(f"{ad} baslatildi. Log: {logfile}")

    print("Bot'lar arka planda calisiyor.")


if __name__ == "__main__":
    main()
