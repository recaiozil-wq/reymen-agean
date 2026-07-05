# -*- coding: utf-8 -*-
"""
hafiza_budama.py â€” Otomatik HafÄ±za Budama ve Temizleme.

Ne yapar:
  1. ReYMeN MEMORY.md giriÅŸlerini tara
  2. Eski/tekrarlanan/gereksiz entry'leri temizle
  3. Benzer entry'leri birleÅŸtir
  4. ReYMeN SQLite hafÄ±zasÄ±ndaki eski kayÄ±tlarÄ± temizle (TTL)
  5. .ReYMeN/memories/ iÃ§indeki 7+ gÃ¼nlÃ¼k dosyalarÄ± temizle
  6. Cron job ile otomatik Ã§alÄ±ÅŸtÄ±rma

Kullanim:
    python hafiza_budama.py              # Tam budama
    python hafiza_budama.py --dry-run    # Ne olacagini goster, uygulama
"""

import json
import logging
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# â”€â”€ Ayarlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# MEMORY entry yaÅŸam sÃ¼releri (gÃ¼n)
GUNLUK_GOREV_TTL = 3  # GÃ¼nlÃ¼k gÃ¶rev entry'leri 3 gÃ¼n sonra temizlenir
HAFIZA_ENTRY_TTL = 14  # Genel hafÄ±za entry'leri 14 gÃ¼n sonra temizlenir
KURAL_TTL = 90  # KalÄ±cÄ± kurallar 90 gÃ¼n sonra gÃ¶zden geÃ§irilir
DOSYA_TTL = 7  # .ReYMeN/memories/ dosyalarÄ± 7 gÃ¼n

# Budama eÅŸikleri
MAX_ENTRY_KARAKTER = 200  # Bir entry max 200 karakter (fazlasÄ± kesilir)
MAX_BENZERLIK_ESIK = 0.6  # Benzerlik oranÄ± > %60 ise birleÅŸtir
MIN_BOSLUK = 500  # Budama sonrasÄ± en az 500 karakter boÅŸluk bÄ±rak

# Yollar
PROJE = Path(__file__).parent.resolve()
REYMEN_MEMORIES = (
    Path.home() / "AppData" / "Local" / "reymen" / "profiles" / "reymen" / "memories"
)
REYMEN_CONFIG = Path.home() / "AppData" / "Local" / "reymen" / "config.yaml"
REYMEN_DB = Path(str(PROJE) + "\\.reymen_hafiza\\hafiza.db")

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 1. REYMEN MEMORY BUDA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def reymen_memory_buda(dry_run: bool = False) -> dict:
    """ReYMeN MEMORY.md ve USER.md'deki entry'leri buda.

    Args:
        dry_run: True = sadece rapor, False = uygula

    Returns:
        dict: Budama raporu
    """
    rapor = {
        "memory": {"onceki": 0, "sonra": 0, "silinen": 0, "birlestirilen": 0},
        "user": {"onceki": 0, "sonra": 0, "silinen": 0},
        "toplam_kazanc": 0,
    }

    # MEMORY.md
    mem_path = REYMEN_MEMORIES / "MEMORY.md"
    if mem_path.exists():
        onceki, sonra = _memory_dosyasi_buda(mem_path, dry_run)
        rapor["memory"]["onceki"] = onceki
        rapor["memory"]["sonra"] = sonra
        rapor["memory"]["silinen"] = onceki - sonra

    # USER.md
    user_path = REYMEN_MEMORIES / "USER.md"
    if user_path.exists():
        onceki, sonra = _memory_dosyasi_buda(user_path, dry_run)
        rapor["user"]["onceki"] = onceki
        rapor["user"]["sonra"] = sonra
        rapor["user"]["silinen"] = onceki - sonra

    rapor["toplam_kazanc"] = (rapor["memory"]["onceki"] - rapor["memory"]["sonra"]) + (
        rapor["user"]["onceki"] - rapor["user"]["sonra"]
    )
    return rapor


