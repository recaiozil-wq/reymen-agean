"""Hata â†’ Ã§Ã¶zÃ¼m hafÄ±zasÄ±. SQLite, TTL, doÄŸrulamalÄ± kayÄ±t, soyut imza.

Ä°yileÅŸtirmeler (v2):
- TTL temizlik: Eski Ã§Ã¶zÃ¼mler otomatik temizlenir
- Retry backoff: OgrenmeDongusu'nde Ã¼stel bekleme
- Motor entegrasyonu: motor.calistir() iÃ§inde hata yakalama â†’ ogren()
"""

import sqlite3, hashlib, traceback, re, time, logging
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = Path(".ReYMeN/db/cozum_merkezi.db")  # consolidated: memory.db + hatalar.db + cozum_hafizasi.db + hata_toplama.db
TTL_GUN = 30
TTL_MUAF_BASARI = 3

# Retry backoff ayarlarÄ±
RETRY_TABAN_BEKLEME = 1.0  # saniye
RETRY_MAX_BEKLEME = 30.0  # saniye
RETRY_CARPAN = 2.0  # Ã¼stel

# â”€â”€ BAÄLANTI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@contextmanager
def _db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH), timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def tablo_olustur():
    with _db() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS cozumler (
                imza            TEXT PRIMARY KEY,
                hata_tipi       TEXT NOT NULL,
                hata_ozet       TEXT NOT NULL,
                cozum_kodu      TEXT NOT NULL,
                kaynak_script   TEXT,
                basarili        INTEGER NOT NULL DEFAULT 0,
                basari_sayisi   INTEGER NOT NULL DEFAULT 0,
                son_gorulme     TEXT,
                olusturma_ts    TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_basarili ON cozumler(basarili);
            CREATE INDEX IF NOT EXISTS idx_hata_tipi ON cozumler(hata_tipi);
        """)


# â”€â”€ Ä°MZA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def imza_uret(hata: Exception) -> str:
    """DeÄŸiÅŸken path/deÄŸer kÄ±sÄ±mlarÄ±nÄ± soyutlar:
    FileNotFoundError: /data/x.csv â†’ hata_tipi:/data/<PATH>"""
    hata_tipi = type(hata).__name__
    son_satir = ""
    if hata.__traceback__:
        tb = traceback.extract_tb(hata.__traceback__)
        if tb:
            son_satir = tb[-1].line or ""
    soyut = re.sub(r"'[^']*'", "'<VAL>'", son_satir)
    soyut = re.sub(r"\d+", "<N>", soyut)
    soyut = re.sub(r"/\S+", "/<PATH>", soyut)
    raw = f"{hata_tipi}:{soyut}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# â”€â”€ SORGULA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def cozum_bul(imza: str) -> str | None:
    """BaÅŸarÄ±lÄ± Ã§Ã¶zÃ¼m varsa dÃ¶ndÃ¼r. TTL dolduysa atla (silme)."""
    tablo_olustur()
    with _db() as con:
        row = con.execute(
            """
            SELECT cozum_kodu, basari_sayisi, son_gorulme
            FROM   cozumler
            WHERE  imza = ? AND basarili = 1
        """,
            (imza,),
        ).fetchone()
    if row is None:
        return None
    if row["basari_sayisi"] < TTL_MUAF_BASARI:
        son = datetime.fromisoformat(row["son_gorulme"])
        if datetime.now() - son > timedelta(days=TTL_GUN):
            return None
    return row["cozum_kodu"]


# â”€â”€ KAYDET â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def cozum_kaydet(
    imza: str,
    hata_tipi: str,
    hata_ozet: str,
    cozum_kodu: str,
    kaynak_script: str,
    basarili: bool,
):
    ts = datetime.now().isoformat()
    with _db() as con:
        mevcut = con.execute(
            "SELECT basarili, basari_sayisi FROM cozumler WHERE imza=?", (imza,)
        ).fetchone()
        if mevcut is None:
            con.execute(
                """
                INSERT INTO cozumler
                    (imza, hata_tipi, hata_ozet, cozum_kodu,
                     kaynak_script, basarili, basari_sayisi,
                     son_gorulme, olusturma_ts)
                VALUES (?,?,?,?,?,?,?,?,?)
            """,
                (
                    imza,
                    hata_tipi,
                    hata_ozet[:500],
                    cozum_kodu,
                    kaynak_script,
                    int(basarili),
                    1 if basarili else 0,
                    ts,
                    ts,
                ),
            )
        elif basarili:
            yeni = (mevcut["basari_sayisi"] or 0) + 1
            con.execute(
                """
                UPDATE cozumler
                SET cozum_kodu=?, basarili=1,
                    basari_sayisi=?, son_gorulme=?
                WHERE imza=?
            """,
                (cozum_kodu, yeni, ts, imza),
            )


# â”€â”€ TEMÄ°ZLÄ°K â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def eski_basarisizlari_temizle():
    """30 gÃ¼nden eski, hiÃ§ baÅŸarÄ± almamÄ±ÅŸ kayÄ±tlarÄ± sil."""
    sinir = (datetime.now() - timedelta(days=TTL_GUN)).isoformat()
    with _db() as con:
        silinen = con.execute(
            """
            DELETE FROM cozumler
            WHERE basarili=0 AND basari_sayisi=0 AND olusturma_ts < ?
        """,
            (sinir,),
        ).rowcount
    if silinen:
        logger.info("[hafÄ±za] ğŸ§¹ %d eski kayÄ±t silindi", silinen)
        print(f"[hafÄ±za] ğŸ§¹ {silinen} eski kayÄ±t silindi")


def ttl_temizle():
    """TTL sÃ¼resi dolmuÅŸ tÃ¼m kayÄ±tlarÄ± temizle (baÅŸarÄ±lÄ± dahil).

    BaÅŸari_sayisi >= TTL_MUAF_BASARI olan kayÄ±tlar muaf tutulur
    (Ã§ok kez baÅŸarÄ±lÄ± olmuÅŸ Ã§Ã¶zÃ¼mler kalÄ±cÄ±dÄ±r).
    """
    sinir = (datetime.now() - timedelta(days=TTL_GUN)).isoformat()
    with _db() as con:
        silinen = con.execute(
            """
            DELETE FROM cozumler
            WHERE son_gorulme < ? AND basari_sayisi < ?
        """,
            (sinir, TTL_MUAF_BASARI),
        ).rowcount
    if silinen:
        logger.info("[hafÄ±za] ğŸ§¹ TTL: %d kayÄ±t temizlendi", silinen)
    return silinen


# â”€â”€ Ä°STATÄ°STÄ°K â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def istatistik() -> dict:
    tablo_olustur()
    with _db() as con:
        toplam = con.execute("SELECT COUNT(*) FROM cozumler").fetchone()[0]
        basarili = con.execute(
            "SELECT COUNT(*) FROM cozumler WHERE basarili=1"
        ).fetchone()[0]
    return {"toplam": toplam, "basarili": basarili, "basarisiz": toplam - basarili}


# â”€â”€ RETRY BACKOFF â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def backoff_bekle(deneme: int) -> float:
    """Ãœstel backoff bekleme sÃ¼resi hesapla.

    Args:
        deneme: Deneme sayÄ±sÄ± (1'den baÅŸlar)

    Returns:
        Bekleme sÃ¼resi (saniye)
    """
    bekleme = min(
        RETRY_TABAN_BEKLEME * (RETRY_CARPAN ** (deneme - 1)), RETRY_MAX_BEKLEME
    )
    return bekleme


# â”€â”€ Ã–ÄRENME DÃ–NGÃœSÃœ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class OgrenmeDongusu:
    """Hata â†’ LLM â†’ Ã§Ã¶zÃ¼m â†’ kaydet dÃ¶ngÃ¼sÃ¼.

    Retry backoff ile Ã¼stel bekleme yapar.
    """

    def __init__(self, max_deneme: int = 3):
        self.max_deneme = max_deneme
        self._toplam_ogrenme = 0
        self._basarili_ogrenme = 0

    def ogren(self, hata: Exception, kod: str = "", kaynak: str = "") -> str | None:
        """Bir hatadan Ã¶ÄŸren: imza Ã¼ret, Ã§Ã¶zÃ¼m ara, yoksa LLM'e sor.

        Args:
            hata: Yakalanan exception
            kod: Hata veren kod (opsiyonel)
            kaynak: Script adÄ± (opsiyonel)

        Returns:
            Ã‡Ã¶zÃ¼m kodu veya None
        """
        self._toplam_ogrenme += 1
        imza = imza_uret(hata)
        hata_tipi = type(hata).__name__
        hata_ozet = str(hata)

        # 1. Ã–nce hafÄ±zadan Ã§Ã¶zÃ¼m ara
        mevcut_cozum = cozum_bul(imza)
        if mevcut_cozum:
            logger.info("[Ã¶ÄŸrenme] âœ… HafÄ±zadan Ã§Ã¶zÃ¼m bulundu: %s", imza)
            self._basarili_ogrenme += 1
            return mevcut_cozum

        # 2. LLM'e sor (retry backoff ile)
        for deneme in range(1, self.max_deneme + 1):
            bekleme = backoff_bekle(deneme)
            if deneme > 1:
                logger.info(
                    "[Ã¶ÄŸrenme] â³ Backoff: %.1fs (deneme %d/%d)",
                    bekleme,
                    deneme,
                    self.max_deneme,
                )
                time.sleep(bekleme)

            try:
                from reymen.core.orchestrator import coz_hata

                cozum = coz_hata(hata_ozet, kod, kaynak)

                if cozum and not cozum.startswith("[COZ]"):
                    # Ã‡Ã¶zÃ¼mÃ¼ kaydet
                    cozum_kaydet(
                        imza, hata_tipi, hata_ozet, cozum, kaynak, basarili=True
                    )
                    self._basarili_ogrenme += 1
                    logger.info("[Ã¶ÄŸrenme] âœ… Yeni Ã§Ã¶zÃ¼m kaydedildi: %s", imza)
                    return cozum
            except Exception as e:
                logger.warning("[Ã¶ÄŸrenme] Deneme %d baÅŸarÄ±sÄ±z: %s", deneme, e)
                continue

        # 3. Ã‡Ã¶zÃ¼m bulunamadÄ± â€” baÅŸarÄ±sÄ±z olarak kaydet
        cozum_kaydet(imza, hata_tipi, hata_ozet, "", kaynak, basarili=False)
        logger.warning("[Ã¶ÄŸrenme] âŒ Ã‡Ã¶zÃ¼m bulunamadÄ±: %s", imza)
        return None

    def istatistik(self) -> dict:
        """Ã–ÄŸrenme dÃ¶ngÃ¼sÃ¼ istatistikleri."""
        return {
            "toplam_ogrenme": self._toplam_ogrenme,
            "basarili_ogrenme": self._basarili_ogrenme,
            "basari_orani": (self._basarili_ogrenme / self._toplam_ogrenme * 100)
            if self._toplam_ogrenme > 0
            else 0,
        }


# â”€â”€ MOTOR ENTEGRASYONU â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_ogren(motor, hata: Exception, kod: str = "", kaynak: str = "") -> str | None:
    """Motor.py'den Ã§aÄŸrÄ±lacak Ã¶ÄŸrenme fonksiyonu.

    motor.calistir() iÃ§inde try/except ile yakalanan hatalarÄ±
    Ã¶ÄŸrenme dÃ¶ngÃ¼sÃ¼ne yÃ¶nlendirir.

    Args:
        motor: Motor nesnesi (opsiyonel, log iÃ§in)
        hata: Yakalanan exception
        kod: Hata veren kod
        kaynak: Script/kaynak adÄ±

    Returns:
        Ã‡Ã¶zÃ¼m kodu veya None
    """
    dongu = OgrenmeDongusu(max_deneme=3)
    cozum = dongu.ogren(hata, kod, kaynak)

    if motor and hasattr(motor, "_log"):
        motor._log(
            f"Ã–ÄŸrenme: {type(hata).__name__} â†’ {'Ã§Ã¶zÃ¼ldÃ¼' if cozum else 'Ã§Ã¶zÃ¼lemedi'}"
        )

    return cozum


def motor_ogrenme_istatistik() -> dict:
    """Motor iÃ§in Ã¶ÄŸrenme istatistikleri."""
    ttl_temizle()  # Her Ã§aÄŸrÄ±da TTL temizlik yap
    return istatistik()
