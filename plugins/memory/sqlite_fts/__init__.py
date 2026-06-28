# -*- coding: utf-8 -*-
"""
plugins/memory/sqlite_fts/__init__.py — SQLite FTS5 Hafıza Plugin'i.

ReYMeN Memory Provider Plugin standardına uygun ReYMeN implementasyonu.
Dış bağımlılık gerektirmez — sadece stdlib SQLite.

Özellikler:
  - FTS5 full-text search (hızlı, token tabanlı)
  - Oturumlar arası kalıcı hafıza (.ReYMeN/memory_fts.db)
  - prefetch(): API çağrısı öncesi ilgili geçmişi getirir
  - tur_senkronize(): tur bittikten sonra arka planda kaydeder (non-blocking)
  - Arama araçları: HAFIZA_ARA, HAFIZA_KAYDET, HAFIZA_LISTELE
"""


__all__ = ['AbstraktHafizaSaglayici', 'Any', 'Dict', 'HafizaPluginKayit', 'List', 'Path', 'SQLiteFTSHafiza', 'ad', 'arac_cagri_isle', 'arac_sema_al', 'baslat', 'kapat', 'kaydet', 'konfig_kaydet', 'konfig_sema_al', 'musait_mi', 'onceden_getir', 'oturum_bitti', 'sistem_prompt_bloku']
import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

from memory_provider import AbstraktHafizaSaglayici, HafizaPluginKayit

logger = logging.getLogger(__name__)

PLUGIN_ADI = "sqlite_fts"
PLUGIN_ACIKLAMA = "SQLite FTS5 tabanlı kalıcı hafıza (bağımlılıksız)"


