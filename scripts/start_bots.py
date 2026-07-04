"""ReYMeN Bot Launcher — İki botu aynı anda başlatır"""

import os, subprocess, sys, time
from pathlib import Path

BASE = Path(r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan")
ENV = BASE / "telegram_bot" / ".env"


def env_oku(key):
    """.env'den değer oku"""
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()
    return ""


def main():
    t1 = env_oku("BOT_TOKEN")
    t2 = env_oku("KIRAL38_TOKEN")
    a1 = env_oku("BOT_AD")
    a2 = env_oku("KIRAL38_AD")

    procs = []
    for token, ad in [(t1, a1), (t2, a2)]:
        if token and not token.startswith("***"):
            env = {**os.environ, "BOT_TOKEN": token, "BOT_AD": ad}
            p = subprocess.Popen(
                [sys.executable, str(BASE / "telegram_bot" / "ai_bot.py")],
                cwd=str(BASE),
                env=env,
            )
            procs.append((ad, p))
            print(f"✅ {ad} baslatildi (pid={p.pid})")
            time.sleep(2)

    if not procs:
        print("❌ Hicbir bot baslatilamadi")
        return 1

    print(f"\n{len(procs)} bot calisiyor. Ctrl+C ile durdur.")
    try:
        for ad, p in procs:
            p.wait()
    except KeyboardInterrupt:
        for ad, p in procs:
            p.terminate()
            print(f"⏹ {ad} durduruldu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
