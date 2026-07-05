# -*- coding: utf-8 -*-
"""
kancalar.py â€” Katman 4: Eylem Ã–ncesi Kural Denetimi (Hook/Guard)

Her eylem Ã§alÄ±ÅŸtÄ±rÄ±lmadan Ã¶nce belirlenen kurallara gÃ¶re denetlenir.
Kural ihlali varsa eylem Ã§alÄ±ÅŸtÄ±rÄ±lmaz, hata mesajÄ± dÃ¶ner.

Desteklenen kural tipleri:
    - AynÄ± eylem N kere art arda â†’ dur
    - YasaklÄ± araÃ§ Ã§aÄŸrÄ±sÄ±
    - AÅŸÄ±rÄ± hÄ±zlÄ± dÃ¶ngÃ¼ (rate limit)
    - Task baÅŸÄ±na maksimum eylem sayÄ±sÄ±
    - Derinlik sÄ±nÄ±rÄ± ihlali

KullanÄ±m:
    from kancalar import kanca_motoru
    hata = kanca_motoru.denetle(task_id, "KOMUT_CALISTIR")
    if hata:
        # Eylem Ã§alÄ±ÅŸtÄ±rÄ±lmaz
    else:
        # Eylem Ã§alÄ±ÅŸtÄ±rÄ±lÄ±r
"""

import os
import sqlite3
import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

VARSAYILAN_MAKS_ART_ARDA = 4  # AynÄ± eylem kaÃ§ kez Ã¼st Ã¼ste?
VARSAYILAN_MAKS_EYLEM = 30  # Task baÅŸÄ±na toplam eylem limiti
VARSAYILAN_MIN_ARALIK = 0.5  # Ä°ki eylem arasÄ± minimum saniye
DANGLING_DERINLIK_UYARISI = 3  # Derinlik > 3 ise 3'ten sonraki her adÄ±m uyarÄ±r
ENGELLENEN_ARACLAR = frozenset(
    {
        "ALT_AJAN_GOREVLENDIR",  # Zincir korumasÄ±
        "SIL_DOSYA",
        "BICAKLA",  # Tehlikeli araÃ§lar
    }
)

# â”€â”€ Audit Log (SQLite) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_PROJE_KOKU = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
AUDIT_DB_DIZINI = os.path.join(_PROJE_KOKU, ".ReYMeN")
AUDIT_DB_YOL = os.path.join(AUDIT_DB_DIZINI, "audit_log.db")

_kilit_audit = threading.Lock()


