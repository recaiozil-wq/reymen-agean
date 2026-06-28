#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_watchdog.py — ReYMeN Bot Watchdog (no_agent=True)
=======================================================
ReYMeN'teki telegram_connection_watchdog.py pattern'inin ReYMeN uyarlaması.
Her 2 dakikada bir çalışır. Sessiz = bot sağlıklı.
Sadece hata bulunca çıktı verir → cron job otomatik Telegram'a iletir.

Kontrol:
1. ReYMeN bot process'i canlı mı? (bot.py PID)
2. Telegram bot token env'de var mı? (belirt, onarım yapma)

Onarım:
- Process ölü = yeniden başlat
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

# === YAPILANDIRMA ===
REYMEN_ROOT = Path(r"C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi")
REYMEN_ENV = Path(r"C:\Users\marko\AppData\Local\ReYMeN\.env")
REYMEN_ENV = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / ".env"
BOT_SCRIPT = REYMEN_ROOT / "bot.py"
PYTHON_EXE = Path(r"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe")
CHAT_ID = "6328823909"


def now_iso():
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


def check_token_ok():
    """Token .env'de duruyor mu (maskeli de olsa) kontrol et."""
    for env_path in [REYMEN_ENV, REYMEN_ENV]:
        if env_path and env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN=") and "=" in line:
                    val = line.split("=", 1)[1].strip()
                    if val and len(val) > 5:
                        return True, f"token_mevcut ({env_path.name})"
    return False, "TOKEN_YOK"


def check_bot_process():
    """ReYMeN bot process'i (bot.py) çalışıyor mu kontrol et."""
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'bot\\.py' } | "
             "Select-Object ProcessId | ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if not output or output == "null":
            return False, ["BOT_PROCESS_YOK"], None

        try:
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]
        except json.JSONDecodeError:
            return False, ["BOT_JSON_PARSE_HATASI"], None

        procs = [{"pid": p.get("ProcessId")} for p in data if p.get("ProcessId")]
        if procs:
            return True, [f"bot_pid={p['pid']}" for p in procs], procs
        return False, ["BOT_PROCESS_YOK"], None
    except subprocess.TimeoutExpired:
        return False, ["PROCESS_KONTROL_TIMEOUT"], None
    except Exception as e:
        return False, [f"PROCESS_KONTROL_HATASI: {e}"], None


def start_bot():
    """ReYMeN bot'u yeniden başlat."""
    try:
        subprocess.Popen(
            [str(PYTHON_EXE), str(BOT_SCRIPT)],
            cwd=str(REYMEN_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, "Bot baslatildi"
    except Exception as e:
        return False, f"Bot baslatilamadi: {e}"


def wait_and_verify(seconds=15):
    time.sleep(seconds)
    ok, msgs, proc_data = check_bot_process()
    if ok and proc_data:
        return True, f"Bot PID {proc_data[0]['pid']} calisiyor"
    return False, f"Bot hala calismiyor: {', '.join(msgs[:3])}"


def run_watchdog():
    problems = []
    actions = []
    ts = now_iso()

    # === ADIM 1: Bot process kontrolü ===
    proc_ok, proc_msgs, proc_data = check_bot_process()
    if proc_ok:
        for pm in proc_msgs:
            actions.append(pm)
    else:
        for pm in proc_msgs:
            problems.append(pm)

    # === ADIM 2: Token varlık kontrolü (sadece uyarı) ===
    tok_ok, tok_msg = check_token_ok()
    if not tok_ok:
        problems.append(tok_msg)

    # === KARAR: Sorun yoksa sessiz çık ===
    if not problems:
        return

    # === ONARIM ===
    alarm_lines = [
        f"⚠️ REYMEN BOT WATCHDOG [{ts}]",
        ""
    ]
    for p in problems:
        alarm_lines.append(f"  ❌ {p}")

    alarm_lines.append("")
    alarm_lines.append("🔄 Onarim basliyor...")

    process_dead = any("BOT_PROCESS" in p or "PROCESS_KONTROL" in p for p in problems)

    if process_dead:
        alarm_lines.append("  🔄 Bot processi olmus, yeniden baslatiliyor...")
        ok, msg = start_bot()
        alarm_lines.append(f"  {'✅' if ok else '❌'} {msg}")
        if ok:
            alarm_lines.append("  ⏳ 15sn bekleniyor...")
            vok, vmsg = wait_and_verify(15)
            alarm_lines.append(f"  {'✅' if vok else '❌'} Dogrulama: {vmsg}")
            if vok:
                alarm_lines.append("  ✅ Bot yeniden calisiyor")
            else:
                alarm_lines.append("  ❌ Bot baslatilamadi — manuel mudahale gerek")
    else:
        alarm_lines.append("  ⚠️ Token eksik/gecersiz — kontrol et")

    alarm_lines.append("")
    alarm_lines.append(f"[reymen-watchdog] {ts}")
    print("\n".join(alarm_lines))


if __name__ == "__main__":
    run_watchdog()
