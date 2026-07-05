#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proaktif_bakim.py â€” ReYMeN 3 profil otomatik bakÄ±m scripti.

Ã‡alÄ±ÅŸma modu: no_agent (cron ile)
  - Sorun yok â†’ sessiz (Ã§Ä±ktÄ±sÄ±z)
  - Sorun var â†’ rapor (stdout)
  - Pazar gÃ¼nÃ¼ â†’ haftalÄ±k rapor (her zaman Ã§Ä±ktÄ±)
"""

import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REYMEN = Path.home() / "AppData" / "Local" / "reymen"
PROFILLER = {
    "default": REYMEN / "profiles" / "default",
    "reymen": REYMEN / "profiles" / "reymen",
    "kiral38": REYMEN / "profiles" / "kiral38",
}
PROJE_KOK = Path(__file__).resolve().parent.parent.parent
MASTER_SOUL = PROJE_KOK / "SOUL.md"
BUGUN = datetime.now(timezone.utc)
PAZAR_MI = BUGUN.weekday() == 6  # Sunday
RAPOR = []
SESSIZ = True  # Sorun yoksa sessiz


def ekle(seviye: str, mesaj: str):
    global SESSIZ
    if seviye in ("HATA", "UYARI"):
        SESSIZ = False
    RAPOR.append(f"[{seviye}] {mesaj}")


# â”€â”€ 1. Config Drift DedektÃ¶rÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def config_drift_kontrol():
    """3 config.yaml kritik alanlarÄ±nÄ± karÅŸÄ±laÅŸtÄ±r."""
    import yaml

    anahtarlar = [
        "model",
        "fallback_providers",
        "gateway",
        "terminal",
        "web",
        "browser",
    ]
    degerler = {}
    for ad, yol in PROFILLER.items():
        cfg_yol = yol / "config.yaml"
        if not cfg_yol.exists():
            ekle("HATA", f"[1] {ad} config.yaml bulunamadi")
            continue
        try:
            with open(cfg_yol, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            degerler[ad] = {k: cfg.get(k) for k in anahtarlar if k in cfg}
        except Exception as e:
            ekle("HATA", f"[1] {ad} config.yaml okunamadi: {e}")

    if len(degerler) < 2:
        return

    ilk_ad, ilk_val = next(iter(degerler.items()))
    for ad, val in degerler.items():
        if val != ilk_val:
            farklar = []
            for k in anahtarlar:
                if val.get(k) != ilk_val.get(k):
                    farklar.append(k)
            ekle("UYARI", f"[1] Config drift: {ad} <> {ilk_ad}: {','.join(farklar)}")
            return

    ekle("BILGI", "[1] Config drift: Yok (3 profil esit)")


# â”€â”€ 2. Gateway Watchdog â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def gateway_watchdog():
    """409 + Ã§Ã¶kme korumasÄ±, lock temizle + restart."""
    for ad, yol in PROFILLER.items():
        lock = yol / "gateway.lock"
        pid = yol / "gateway.pid"

        # Lock var mÄ±?
        if not lock.exists():
            ekle("UYARI", f"[2] {ad} gateway.lock yok (bot calismiyor olabilir)")
            continue

        # PID canlÄ± mÄ±?
        if pid.exists():
            try:
                pid_str = pid.read_text().strip()
                pid_int = int(pid_str)
                # Windows'ta process var mÄ± kontrolÃ¼
                if platform.system() == "Windows":
                    r = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid_int}", "/NH"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if str(pid_int) not in r.stdout:
                        ekle(
                            "UYARI", f"[2] {ad} PID {pid_int} olmus, lock temizleniyor"
                        )
                        lock.unlink(missing_ok=True)
                        pid.unlink(missing_ok=True)
            except (ValueError, subprocess.TimeoutExpired):
                logger.warning("[fix_01_sessiz_except] Exception")

    # Debug log'da 409 kontrolÃ¼
    debug_log = PROJE_KOK / "bot_debug.log"
    if debug_log.exists():
        icerik = debug_log.read_text(encoding="utf-8", errors="ignore")
        conflict_say = icerik.count("409 Conflict")
        if conflict_say > 5:
            ekle("UYARI", f"[2] 409 Conflict tespit: {conflict_say} kez (bot tekrari)")
            # Log'u temizle
            debug_log.write_text("")

    ekle("BILGI", "[2] Gateway watchdog: Tamam")


# â”€â”€ 3. SOUL.md Master Sync â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def soul_sync():
    """Master SOUL.md'yi 3 profile otomatik kopyala."""
    if not MASTER_SOUL.exists():
        ekle("HATA", "[3] Master SOUL.md bulunamadi")
        return

    master_icerik = MASTER_SOUL.read_bytes()
    for ad, yol in PROFILLER.items():
        hedef = yol / "SOUL.md"
        if not hedef.exists():
            ekle("UYARI", f"[3] {ad} SOUL.md yok, olusturuluyor")
            shutil.copy2(MASTER_SOUL, hedef)
        elif hedef.read_bytes() != master_icerik:
            ekle("BILGI", f"[3] {ad} SOUL.md farkli, guncelleniyor")
            shutil.copy2(MASTER_SOUL, hedef)

    ekle("BILGI", "[3] SOUL.md sync: Tamam")