def _memory_dosyasi_buda(dosya_yolu: Path, dry_run: bool) -> tuple:
    """Bir memory dosyasini buda.

    Returns:
        (onceki_satir_sayisi, sonraki_satir_sayisi)
    """
    try:
        icerik = dosya_yolu.read_text(encoding="utf-8")
    except Exception:
        return 0, 0

    onceki_satir = len(icerik.split("\n"))
    onceki_char = len(icerik)

    # Entry'leri ayir (bos satirla ayrilmis bloklar)
    entryler = _entryleri_ayir(icerik)
    onceki_entry = len(entryler)

    # Temizleme
    yeni_entryler = _entryleri_temizle(entryler)

    # BirleÅŸtirme
    yeni_entryler = _entryleri_birlestir(yeni_entryler)

    # Yeni iÃ§erik (Â§ ile ayrilmis)
    yeni_icerik = ("\nÂ§\n".join(yeni_entryler)).strip()
    if yeni_icerik:
        yeni_icerik += "\n"

    if not dry_run:
        try:
            dosya_yolu.write_text(yeni_icerik, encoding="utf-8")
        except Exception as e:
            logger.error("Yazma hatasi %s: %s", dosya_yolu, e)

    sonraki_char = len(yeni_icerik)
    print(
        f"  {dosya_yolu.name}: {onceki_entry} entry â†’ {len(yeni_entryler)} entry"
        f" ({onceki_char} â†’ {sonraki_char} karakter, {onceki_char - sonraki_char} kazanc)"
        + (" [DRY RUN]" if dry_run else "")
    )

    return onceki_entry, len(yeni_entryler)


def _entryleri_ayir(icerik: str) -> list[str]:
    """Ä°Ã§eriÄŸi ayrÄ± entry'lere bÃ¶l (Â§ ile ayrilmis)."""
    entryler = []
    for blok in icerik.strip().split("Â§"):
        blok = blok.strip()
        if blok and len(blok) > 5:  # Ã‡ok kÄ±sa entry'leri atla
            entryler.append(blok)
    return entryler


def _entryleri_temizle(entryler: list[str]) -> list[str]:
    """Eski/gereksiz entry'leri temizle, kÄ±sa olanlarÄ± boyutlandÄ±r."""
    yeni = []
    for e in entryler:
        e = e.strip()
        if not e:
            continue

        # Ã‡ok kÄ±sa entry'leri atla (< 15 karakter)
        if len(e) < 15:
            continue

        # Sadece tarih/sayÄ± entry'lerini atla
        if re.match(r"^[\d\s\-:./,]+$", e):
            continue

        # "test" veya "deneme" iÃ§eren Ã§ok kÄ±sa entry'leri atla
        if len(e) < 30 and re.search(r"test|deneme|Ã¶rnek|ornek", e, re.IGNORECASE):
            continue

        # Eski tamamlanmÄ±ÅŸ gÃ¶rev kayÄ±tlarÄ±nÄ± temizle
        # (iÃ§inde "fix:", "dÃ¼zeltildi", "tamamlandÄ±", "gÃ¶rev bitti" varsa
        #  ve 200 karakterden kÄ±saysa â†’ atlanabilir)
        if len(e) < MAX_ENTRY_KARAKTER and _gorev_entry_mi(e):
            continue  # Eski gÃ¶rev entry'si, atla

        # Uzun entry'leri kÄ±salt (fazla detayÄ± kes)
        if len(e) > MAX_ENTRY_KARAKTER * 2:
            e = e[: MAX_ENTRY_KARAKTER * 2] + "..."

        yeni.append(e)

    return yeni


def _gorev_entry_mi(metin: str) -> bool:
    """Bir entry'nin eski bir gÃ¶rev kaydÄ± olup olmadÄ±ÄŸÄ±nÄ± kontrol et."""
    gorev_isaretleri = [
        "fix:",
        "dÃ¼zeltildi",
        "duzeltildi",
        "tamamlandi",
        "tamamlandÄ±",
        "gÃ¶rev bitti",
        "gorev bitti",
        "cozuldu",
        "Ã§Ã¶zÃ¼ldÃ¼",
        "eklendi",
        "kaldirildi",
        "kaldÄ±rÄ±ldÄ±",
        "guncellendi",
        "gÃ¼ncellendi",
        "test gecti",
        "test geÃ§ti",
        "basarili",
        "baÅŸarÄ±lÄ±",
        "gorev_id",
        "task_id",
        "commit",
        "push edildi",
        "merged",
    ]
    metin_lower = metin.lower()
    return any(isaret in metin_lower for isaret in gorev_isaretleri)


