# -*- coding: utf-8 -*-
"""cli_commands.py â€” ReYMeN CLI alt komutlarÄ± (gateway, config, session, doctor, backup)."""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_KOK = Path(__file__).parent.parent.parent.resolve()

# â”€â”€ Renkler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_R = "\033[0m"
_C = "\033[96m"
_G = "\033[92m"
_Y = "\033[93m"
_B = "\033[94m"
_M = "\033[95m"
_D = "\033[2m"
_RED = "\033[91m"


def _c(t):
    return f"{_C}{t}{_R}"


def _g(t):
    return f"{_G}{t}{_R}"


def _y(t):
    return f"{_Y}{t}{_R}"


def _d(t):
    return f"{_D}{t}{_R}"


def _r(t):
    return f"{_RED}{t}{_R}"


# â”€â”€ GATEWAY (ReYMeN bagimsiz) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cmd_gateway(args) -> int:
    """Gateway yönetimi â€” ReYMeN kendi gateway sistemi."""
    alt = args.sub or "status"
    profil = getattr(args, "profil", None) or "reymen"

    if alt == "list":
        profiller = ["default", "reymen", "kiral38"]
        for p in profiller:
            _gateway_durum(p)
        return 0

    if alt == "status":
        return _gateway_durum(profil)
    if alt == "start":
        return _gateway_baslat(profil)
    if alt == "stop":
        return _gateway_durdur(profil)
    if alt == "restart":
        _gateway_durdur(profil)
        time.sleep(1)
        return _gateway_baslat(profil)

    print(f"  {_r('[HATA]')} Bilinmeyen gateway alt komutu: {alt}")
    return 1


def _gateway_durum(profil: str) -> int:
    """ReYMeN gateway durumunu kontrol et â€” process + PID bazli."""
    # 1. Process kontrolu (reymen gateway / telegram_bot)
    try:
        # Telegram bot process'i var mi?
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # reymen ile ilgili python process'lerini bul
        reymen_pids = []
        for line in r.stdout.splitlines():
            if "reymen" in line.lower() or "telegram" in line.lower():
                parts = line.split(",")
                if len(parts) >= 2:
                    pid = parts[1].strip('"')
                    reymen_pids.append(pid)

        if reymen_pids:
            print(
                f"  {_c('âŠ¡')} {_g(profil):<10} {_g('calisiyor')} PID: {', '.join(reymen_pids[:3])}"
            )
        else:
            print(f"  {_c('âŠ¡')} {_y(profil):<10} {_d('kapali')}")
        return 0
    except Exception as e:
        print(f"  {_c('âŠ¡')} {_y(profil):<10} {_d('kontrol basarisiz')}")
        return 1


def _gateway_baslat(profil: str) -> int:
    """ReYMeN gateway'ini baslat â€” dogrudan Python process'i olarak."""
    try:
        # reymen_launcher.py uzerinden gateway baslat
        reymen_bin = str(_KOK / "reymen_launcher.py")
        reymen_python = _KOK / ".venv_reymen" / "Scripts" / "python.exe"
        if not reymen_python.exists():
            import sys as _sys
            reymen_python = _sys.executable
        cmd = f'start /MIN cmd /c ""{reymen_python}" "{reymen_bin}" --profil {profil} gateway start"'
        subprocess.Popen(cmd, shell=True)
        print(f"  {_g('âœ“')} {profil} gateway baslatiliyor...")
        return 0
    except Exception as e:
        print(f"  {_r('[HATA]')} {e}")
        return 1


def _gateway_durdur(profil: str) -> int:
    """ReYMeN gateway process'lerini durdur."""
    try:
        # reymen ile ilgili python process'lerini bul ve oldur
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in r.stdout.splitlines():
            if "reymen" in line.lower() or "telegram" in line.lower():
                parts = line.split(",")
                if len(parts) >= 2:
                    pid = parts[1].strip('"')
                    subprocess.run(
                        ["taskkill", "/F", "/PID", pid], capture_output=True, timeout=3
                    )
        print(f"  {_g('âœ“')} Gateway process'leri durduruldu.")
        return 0
    except Exception as e:
        print(f"  {_y('!')} Durdurma hatasi: {e}")
        return 1


# â”€â”€ CONFIG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cmd_config(args) -> int:
    """Config goruntuleme."""
    alt = getattr(args, "sub", None) or "show"

    if alt == "show":
        return _config_goster()
    if alt == "path":
        print(str(_KOK / "config.yaml"))
        return 0
    if alt == "env":
        return _config_env_goster()

    print(f"  {_r('[HATA]')} Bilinmeyen config alt komutu: {alt}")
    return 1


def _config_goster() -> int:
    yaml_yol = _KOK / "config.yaml"
    if not yaml_yol.exists():
        print(f"  {_y('!')} config.yaml bulunamadi: {yaml_yol}")
        return 1
    icerik = yaml_yol.read_text(encoding="utf-8", errors="replace")
    # Hassas bilgileri temizle
    import re

    icerik = re.sub(
        r'(api_key|token|password|secret):\s*["\']?[^"\'\n]+["\']?',
        r"\1: ***",
        icerik,
        flags=re.IGNORECASE,
    )
    print(icerik)
    return 0