# â”€â”€ 4. state.db Prune â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def state_db_prune():
    """30 gÃ¼n eski session'larÄ± temizle."""
    kesim_saniye = (BUGUN - timedelta(days=30)).timestamp()

    for ad, yol in PROFILLER.items():
        db_yol = yol / "state.db"
        if not db_yol.exists():
            continue

        try:
            conn = sqlite3.connect(str(db_yol))
            c = conn.cursor()

            # Session tablosu var mÄ±?
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            if not c.fetchone():
                conn.close()
                continue

            c.execute(
                "SELECT COUNT(*) FROM sessions WHERE started_at < ?", (kesim_saniye,)
            )
            eski_sayisi = c.fetchone()[0]

            if eski_sayisi > 0:
                c.execute("DELETE FROM sessions WHERE started_at < ?", (kesim_saniye,))
                conn.commit()
                ekle("BILGI", f"[4] {ad}: {eski_sayisi} eski session temizlendi")

            # VACUUM (2 haftada bir)
            gun = BUGUN.day
            if gun % 14 == 0:
                c.execute("VACUUM")
                ekle("BILGI", f"[4] {ad}: VACUUM yapildi")

            conn.close()
        except Exception as e:
            ekle("UYARI", f"[4] {ad} state.db prune hatasi: {e}")

    ekle("BILGI", "[4] state.db prune: Tamam")


# â”€â”€ 5. MEMORY.md Sync â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def memory_sync():
    """3 profil arasÄ±nda MEMORY.md eÅŸitle (shared_memories kullan)."""
    shared = REYMEN / "shared_memories" / "MEMORY.md"
    if not shared.exists():
        ekle("BILGI", "[5] shared MEMORY.md yok, atlaniyor")
        return

    shared_icerik = shared.read_bytes()
    for ad, yol in PROFILLER.items():
        hedef = yol / "MEMORY.md"
        if not hedef.exists():
            hedef.touch()
        elif hedef.read_bytes() == shared_icerik:
            continue

        # Symlink mi kontrol et
        if hedef.is_symlink():
            continue  # Symlink zaten shared'i gÃ¶steriyor

        shutil.copy2(shared, hedef)
        ekle("BILGI", f"[5] {ad} MEMORY.md guncellendi")

    ekle("BILGI", "[5] MEMORY.md sync: Tamam")


