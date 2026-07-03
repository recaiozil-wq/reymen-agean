"""
reymen_watchdog.py — ReYMeN Bot Watchdog (Hermes'ten Bağımsız)

Risk 2 (Reboot sonrası botlar ölür) + Risk 3 (Hermes kapalıyken watchdog çalışmaz)
ÇÖZÜMÜ: Hermes Agent'e ihtiyaç duymadan, doğrudan hermes.exe binary'sini kullanarak
botları ayakta tutar. Startup'ta başlatılır, reboot'ta otomatik çalışır.

Kontroller:
- Her 60 sn'de bir 3 bot profilini tarar
- Ölü botları yeniden başlatır
- Log dosyası 1MB'ı geçince rotate eder
"""

import subprocess
import time
import re
import os
import sys
from pathlib import Path
from datetime import datetime

# --- KONFİGÜASYON ---
PROFILER = ["default", "reymen", "kiral38"]
HERMES_BIN = str(Path.home() / "AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe")
PROJE_DIR = Path(__file__).parent.resolve()
LOG_FILE = PROJE_DIR / ".ReYMeN" / "watchdog.log"
MAX_LOG_BYTES = 1_048_576  # 1MB
CHECK_INTERVAL = 60  # saniye

# --- LOG ---
def log_yaz(msg: str):
    """Log dosyasına zaman damgalı yaz, 1MB'da rotate et."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{timestamp}] {msg}\n"

    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_BYTES:
        rotate = LOG_FILE.with_suffix(".log.1")
        LOG_FILE.rename(rotate) if not rotate.exists() else LOG_FILE.unlink()

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(satir)
    print(satir.strip())


def aktif_profiller() -> set[str]:
    """
    PowerShell ile çalışan gateway process'lerini tara.
    Hangi profillerin ayakta olduğunu döndür.
    """
    aktif = set()

    try:
        # PowerShell: Win32_Process ile komut satırını oku
        ps_cmd = (
            'Get-CimInstance Win32_Process -Filter "name=\'python.exe\' or name=\'hermes.exe\'" '
            "| Select-Object CommandLine | Format-Table -HideTableHeaders"
        )
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if "--profile" in line:
                m = re.search(r'--profile\s+(\S+)', line)
                if m:
                    aktif.add(m.group(1))

        # Fallback: tasklist ile hermes.exe var mı kontrol et
        r2 = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq hermes.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        if "hermes.exe" not in r2.stdout and not aktif:
            log_yaz("⚠️ hermes.exe tasklist'te görünmüyor, tüm profiller eksik sayılacak")

    except Exception as e:
        log_yaz(f"⚠️ Process tarama hatası: {e}")

    return aktif


def bot_baslat(profil: str) -> bool:
    """Her profil için hermes gateway başlat."""
    try:
        cmd = [HERMES_BIN, "gateway", "--profile", profil]
        log_yaz(f"🚀 Başlatılıyor: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            close_fds=True
        )
        log_yaz(f"✅ {profil} başlatıldı (PID: {process.pid})")
        return True

    except FileNotFoundError:
        log_yaz(f"❌ HERMES_BIN bulunamadı: {HERMES_BIN}")
        return False
    except Exception as e:
        log_yaz(f"❌ {profil} başlatılamadı: {e}")
        return False


def ana_dongu():
    """Ana watchdog döngüsü — her CHECK_INTERVAL saniyede bir kontrol."""
    log_yaz("=" * 50)
    log_yaz("🛡️ ReYMeN Watchdog başlatıldı")
    log_yaz(f"📁 Hermes: {HERMES_BIN}")
    log_yaz(f"📁 Proje: {PROJE_DIR}")
    log_yaz(f"⏱️ Kontrol aralığı: {CHECK_INTERVAL}s")
    log_yaz("=" * 50)

    while True:
        try:
            aktif = aktif_profiller()
            eksik = set(PROFILER) - aktif

            if eksik:
                log_yaz(f"🔴 Eksik profiller: {', '.join(sorted(eksik))}")
                for profil in sorted(eksik):
                    bot_baslat(profil)
                    time.sleep(2)  # ardışık başlatmalar arasında nefes
            else:
                log_yaz(f"🟢 Tüm profiller ayakta: {', '.join(sorted(aktif))}")

        except Exception as e:
            log_yaz(f"⚠️ Döngü hatası: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    # --- TEK INSTANCE KONTROLÜ ---
    lock_file = PROJE_DIR / ".ReYMeN" / "watchdog.lock"
    try:
        if lock_file.exists():
            pid_str = lock_file.read_text().strip()
            if pid_str:
                # Process yaşıyor mu kontrol et
                r = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid_str}", "/FO", "CSV", "/NH"],
                    capture_output=True, text=True, timeout=5
                )
                if pid_str in r.stdout:
                    print(f"⚠️ Watchdog zaten çalışıyor (PID: {pid_str}), çıkılıyor.")
                    sys.exit(0)
        lock_file.write_text(str(os.getpid()))
    except Exception:
        pass  # Lock hatası kritik değil, devam et

    try:
        ana_dongu()
    except KeyboardInterrupt:
        log_yaz("⛔ Watchdog durduruldu (Ctrl+C)")
        sys.exit(0)
