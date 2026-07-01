#!/usr/bin/env python3
"""
ReYMeN Proaktif Bakım Script'i — 8 önlem tek pakette.

Ne yapar:
1. Config drift dedektörü — 3 config.yaml karşılaştır
2. Gateway watchdog — default + reymen 409/çökme koruması
3. SOUL.md master sync — master SOUL.md'yi 3 profile kopyala
4. state.db prune — 30 gün eski session'ları temizle
5. MEMORY.md sync — 3 profil MEMORY.md'yi eşitle
6. Haftalık durum raporu (sadece Pazar)
7. Config template doğrulama
8. Gateway health kontrol

Çalışma: her 30 dakikada bir cron job ile (haftalık rapor Pazar 09:00)
"""

import os
import re
import json
import shutil
import time
import subprocess
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# --- Konfigürasyon ---
HOME = Path.home()
HERMES_PROFILLER = HOME / "AppData/Local/hermes/profiles"
PROFILER = ["default", "reymen", "kiral38"]
MASTER_SOUL = HOME / "Desktop/Reymen Proje/ReYMeN-Ajan/SOUL.md"
PROJE_KOK = HOME / "Desktop/Reymen Proje/ReYMeN-Ajan"
HERMES_BIN = str(HOME / "AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe")
STATE_DB_KORU_GUN = 30  # 30 günden eski session'ları temizle
_SESSIZ = True  # Müdahale yoksa sessiz

# --- Loglama ---
def log(msg):
    if not _SESSIZ:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Bakim] {msg}")


def process_yasiyor(pid):
    try:
        r = subprocess.run(["tasklist", "//FI", f"PID eq {pid}"],
                          capture_output=True, text=True, timeout=5)
        return "No tasks" not in r.stdout and pid > 0
    except:
        return False


def process_oldur(pid):
    try:
        subprocess.run(["taskkill", "//PID", str(pid), "//F"],
                       capture_output=True, timeout=5)
        return True
    except:
        return False


# ========== 1. CONFIG DRIFT DEDEKTÖRÜ ==========
def config_drift_kontrol():
    """3 config.yaml'ı karşılaştır, kritik farkları bul"""
    global _SESSIZ
    anahtarlar = ["model.default", "model.provider", "display.skin",
                  "approvals.mode", "terminal.cwd", "web.backend",
                  "skills.external_dirs"]
    sonuc = {}

    for p in PROFILER:
        config_yol = HERMES_PROFILLER / p / "config.yaml"
        if not config_yol.exists():
            sonuc[p] = {}
            continue
        icerik = config_yol.read_text(encoding="utf-8")
        cfg = {}
        # Basit anahtar-değer tarama
        for anahtar in anahtarlar:
            katmanlar = anahtar.split(".")
            pattern = katmanlar[-1]
            eslesme = re.search(rf"^\s*{pattern}:\s*(.+)$", icerik, re.MULTILINE)
            cfg[anahtar] = eslesme.group(1).strip() if eslesme else "?"
        sonuc[p] = cfg

    # Karşılaştır
    farklar = []
    for anahtar in anahtarlar:
        degerler = set()
        for p in PROFILER:
            if p in sonuc and anahtar in sonuc[p]:
                degerler.add(sonuc[p][anahtar])
        if len(degerler) > 1:
            farklar.append(anahtar)

    if farklar:
        _SESSIZ = False
        log(f"⚠️ Config drift tespit edildi: {', '.join(farklar)}")
        for p in PROFILER:
            if p in sonuc:
                driftli = [f"{a}={sonuc[p].get(a,'?')}" for a in farklar]
                log(f"   {p}: {', '.join(driftli)}")

    return len(farklar) == 0


