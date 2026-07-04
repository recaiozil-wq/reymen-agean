# -*- coding: utf-8 -*-
"""cozum_hafizasi.py — Cozulmus sorunlari yapilandirilmis bicimde tutar.

Her kayit: sorun, kok neden, cozum, basari/fail sayisi, guven skoru.
Yeni sorun geldiginde once buraya bak, eslesen varsa uygula.
Cozum uygulandiktan sonra "ise yaradi mi?" geri bildirimi al.

Kullanim:
    from reymen.sistem.cozum_hafizasi import CozumHafizasi
    ch = CozumHafizasi()
    eslesme = ch.bul(sorun_metni)
    if eslesme:
        ... cozumu uygula ...
        ch.geri_bildirim(eslesme['id'], basarili=True)
    else:
        ... LLM ile coz ...
        ch.kaydet(sorun, kok_neden, cozum, kategori)
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "CozumHafizasi",
    "cozum_bul",
    "cozum_kaydet",
    "cozum_geri_bildirim",
    "motor_kaydet",
]

# ── Varsayilan yapilandirma ──────────────────────────────────────────────

_VARSAYILAN_DB = Path(__file__).resolve().parent.parent.parent / "reymen" / "merkez_db" / "cozum_hafizasi.db"
_VARSAYILAN_CONFIDENCE = 0.0  # Yeni kayit: test edilmemis, gizli


# ── Veritabani ───────────────────────────────────────────────────────────

def _db_baglan(db_yolu: str | Path | None = None) -> sqlite3.Connection:
    if db_yolu is None:
        db_yolu = _VARSAYILAN_DB
    db_yolu = Path(db_yolu)
    db_yolu.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_yolu))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    return conn


def _db_olustur(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cozumler (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            problem     TEXT NOT NULL,
            root_cause  TEXT DEFAULT '',
            cozum       TEXT NOT NULL,
            kategori    TEXT DEFAULT '',
            success     INTEGER DEFAULT 0,
            fail        INTEGER DEFAULT 0,
            confidence  REAL DEFAULT 0.5,
            created_at  REAL NOT NULL,
            last_used   REAL DEFAULT 0,
            tags        TEXT DEFAULT '[]',
            metadata    TEXT DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_cozumler_problem ON cozumler(problem);
        CREATE INDEX IF NOT EXISTS idx_cozumler_kategori ON cozumler(kategori);
        CREATE INDEX IF NOT EXISTS idx_cozumler_confidence ON cozumler(confidence DESC);
        -- FTS5 for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS cozumler_fts USING fts5(
            problem, cozum, root_cause, kategori,
            content='cozumler',
            content_rowid='id'
        );
    """)


# ── CozumHafizasi Sinifi ─────────────────────────────────────────────────

