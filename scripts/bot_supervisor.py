"""bot_supervisor.py — ReYMeN Bot Supervisor.
3 bot'u 3 farkli profil ile Gateway uzerinden baslatir.

Kullanim:
    python bot_supervisor.py              # 3 botu baslat (supervisor)
    python bot_supervisor.py --once       # Tek seferlik baslat
    python bot_supervisor.py --stop       # Tum botlari durdur
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SUPERVISOR] %(message)s",
)
log = logging.getLogger("supervisor")

PROJE_KOK = Path(__file__).resolve().parent.parent  # ReYMeN-Ajan/
HERMES_BASE = Path.home() / "AppData" / "Local" / "hermes" / "profiles"

# Hermes CLI yolu
_HERMES_CLI = str(
    Path.home()
    / "AppData"
    / "Local"
    / "hermes"
    / "hermes-agent"
    / "venv"
    / "Scripts"
    / "hermes.exe"
)

BOTLAR = [
    {"ad": "Pasa_38", "profil": "default"},
    {"ad": "Kiral38", "profil": "kiral38"},
    # ReYMeN_Bot ayri bir Gateway ile calisir — bu supervisor onu yonetmez
]


class BotYonetici:
    """Tek bir bot process'ini Gateway uzerinden yonetir + crash'te restart."""

    def __init__(self, bot_bilgi: dict):
        self.ad = bot_bilgi["ad"]
        self.profil = bot_bilgi["profil"]
        self.process = None
        self.durduruldu = False

    def baslat(self):
        """Bot'u Gateway uzerinden baslat (bypass yok)."""
        if self.process and self.process.poll() is None:
            log.info("[%s] Zaten calisiyor (PID %d)", self.ad, self.process.pid)
            return True

        hermes = _HERMES_CLI
        if not Path(hermes).exists():
            hermes = "hermes"  # PATH'te ara

        log.info(
            "[%s] Baslatiliyor... (hermes -p %s gateway run --replace)",
            self.ad,
            self.profil,
        )
        self.process = subprocess.Popen(
            [hermes, "-p", self.profil, "gateway", "run", "--replace"],
            env=os.environ.copy(),
            cwd=str(PROJE_KOK),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Log dinleme thread'i
        def _log_dinle():
            for satir in self.process.stdout:
                if self.durduruldu:
                    break
                print(f"[{self.ad}] {satir.decode('utf-8', errors='replace').strip()}")

        Thread(target=_log_dinle, daemon=True).start()
        return True

    def durdur(self):
        """Bot'u durdur."""
        self.durduruldu = True
        if self.process and self.process.poll() is None:
            log.info("[%s] Durduruluyor...", self.ad)
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            log.info("[%s] Durduruldu.", self.ad)

    def restart(self):
        """Bot'u yeniden baslat."""
        self.durdur()
        time.sleep(2)
        self.durduruldu = False
        return self.baslat()


def supervisor():
    """Ana supervisor dongusu — botlari Gateway uzerinden yonetir."""
    yoneticiler = [BotYonetici(b) for b in BOTLAR]

    def _sinyal_handler(sig, frame):
        log.info("Sinyal alindi, botlar durduruluyor...")
        for y in yoneticiler:
            y.durdur()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sinyal_handler)
    signal.signal(signal.SIGTERM, _sinyal_handler)

    # Tum botlari baslat
    for y in yoneticiler:
        y.baslat()
        time.sleep(1)

    log.info("=" * 50)
    log.info("2 bot Gateway uzerinden baslatildi. Supervisor aktif.")
    log.info("Durdurmak icin: Ctrl+C")
    log.info("=" * 50)

    # Crash kontrol dongusu
    while True:
        time.sleep(5)
        for y in yoneticiler:
            if y.durduruldu:
                continue
            if y.process and y.process.poll() is not None:
                log.warning(
                    "[%s] Crash! (exit: %d) 5sn sonra restart...",
                    y.ad,
                    y.process.returncode,
                )
                time.sleep(5)
                y.baslat()


def main():
    if "--stop" in sys.argv:
        import subprocess as sp

        # Gateway process'lerini bul ve oldur
        result = sp.run(
            ["tasklist", "/fi", "imagename eq hermes.exe", "/v", "/fo", "csv"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        killed = 0
        for line in result.stdout.split("\n"):
            if "gateway" in line.lower() or "hermes.exe" in line:
                parts = line.split(",")
                if len(parts) >= 2:
                    pid = parts[1].strip().strip('"')
                    if pid.isdigit():
                        sp.run(
                            ["taskkill", "/f", "/pid", pid],
                            capture_output=True,
                            timeout=5,
                        )
                        killed += 1
                        print(f"  PID {pid} olduruldu")
        print(f"Toplam {killed} Gateway process'i durduruldu.")
        return

    if "--once" in sys.argv:
        for bot in BOTLAR:
            hermes = _HERMES_CLI
            if not Path(hermes).exists():
                hermes = "hermes"
            log.info(
                "[%s] Baslatiliyor... (hermes -p %s gateway run --replace)",
                bot["ad"],
                bot["profil"],
            )
            subprocess.Popen(
                [hermes, "-p", bot["profil"], "gateway", "run", "--replace"],
                env=os.environ.copy(),
                cwd=str(PROJE_KOK),
                stdout=open(
                    PROJE_KOK / ".ReYMeN" / f"{bot['ad'].lower()}_bot.log", "w"
                ),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            )
            print(f"[{bot['ad']}] Baslatildi (arka planda).")
            time.sleep(2)
        return

    supervisor()


if __name__ == "__main__":
    main()
