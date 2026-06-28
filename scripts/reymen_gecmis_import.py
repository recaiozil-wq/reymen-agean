#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_gecmis_import.py — ReYMeN session DB'lerinden ReYMeN hafizasina import.

Tum gecmis konusmalari:
  1. .ReYMeN/memories/ altina markdown log olarak yazar
  2. ReYMeN SQLite hafizasina kaydeder
  3. SOUL.md'ye onemli kazanimlari ekler
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# ReYMeN proje kok
PROJE_KOK = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
REYMEN_MEMORIES = PROJE_KOK / ".ReYMeN" / "memories"
REYMEN_HAFIZA_DB = PROJE_KOK / ".reymen_hafiza" / "hafiza.db"

# ReYMeN session DB'leri
REYMEN_DBS = [
    ("reymen", r"C:\Users\marko\AppData\Local\hermes\profiles\reymen\state.db"),
    ("default", r"C:\Users\marko\AppData\Local\hermes\state.db"),
]

# Kategorize edilmis anahtar kelimeler
KATEGORILER = {
    "MCP": ["mcp", "model context protocol", "tool registry"],
    "Voice": ["voice", "ses", "tts", "speech", "konus", "mikrofon"],
    "Personality": ["personality", "kisilik", "soul", "character"],
    "Terminal": ["terminal", "bash", "shell", "subprocess", "komut"],
    "Memory": ["memory", "hafiza", "remember", "kaydet"],
    "Skills": ["skill", "beceri", "procedural"],
    "Security": ["security", "guvenlik", "approval", "onay", "yolo"],
    "Browser": ["browser", "tarayici", "navigate", "web"],
    "HomeAssistant": ["ha_", "home assistant", "akilli ev", "light"],
    "Spotify": ["spotify", "muzik", "music", "cal"],
    "Git/GitHub": ["git", "github", "pr", "branch", "commit", "merge"],
    "Docker": ["docker", "konteyner", "container"],
    "Python": ["python", "pip", "pytest", "venv"],
    "Windows": ["windows", "win32", "sapi", "powershell"],
}


def mesaj_kategorisi(mesaj: str) -> list[str]:
    """Mesajin kategorilerini tespit et."""
    kategoriler = []
    mesaj_lower = mesaj.lower()
    for kat, kelimeler in KATEGORILER.items():
        if any(k in mesaj_lower for k in kelimeler):
            kategoriler.append(kat)
    return kategoriler or ["Genel"]


def session_ozeti(mesajlar: list[tuple]) -> str:
    """Session mesajlarindan ozet cikar."""
    if not mesajlar:
        return "Bos session"

    # Ilk kullanici mesaji
    ilk_kullanici = ""
    # Son asistan mesaji
    son_asistan = ""

    for mesaj_turu, icerik, _ in mesajlar[:20]:
        if mesaj_turu in ("user", "human") and not ilk_kullanici:
            ilk_kullanici = icerik[:200]
            break

    for mesaj_turu, icerik, _ in reversed(mesajlar[-10:]):
        if mesaj_turu in ("assistant", "ai"):
            son_asistan = icerik[:300]
            break

    # Kategoriler
    tum_metin = " ".join(m for _, m, _ in mesajlar if m)
    kategoriler = mesaj_kategorisi(tum_metin)

    ozet = f"Hedef: {ilk_kullanici or 'Belirtilmemis'}"
    ozet += f"\nKategoriler: {', '.join(kategoriler)}"
    ozet += f"\nSonuc: {son_asistan or 'Yanit yok'}"
    ozet += f"\nMesaj sayisi: {len(mesajlar)}"
    return ozet