def _audit_tablo_var_mi() -> bool:
    """audit_log tablosunun var olduÄŸunu kontrol eder, yoksa oluÅŸturur."""
    os.makedirs(AUDIT_DB_DIZINI, exist_ok=True)
    with _kilit_audit:
        con = sqlite3.connect(AUDIT_DB_YOL)
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    eylem       TEXT    NOT NULL,
                    kullanici   TEXT    NOT NULL DEFAULT 'system',
                    hedef       TEXT    NOT NULL DEFAULT '',
                    durum       TEXT    NOT NULL DEFAULT 'pending',
                    timestamp   TEXT    NOT NULL
                )
                """
            )
            con.commit()
        finally:
            con.close()
    return True


def audit_kaydet(
    eylem: str,
    kullanici: str = "system",
    hedef: str = "",
    durum: str = "pending",
) -> None:
    """Bir eylemi audit log'a kaydeder.

    Args:
        eylem: GerÃ§ekleÅŸtirilen eylem adÄ± (Ã¶rn. \"KOMUT_CALISTIR\").
        kullanici: Eylemi baÅŸlatan kullanÄ±cÄ±/gÃ¶rev ID'si (varsayÄ±lan: 'system').
        hedef: Eylemin hedefi (varsayÄ±lan: '').
        durum: Eylem durumu (varsayÄ±lan: 'pending').

    Tablo ÅŸemasÄ±: audit_log(id, eylem, kullanici, hedef, durum, timestamp)
    """
    _audit_tablo_var_mi()
    ts = datetime.now(timezone.utc).isoformat()
    with _kilit_audit:
        con = sqlite3.connect(AUDIT_DB_YOL)
        try:
            con.execute(
                """
                INSERT INTO audit_log (eylem, kullanici, hedef, durum, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (eylem, kullanici, hedef, durum, ts),
            )
            con.commit()
        finally:
            con.close()


# â”€â”€ Veri YapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class TaskKancaDurumu:
    """Bir task'Ä±n kanca durumu."""

    son_eylem: Optional[str] = None
    art_arda_sayac: int = 0
    toplam_eylem: int = 0
    son_ts: float = 0.0
    bloke: bool = False
    bloke_nedeni: str = ""


class KancaMotoru:
    """Eylem Ã¶ncesi kural denetimi yapar.

    Thread-safe: defaultdict + lock ile farklÄ± task'lar birbirini etkilemez.
    """

    def __init__(self):
        self._durum: dict[str, TaskKancaDurumu] = defaultdict(TaskKancaDurumu)
        self._kilit = threading.Lock()

    def denetle(
        self,
        task_id: str,
        arac: str,
        derinlik: int = 1,
        maks_art_arda: int = VARSAYILAN_MAKS_ART_ARDA,
        maks_eylem: int = VARSAYILAN_MAKS_EYLEM,
        min_aralik: float = VARSAYILAN_MIN_ARALIK,
    ) -> Optional[str]:
        """Bir eylemi kural denetiminden geÃ§irir.

        Args:
            task_id: Alt ajan task ID'si
            arac: Ã‡alÄ±ÅŸtÄ±rÄ±lacak araÃ§ adÄ± (Ã¶rn. "KOMUT_CALISTIR")
            derinlik: Alt ajan derinliÄŸi (1 = ana ajan, 2+ = alt ajan)
            maks_art_arda: Ãœst Ã¼ste aynÄ± eylem limiti
            maks_eylem: Task baÅŸÄ±na toplam eylem limiti
            min_aralik: Ä°ki eylem arasÄ± minimum sÃ¼re (saniye)

        Returns:
            None = kural ihlali yok (eylem Ã§alÄ±ÅŸtÄ±rÄ±labilir)
            str = kural ihlali mesajÄ± (eylem Ã§alÄ±ÅŸtÄ±rÄ±lmaz)
        """
        with self._kilit:
            durum = self._durum[task_id]

            # Audit log â€” her eylem Ã¶ncesi kayÄ±t
            audit_kaydet(
                eylem=arac,
                kullanici=task_id,
                hedef=f"derinlik={derinlik}",
                durum="denetleniyor",
            )

            # Bloke kontrolÃ¼
            if durum.bloke:
                return f"[KANCA] Task {task_id} bloke: {durum.bloke_nedeni}"

            # YasaklÄ± araÃ§ kontrolÃ¼
            if arac in ENGELLENEN_ARACLAR:
                durum.bloke = True
                durum.bloke_nedeni = f"'{arac}' yasaklÄ± araÃ§"
                return f"[KANCA] '{arac}' yasaklÄ±. Task bloke edildi."

            # Derinlik uyarÄ±sÄ±
            if derinlik > DANGLING_DERINLIK_UYARISI:
                return (
                    f"[KANCA] UYARI: Derinlik {derinlik} (limit: {DANGLING_DERINLIK_UYARISI}). "
                    f"Ã‡ok derin alt ajan zinciri â€” GOREV_BITTI ile sonlandÄ±r."
                )

            # AynÄ± eylem art arda kontrolÃ¼
            if arac == durum.son_eylem:
                durum.art_arda_sayac += 1
                if durum.art_arda_sayac >= maks_art_arda:
                    durum.bloke = True
                    durum.bloke_nedeni = f"'{arac}' {maks_art_arda}kere art arda"
                    return (
                        f"[KANCA] '{arac}' {maks_art_arda} kere art arda Ã§aÄŸrÄ±ldÄ±. "
                        f"Muhtemel dÃ¶ngÃ¼ â€” task bloke edildi."
                    )
            else:
                durum.art_arda_sayac = 1
            durum.son_eylem = arac

            # Toplam eylem limiti
            durum.toplam_eylem += 1
            if durum.toplam_eylem > maks_eylem:
                durum.bloke = True
                durum.bloke_nedeni = f"Toplam {maks_eylem} eylem limiti aÅŸÄ±ldÄ±"
                return (
                    f"[KANCA] Task {task_id}: {maks_eylem} eylem limiti aÅŸÄ±ldÄ±. "
                    f"Task bloke edildi."
                )

            # HÄ±zlÄ± dÃ¶ngÃ¼ kontrolÃ¼
            simdi = time.time()
            if durum.son_ts > 0 and (simdi - durum.son_ts) < min_aralik:
                return (
                    f"[KANCA] Ã‡ok hÄ±zlÄ±: {(simdi - durum.son_ts):.2f}s < {min_aralik}s"
                )
            durum.son_ts = simdi

        return None  # Ä°hlal yok

    def bloke_coz(self, task_id: str) -> bool:
        """Bloke edilmiÅŸ bir task'Ä±n blokesini kaldÄ±r."""
        with self._kilit:
            if task_id in self._durum:
                self._durum[task_id].bloke = False
                self._durum[task_id].bloke_nedeni = ""
                return True
            return False

    def task_durum(self, task_id: str) -> dict:
        """Bir task'Ä±n kanca durumunu dÃ¶ndÃ¼rÃ¼r."""
        with self._kilit:
            d = self._durum.get(task_id)
            if d:
                return {
                    "son_eylem": d.son_eylem,
                    "art_arda_sayac": d.art_arda_sayac,
                    "toplam_eylem": d.toplam_eylem,
                    "bloke": d.bloke,
                    "bloke_nedeni": d.bloke_nedeni,
                }
            return {"bloke": False}

    def task_temizle(self, task_id: str):
        """Task bitince durumu temizle."""
        with self._kilit:
            self._durum.pop(task_id, None)

    def istatistik(self) -> dict:
        """TÃ¼m aktif task'larÄ±n kanca istatistikleri."""
        with self._kilit:
            toplam = len(self._durum)
            blokeli = sum(1 for d in self._durum.values() if d.bloke)
            return {"aktif_task": toplam, "blokeli_task": blokeli}


# â”€â”€ Singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

kanca_motoru = KancaMotoru()


# â”€â”€ Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    # Test 1: Normal eylem â€” ihlal yok
    hata = kanca_motoru.denetle("test_001", "DOSYA_OKU")
    assert hata is None, "Normal eylem ihlal vermemeli"
    print("[OK] Normal eylem â€” ihlal yok")

    # Test 2: AynÄ± eylem 4 kere art arda â†’ bloke
    for i in range(5):
        hata = kanca_motoru.denetle("test_002", "WEB_ARA")
    assert hata is not None, "5. ayni eylem bloke etmeli"
    assert "bloke" in hata.lower(), "Bloke mesaji icermeli"
    print(f"[OK] Art arda ayni eylem blokesi: {hata[:50]}...")

    # Test 3: YasaklÄ± araÃ§
    hata = kanca_motoru.denetle("test_003", "ALT_AJAN_GOREVLENDIR")
    assert hata is not None, "Yasakli arac bloke etmeli"
    print(f"[OK] Yasakli arac blokesi: {hata[:50]}...")

    # Test 4: Bloke Ã§Ã¶zme
    assert kanca_motoru.bloke_coz("test_002"), "Bloke cozulebilmeli"
    durum = kanca_motoru.task_durum("test_002")
    assert not durum["bloke"], "Cozum sonrasi bloke=False olmali"
    print("[OK] Bloke cozme basarili")

    # Test 5: Ä°statistik
    istat = kanca_motoru.istatistik()
    print(f"[OK] Istatistik: {istat}")

    # Temizlik
    kanca_motoru.task_temizle("test_001")
    kanca_motoru.task_temizle("test_002")
    kanca_motoru.task_temizle("test_003")
    print("[OK] Tum testler gecti")