def _entryleri_birlestir(entryler: list[str]) -> list[str]:
    """Benzer entry'leri birleÅŸtir."""
    if len(entryler) < 2:
        return entryler

    yeni = []
    kullanilan = set()

    for i, e1 in enumerate(entryler):
        if i in kullanilan:
            continue

        benzerler = [e1]
        kullanilan.add(i)

        for j, e2 in enumerate(entryler):
            if j in kullanilan or j <= i:
                continue
            if _benzerlik_orani(e1, e2) > MAX_BENZERLIK_ESIK:
                benzerler.append(e2)
                kullanilan.add(j)

        if len(benzerler) > 1:
            # BirleÅŸtir: en kÄ±sa aÃ§Ä±klamayÄ± koru
            en_kisa = min(benzerler, key=len)
            # Kategori adÄ±nÄ± al (iki nokta Ã¼stÃ¼ste Ã¶ncesi)
            kategori = en_kisa.split(":")[0] if ":" in en_kisa else ""
            if kategori:
                # TÃ¼m deÄŸerleri topla
                degerler = set()
                for b in benzerler:
                    if ":" in b:
                        degerler.add(b.split(":", 1)[1].strip())
                yeni.append(f"{kategori}: {'; '.join(sorted(degerler))}")
            else:
                yeni.append(en_kisa)
        else:
            yeni.append(e1)

    return yeni