class CozumHafizasi:
    """Cozulmus sorunlarin yapilandirilmis hafizasi.

    Ozellikler:
      - bul(metin) -> eslesen cozum (confidence sirali)
      - kaydet(problem, root_cause, cozum, kategori) -> id
      - geri_bildirim(id, basarili) -> confidence guncelle
      - json_export() -> tum kayitlar JSON
      - istatistik() -> oran/kategori bazli
    """

    def __init__(self, db_yolu: str | Path | None = None):
        self._db_yolu = Path(db_yolu) if db_yolu else _VARSAYILAN_DB
        self._ilk_olusum()

    def _ilk_olusum(self) -> None:
        conn = _db_baglan(self._db_yolu)
        try:
            _db_olustur(conn)
        finally:
            conn.close()

    def _baglan(self) -> sqlite3.Connection:
        return _db_baglan(self._db_yolu)

    # ── SORGU ────────────────────────────────────────────────────────────

    def bul(self, metin: str, limit: int = 5) -> list[dict[str, Any]]:
        """Sorun metnine gore en uygun cozumu bul (FTS5 + 3-katmanli confidence).

        Katmanlar:
          - 0.6+  : yuksek guven → normal goster, siralamada onde
          - 0.3-0.6: dusuk guven → "dusuk guvenilirlik" etiketiyle goster
          - 0.0-0.3: guvensiz → tamamen gizle

        Hic 0.3+ sonuc yoksa bos liste don (cagiran 'guvenilir cozum yok' mesaji verir).

        Args:
            metin: Sorun tanimi (hata mesaji, hata kodu, arama kelimesi)
            limit: Maks sonuc sayisi

        Returns:
            [{"id", "problem", "root_cause", "cozum", "kategori",
              "confidence", "success", "fail", "guven_etiketi", ...}]
            guven_etiketi: "yuksek" | "dusuk"
        """
        if not metin or len(metin.strip()) < 3:
            return []

        conn = self._baglan()
        try:
            # TUM eslesmeleri getir (confidence filtrelemesi Python'da yapilacak)
            ham_sonuc = []
            try:
                fts_sorgu = ' OR '.join(
                    f'"{k}"' for k in metin.split() if len(k) > 2
                )
                if fts_sorgu:
                    rows = conn.execute(
                        """SELECT c.* FROM cozumler_fts f
                           JOIN cozumler c ON f.rowid = c.id
                           WHERE cozumler_fts MATCH ?
                           ORDER BY c.confidence DESC LIMIT ?""",
                        (fts_sorgu, limit * 3),
                    ).fetchall()
                    ham_sonuc = [dict(r) for r in rows]
            except sqlite3.OperationalError as e:
                log.warning(f"[cozum_hafizasi] FTS5 sorgu hatasi: {e}")
                pass

            if not ham_sonuc:
                like_sorgu = f'%{metin}%'
                rows = conn.execute(
                    """SELECT * FROM cozumler
                       WHERE problem LIKE ? OR cozum LIKE ? OR root_cause LIKE ?
                       ORDER BY confidence DESC LIMIT ?""",
                    (like_sorgu, like_sorgu, like_sorgu, limit * 3),
                ).fetchall()
                ham_sonuc = [dict(r) for r in rows]

            # 3-katmanli confidence filtrele
            sonuc = []
            for kayit in ham_sonuc:
                c = kayit.get("confidence", 0.0)
                if c >= 0.6:
                    kayit["guven_etiketi"] = "yuksek"
                    sonuc.append(kayit)
                elif c >= 0.3:
                    kayit["guven_etiketi"] = "dusuk"
                    sonuc.append(kayit)
                # < 0.3 tamamen gizle, ekleme

            # Sirala: yuksek onde, sonra dusuk
            sonuc.sort(key=lambda x: (
                0 if x.get("guven_etiketi") == "yuksek" else 1,
                -x.get("confidence", 0)
            ))

            # Limiti uygula
            sonuc = sonuc[:limit]

            # Son kullanim tarihini guncelle
            for kayit in sonuc:
                conn.execute(
                    "UPDATE cozumler SET last_used=? WHERE id=?",
                    (time.time(), kayit["id"]),
                )
            conn.commit()
            return sonuc
        finally:
            conn.close()

    # ── KAYIT ─────────────────────────────────────────────────────────────

    def kaydet(
        self,
        problem: str,
        root_cause: str,
        cozum: str,
        kategori: str = "",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Yeni bir cozum kaydet.

        Args:
            problem: Sorun tanimi
            root_cause: Kok neden analizi
            cozum: Uygulanan cozum
            kategori: Kategori (or: "import", "bagimlilik", "config")
            tags: Etiket listesi
            metadata: Ek metadata (or: {"dosya": "x.py", "satir": 42})

        Returns:
            Kaydin ID'si
        """
        now = time.time()
        conn = self._baglan()
        try:
            cur = conn.execute(
                """INSERT INTO cozumler
                   (problem, root_cause, cozum, kategori,
                    success, fail, confidence, created_at, last_used,
                    tags, metadata)
                   VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?)""",
                (
                    problem.strip(),
                    root_cause.strip(),
                    cozum.strip(),
                    kategori.strip(),
                    _VARSAYILAN_CONFIDENCE, now, now,
                    json.dumps(tags or [], ensure_ascii=False),
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
            kayit_id = cur.lastrowid or 0

            # FTS5 index'i guncelle
            try:
                conn.execute(
                    """INSERT INTO cozumler_fts (rowid, problem, cozum, root_cause, kategori)
                       VALUES (?, ?, ?, ?, ?)""",
                    (kayit_id, problem, cozum, root_cause, kategori),
                )
            except sqlite3.OperationalError as e:
                log.warning(f"[cozum_hafizasi] DB yazma hatasi: {e}")
                pass
            conn.commit()
            logger.info("[CozumHafizasi] Kaydedildi: #%d — %s", kayit_id, problem[:60])
            return kayit_id
        finally:
            conn.close()

    # ── GERI BILDIRIM ────────────────────────────────────────────────────

    def geri_bildirim(self, kayit_id: int, basarili: bool) -> dict[str, Any]:
        """Cozumun ise yarayip yaramadigini kaydet.

        Args:
            kayit_id: Cozum kaydinin ID'si
            basarili: True = ise yaradi, False = yaramadi

        Returns:
            Guncellenmis kayit bilgisi
        """
        conn = self._baglan()
        try:
            if basarili:
                conn.execute(
                    "UPDATE cozumler SET success=success+1, last_used=? WHERE id=?",
                    (time.time(), kayit_id),
                )
            else:
                conn.execute(
                    "UPDATE cozumler SET fail=fail+1, last_used=? WHERE id=?",
                    (time.time(), kayit_id),
                )

            # Confidence guncelle
            row = conn.execute(
                "SELECT success, fail FROM cozumler WHERE id=?",
                (kayit_id,),
            ).fetchone()
            if row:
                toplam = row["success"] + row["fail"]
                confidence = round(row["success"] / toplam, 3) if toplam > 0 else 0.5
                conn.execute(
                    "UPDATE cozumler SET confidence=? WHERE id=?",
                    (confidence, kayit_id),
                )

            conn.commit()

            sonuc = dict(
                conn.execute("SELECT * FROM cozumler WHERE id=?", (kayit_id,)).fetchone()
            )
            durum = "✅" if basarili else "❌"
            logger.info(
                "[CozumHafizasi] Geri bildirim #%d: %s (confidence=%.2f)",
                kayit_id, durum, sonuc.get("confidence", 0),
            )
            return sonuc
        finally:
            conn.close()

    # ── DISARI AKTARIM ───────────────────────────────────────────────────

    def json_export(
        self,
        kategori: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> str:
        """Kayitlari JSON formatinda disari aktar.

        Args:
            kategori: Filtre (None = tumu)
            min_confidence: Minimum guven skoru
            limit: Maks kayit sayisi

        Returns:
            JSON string (insan-okunur)
        """
        conn = self._baglan()
        try:
            sorgu = "SELECT * FROM cozumler WHERE confidence >= ?"
            params: list[Any] = [min_confidence]
            if kategori:
                sorgu += " AND kategori=?"
                params.append(kategori)
            sorgu += " ORDER BY confidence DESC, last_used DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sorgu, params).fetchall()
            kayitlar = []
            for r in rows:
                d = dict(r)
                d["created_at"] = datetime.fromtimestamp(
                    d["created_at"], tz=timezone.utc
                ).isoformat()
                d["last_used"] = (
                    datetime.fromtimestamp(d["last_used"], tz=timezone.utc).isoformat()
                    if d["last_used"]
                    else None
                )
                try:
                    d["tags"] = json.loads(d["tags"])
                except (json.JSONDecodeError, TypeError):
                    d["tags"] = []
                try:
                    d["metadata"] = json.loads(d["metadata"])
                except (json.JSONDecodeError, TypeError):
                    d["metadata"] = {}
                kayitlar.append(d)

            return json.dumps(
                {
                    "toplam": len(kayitlar),
                    "kategori_filtre": kategori,
                    "min_confidence": min_confidence,
                    "kayitlar": kayitlar,
                },
                indent=2,
                ensure_ascii=False,
            )
        finally:
            conn.close()

    # ── ISTATISTIK ───────────────────────────────────────────────────────

    def istatistik(self) -> dict[str, Any]:
        """Cozum havuzu istatistikleri."""
        conn = self._baglan()
        try:
            toplam = conn.execute("SELECT COUNT(*) FROM cozumler").fetchone()[0]
            kategoriler = conn.execute(
                "SELECT kategori, COUNT(*) as adet FROM cozumler "
                "WHERE kategori != '' GROUP BY kategori ORDER BY adet DESC"
            ).fetchall()

            basarili = conn.execute(
                "SELECT COUNT(*) FROM cozumler WHERE success > 0"
            ).fetchone()[0]

            ort_confidence = conn.execute(
                "SELECT AVG(confidence) FROM cozumler"
            ).fetchone()[0] or 0.0

            son_kullanim = conn.execute(
                "SELECT COUNT(*) FROM cozumler WHERE last_used > ?",
                (time.time() - 7 * 86400,),
            ).fetchone()[0]

            return {
                "toplam_cozum": toplam,
                "kategoriler": {r["kategori"]: r["adet"] for r in kategoriler},
                "en_az_1_basari": basarili,
                "ortalama_confidence": round(ort_confidence, 3),
                "son_7_gun_kullanilan": son_kullanim,
            }
        finally:
            conn.close()

    def sil(self, kayit_id: int) -> bool:
        """Cozum kaydini sil."""
        conn = self._baglan()
        try:
            cur = conn.execute("DELETE FROM cozumler WHERE id=?", (kayit_id,))
            try:
                conn.execute("DELETE FROM cozumler_fts WHERE rowid=?", (kayit_id,))
            except sqlite3.OperationalError as e:
                log.warning(f"[cozum_hafizasi] DB silme hatasi: {e}")
                pass
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


# ── Modul seviyesi fonksiyonlar (dogrudan erisim) ────────────────────────

_singleton = CozumHafizasi()


def cozum_bul(metin: str, limit: int = 5) -> list[dict[str, Any]]:
    return _singleton.bul(metin, limit)


def cozum_kaydet(
    problem: str, root_cause: str, cozum: str,
    kategori: str = "", tags: list[str] | None = None,
) -> int:
    return _singleton.kaydet(problem, root_cause, cozum, kategori, tags)


def cozum_geri_bildirim(kayit_id: int, basarili: bool) -> dict[str, Any]:
    return _singleton.geri_bildirim(kayit_id, basarili)


# ── Motor kaydi ──────────────────────────────────────────────────────────

def _tool_cozum_bul(**kw) -> str:
    metin = kw.get("metin") or kw.get("sorun") or ""
    if not metin:
        return "[CozumHafizasi] 'metin' parametresi gerekli."
    sonuc = _singleton.bul(metin)
    if not sonuc:
        return "[CozumHafizasi] Bu sorun icin guvenilir bir gecmis cozum yok."
    return json.dumps(sonuc, indent=2, ensure_ascii=False)


def _tool_cozum_kaydet(**kw) -> str:
    problem = kw.get("problem") or ""
    root_cause = kw.get("root_cause") or kw.get("kok_neden") or ""
    cozum = kw.get("cozum") or ""
    kategori = kw.get("kategori") or ""
    if not problem or not cozum:
        return "[CozumHafizasi] 'problem' ve 'cozum' parametreleri zorunlu."
    kayit_id = _singleton.kaydet(problem, root_cause, cozum, kategori)
    return f"[CozumHafizasi] Cozum kaydedildi. ID: {kayit_id}"


def _tool_cozum_geri_bildirim(**kw) -> str:
    try:
        kayit_id = int(kw.get("id") or kw.get("kayit_id") or 0)
    except (ValueError, TypeError):
        return "[CozumHafizasi] Gecersiz ID."
    basarili = str(kw.get("basarili", "true")).lower() in ("true", "1", "evet")
    sonuc = _singleton.geri_bildirim(kayit_id, basarili)
    return (
        f"[CozumHafizasi] Geri bildirim kaydedildi. "
        f"ID: {kayit_id}, Confidence: {sonuc.get('confidence', 0):.2f}"
    )


def _tool_cozum_export(**kw) -> str:
    kategori = kw.get("kategori")
    try:
        min_confidence = float(kw.get("min_confidence", 0.0))
    except (ValueError, TypeError):
        min_confidence = 0.0
    try:
        limit = int(kw.get("limit", 100))
    except (ValueError, TypeError):
        limit = 100
    return _singleton.json_export(kategori, min_confidence, limit)


def _tool_cozum_istatistik(**kw) -> str:
    return json.dumps(_singleton.istatistik(), indent=2, ensure_ascii=False)


def motor_kaydet(motor) -> None:
    """Cozum Hafizasi araclarini motor'a kaydet."""
    motor._plugin_arac_kaydet(
        "COZUM_BUL", _tool_cozum_bul,
        "Cozum hafizasinda sorun ara. Parametreler: metin/sorun (str). "
        "Donus: confidence>=0.6 yuksek, 0.3-0.6 dusuk etiketli, <0.3 gizlenir."
    )
    motor._plugin_arac_kaydet(
        "COZUM_KAYDET", _tool_cozum_kaydet,
        "Yeni cozum kaydet. Parametreler: problem, root_cause/kok_neden, "
        "cozum, kategori"
    )
    motor._plugin_arac_kaydet(
        "COZUM_GERI_BILDIRIM", _tool_cozum_geri_bildirim,
        "Cozumun ise yarayip yaramadigini bildir. "
        "Parametreler: id/kayit_id (int), basarili (bool)"
    )
    motor._plugin_arac_kaydet(
        "COZUM_EKSPORT", _tool_cozum_export,
        "Cozumleri JSON olarak disari aktar. "
        "Parametreler: kategori (str), min_confidence (float), limit (int)"
    )
    motor._plugin_arac_kaydet(
        "COZUM_ISTATISTIK", _tool_cozum_istatistik,
        "Cozum havuzu istatistikleri."
    )
    logger.info("[CozumHafizasi] Motor'a 5 arac kaydedildi")


if __name__ == "__main__":
    # Test
    ch = CozumHafizasi()
    print(json.dumps(ch.istatistik(), indent=2, ensure_ascii=False))