def _config_env_goster() -> int:
    """Aktif .evn degiskenlerini goster (sifreleri gizle)."""
    import re

    env_yol = _KOK / ".env"
    if not env_yol.exists():
        print(f"  {_y('!')} .env bulunamadi")
        return 1
    for satir in env_yol.read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#"):
            continue
        if "=" in satir:
            key, val = satir.split("=", 1)
            if any(
                k in key.upper() for k in ["API_KEY", "TOKEN", "SECRET", "PASSWORD"]
            ):
                val = "***" if val else ""
            print(f"  {key}={val}")
    return 0


# â”€â”€ SESSION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cmd_session(args) -> int:
    """Session listeleme."""
    alt = getattr(args, "sub", None) or "list"

    if alt == "list":
        return _session_listele(getattr(args, "limit", 10))
    if alt == "last":
        return _session_son()

    print(f"  {_r('[HATA]')} Bilinmeyen session alt komutu: {alt}")
    return 1


def _session_listele(limit: int = 10) -> int:
    """~/.reymen/reymen/state.db'den son session'lari listele."""
    import sqlite3

    db_yollari = [
        _KOK / ".ReYMeN" / "state.db",
        Path.home()
        / "AppData"
        / "Local"
        / "reymen"
        / "profiles"
        / "reymen"
        / "state.db",
        Path.home() / "AppData" / "Local" / "reymen" / "state.db",
    ]
    for db in db_yollari:
        if db.exists():
            try:
                conn = sqlite3.connect(str(db))
                cur = conn.cursor()
                cur.execute(
                    "SELECT session_id, created_at, message_count FROM sessions "
                    "ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )
                rows = cur.fetchall()
                conn.close()
                if rows:
                    for sid, ts, cnt in rows:
                        print(
                            f"  {_c('â—ˆ')} {_g(sid[:12]):<14} "
                            f"{_d(str(ts)[:19]):<22} {cnt} mesaj"
                        )
                    return 0
            except Exception as e:
                logger.warning("[CliCommands] except Exception (L209): %s", Exception)
                pass

    print(f"  {_y('!')} Session kaydi bulunamadi")
    return 1


def _session_son() -> int:
    return _session_listele(1)


# â”€â”€ DOCTOR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def cmd_doctor(args) -> int:
    """Sistem saglik kontrolu."""
    sorun = 0
    print(f"\n  {_c('ReYMeN Sistem Kontrolü')}")
    print(f"  {_d('â”€'*50)}")

    # 1. Proje dizini
    if _KOK.exists():
        print(f"  {_g('âœ“')} Proje: {_KOK}")
    else:
        print(f"  {_r('âœ—')} Proje bulunamadi")
        sorun += 1

    # 2. .env
    env = _KOK / ".env"
    print(
        f"  {_g('âœ“') if env.exists() else _r('âœ—')} .env: {'var' if env.exists() else 'YOK'}"
    )

    # 3. config.yaml
    yaml = _KOK / "config.yaml"
    print(
        f"  {_g('âœ“') if yaml.exists() else _y('?')} config.yaml: {'var' if yaml.exists() else 'yok'}"
    )

    # 4. API key test
    import http.client as _hc

    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if deepseek_key:
        try:
            conn = _hc.HTTPSConnection("api.deepseek.com", timeout=3)
            conn.request(
                "GET", "/v1/models", headers={"Authorization": f"Bearer {deepseek_key}"}
            )
            resp = conn.getresponse()
            ok = resp.status == 200
            conn.close()
            print(
                f"  {_g('âœ“') if ok else _r('âœ—')} DeepSeek API: {'calisiyor' if ok else f'hata {resp.status}'}"
            )
        except Exception as e:
            print(f"  {_r('âœ—')} DeepSeek API: {_d(str(e)[:40])}")
            sorun += 1
    else:
        print(f"  {_r('âœ—')} DeepSeek API: KEY YOK")
        sorun += 1

    # 5. SOUL.md
    soul = _KOK / "SOUL.md"
    if soul.exists():
        s_len = len(soul.read_text(encoding="utf-8"))
        print(f"  {_g('âœ“')} SOUL.md: {s_len} karakter")
    else:
        print(f"  {_y('?')} SOUL.md: yok")

    # 6. ConversationLoop
    try:
        from reymen.cereyan.conversation_loop import ConversationLoop

        print(f"  {_g('âœ“')} ConversationLoop: hazir")
    except Exception as e:
        print(f"  {_r('âœ—')} ConversationLoop: {e}")
        sorun += 1

    # 7. ReYMeN binary
    reymen = str(_KOK / "reymen_launcher.py")
    print(
        f"  {_g('âœ“') if os.path.exists(reymen) else _y('?')} Launcher: {'reymen_launcher.py' if os.path.exists(reymen) else 'bulunamadi'}"
    )

    print(f"  {_d('â”€'*50)}")
    if sorun:
        print(f"  {_r(f'{sorun} sorun bulundu')}")
    else:
        print(f"  {_g('âœ“ Tum kontroller basarili')}")
    print()
    return sorun


# â”€â”€ BACKUP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ── WEB (Hermes Studio) ─────────────────────────────────────────────────────
def cmd_web(args=None) -> int:
    """Hermes Studio'yu başlat (EKKOLearnAI/hermes-studio)."""
    import subprocess as _sp
    import time as _time
    import shutil as _shutil

    # npm global bin yolunu bul
    _npm_bin = _shutil.which("hermes-web-ui.cmd") or _shutil.which("hermes-web-ui")
    if not _npm_bin:
        _npm_bin = _shutil.which("hermes-web-ui.cmd", path=os.environ.get("PATH","") + os.pathsep + os.path.expanduser("~/AppData/Roaming/npm"))
    if not _npm_bin:
        print(f"  {_r('[HATA]')} hermes-web-ui bulunamadi — 'npm install -g hermes-web-ui' ile kur")
        return 1

    # 1. Hermes Studio çalışıyor mu kontrol et
    r = _sp.run(
        [_npm_bin, "status"],
        capture_output=True, text=True, timeout=10, shell=False
    )

    if "is running" in r.stdout:
        print(f"  {_g('✓')} Hermes Studio zaten çalışıyor (localhost:8648)")
    else:
        print(f"  {_c('∘')} Hermes Studio başlatılıyor...")
        _sp.Popen(
            [_npm_bin, "start", "8648"],
            creationflags=_sp.CREATE_NO_WINDOW if os.name == "nt" else 0,
            stdout=_sp.DEVNULL, stderr=_sp.DEVNULL
        )
        _time.sleep(3)
        r2 = _sp.run(
            [_npm_bin, "status"],
            capture_output=True, text=True, timeout=10
        )
        if "is running" in r2.stdout:
            print(f"  {_g('✓')} Hermes Studio başlatıldı (localhost:8648)")
        else:
            print(f"  {_y('!')} Hermes Studio başlatılamadı — 'hermes-web-ui start' ile manuel dene")
            return 1

    # 2. Browser'da aç
    print(f"  {_c('∘')} Browser açılıyor...")
    try:
        _sp.run(
            ["cmd", "/c", "start", "http://localhost:8648"],
            timeout=5, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL
        )
        print(f"  {_g('✓')} http://localhost:8648 açıldı")
        print(f"  {_d('Giriş: admin / 123456')}")
        print(f"  {_d('Profiller → reymen seçeneğini kullan')}")
    except Exception:
        print(f"  {_y('!')} Browser açılamadı, manuel: http://localhost:8648")
    return 0


def cmd_backup(args) -> int:
    """Git push ile yedekle."""
    alt = getattr(args, "sub", None) or "status"

    if alt == "status":
        return _backup_durum()
    if alt == "push":
        return _backup_push()
    if alt == "log":
        return _backup_log()

    print(f"  {_r('[HATA]')} Bilinmeyen backup alt komutu")
    return 1


def _backup_durum() -> int:
    try:
        import subprocess

        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(_KOK),
            capture_output=True,
            text=True,
            timeout=10,
        )
        cikti = r.stdout.strip()
        if cikti:
            lines = cikti.splitlines()
            print(f"  {_y(f'{len(lines)}')} degisiklik bekliyor")
            for line in lines[:20]:
                print(f"    {_d(line)}")
        else:
            print(f"  {_g('âœ“')} Temiz (degisiklik yok)")
        return 0
    except Exception as e:
        print(f"  {_r('[HATA]')} {e}")
        return 1


def _backup_push() -> int:
    print(f"  {_c('âˆ˜')} Git push yapiliyor...")
    try:
        r = subprocess.run(
            ["git", "add", "-A"],
            cwd=str(_KOK),
            capture_output=True,
            text=True,
            timeout=30,
        )
        r = subprocess.run(
            ["git", "commit", "-m", f"otomatik yedek [$(date +%Y-%m-%d_%H:%M)]"],
            cwd=str(_KOK),
            capture_output=True,
            text=True,
            timeout=30,
        )
        r = subprocess.run(
            ["git", "push"], cwd=str(_KOK), capture_output=True, text=True, timeout=60
        )
        out = (r.stdout + r.stderr).strip()
        if "Everything up-to-date" in out or r.returncode == 0:
            print(f"  {_g('âœ“')} Yedeklendi")
        else:
            print(f"  {_y('!')} {out[:100]}")
        return r.returncode
    except Exception as e:
        print(f"  {_r('[HATA]')} {e}")
        return 1


def _backup_log() -> int:
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=str(_KOK),
            capture_output=True,
            text=True,
            timeout=10,
        )
        print(r.stdout.strip() or "Kayit yok")
        return 0
    except Exception as e:
        print(f"  {_r('[HATA]')} {e}")
        return 1
