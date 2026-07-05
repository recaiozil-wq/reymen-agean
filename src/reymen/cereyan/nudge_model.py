# -*- coding: utf-8 -*-
"""
nudge_model.py â€” Stealth User Modelling System (ReYMeN Honcho-like)

Silently observes user preferences, response style, technical level,
language preference, and tool usage frequency to build a "user model".
All observations are stored in SQLite under .ReYMeN/nudge_model.db.

Basic flow:
    1. gozlemle(message, response) â†’ processes each interaction, updates model
    2. kullanici_modeli_al() â†’ returns current user model
    3. sistem_prompu_ekle() â†’ text block to append to system prompt
    4. nudge() â†’ returns a context-appropriate reminder/suggestion
    5. rapor_uret() â†’ generates a summary report for the user

Usage:
    from nudge_model import NudgeModel
    nm = NudgeModel()
    nm.gozlemle("merhaba, nasÄ±lsÄ±n?", "iyiyim teÅŸekkürler!")
    model = nm.kullanici_modeli_al()
    prompt_ek = nm.sistem_prompu_ekle()
    hatirlatma = nm.nudge()
    print(nm.rapor_uret())
"""

import json
import logging
import math
import re
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

ROOT = Path(__file__).parent.resolve()
VERITABANI_YOLU = ROOT.parent.parent / ".ReYMeN" / "db" / "cereyan.db"  # consolidated: nudge_model + continuous_learning + steering

# Gozlem limitleri
MAKS_SATIR = 5000  # Veritabaninda en fazla satir
MAKS_GUN = 90  # Kac gunluk veri tutulacak
MAKS_NUDGE = 20  # nudge() dondrugunde en fazla kac oge

# Model agirliklandirma
SON_KONUSMA_AGRILIK = 0.6  # Son konusmalarin agirligi
ESKI_KONUSMA_AGRILIK = 0.4  # Eski konusmalarin agirligi
GUVEN_ESIGI = 3  # Guven puani icin minimum gozlem sayisi

# Stil/teknik/dil sabitleri
STIL_KATEGORILERI = [
    "resmi",
    "samimi",
    "teknik",
    "kisa",
    "detayli",
    "komut",
    "soru",
    "hata_bildirimi",
]

TEKNIK_SEVIYE_ETIKETLERI = {
    1: "cok dusuk",
    2: "dusuk",
    3: "orta",
    4: "yuksek",
    5: "cok yuksek",
}

ARAC_KATEGORILERI = [
    "terminal",
    "dosya_oku",
    "dosya_yaz",
    "ara",
    "web",
    "kod_calistir",
    "diger",
]


# â”€â”€ Yardimci Fonksiyonlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _simdiki_zaman() -> str:
    """ISO formatinda su anki zamani dondur."""
    return datetime.now().isoformat(timespec="seconds")


def _zaman_damgasi() -> float:
    """Unix timestamp dondur."""
    return time.time()