# â”€â”€ 6. HaftalÄ±k Rapor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def haftalik_rapor():
    """Pazar gÃ¼nÃ¼ 3 bot durum Ã¶zeti."""
    if not PAZAR_MI:
        return

    global SESSIZ
    SESSIZ = False  # Pazar raporu her zaman gÃ¶ster

    ekle("RAPOR", "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    ekle("RAPOR", f"  Haftalik Bot Raporu â€” {BUGUN.strftime('%d %B %Y')}")
    ekle("RAPOR", "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")

    for ad, yol in PROFILLER.items():
        soul = yol / "SOUL.md"
        mem = yol / "MEMORY.md"
        cfg = yol / "config.yaml"
        db = yol / "state.db"
        lock = yol / "gateway.lock"

        soul_boyut = soul.stat().st_size if soul.exists() else 0
        mem_boyut = mem.stat().st_size if mem.exists() else 0
        cfg_boyut = cfg.stat().st_size if cfg.exists() else 0
        db_boyut = db.stat().st_size if db.exists() else 0
        lock_durum = "AKTIF" if lock.exists() else "PASIF"

        ekle("RAPOR", f"  [{ad}]")
        ekle("RAPOR", f"    SOUL.md: {soul_boyut}B")
        ekle("RAPOR", f"    MEMORY.md: {mem_boyut}B")
        ekle("RAPOR", f"    config.yaml: {cfg_boyut}B")
        ekle("RAPOR", f"    state.db: {db_boyut // 1024 // 1024}MB")
        ekle("RAPOR", f"    Gateway: {lock_durum}")

    ekle("RAPOR", "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")


# â”€â”€ 7. Config Template Kontrol â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def config_template_kontrol():
    """Gerekli alanlar var mÄ± diye doÄŸrula."""
    import yaml

    gerekli = {
        "model": ["default", "provider"],
        "fallback_providers": None,  # Liste olarak var olmalÄ±
        "terminal": ["cwd", "backend", "timeout"],
        "gateway": None,  # Obje olarak var olmalÄ±
    }

    for ad, yol in PROFILLER.items():
        cfg_yol = yol / "config.yaml"
        if not cfg_yol.exists():
            ekle("HATA", f"[7] {ad} config.yaml yok")
            continue

        try:
            with open(cfg_yol, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except Exception as e:
            ekle("HATA", f"[7] {ad} config.yaml bozuk: {e}")
            continue

        for alan, alt_alanlar in gerekli.items():
            if alan not in cfg:
                ekle("HATA", f"[7] {ad} config.yaml'de '{alan}' eksik")
                continue

            if alt_alanlar:
                for alt in alt_alanlar:
                    deger = cfg[alan]
                    if isinstance(deger, dict) and alt not in deger:
                        ekle("UYARI", f"[7] {ad} config.yaml '{alan}.{alt}' eksik")

    ekle("BILGI", "[7] Config template kontrol: Tamam")


# â”€â”€ 8. Gateway Health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def gateway_health():
    """PID/state/uptime kontrol, sorunluysa raporla."""
    for ad, yol in PROFILLER.items():
        lock = yol / "gateway.lock"
        pidf = yol / "gateway.pid"
        state = yol / "gateway_state.json"

        # PID kontrol
        if pidf.exists():
            try:
                pid_int = int(pidf.read_text().strip())
                if platform.system() == "Windows":
                    r = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid_int}", "/NH"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if str(pid_int) not in r.stdout:
                        ekle("UYARI", f"[8] {ad} PID {pid_int} calismiyor")
            except (ValueError, subprocess.TimeoutExpired):
                logger.warning("[fix_01_sessiz_except] Exception")

        # Gateway state kontrol
        if state.exists():
            try:
                s = json.loads(state.read_text())
                uptime = s.get("uptime", 0)
                if uptime < 0:
                    ekle("UYARI", f"[8] {ad} gateway state anormal: uptime={uptime}")
            except (json.JSONDecodeError, Exception):
                ekle("UYARI", f"[8] {ad} gateway_state.json bozuk")

    ekle("BILGI", "[8] Gateway health: Tamam")


# â”€â”€ Ana â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    ekle("BILGI", f"Proaktif bakim basladi: {BUGUN.isoformat()}")

    config_drift_kontrol()
    gateway_watchdog()
    soul_sync()
    state_db_prune()
    memory_sync()
    haftalik_rapor()
    config_template_kontrol()
    gateway_health()

    # SonuÃ§
    hata_say = sum(1 for r in RAPOR if r.startswith("[HATA]"))
    uyari_say = sum(1 for r in RAPOR if r.startswith("[UYARI]"))

    if PAZAR_MI:
        print("\n".join(RAPOR))
    elif not SESSIZ:
        print(f"[proaktif_bakim] {hata_say} hata, {uyari_say} uyari")
        print("\n".join(RAPOR))
    else:
        # Tamamen sessiz â€” cron no_agent modunda sorunsuz Ã§alÄ±ÅŸma
        pass


if __name__ == "__main__":
    main()