# ========== 2. GATEWAY WATCHDOG ==========
def gateway_watchdog(profil):
    """Tek profil için watchdog — kiral38'deki pattern"""
    global _SESSIZ
    profil_yol = HERMES_PROFILLER / profil

    # Gateway down mı?
    pid_dosya = profil_yol / "gateway.pid"
    down = True
    if pid_dosya.exists():
        try:
            data = json.loads(pid_dosya.read_text(encoding="utf-8"))
            pid = data.get("pid", 0)
            if pid and process_yasiyor(pid):
                down = False
        except:
            pass

    # 409 Conflict say
    gateway_log = profil_yol / "logs/gateway.log"
    _409_say = 0
    if gateway_log.exists():
        kesim = datetime.now() - timedelta(minutes=30)
        for satir in gateway_log.read_text(encoding="utf-8", errors="ignore").split("\n"):
            eslesme = re.match(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", satir)
            if eslesme:
                try:
                    satir_zaman = datetime.strptime(eslesme.group(1), "%Y-%m-%d %H:%M:%S")
                    if satir_zaman < kesim:
                        continue
                except:
                    continue
            if "409" in satir or "Conflict" in satir:
                _409_say += 1

    mudahale = False
    if down:
        mudahale = True
    elif _409_say >= 10:
        mudahale = True

    if mudahale:
        _SESSIZ = False
        log(f"⚠️ {profil}: Mudahale gerekli (down={down}, 409={_409_say})")

        # Bayat lock temizle
        for f in ["gateway.lock", "gateway.pid"]:
            dosya = profil_yol / f
            if dosya.exists():
                try:
                    dosya.unlink()
                except:
                    pass
        for sfx in ["-shm", "-wal"]:
            dosya = profil_yol / f"state.db{sfx}"
            if dosya.exists():
                try:
                    dosya.unlink()
                except:
                    pass

        # Gateway restart
        subprocess.run([
            "cmd", "//c", "start", "/MIN",
            HERMES_BIN, "-p", profil, "gateway", "restart"
        ], capture_output=True, timeout=10)
        log(f"✅ {profil}: Gateway restart gonderildi")

    return mudahale


# ========== 3. SOUL.md MASTER SYNC ==========
def soul_sync():
    """Master SOUL.md'yi 3 profile kopyala (farklıysa)"""
    global _SESSIZ
    if not MASTER_SOUL.exists():
        return False

    master_icerik = MASTER_SOUL.read_text(encoding="utf-8")
    master_hash = hash(master_icerik)
    guncellenen = 0

    for p in PROFILER:
        hedef = HERMES_PROFILLER / p / "SOUL.md"
        if hedef.exists():
            mevcut = hedef.read_text(encoding="utf-8")
            if hash(mevcut) != master_hash:
                hedef.write_text(master_icerik, encoding="utf-8")
                guncellenen += 1
        else:
            hedef.write_text(master_icerik, encoding="utf-8")
            guncellenen += 1

    if guncellenen > 0:
        _SESSIZ = False
        log(f"✅ SOUL.md sync: {guncellenen} profil guncellendi")

    return guncellenen


# ========== 4. STATE.DB PRUNE ==========
def state_db_prune(profil):
    """30 günden eski session'ları temizle"""
    db_yol = HERMES_PROFILLER / profil / "state.db"
    if not db_yol.exists():
        return 0

    kesim_tarih = (datetime.now() - timedelta(days=STATE_DB_KORU_GUN)).isoformat()
    try:
        conn = sqlite3.connect(str(db_yol), timeout=5)
        cur = conn.cursor()
        # Session tablosu var mı?
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablolar = [r[0] for r in cur.fetchall()]

        silinen = 0
        if "sessions" in tablolar:
            cur.execute("SELECT COUNT(*) FROM sessions")
            once = cur.fetchone()[0]
            cur.execute("DELETE FROM sessions WHERE created_at < ?", (kesim_tarih,))
            conn.commit()
            sonra = cur.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            silinen = once - sonra

        conn.close()
        if silinen > 0:
            global _SESSIZ
            _SESSIZ = False
            log(f"🧹 {profil}: {silinen} eski session temizlendi (state.db)")
        return silinen
    except Exception as e:
        return 0


# ========== 5. MEMORY.md SYNC ==========
def memory_sync():
    """3 profil arasında MEMORY.md içeriğini eşitle"""
    global _SESSIZ

    # En güncel MEMORY.md'yi bul (son değiştirilme tarihine göre)
    en_guncel = None
    en_guncel_icerik = ""
    en_guncel_zaman = 0

    for p in PROFILER:
        mem_yol = HERMES_PROFILLER / p / "MEMORY.md"
        if mem_yol.exists():
            mtime = mem_yol.stat().st_mtime
            icerik = mem_yol.read_text(encoding="utf-8")
            if mtime > en_guncel_zaman and len(icerik) > 0:
                en_guncel = p
                en_guncel_icerik = icerik
                en_guncel_zaman = mtime

    # USER.md için de aynı
    en_guncel_user = None
    en_guncel_user_icerik = ""
    en_guncel_user_zaman = 0

    for p in PROFILER:
        usr_yol = HERMES_PROFILLER / p / "USER.md"
        if usr_yol.exists():
            mtime = usr_yol.stat().st_mtime
            icerik = usr_yol.read_text(encoding="utf-8")
            if mtime > en_guncel_user_zaman and len(icerik) > 0:
                en_guncel_user = p
                en_guncel_user_icerik = icerik
                en_guncel_user_zaman = mtime

    guncellenen = 0

    # MEMORY.md sync
    if en_guncel_icerik:
        for p in PROFILER:
            hedef = HERMES_PROFILLER / p / "MEMORY.md"
            if not hedef.exists() or hedef.read_text(encoding="utf-8") != en_guncel_icerik:
                hedef.write_text(en_guncel_icerik, encoding="utf-8")
                guncellenen += 1

    # USER.md sync
    if en_guncel_user_icerik:
        for p in PROFILER:
            hedef = HERMES_PROFILLER / p / "USER.md"
            if not hedef.exists() or hedef.read_text(encoding="utf-8") != en_guncel_user_icerik:
                hedef.write_text(en_guncel_user_icerik, encoding="utf-8")
                guncellenen += 1

    if guncellenen > 0:
        _SESSIZ = False
        log(f"✅ Memory sync: {guncellenen} dosya guncellendi")

    return guncellenen


# ========== 6. HAFTALIK DURUM RAPORU ==========
def haftalik_rapor():
    """Pazar günü çalışır, 3 bot'un durum özetini çıkarır"""
    bugun = datetime.now()
    if bugun.weekday() != 6:  # Pazar = 6
        return

    global _SESSIZ
    _SESSIZ = False  # Rapor her zaman gösterilir

    print(f"\n{'='*60}")
    print(f"📊 HAFTALIK BOT DURUM RAPORU — {bugun.strftime('%d %B %Y')}")
    print(f"{'='*60}")

    for p in PROFILER:
        profil_yol = HERMES_PROFILLER / p

        # SOUL.md
        soul = profil_yol / "SOUL.md"
        soul_boyut = len(soul.read_text(encoding="utf-8")) if soul.exists() else 0

        # MEMORY.md
        mem = profil_yol / "MEMORY.md"
        mem_boyut = len(mem.read_text(encoding="utf-8")) if mem.exists() else 0

        # state.db
        db = profil_yol / "state.db"
        db_boyut = db.stat().st_size // 1024 if db.exists() else 0

        # Gateway state
        gs = profil_yol / "gateway_state.json"
        gateway_durum = "?"
        if gs.exists():
            try:
                data = json.loads(gs.read_text(encoding="utf-8"))
                gateway_durum = data.get("gateway_state", "?")
            except:
                pass

        # Process kontrol
        pid_dosya = profil_yol / "gateway.pid"
        process_aktif = "❌"
        if pid_dosya.exists():
            try:
                data = json.loads(pid_dosya.read_text(encoding="utf-8"))
                pid = data.get("pid", 0)
                if pid and process_yasiyor(pid):
                    process_aktif = "✅"
            except:
                pass

        print(f"\n📌 {p}")
        print(f"   SOUL.md: {soul_boyut}b | MEMORY: {mem_boyut}b | state.db: {db_boyut}KB")
        print(f"   Gateway: {gateway_durum} | Process: {process_aktif}")

    print(f"\n{'='*60}\n")


# ========== 7. CONFIG TEMPLATE DOĞRULAMA ==========
def config_template_dogrula():
    """3 config.yaml'ın gerekli alanları içerdiğini doğrula"""
    global _SESSIZ
    gerekli = ["model.default", "model.provider", "display.language",
               "terminal.cwd", "approvals.mode"]
    sorunlar = []

    for p in PROFILER:
        config_yol = HERMES_PROFILLER / p / "config.yaml"
        if not config_yol.exists():
            sorunlar.append(f"{p}: config.yaml YOK")
            continue
        icerik = config_yol.read_text(encoding="utf-8")
        for alan in gerekli:
            katmanlar = alan.split(".")
            if not re.search(rf"^\s*{katmanlar[-1]}:", icerik, re.MULTILINE):
                sorunlar.append(f"{p}: {alan} eksik")

    if sorunlar:
        _SESSIZ = False
        for s in sorunlar:
            log(f"⚠️ Config template: {s}")

    return len(sorunlar) == 0


# ========== 8. GATEWAY HEALTH ==========
def gateway_health():
    """3 gateway'in sağlık durumunu kontrol et"""
    global _SESSIZ
    sorunlu = []

    for p in PROFILER:
        profil_yol = HERMES_PROFILLER / p
        pid_dosya = profil_yol / "gateway.pid"
        state_dosya = profil_yol / "gateway_state.json"

        # 1. PID dosyası var mı?
        if not pid_dosya.exists():
            sorunlu.append(f"{p}: gateway.pid YOK")
            continue

        # 2. Process yaşıyor mu?
        try:
            data = json.loads(pid_dosya.read_text(encoding="utf-8"))
            pid = data.get("pid", 0)
            if not process_yasiyor(pid):
                sorunlu.append(f"{p}: PID {pid} olU")
                continue
        except:
            sorunlu.append(f"{p}: PID okunamadi")
            continue

        # 3. State dosyası güncel mi?
        if state_dosya.exists():
            try:
                data = json.loads(state_dosya.read_text(encoding="utf-8"))
                state = data.get("gateway_state", "")
                if state != "running":
                    sorunlu.append(f"{p}: state={state}")
                # updated_at 5 dk'dan eski mi?
                updated = data.get("updated_at", "")
                if updated:
                    try:
                        up_time = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                        if datetime.now().astimezone() - up_time > timedelta(minutes=5):
                            sorunlu.append(f"{p}: state guncel degil ({updated})")
                    except:
                        pass
            except:
                sorunlu.append(f"{p}: state dosyasi bozuk")

    if sorunlu:
        _SESSIZ = False
        for s in sorunlu:
            log(f"🚨 Health: {s}")

    return len(sorunlu) == 0


# ========== ANA DÖNGÜ ==========
def ana():
    global _SESSIZ
    _SESSIZ = True  # Varsayılan sessiz

    basla = time.time()

    # 6. Haftalık rapor (Pazar günü)
    haftalik_rapor()

    # 1. Config drift
    config_drift_kontrol()

    # 8. Gateway health
    gateway_health()

    # 2. Gateway watchdog (tüm profiller)
    for p in PROFILER:
        gateway_watchdog(p)

    # 3. SOUL.md sync
    soul_sync()

    # 5. MEMORY.md sync
    memory_sync()

    # 4. state.db prune
    for p in PROFILER:
        state_db_prune(p)

    # 7. Config template doğrulama
    config_template_dogrula()

    gecen = time.time() - basla

    if not _SESSIZ:
        log(f"✅ Bakim tamam ({gecen:.1f}s)")
    else:
        # Sessiz mod: hiçbir şey yazma — cron no_agent=True sessiz kalır
        pass


if __name__ == "__main__":
    try:
        ana()
    except Exception as e:
        print(f"[HATA] Bakim scripti: {e}")
        import traceback
        traceback.print_exc()