# â”€â”€ NudgeModel Sinifi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class NudgeModel:
    """Gizli kullanici modelleme sistemi.

    Kullanicinin konusma desenlerinden yanit stili, teknik seviye,
    dil tercihi ve arac kullanim sikligi gibi ozellikleri sessizce cikarir.
    Gozlemleri SQLite veritabaninda saklar ve sistem prompt'una enjekte
    edilecek baglam uretir.
    """

    def __init__(self, veritabani_yolu: Optional[Path] = None):
        """NudgeModel baslatici.

        Args:
            veritabani_yolu: SQLite veritabani yolu (None = varsayilan)
        """
        self._vt_yolu = veritabani_yolu or VERITABANI_YOLU
        self._vt_yolu.parent.mkdir(parents=True, exist_ok=True)
        self._baglanti: Optional[sqlite3.Connection] = None
        self._baglan()
        self._tablolari_olustur()
        self._temizle()
        logger.debug("[NudgeModel] Baslatildi: %s", self._vt_yolu)

    # â”€â”€ Veritabani Yonetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _baglan(self) -> sqlite3.Connection:
        """SQLite baglantisi ac (thread-safe caching ile)."""
        if self._baglanti is None:
            self._baglanti = sqlite3.connect(
                str(self._vt_yolu),
                check_same_thread=False,
            )
            self._baglanti.row_factory = sqlite3.Row
            self._baglanti.execute("PRAGMA journal_mode=WAL;")
            self._baglanti.execute("PRAGMA synchronous=NORMAL;")
        return self._baglanti

    def _tablolari_olustur(self):
        """Gerekli veritabani tablolarini olustur."""
        vt = self._baglan()
        vt.executescript("""
            CREATE TABLE IF NOT EXISTS gozlemler (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman           TEXT    NOT NULL,
                zaman_damgasi   REAL    NOT NULL,
                mesaj           TEXT    NOT NULL,
                yanit           TEXT    NOT NULL,
                mesaj_uzunluk   INTEGER DEFAULT 0,
                yanit_uzunluk   INTEGER DEFAULT 0,
                stil_tahmini    TEXT    DEFAULT 'bilinmiyor',
                teknik_seviye   INTEGER DEFAULT 3,
                dil_kodu        TEXT    DEFAULT 'tr',
                arac_kullanimi  TEXT    DEFAULT 'yok',
                duygu_tonu      TEXT    DEFAULT 'notr'
            );

            CREATE TABLE IF NOT EXISTS kullanici_modeli (
                anahtar         TEXT PRIMARY KEY,
                deger           TEXT    NOT NULL,
                guven_puani     REAL    DEFAULT 0.0,
                son_guncelleme  TEXT    NOT NULL,
                gozlem_sayisi   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS nudge_gecmisi (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman           TEXT    NOT NULL,
                tur             TEXT    NOT NULL,
                icerik          TEXT    NOT NULL,
                kullanildi      INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_gozlem_zaman
                ON gozlemler(zaman_damgasi);
            CREATE INDEX IF NOT EXISTS idx_gozlem_stil
                ON gozlemler(stil_tahmini);
            CREATE INDEX IF NOT EXISTS idx_gozlem_dil
                ON gozlemler(dil_kodu);
        """)

    def _calistir(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Guvenli SQL calistirma."""
        vt = self._baglan()
        try:
            return vt.execute(sql, params)
        except sqlite3.Error as e:
            logger.warning("[NudgeModel] SQL hatasi: %s | SQL: %s", e, sql[:100])
            raise

    def _temizle(self):
        """Eski verileri temizle ve satir sinirini uygula."""
        try:
            sinir_damga = _zaman_damgasi() - MAKS_GUN * 86400
            self._calistir(
                "DELETE FROM gozlemler WHERE zaman_damgasi < ?",
                (sinir_damga,),
            )
            self._calistir(
                "DELETE FROM gozlemler WHERE id NOT IN "
                "(SELECT id FROM gozlemler ORDER BY id DESC LIMIT ?)",
                (MAKS_SATIR,),
            )
            self._baglan().commit()
        except Exception as e:
            logger.debug("[NudgeModel] Temizlik hatasi (onemsiz): %s", e)

    # â”€â”€ Gozlem Motoru â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def gozlemle(self, mesaj: str, yanit: str) -> Dict[str, Any]:
        """Bir kullanici-ajan etkilesimini sessizce gozlemler ve isler.

        Konusma stilini, teknik seviyeyi, dil tercihini ve arac kullanimini
        analiz eder, ardindan kullanici modelini gunceller.

        Args:
            mesaj: Kullanicinin gonderdigi mesaj
            yanit: Ajanin urettigi yanit

        Returns:
            Islenmis gozlem verilerini iceren sozluk
        """
        mesaj_uzunluk = len(mesaj.strip())
        yanit_uzunluk = len(yanit.strip())
        simdi = _simdiki_zaman()
        damga = _zaman_damgasi()

        stil = self._stil_tahmin_et(mesaj)
        teknik = self._teknik_seviye_tahmin_et(mesaj)
        dil = self._dil_tespit_et(mesaj)
        arac = self._arac_tespit_et(yanit)
        duygu = self._duygu_tonu_tahmin_et(mesaj)

        self._calistir(
            """INSERT INTO gozlemler
               (zaman, zaman_damgasi, mesaj, yanit, mesaj_uzunluk,
                yanit_uzunluk, stil_tahmini, teknik_seviye, dil_kodu,
                arac_kullanimi, duygu_tonu)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                simdi,
                damga,
                mesaj[:500],
                yanit[:500],
                mesaj_uzunluk,
                yanit_uzunluk,
                stil,
                teknik,
                dil,
                arac,
                duygu,
            ),
        )

        self._model_guncelle("stil", stil)
        self._model_guncelle("teknik_seviye", str(teknik))
        self._model_guncelle("dil", dil)
        self._model_guncelle("son_arac", arac)

        if arac != "yok":
            self._model_sayac_arttir(f"arac_sayisi_{arac}")

        self._model_sayac_arttir("toplam_konusma")
        self._model_sayisal_ekle("toplam_karakter", mesaj_uzunluk)
        self._model_guncelle("son_etkilesim", simdi)

        self._baglan().commit()

        gozlem = {
            "stil": stil,
            "teknik_seviye": teknik,
            "dil": dil,
            "arac": arac,
            "duygu": duygu,
            "mesaj_uzunluk": mesaj_uzunluk,
            "zaman": simdi,
        }
        logger.debug("[NudgeModel] gozlemle: %s", gozlem)
        return gozlem

    # â”€â”€ Ozellik Cikarimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _stil_tahmin_et(self, metin: str) -> str:
        """Mesajin iletisim stilini tahmin et.

        Kategoriler: resmi, samimi, teknik, kisa, detayli, komut, soru, hata_bildirimi
        """
        metin = metin.strip()
        if not metin:
            return "bilinmiyor"

        uzunluk = len(metin)

        if uzunluk < 10:
            return "kisa"

        if metin.endswith("?") or "?" in metin:
            teknik_soru = [
                "kod",
                "api",
                "fonksiyon",
                "hata",
                "error",
                "debug",
                "import",
                "class",
                "def ",
                "neden",
            ]
            if any(k in metin.lower() for k in teknik_soru):
                return "teknik"
            return "soru"

        komut_ifadeleri = [
            "yap",
            "olustur",
            "yaz",
            "goster",
            "sil",
            "calistir",
            "getir",
            "ara",
            "bul",
            "kur",
            "ac",
            "kapat",
            "yukle",
        ]
        ilk_kelime = metin.split()[0].lower() if metin.split() else ""
        if ilk_kelime in komut_ifadeleri:
            return "komut"

        hata_ifadeleri = [
            "hata",
            "error",
            "calismiyor",
            "patladi",
            "olmuyor",
            "sorun",
            "bug",
            "kirik",
            "beklemiyordum",
        ]
        if any(h in metin.lower() for h in hata_ifadeleri):
            return "hata_bildirimi"

        teknik_ifadeler = [
            "implement",
            "refactor",
            "deploy",
            "migration",
            "dependency",
            "config",
            "pipeline",
            "docker",
            "kubernetes",
            "postgres",
            "redis",
            "nginx",
            "localhost",
            "port",
            "endpoint",
        ]
        teknik_sayisi = sum(1 for t in teknik_ifadeler if t in metin.lower())
        if teknik_sayisi >= 2:
            return "teknik"

        resmi_ifadeler = [
            "lutfen",
            "rica",
            "sayin",
            "saygiyla",
            "tesekkur",
            "merhaba",
            "iyi gunler",
            "yardimci olabilir",
            "acaba",
            "mumkun mu",
        ]
        if any(r in metin.lower() for r in resmi_ifadeler) and uzunluk > 50:
            return "resmi"

        if uzunluk > 200:
            return "detayli"

        return "samimi"

    def _teknik_seviye_tahmin_et(self, metin: str) -> int:
        """Kullanicinin teknik bilgi seviyesini 1-5 arasi tahmin et.

        1=cok_dusuk, 2=dusuk, 3=orta, 4=yuksek, 5=cok_yuksek
        """
        if not metin.strip():
            return 3

        metin_lower = metin.lower()
        puan = 0.0

        ileri_teknik = [
            "asenkron",
            "senkronizasyon",
            "paralel",
            "thread",
            "process",
            "deadlock",
            "race condition",
            "memory leak",
            "buffer overflow",
            "dependency injection",
            "ioc",
            "aop",
            "orm",
            "sql injection",
            "ci/cd",
            "devops",
            "microservice",
            "monolith",
            "event driven",
            "message queue",
            "load balancer",
            "horizontal scaling",
            "vertical scaling",
            "sharding",
            "replication",
            "consensus",
            "distributed system",
            "restful",
            "graphql",
            "grpc",
            "websocket",
            "oauth",
            "jwt",
            "ssl/tls",
            "certificate",
            "asymmetric",
            "time complexity",
            "space complexity",
            "big o",
            "recursive",
            "dynamic programming",
            "machine learning",
            "deep learning",
            "neural network",
            "transformer",
            "embedding",
            "vector db",
            "rag",
            "fine tuning",
            "tokenization",
            "inference",
        ]
        for terim in ileri_teknik:
            if terim in metin_lower:
                puan += 2.0
                break

        orta_teknik = [
            "python",
            "java",
            "javascript",
            "typescript",
            "rust",
            "go",
            "c++",
            "c#",
            "ruby",
            "php",
            "shell",
            "bash",
            "powershell",
            "sql",
            "nosql",
            "mongodb",
            "redis",
            "postgresql",
            "mysql",
            "docker",
            "kubernetes",
            "git",
            "github",
            "linux",
            "unix",
            "api",
            "rest",
            "json",
            "xml",
            "yaml",
            "toml",
            "framework",
            "library",
            "kutuphane",
            "paket",
            "modul",
            "fonksiyon",
            "degisken",
            "sinif",
            "nesne",
            "interface",
            "veritabani",
            "sunucu",
            "istemci",
            "backend",
            "frontend",
            "debug",
            "log",
            "test",
            "unit test",
            "integration",
            "deploy",
            "build",
            "compile",
            "runtime",
            "dependency",
            "algoritma",
            "veri yapisi",
            "liste",
            "sozluk",
            "kume",
            "dongu",
            "kosul",
            "hata yakalama",
            "try catch",
        ]
        for terim in orta_teknik:
            if terim in metin_lower:
                puan += 1.0
                break

        if "```" in metin or "`" in metin:
            puan += 1.0

        if re.search(r"[\\/][\w.]+[\\/]", metin):
            puan += 0.5
        if re.search(r"\b\d{1,5}\b", metin):
            puan += 0.5

        kelimeler = metin.split()
        if kelimeler:
            uzun_teknik = sum(1 for k in kelimeler if len(k) > 10)
            if uzun_teknik / len(kelimeler) > 0.15:
                puan += 1.0

        ham = int(round(3 + puan))
        return max(1, min(5, ham))

    def _dil_tespit_et(self, metin: str) -> str:
        """Mesajin hangi dilde yazildigini tahmin et.

        Turkce ve Ingilizce arasinda ayrim yapar.
        """
        if not metin.strip():
            return "tr"

        tr_krk = len(re.findall(r"[cgiisuCGIISU]", metin))
        en_krk = len(re.findall(r"[a-zA-Z]", metin))

        if tr_krk > 0 and (en_krk == 0 or tr_krk / (tr_krk + en_krk + 1) > 0.1):
            return "tr"

        tr_kelimeler = [
            "bir",
            "ve",
            "bu",
            "icin",
            "ile",
            "ama",
            "veya",
            "gibi",
            "kadar",
            "sonra",
            "once",
            "ancak",
            "cunku",
            "eger",
            "her",
            "sey",
            "yani",
            "veya",
            "degil",
            "ne",
            "nasil",
            "neden",
            "nerede",
            "hangi",
        ]
        kelimeler = set(metin.lower().split())
        tr_skor = sum(1 for k in tr_kelimeler if k in kelimeler)

        if tr_skor >= 2:
            return "tr"

        en_krk_skor = len(re.findall(r"[a-zA-Z]", metin))
        if en_krk_skor > 20:
            return "en"
        return "tr"

    def _arac_tespit_et(self, yanit: str) -> str:
        """Yanitta hangi aracin kullanildigini tespit et."""
        yanit_lower = yanit.lower()

        if not yanit.strip():
            return "yok"

        eslesmeler = {
            "terminal": ["[terminal]", "shell", "bash", "$ ", "> ", "exit code"],
            "dosya_oku": ["[dosya_oku]", "read_file", "cat ", "dosya icerigi"],
            "dosya_yaz": ["[dosya_yaz]", "write_file", "write(", "dosyaya yaz"],
            "ara": ["[ara]", "search", "grep", "find ", "araniyor"],
            "web": ["[web]", "http", "fetch", "curl ", "indir"],
            "kod_calistir": ["[kod_calistir]", "run ", "calistir", "exec "],
        }

        en_yuksek = ("yok", 0)
        for arac, anahtarlar in eslesmeler.items():
            skor = sum(1 for a in anahtarlar if a in yanit_lower)
            if skor > en_yuksek[1]:
                en_yuksek = (arac, skor)

        return en_yuksek[0] if en_yuksek[1] > 0 else "diger"

    def _duygu_tonu_tahmin_et(self, metin: str) -> str:
        """Mesajin duygu tonunu tahmin et."""
        if not metin.strip():
            return "notr"

        metin_lower = metin.lower()
        pozitif = [
            "tesekkur",
            "harika",
            "mukemmel",
            "guzel",
            "super",
            "cok iyi",
            "ellerine saglik",
            "helal",
            "muhtesem",
            "tam istedigim",
            "calisti",
            "oldu",
            "basardin",
        ]
        negatif = [
            "hata",
            "kotu",
            "berbat",
            "ise yaramaz",
            "olmuyor",
            "calismiyor",
            "patladi",
            "yapma",
            "hayir",
            "degil",
            "duzel",
            "tekrar",
            "bozuk",
            "yanlis",
        ]
        acil = [
            "hemen",
            "acil",
            "cabuk",
            "lutfen yardim",
            "kritik",
            "patladi",
            "durdu",
            "oldu",
            "coktu",
        ]

        if any(a in metin_lower for a in acil):
            return "acil"
        if any(n in metin_lower for n in negatif):
            return "negatif"
        if any(p in metin_lower for p in pozitif):
            return "pozitif"
        return "notr"

    # â”€â”€ Model Yonetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _model_guncelle(self, anahtar: str, deger: str):
        """Kullanici modelinde bir anahtari guncelle (veya ekle)."""
        simdi = _simdiki_zaman()
        mevcut = self._model_oku(anahtar)

        if mevcut:
            yeni_guven = min(1.0, mevcut["guven_puani"] + 0.1)
            yeni_sayi = mevcut["gozlem_sayisi"] + 1
            self._calistir(
                """UPDATE kullanici_modeli SET
                   deger = ?, guven_puani = ?,
                   son_guncelleme = ?, gozlem_sayisi = ?
                   WHERE anahtar = ?""",
                (deger, yeni_guven, simdi, yeni_sayi, anahtar),
            )
        else:
            self._calistir(
                """INSERT INTO kullanici_modeli
                   (anahtar, deger, guven_puani, son_guncelleme, gozlem_sayisi)
                   VALUES (?, ?, ?, ?, ?)""",
                (anahtar, deger, 0.2, simdi, 1),
            )

    def _model_oku(self, anahtar: str) -> Optional[Dict[str, Any]]:
        """Kullanici modelinden bir anahtari oku."""
        cursor = self._calistir(
            "SELECT * FROM kullanici_modeli WHERE anahtar = ?", (anahtar,)
        )
        satir = cursor.fetchone()
        if satir:
            return dict(satir)
        return None

    def _model_sayac_arttir(self, anahtar: str, miktar: int = 1):
        """Bir sayac degerini arttir."""
        simdi = _simdiki_zaman()
        mevcut = self._model_oku(anahtar)

        if mevcut:
            yeni_deger = int(mevcut["deger"]) + miktar
            yeni_guven = min(1.0, mevcut["guven_puani"] + 0.05)
            yeni_sayi = mevcut["gozlem_sayisi"] + 1
            self._calistir(
                """UPDATE kullanici_modeli SET
                   deger = ?, guven_puani = ?,
                   son_guncelleme = ?, gozlem_sayisi = ?
                   WHERE anahtar = ?""",
                (str(yeni_deger), yeni_guven, simdi, yeni_sayi, anahtar),
            )
        else:
            self._calistir(
                """INSERT INTO kullanici_modeli
                   (anahtar, deger, guven_puani, son_guncelleme, gozlem_sayisi)
                   VALUES (?, ?, ?, ?, ?)""",
                (anahtar, str(miktar), 0.1, simdi, 1),
            )

    def _model_sayisal_ekle(self, anahtar: str, deger: int):
        """Bir sayisal degeri modele ekle (toplama)."""
        simdi = _simdiki_zaman()
        mevcut = self._model_oku(anahtar)

        if mevcut:
            yeni_deger = int(mevcut["deger"]) + deger
            yeni_sayi = mevcut["gozlem_sayisi"] + 1
            self._calistir(
                """UPDATE kullanici_modeli SET
                   deger = ?, guven_puani = ?,
                   son_guncelleme = ?, gozlem_sayisi = ?
                   WHERE anahtar = ?""",
                (str(yeni_deger), mevcut["guven_puani"], simdi, yeni_sayi, anahtar),
            )
        else:
            self._calistir(
                """INSERT INTO kullanici_modeli
                   (anahtar, deger, guven_puani, son_guncelleme, gozlem_sayisi)
                   VALUES (?, ?, ?, ?, ?)""",
                (anahtar, str(deger), 0.2, simdi, 1),
            )

    # â”€â”€ Kullanici Modeli Sorgulama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def kullanici_modeli_al(self) -> Dict[str, Any]:
        """Mevcut kullanici modelini guven puanlariyla dondur.

        Returns:
            Kullanici profili sozlugu. Her ozellik icin deger ve guven puani icerir.
        """
        model = {
            "stil": {"deger": "samimi", "guven": 0.0},
            "teknik_seviye": {"deger": 3, "guven": 0.0},
            "dil": {"deger": "tr", "guven": 0.0},
            "toplam_konusma": 0,
            "toplam_karakter": 0,
            "son_etkilesim": None,
            "arac_kullanim": {},
            "duygu_profili": {},
        }

        cursor = self._calistir("SELECT * FROM kullanici_modeli")
        for satir in cursor.fetchall():
            anahtar = satir["anahtar"]
            deger = satir["deger"]
            guven = satir["guven_puani"]
            sayi = satir["gozlem_sayisi"]

            if anahtar in ("stil", "dil", "son_etkilesim"):
                if anahtar == "son_etkilesim":
                    model[anahtar] = deger
                else:
                    model[anahtar] = {
                        "deger": deger,
                        "guven": round(guven, 2),
                        "gozlem_sayisi": sayi,
                    }
            elif anahtar == "teknik_seviye":
                model[anahtar] = {
                    "deger": int(deger),
                    "guven": round(guven, 2),
                    "gozlem_sayisi": sayi,
                }
            elif anahtar.startswith("arac_sayisi_"):
                arac_adi = anahtar.replace("arac_sayisi_", "")
                model["arac_kullanim"][arac_adi] = {
                    "sayi": int(deger),
                    "guven": round(guven, 2),
                }
            elif anahtar in ("toplam_konusma", "toplam_karakter"):
                model[anahtar] = int(deger)

        cursor = self._calistir(
            "SELECT duygu_tonu, COUNT(*) as sayi FROM gozlemler GROUP BY duygu_tonu"
        )
        toplam = 0
        for satir in cursor.fetchall():
            ton = satir["duygu_tonu"]
            sayi = satir["sayi"]
            model["duygu_profili"][ton] = sayi
            toplam += sayi
        if toplam > 0:
            for ton in model["duygu_profili"]:
                model["duygu_profili"][ton] = {
                    "sayi": model["duygu_profili"][ton],
                    "oran": round(model["duygu_profili"][ton] / toplam, 3),
                }

        if model["arac_kullanim"]:
            en_sik = max(model["arac_kullanim"].items(), key=lambda x: x[1]["sayi"])
            model["en_sik_arac"] = en_sik[0]

        return model

    def _teknik_seviye_etiketi(self, seviye: int) -> str:
        """Teknik seviye sayisinietikete cevir."""
        return TEKNIK_SEVIYE_ETIKETLERI.get(seviye, "bilinmiyor")

    def _stil_tutarlilik(self) -> float:
        """Kullanicinin stilde ne kadar tutarli oldugunu 0-1 arasi dondur."""
        cursor = self._calistir(
            "SELECT stil_tahmini, COUNT(*) as sayi FROM gozlemler "
            "GROUP BY stil_tahmini ORDER BY sayi DESC LIMIT 3"
        )
        toplam = 0
        en_yuksek = 0
        for satir in cursor.fetchall():
            toplam += satir["sayi"]
            if satir["sayi"] > en_yuksek:
                en_yuksek = satir["sayi"]
        if toplam == 0:
            return 0.0
        return round(en_yuksek / toplam, 2)

    # â”€â”€ Sistem Prompt Enjeksiyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def sistem_prompu_ekle(self) -> str:
        """Kullanici modeline dayali sistem prompt blogu uretir.

        Returns:
            Sistem prompt'una eklenecek formatli metin (bos da olabilir).
        """
        model = self.kullanici_modeli_al()
        bolumler = []

        toplam = model.get("toplam_konusma", 0)
        if toplam == 0:
            return ""

        stil = model.get("stil", {})
        if isinstance(stil, dict) and stil.get("guven", 0) >= 0.3:
            etiket = stil["deger"]
            if etiket == "teknik":
                etiket = "teknik detaylara onem veren"
            elif etiket == "kisa":
                etiket = "kisa ve oz"
            elif etiket == "resmi":
                etiket = "resmi ve nazik"
            elif etiket == "samimi":
                etiket = "samimi ve dogal"
            elif etiket == "komut":
                etiket = "dogrudan komut"
            bolumler.append(
                f"Kullanici genellikle **{etiket}** bir iletisim stili kullaniyor."
            )

        teknik = model.get("teknik_seviye", {})
        if isinstance(teknik, dict) and teknik.get("guven", 0) >= 0.3:
            etiket = self._teknik_seviye_etiketi(teknik["deger"])
            bolumler.append(
                f"Kullanicinin teknik bilgi seviyesi: **{etiket}** "
                f"(seviye {teknik['deger']}/5)."
            )

        dil = model.get("dil", {})
        if isinstance(dil, dict) and dil.get("guven", 0) >= 0.3:
            dil_adi = "Turkce" if dil["deger"] == "tr" else "Ingilizce"
            bolumler.append(f"Dil tercihi: **{dil_adi}**.")

        arac_model = model.get("arac_kullanim", {})
        if arac_model:
            en_sik = model.get("en_sik_arac", "diger")
            arac_etiket = {
                "terminal": "terminal komutlari",
                "dosya_oku": "dosya okuma",
                "dosya_yaz": "dosya yazma",
                "ara": "arama",
                "web": "web erisimi",
                "kod_calistir": "kod calistirma",
            }.get(en_sik, en_sik)
            toplam_arac = sum(v["sayi"] for v in arac_model.values())
            bolumler.append(
                f"En sik kullanilan arac: **{arac_etiket}** "
                f"({toplam} konusmada {toplam_arac} arac kullanimi)."
            )

        duygu = model.get("duygu_profili", {})
        if duygu:
            toplam_duygu = sum(v["sayi"] for v in duygu.values())
            if toplam_duygu >= 5:
                pozitif = duygu.get("pozitif", {}).get("sayi", 0)
                negatif = duygu.get("negatif", {}).get("sayi", 0)
                acil = duygu.get("acil", {}).get("sayi", 0)
                if negatif + acil > pozitif and (negatif + acil) > 3:
                    bolumler.append(
                        "Kullanici son zamanlarda sik hata/aksaklik bildiriyor. "
                        "Cozum odakli ve sabirli yanit ver."
                    )

        tutarlilik = self._stil_tutarlilik()
        if tutarlilik > 0.5:
            bolumler.append(
                f"Kullanici davranisi **%{int(tutarlilik * 100)}** oraninda tutarli."
            )

        if not bolumler:
            return ""

        baslik = "KULLANICI MODELI (gizli gozlemlerle olusturuldu)"
        govde = "\n".join(f"- {b}" for b in bolumler)
        return f"\n\n{baslik}\n{govde}\n"

    # â”€â”€ Nudge Sistemi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def nudge(self) -> List[Dict[str, Any]]:
        """Mevcut duruma gore ilgili bir hatirlatma/oneri dondur.

        Kullanici modeline ve son gozlemlere dayanarak baglama uygun
        en fazla MAKS_NUDGE kadar "nudge" (durtme/oneri) listeler.

        Returns:
            Her biri {"tur": str, "icerik": str, "guven": float} olan nudge listesi.
        """
        nudges = []
        model = self.kullanici_modeli_al()
        toplam_konusma = model.get("toplam_konusma", 0)

        if toplam_konusma == 0:
            return nudges

        stil = model.get("stil", {})
        if isinstance(stil, dict) and stil.get("guven", 0) > 0.5:
            if stil["deger"] == "teknik" and toplam_konusma > 5:
                nudges.append(
                    {
                        "tur": "stil_uyari",
                        "icerik": "Kullanici teknik detaylari tercih ediyor "
                        "yanitlarda spesifik ol.",
                        "guven": stil["guven"],
                    }
                )
            elif stil["deger"] == "kisa":
                nudges.append(
                    {
                        "tur": "stil_uyari",
                        "icerik": "Kullanici kisa yanitlari tercih ediyor " "ozlu ol.",
                        "guven": stil["guven"],
                    }
                )

        teknik = model.get("teknik_seviye", {})
        if isinstance(teknik, dict) and teknik.get("guven", 0) > 0.4:
            if teknik["deger"] <= 2:
                nudges.append(
                    {
                        "tur": "teknik_seviye",
                        "icerik": "Kullanici dusuk teknik seviyede "
                        "jargon kullanma basit acikla.",
                        "guven": teknik["guven"],
                    }
                )
            elif teknik["deger"] >= 4:
                nudges.append(
                    {
                        "tur": "teknik_seviye",
                        "icerik": "Kullanici ileri teknik seviyede "
                        "detayli teknik aciklama yapabilirsin.",
                        "guven": teknik["guven"],
                    }
                )

        dil = model.get("dil", {})
        if isinstance(dil, dict) and dil.get("guven", 0) > 0.5:
            dil_sembol = "Turkce" if dil["deger"] == "tr" else "Ingilizce"
            nudges.append(
                {
                    "tur": "dil_tercihi",
                    "icerik": f"Kullanici tercih ettigi dil: {dil_sembol}.",
                    "guven": dil["guven"],
                }
            )

        duygu = model.get("duygu_profili", {})
        if duygu:
            toplam_duygu = sum(v["sayi"] for v in duygu.values())
            if toplam_duygu >= 3:
                negatif_oran = duygu.get("negatif", {}).get("oran", 0)
                if negatif_oran > 0.4:
                    nudges.append(
                        {
                            "tur": "duygu_uyari",
                            "icerik": "Kullanici son zamanlarda sik "
                            "olumsuz geribildirim veriyor. Cozum odakli ol.",
                            "guven": min(0.8, negatif_oran),
                        }
                    )

        arac_model = model.get("arac_kullanim", {})
        if arac_model and sum(v["sayi"] for v in arac_model.values()) > 10:
            nadir_araclar = [k for k, v in arac_model.items() if v["sayi"] == 1]
            if nadir_araclar:
                nudges.append(
                    {
                        "tur": "arac_kesfi",
                        "icerik": f"Kullanici '{nadir_araclar[0]}' aracini "
                        f"sadece 1 kere kullandi belki tanitmak "
                        f"faydali olabilir.",
                        "guven": 0.3,
                    }
                )

        son_etkilesim = model.get("son_etkilesim")
        if son_etkilesim:
            try:
                son = datetime.fromisoformat(son_etkilesim)
                fark = datetime.now() - son
                if fark > timedelta(hours=24):
                    nudges.append(
                        {
                            "tur": "zaman_uyari",
                            "icerik": f"Kullanici son {int(fark.total_seconds() / 3600)} "
                            f"saattir yeni bir konu acmamis.",
                            "guven": 0.5,
                        }
                    )
            except (ValueError, TypeError):
                logger.warning("[fix_01_sessiz_except] Exception")

        if toplam_konusma >= 10:
            cursor = self._calistir(
                "SELECT arac_kullanimi, COUNT(*) as sayi "
                "FROM gozlemler WHERE arac_kullanimi != 'yok' "
                "GROUP BY arac_kullanimi ORDER BY sayi DESC"
            )
            arac_satirlari = cursor.fetchall()
            if len(arac_satirlari) >= 2:
                en_cok = arac_satirlari[0]["sayi"]
                en_az = arac_satirlari[-1]["sayi"]
                if en_cok > en_az * 3 and en_az > 0:
                    nudges.append(
                        {
                            "tur": "desen_kesfi",
                            "icerik": f"Kullanici '{arac_satirlari[0]['arac_kullanimi']}' "
                            f"aracini '{arac_satirlari[-1]['arac_kullanimi']}' "
                            f"aracina kiyasla {en_cok // en_az} kat "
                            f"daha fazla kullaniyor.",
                            "guven": 0.4,
                        }
                    )

        nudges.sort(key=lambda x: x["guven"], reverse=True)

        simdi = _simdiki_zaman()
        for n in nudges[:MAKS_NUDGE]:
            self._calistir(
                "INSERT INTO nudge_gecmisi (zaman, tur, icerik) VALUES (?, ?, ?)",
                (simdi, n["tur"], n["icerik"]),
            )
        self._baglan().commit()

        return nudges[:MAKS_NUDGE]

    # â”€â”€ Raporlama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def rapor_uret(self) -> str:
        """Kullanici modelinin ozet raporunu uretir.

        Kullaniciya kendisi hakkinda neler ogrenildigini seffafca gosterir.

        Returns:
            Insan tarafindan okunabilir rapor metni.
        """
        model = self.kullanici_modeli_al()
        toplam = model.get("toplam_konusma", 0)

        if toplam == 0:
            return (
                "Kullanici Modeli Raporu\n\n"
                "Henuz yeterli gozlem verisi yok.\n"
                "Birkac konusma sonra tekrar dene."
            )

        satirlar = []
        satirlar.append("Kullanici Modeli Raporu")
        satirlar.append(f"Tarih: {datetime.now().strftime('%d %B %Y %H:%M')}")
        satirlar.append("")
        satirlar.append(f"Toplam Konusma: {toplam}")
        satirlar.append(f"Toplam Karakter: {model.get('toplam_karakter', 0):,}")
        satirlar.append(f"Stil Tutarliligi: %{int(self._stil_tutarlilik() * 100)}")
        satirlar.append("")

        stil = model.get("stil", {})
        if isinstance(stil, dict):
            satirlar.append(
                f"Iletisim Stili: {stil.get('deger', '?')} "
                f"(guven: %{int(stil.get('guven', 0) * 100)})"
            )

        teknik = model.get("teknik_seviye", {})
        if isinstance(teknik, dict):
            etiket = self._teknik_seviye_etiketi(teknik.get("deger", 3))
            satirlar.append(
                f"Teknik Seviye: {etiket} ({teknik.get('deger', '?')}/5, "
                f"guven: %{int(teknik.get('guven', 0) * 100)})"
            )

        dil = model.get("dil", {})
        if isinstance(dil, dict):
            dil_adi = "Turkce" if dil.get("deger") == "tr" else "Ingilizce"
            satirlar.append(
                f"Dil Tercihi: {dil_adi} " f"(guven: %{int(dil.get('guven', 0) * 100)})"
            )

        satirlar.append("")

        arac_model = model.get("arac_kullanim", {})
        if arac_model:
            satirlar.append("Arac Kullanim Dagitimi:")
            for arac, bilgi in sorted(
                arac_model.items(), key=lambda x: x[1]["sayi"], reverse=True
            ):
                bar = chr(9608) * min(bilgi["sayi"], 20)
                satirlar.append(f"  {arac}: {bilgi['sayi']} {bar}")

        satirlar.append("")

        duygu = model.get("duygu_profili", {})
        if duygu:
            satirlar.append("Duygu Profili:")
            for ton, bilgi in duygu.items():
                bar = chr(9616) * int(bilgi.get("oran", 0) * 10)
                satirlar.append(f"  {ton}: %{int(bilgi.get('oran', 0) * 100)} {bar}")

        satirlar.append("")

        cursor = self._calistir(
            "SELECT COUNT(*) as sayi FROM nudge_gecmisi WHERE kullanildi = 0"
        )
        satir = cursor.fetchone()
        if satir and satir["sayi"] > 0:
            satirlar.append(f"Bekleyen Nudge: {satir['sayi']} adet")

        return "\n".join(satirlar)

    # â”€â”€ Yardimci Metodlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def veri_durumu(self) -> Dict[str, Any]:
        """Veritabanindaki veri durumu hakkinda bilgi dondur."""
        durum = {}
        try:
            cursor = self._calistir("SELECT COUNT(*) as sayi FROM gozlemler")
            durum["gozlem_sayisi"] = cursor.fetchone()["sayi"]

            cursor = self._calistir("SELECT COUNT(*) as sayi FROM kullanici_modeli")
            durum["model_ozellik_sayisi"] = cursor.fetchone()["sayi"]

            cursor = self._calistir("SELECT COUNT(*) as sayi FROM nudge_gecmisi")
            durum["nudge_sayisi"] = cursor.fetchone()["sayi"]

            cursor = self._calistir(
                "SELECT MIN(zaman_damgasi) as en_eski, "
                "MAX(zaman_damgasi) as en_yeni FROM gozlemler"
            )
            satir = cursor.fetchone()
            if satir and satir["en_eski"]:
                durum["en_eski_gozlem"] = datetime.fromtimestamp(
                    satir["en_eski"]
                ).isoformat()
                durum["en_yeni_gozlem"] = datetime.fromtimestamp(
                    satir["en_yeni"]
                ).isoformat()
        except Exception as e:
            durum["hata"] = str(e)

        vt_boyut = self._vt_yolu.stat().st_size if self._vt_yolu.exists() else 0
        durum["veritabani_boyut"] = f"{vt_boyut / 1024:.1f} KB"
        return durum

    def sifirla(self):
        """Tum gozlem ve model verilerini sil. (Test/geri alma icin)"""
        for tablo in ["gozlemler", "kullanici_modeli", "nudge_gecmisi"]:
            self._calistir(f"DELETE FROM {tablo}")
        self._baglan().commit()
        logger.info("[NudgeModel] Tum veriler sifirlandi.")

    def kapat(self):
        """Baglantiyi kapat."""
        if self._baglanti:
            self._baglanti.close()
            self._baglanti = None