class SQLiteFTSHafiza(AbstraktHafizaSaglayici):
    """
    SQLite FTS5 ile oturumlar arası tam metin arama hafızası.
    Kurulum gerektirmez; sadece Python stdlib kullanır.
    """

    def __init__(self):
        self._db_yolu: Path | None = None
        self._oturum_id: str = "varsayilan"

    @property
    def ad(self) -> str:
        return PLUGIN_ADI

    def musait_mi(self) -> bool:
        # SQLite her Python kurulumunda mevcut
        try:
            import sqlite3 as _s
            _s.connect(":memory:").execute("CREATE VIRTUAL TABLE t USING fts5(x)").connection.close()
            return True
        except Exception:
            return False

    def baslat(self, oturum_id: str, **kwargs) -> None:
        self._oturum_id = oturum_id
        reymen_dizin = Path(kwargs.get("reymen_dizin", Path(__file__).parent.parent.parent.parent / ".ReYMeN"))
        reymen_dizin.mkdir(parents=True, exist_ok=True)
        self._db_yolu = reymen_dizin / "memory_fts.db"
        self._tablolari_kur()
        logger.info(f"[sqlite_fts] Baslatildi — DB: {self._db_yolu}")

    def _baglan(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self._db_yolu), timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        return con

    def _tablolari_kur(self) -> None:
        con = self._baglan()
        try:
            con.executescript("""
                CREATE VIRTUAL TABLE IF NOT EXISTS hafiza USING fts5(
                    oturum_id,
                    rol,
                    icerik,
                    etiketler UNINDEXED,
                    zaman UNINDEXED
                );
                CREATE TABLE IF NOT EXISTS hafiza_meta (
                    rowid_ref INTEGER PRIMARY KEY,
                    oturum_id TEXT,
                    zaman REAL
                );
            """)
            con.commit()
        finally:
            con.close()

    # ── Araç şemaları ──────────────────────────────────────────────────────

    def arac_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "ad": "HAFIZA_ARA",
                "aciklama": "Geçmiş konuşmalarda FTS5 ile arama yap",
                "parametreler": {
                    "sorgu": {"tur": "str", "aciklama": "Arama metni"},
                    "limit": {"tur": "int", "varsayilan": 5},
                },
            },
            {
                "ad": "HAFIZA_KAYDET",
                "aciklama": "Hafızaya yeni bir giriş kaydet",
                "parametreler": {
                    "icerik": {"tur": "str", "aciklama": "Kaydedilecek metin"},
                    "etiketler": {"tur": "str", "varsayilan": ""},
                },
            },
            {
                "ad": "HAFIZA_LISTELE",
                "aciklama": "Son N hafıza girişini listele",
                "parametreler": {
                    "limit": {"tur": "int", "varsayilan": 10},
                },
            },
        ]

    def arac_cagri_isle(self, arac_adi: str, args: Dict[str, Any], **kwargs) -> str:
        if arac_adi == "HAFIZA_ARA":
            return self._ara(args.get("sorgu", ""), int(args.get("limit", 5)))
        if arac_adi == "HAFIZA_KAYDET":
            return self._manuel_kaydet(args.get("icerik", ""), args.get("etiketler", ""))
        if arac_adi == "HAFIZA_LISTELE":
            return self._listele(int(args.get("limit", 10)))
        return f"Bilinmeyen arac: {arac_adi}"

    # ── Lifecycle hooks ────────────────────────────────────────────────────

    def sistem_prompt_bloku(self) -> str:
        return (
            f"[Hafıza: SQLite FTS5 aktif — DB: {self._db_yolu}]\n"
            "Geçmiş konuşmaları aramak için HAFIZA_ARA, kaydetmek için HAFIZA_KAYDET kullan."
        )

    def onceden_getir(self, sorgu: str) -> str:
        if not sorgu or not self._db_yolu:
            return ""
        sonuclar = self._ara_ham(sorgu, limit=3)
        if not sonuclar:
            return ""
        satirlar = [f"[Hafıza/{r['oturum_id']}] {r['rol']}: {r['icerik'][:200]}" for r in sonuclar]
        return "İlgili hafıza:\n" + "\n".join(satirlar)

    def _tur_senkronize_impl(self, mesajlar: List[Dict[str, Any]]) -> None:
        """Arka plan thread'inde çalışır (non-blocking garantili)."""
        if not self._db_yolu or not mesajlar:
            return
        con = self._baglan()
        try:
            for m in mesajlar:
                rol = m.get("role", "unknown")
                icerik = m.get("content", "")
                if not icerik or not isinstance(icerik, str):
                    continue
                con.execute(
                    "INSERT INTO hafiza(oturum_id, rol, icerik, etiketler, zaman) VALUES (?,?,?,?,?)",
                    (self._oturum_id, rol, icerik, "", str(time.time()))
                )
            con.commit()
        except Exception as e:
            logger.debug(f"[sqlite_fts] tur_senkronize_impl hata: {e}")
        finally:
            con.close()

    def oturum_bitti(self) -> None:
        logger.debug(f"[sqlite_fts] Oturum bitti: {self._oturum_id}")

    def kapat(self) -> None:
        logger.debug(f"[sqlite_fts] Kapatildi.")

    # ── Konfigurasyon ───────────────────────────────────────────────────────

    def konfig_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": "max_kayit",
                "label": "Maksimum hafıza kaydı",
                "secret": False,
                "required": False,
                "default": "50000",
            }
        ]

    def konfig_kaydet(self, degerler: Dict[str, str], reymen_dizin: Path) -> None:
        konfig_dosya = reymen_dizin / "sqlite_fts_konfig.json"
        with open(konfig_dosya, "w", encoding="utf-8") as f:
            json.dump(degerler, f, ensure_ascii=False, indent=2)

    # ── İç metodlar ────────────────────────────────────────────────────────

    def _ara_ham(self, sorgu: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self._db_yolu:
            return []
        con = self._baglan()
        try:
            # FTS5 özel karakterlerini temizle
            guvenli_sorgu = sorgu.replace('"', '""').strip()
            cursor = con.execute(
                "SELECT oturum_id, rol, icerik, zaman FROM hafiza WHERE hafiza MATCH ? ORDER BY rank LIMIT ?",
                (guvenli_sorgu, limit)
            )
            return [
                {"oturum_id": r[0], "rol": r[1], "icerik": r[2], "zaman": r[3]}
                for r in cursor.fetchall()
            ]
        except Exception as e:
            logger.debug(f"[sqlite_fts] FTS hata, LIKE fallback: {e}")
            try:
                cursor = con.execute(
                    "SELECT oturum_id, rol, icerik, zaman FROM hafiza WHERE icerik LIKE ? LIMIT ?",
                    (f"%{sorgu}%", limit)
                )
                return [
                    {"oturum_id": r[0], "rol": r[1], "icerik": r[2], "zaman": r[3]}
                    for r in cursor.fetchall()
                ]
            except Exception:
                return []
        finally:
            con.close()

    def _ara(self, sorgu: str, limit: int = 5) -> str:
        sonuclar = self._ara_ham(sorgu, limit)
        if not sonuclar:
            return f"'{sorgu}' için hafızada sonuç bulunamadı."
        cikti = [f"[{r['oturum_id']}|{r['rol']}] {r['icerik'][:300]}" for r in sonuclar]
        return f"{len(sonuclar)} sonuç:\n" + "\n---\n".join(cikti)

    def _manuel_kaydet(self, icerik: str, etiketler: str = "") -> str:
        if not icerik or not self._db_yolu:
            return "Hata: içerik boş veya DB başlatılmadı."
        con = self._baglan()
        try:
            con.execute(
                "INSERT INTO hafiza(oturum_id, rol, icerik, etiketler, zaman) VALUES (?,?,?,?,?)",
                (self._oturum_id, "kullanici", icerik, etiketler, str(time.time()))
            )
            con.commit()
            return "Hafızaya kaydedildi."
        except Exception as e:
            return f"Kayıt hatası: {e}"
        finally:
            con.close()

    def _listele(self, limit: int = 10) -> str:
        if not self._db_yolu:
            return "DB başlatılmadı."
        con = self._baglan()
        try:
            cursor = con.execute(
                "SELECT oturum_id, rol, icerik, zaman FROM hafiza ORDER BY rowid DESC LIMIT ?",
                (limit,)
            )
            satirlar = cursor.fetchall()
            if not satirlar:
                return "Hafıza boş."
            return "\n".join(
                f"[{r[0]}|{r[1]}|{r[3]}] {r[2][:150]}" for r in satirlar
            )
        except Exception as e:
            return f"Listeleme hatası: {e}"
        finally:
            con.close()


# ── Plugin kayıt giriş noktası ────────────────────────────────────────────

def kaydet(ctx: HafizaPluginKayit) -> None:
    """ReYMeN Memory Provider Plugin standardı — kayıt giriş noktası."""
    ctx.hafiza_saglayici_kaydet(SQLiteFTSHafiza())


if __name__ == "__main__":
    from memory_provider import HafizaPluginKayit
    ctx = HafizaPluginKayit()
    kaydet(ctx)
    aktif = ctx.aktif_saglayici_sec("sqlite_fts", "test-oturum")
    print(f"Aktif: {aktif}, musait: {ctx.aktif_al().musait_mi() if ctx.aktif_al() else False}")
    saglayici = ctx.aktif_al()
    if saglayici:
        print(saglayici.sistem_prompt_bloku())
        print(saglayici.arac_cagri_isle("HAFIZA_KAYDET", {"icerik": "Test hafıza girişi"}))
        print(saglayici.arac_cagri_isle("HAFIZA_ARA", {"sorgu": "test"}))