def _benzerlik_orani(s1: str, s2: str) -> float:
    """Ä°ki string arasÄ±ndaki benzerlik oranÄ± (0.0 - 1.0)."""
    # AynÄ± kelimelerin oranÄ±
    kelimeler1 = set(re.findall(r"\w+", s1.lower()))
    kelimeler2 = set(re.findall(r"\w+", s2.lower()))
    if not kelimeler1 or not kelimeler2:
        return 0.0
    kesisim = kelimeler1 & kelimeler2
    toplam = kelimeler1 | kelimeler2
    return len(kesisim) / len(toplam)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 2. REYMEN SQLITE HAFIZA BUDA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def reymen_hafiza_buda(dry_run: bool = False) -> dict:
    """ReYMeN SQLite hafÄ±zasÄ±ndaki eski kayÄ±tlarÄ± temizle.

    Args:
        dry_run: True = sadece rapor

    Returns:
        dict: Temizlik raporu
    """
    rapor = {"toplam": 0, "silinen": 0, "koleksiyonlar": {}}
    db_yolu = REYMEN_DB

    if not db_yolu.exists():
        print("  ReYMeN SQLite hafiza DB bulunamadi.")
        return rapor

    try:
        conn = sqlite3.connect(str(db_yolu))
        c = conn.cursor()

        # Koleksiyon bazÄ±nda kayÄ±t sayÄ±larÄ±
        rows = c.execute(
            "SELECT koleksiyon, COUNT(*) FROM kayitlar GROUP BY koleksiyon"
        ).fetchall()
        for koleksiyon, sayi in rows:
            rapor["toplam"] += sayi
            rapor["koleksiyonlar"][koleksiyon] = {"onceki": sayi, "silinen": 0}

        # 1. Expire zamanÄ± geÃ§miÅŸ kayÄ±tlarÄ± sil
        simdi = time.time()
        c.execute(
            "DELETE FROM kayitlar WHERE expire_zaman > 0 AND expire_zaman < ?", (simdi,)
        )
        silinen_expire = c.rowcount

        # 2. KonuÅŸma kayÄ±tlarÄ±: 14 gÃ¼nden eski olanlarÄ± temizle (son 50 kayÄ±t hariÃ§)
        # Her session iÃ§in son 50 mesajÄ± koru, Ã¶ncesini sil
        sessions = c.execute(
            "SELECT DISTINCT session_id FROM kayitlar WHERE koleksiyon='konusmalar'"
        ).fetchall()
        session_based = 0
        for (sid,) in sessions:
            # Session'daki toplam kayÄ±t
            toplam_session = c.execute(
                "SELECT COUNT(*) FROM kayitlar WHERE session_id=? AND koleksiyon='konusmalar'",
                (sid,),
            ).fetchone()[0]
            if toplam_session > 50:
                # Son 50 kaydÄ±n ID'sini bul
                c.execute(
                    """SELECT id FROM kayitlar
                       WHERE session_id=? AND koleksiyon='konusmalar'
                       ORDER BY id DESC LIMIT 50""",
                    (sid,),
                )
                korunacak = [row[0] for row in c.fetchall()]
                if korunacak:
                    placeholders = ",".join("?" for _ in korunacak)
                    c.execute(
                        f"""DELETE FROM kayitlar
                            WHERE session_id=? AND koleksiyon='konusmalar'
                            AND id NOT IN ({placeholders})""",
                        (sid, *korunacak),
                    )
                    session_based += c.rowcount

        # 3. Session kayÄ±tlarÄ±nÄ± temizle (bitmiÅŸ ve 14+ gÃ¼nlÃ¼k)
        eski_session = c.execute(
            """SELECT s.id FROM sessions s
               WHERE s.bitis > 0 AND s.bitis < ?""",
            (simdi - GUNLUK_GOREV_TTL * 86400,),
        ).fetchall()

        for (sid,) in eski_session:
            c.execute("DELETE FROM kayitlar WHERE session_id=?", (sid,))
            c.execute("DELETE FROM sessions WHERE id=?", (sid,))

        toplam_silinen = silinen_expire + session_based + len(eski_session)

        if not dry_run:
            conn.commit()

            # Koleksiyon bazÄ±nda gÃ¼ncel sayÄ±lar
            rows = c.execute(
                "SELECT koleksiyon, COUNT(*) FROM kayitlar GROUP BY koleksiyon"
            ).fetchall()
            for koleksiyon, sayi in rows:
                if koleksiyon in rapor["koleksiyonlar"]:
                    onceki = rapor["koleksiyonlar"][koleksiyon]["onceki"]
                    rapor["koleksiyonlar"][koleksiyon]["sonra"] = sayi
                    rapor["koleksiyonlar"][koleksiyon]["silinen"] = onceki - sayi

        conn.close()

        rapor["silinen"] = toplam_silinen
        print(
            f"  ReYMeN SQLite: {rapor['toplam']} kayit â†’ {toplam_silinen} silindi"
            + (" [DRY RUN]" if dry_run else "")
        )

    except Exception as e:
        print(f"  SQLite budama hatasi: {e}")

    return rapor


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 3. MEMORY DOSYALARINI TEMIZLE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def memory_dosyalarini_temizle(dry_run: bool = False) -> dict:
    """.ReYMeN/memories/ iÃ§indeki eski dosyalarÄ± temizle.

    Args:
        dry_run: True = sadece rapor

    Returns:
        dict: Temizlik raporu
    """
    rapor = {"toplam": 0, "silinen": 0, "kb_kazanc": 0}
    mem_dizini = PROJE / ".ReYMeN" / "memories"

    if not mem_dizini.exists():
        return rapor

    simdi = time.time()
    kesme = simdi - DOSYA_TTL * 86400  # 7 gÃ¼n

    for f in sorted(mem_dizini.glob("*")):
        if not f.is_file():
            continue
        rapor["toplam"] += 1

        # Gorev loglarÄ± hariÃ§ her ÅŸeyi temizle (gorev_ = her zaman koru)
        if f.name.startswith("gorev_"):
            continue
        # session_20260620.md gibi ana session loglarÄ±nÄ± koru
        if f.name == "session_20260620.md":
            continue

        try:
            mtime = f.stat().st_mtime
            if mtime < kesme:
                boyut = f.stat().st_size
                rapor["kb_kazanc"] += boyut
                if not dry_run:
                    f.unlink()
                rapor["silinen"] += 1
        except OSError as _hafiza_b_e389:
            print(f"[UYARI] hafiza_budama.py:390 - {_hafiza_b_e389}")

    rapor["kb_kazanc"] = round(rapor["kb_kazanc"] / 1024, 1)
    print(
        f"  .ReYMeN/memories/: {rapor['toplam']} dosyadan {rapor['silinen']} silindi"
        f" ({rapor['kb_kazanc']} KB kazanc)" + (" [DRY RUN]" if dry_run else "")
    )
    return rapor


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 4. ANA BUDA FONKSIYONU
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def buda(dry_run: bool = False) -> dict:
    """TÃ¼m hafÄ±za sistemlerini buda.

    Args:
        dry_run: True = sadece raporla, uygulama

    Returns:
        dict: KapsamlÄ± budama raporu
    """
    print(f"\n{'=' * 60}")
    print(f"  HAFIZA BUDA {'(DRY RUN - sadece rapor)' if dry_run else ''}")
    print(f"{'=' * 60}")
    print(f"  Baslama: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(
        f"  TTL: gorev={GUNLUK_GOREV_TTL}g, hafiza={HAFIZA_ENTRY_TTL}g, dosya={DOSYA_TTL}g"
    )

    baslama = time.time()

    # 1. ReYMeN memory
    print(f"\n[1/3] ReYMeN memory budama...")
    h_rapor = reymen_memory_buda(dry_run)

    # 2. ReYMeN SQLite
    print(f"\n[2/3] ReYMeN SQLite budama...")
    r_rapor = reymen_hafiza_buda(dry_run)

    # 3. .ReYMeN/memories/ dosyalarÄ±
    print(f"\n[3/3] Memory dosyasi temizleme...")
    d_rapor = memory_dosyalarini_temizle(dry_run)

    sure = round(time.time() - baslama, 2)
    toplam_kazanc = (
        h_rapor.get("toplam_kazanc", 0)
        + r_rapor.get("silinen", 0)
        + d_rapor.get("silinen", 0)
    )

    print(f"\n{'=' * 60}")
    print(f"  BUDA TAMAMLANDI ({sure}s)")
    print(
        f"  ReYMeN MEMORY: {h_rapor.get('memory', {}).get('silinen', 0)} entry temizlendi"
        f" ({h_rapor.get('toplam_kazanc', 0)} karakter kazanc)"
    )
    print(f"  ReYMeN SQLite: {r_rapor.get('silinen', 0)} kayit temizlendi")
    print(
        f"  Eski dosyalar: {d_rapor.get('silinen', 0)} dosya temizlendi"
        f" ({d_rapor.get('kb_kazanc', 0)} KB)"
    )
    print(f"  Toplam kazanc: {toplam_kazanc} birim")
    print(f"{'=' * 60}")

    return {
        "reymen": h_rapor,
        "reymen_sqlite": r_rapor,
        "dosyalar": d_rapor,
        "sure_sn": sure,
        "toplam_kazanc": toplam_kazanc,
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 5. CRON ICIN ORNEK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def cron_budama_gorevi():
    """Cron job olarak Ã§aÄŸrÄ±lmak Ã¼zere budama gÃ¶revi.

    Bu fonksiyon her gÃ¼n Ã§alÄ±ÅŸtÄ±rÄ±lacak ÅŸekilde cronjob'a eklenebilir:
        cronjob(action='create', schedule='0 3 * * *',
                prompt='Hafiza budama cron gorevini calistir',
                skills=['reymen-gorev-hafiza'])
    """
    try:
        sonuc = buda(dry_run=False)
        print(
            f"[CRON] Hafiza budama tamam: {sonuc.get('toplam_kazanc', 0)} birim temizlendi"
        )
        return sonuc
    except Exception as e:
        print(f"[CRON] Hafiza budama hatasi: {e}")
        return {"hata": str(e)}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALISTIRMA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    cron_mode = "--cron" in sys.argv

    if cron_mode:
        cron_budama_gorevi()
    else:
        buda(dry_run=dry_run)