def import_hermes_db(profil: str, db_path: str) -> int:
    """Bir ReYMeN DB'sinden session'lari import et."""
    if not os.path.exists(db_path):
        print(f"  [!] DB bulunamadi: {db_path}")
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Session'lari al
    cur.execute("SELECT id, title, source, started_at, ended_at, message_count FROM sessions ORDER BY started_at")
    sessions = cur.fetchall()
    print(f"  [*] {len(sessions)} session bulundu")

    import_edilen = 0
    hafiza_conn = None
    try:
        if REYMEN_HAFIZA_DB.exists():
            hafiza_conn = sqlite3.connect(str(REYMEN_HAFIZA_DB))
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    for session in sessions:
        session_id = session["id"]
        title = session["title"] or f"{session['source'] or '?'} {session_id[:8]}"
        kaynak = session["source"] or "?"
        started = session["started_at"] or 0
        baslama = datetime.fromtimestamp(started).isoformat() if started else "?"

        # Mesajlari al
        cur.execute(
            "SELECT role, content, timestamp FROM messages "
            "WHERE session_id = ? AND active = 1 ORDER BY id",
            (session_id,)
        )
        mesajlar = cur.fetchall()

        if len(mesajlar) < 2:
            continue  # Bos session'lari atla

        # Ozet cikar
        ozet = session_ozeti(mesajlar)

        # Markdown log yaz
        tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"hermes_{profil}_{str(session_id)[:8]}_{tarih}.md"
        dosya_yolu = REYMEN_MEMORIES / dosya_adi

        markdown = [
            f"# ReYMeN Session Import: {title}",
            f"",
            f"**Kaynak:** ReYMeN ({profil})",
            f"**Session ID:** {session_id}",
            f"**Platform:** {kaynak}",
            f"**Baslama:** {baslama}",
            f"**Import:** {datetime.now().isoformat()}",
            f"**Mesaj sayisi:** {len(mesajlar)}",
            f"",
            f"## Ozet",
            f"",
            ozet,
            f"",
            f"## Mesajlar",
            f"",
        ]

        for i, (role, content, msg_time) in enumerate(mesajlar[:50], 1):
            if content:
                zaman = datetime.fromtimestamp(msg_time).isoformat() if msg_time else "?"
                kisaltma = content[:500]
                markdown.append(f"### {i}. [{role.upper()}] ({zaman})")
                markdown.append(f"")
                markdown.append(kisaltma)
                markdown.append(f"")

        if len(mesajlar) > 50:
            markdown.append(f"... ve {len(mesajlar) - 50} mesaj daha")

        REYMEN_MEMORIES.mkdir(parents=True, exist_ok=True)
        with open(str(dosya_yolu), "w", encoding="utf-8") as f:
            f.write("\n".join(markdown))

        # SQLite hafizaya kaydet
        if hafiza_conn:
            try:
                hafiza_conn.execute(
                    "INSERT OR IGNORE INTO memories "
                    "(session_id, title, content, categories, message_count, imported_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (str(session_id), title, ozet,
                     json.dumps(mesaj_kategorisi(ozet)),
                     len(mesajlar), datetime.now().isoformat())
                )
                hafiza_conn.commit()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        import_edilen += 1

    conn.close()
    if hafiza_conn:
        hafiza_conn.close()
    return import_edilen


def main():
    print("=" * 60)
    print("REYMEN GECMIS IMPORT")
    print("=" * 60)
    print()

    REYMEN_MEMORIES.mkdir(parents=True, exist_ok=True)
    PROJE_KOK.joinpath(".reymen_hafiza").mkdir(parents=True, exist_ok=True)

    # Hafiza DB'sini olustur (yoksa)
    if not REYMEN_HAFIZA_DB.exists():
        conn = sqlite3.connect(str(REYMEN_HAFIZA_DB))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                title TEXT,
                content TEXT,
                categories TEXT,
                message_count INTEGER,
                imported_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER,
                tag TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        conn.commit()
        conn.close()
        print("[*] Hafiza DB olusturuldu")

    toplam = 0
    for profil, db_path in REYMEN_DBS:
        print(f"\n[Profil: {profil}]")
        print(f"  DB: {db_path}")
        adet = import_hermes_db(profil, db_path)
        toplam += adet
        print(f"  -> {adet} session import edildi")

    print(f"\n{'=' * 60}")
    print(f"TOPLAM: {toplam} session import edildi")
    print(f"Hedef: {REYMEN_MEMORIES}")
    print(f"DB: {REYMEN_HAFIZA_DB}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