# â”€â”€ Global Ornek â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_nudge_model_ornegi: Optional[NudgeModel] = None


def nudge_model_al() -> NudgeModel:
    """Global NudgeModel ornegi al (singleton)."""
    global _nudge_model_ornegi
    if _nudge_model_ornegi is None:
        _nudge_model_ornegi = NudgeModel()
    return _nudge_model_ornegi


# â”€â”€ Dogrudan Calistirma / Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s | %(message)s",
        stream=sys.stdout,
    )

    print("=" * 60)
    print("NudgeModel  Gizli  Kullanici Modelleme  Sistemi")
    print("=" * 60)

    nm = NudgeModel()

    test_konusmalar = [
        (
            "merhaba chatbot, nasilsin?",
            "iyiyim tesekkurler, sana nasil yardimci olabilirim?",
        ),
        (
            "bir python script'i yaz, dosyalari okuyup JSON'a cevirsin",
            "```python\nimport json\n...``` terminal ile calistirabilirsin.",
        ),
        ("terminal ciktisini kontrol edelim", "[terminal] cikti: basarili"),
        ("hata aliyorum, neden calismiyor?", "[hata] dosya bulunamadi..."),
        ("tesekkurler, harika oldu!", "rica ederim, baska bir sey var mi?"),
        ("hayir, her zaman UTF-8 kullan", "not edildi, UTF-8 kullanacagim."),
        (
            "su API endpoint'ini dene, port 3000'de",
            "http://localhost:3000/api'ye istek atiyorum...",
        ),
        ("bu projeyi dockerize et", "Dockerfile olusturuluyor..."),
        (
            "lutfen su kodu refactor eder misin?",
            "tabii, dependency injection ile yeniden yazalim...",
        ),
        (
            "cok tesekkur ederim, mukemmel bir cozum oldu!",
            "ne demek, yardimci olabildiysem ne mutlu!",
        ),
    ]

    print(f"\n> {len(test_konusmalar)} test konusmasi isleniyor...\n")
    for i, (mesaj, yanit) in enumerate(test_konusmalar, 1):
        gozlem = nm.gozlemle(mesaj, yanit)
        print(
            f"  [{i}] Stil={gozlem['stil']:>10} "
            f"| Teknik={gozlem['teknik_seviye']} "
            f"| Dil={gozlem['dil']} "
            f"| Arac={gozlem['arac']:>12} "
            f"| Duygu={gozlem['duygu']:>8}"
        )

    print("\n" + "-" * 60)
    print(nm.rapor_uret())

    print("\n" + "-" * 60)
    print("SISTEM PROMPT EKI:")
    prompt_ek = nm.sistem_prompu_ekle()
    print(prompt_ek if prompt_ek else "(yeterli veri yok)")

    print("\n" + "-" * 60)
    print("NUDGE CIKTILARI:")
    hatirlatmalar = nm.nudge()
    if hatirlatmalar:
        for h in hatirlatmalar:
            print(f"  [{h['tur']}] (guven: %{int(h['guven'] * 100)}) " f"{h['icerik']}")
    else:
        print("  (henuz nudge uretilemedi)")

    print("\n" + "-" * 60)
    print("KULLANICI MODELI (ham):")
    model = nm.kullanici_modeli_al()
    for anahtar, deger in model.items():
        if isinstance(deger, dict):
            print(f"  {anahtar}: {json.dumps(deger, ensure_ascii=False)}")
        else:
            print(f"  {anahtar}: {deger}")

    print("\n" + "-" * 60)
    print("VERI DURUMU:")
    durum = nm.veri_durumu()
    for k, v in durum.items():
        print(f"  {k}: {v}")

    print("\n" + "-" * 60)
    print("Test verileri temizleniyor...")
    nm.sifirla()
    print("Temizlendi.")
    nm.kapat()
    print("\nTest tamamlandi.")
