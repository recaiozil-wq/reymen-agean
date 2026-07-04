"""Ogvenme hafizasi - OnceHafiza benzeri SQLite."""
import json, os, sqlite3, time
from pathlib import Path

DB_DIR = Path.home() / ".deepseek_ajan"
DB_FILE = DB_DIR / "hafiza.db"
_TTL = 30 * 24 * 3600
_MAX_KAYIT = 5000

def _db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS ogrenmeler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imza TEXT UNIQUE NOT NULL,
        hedef TEXT NOT NULL,
        cozum TEXT NOT NULL,
        kaynak TEXT DEFAULT 'kullanici',
        guven REAL DEFAULT 0.5,
        basari INTEGER DEFAULT 0,
        hata INTEGER DEFAULT 0,
        tarih INTEGER DEFAULT 0,
        kategori TEXT DEFAULT ''
    )""")
    conn.execute("""CREATE INDEX IF NOT EXISTS idx_ogrenmeler_imza ON ogrenmeler(imza)""")
    conn.execute("""CREATE INDEX IF NOT EXISTS idx_ogrenmeler_hedef ON ogrenmeler(hedef)""")
    conn.commit()
    return conn

def imza_uret(hedef, detay=""):
    h = str(hash(hedef + detay))
    return h

def hafizada_ara(hedef, esik=0.5):
    conn = _db()
    cur = conn.execute(
        "SELECT hedef, cozum, kaynak, guven, basari, hata, kategori FROM ogrenmeler WHERE hedef LIKE ?",
        (f"%{hedef}%",)
    )
    sonuc = []
    for row in cur.fetchall():
        sonuc.append({
            "hedef": row[0], "cozum": row[1], "kaynak": row[2],
            "guven": row[3], "basari": row[4], "hata": row[5], "kategori": row[6]
        })
    conn.close()
    sonuc.sort(key=lambda x: x["guven"], reverse=True)
    return sonuc[:5] if sonuc else []

def kaydet(hedef, cozum, kaynak="kullanici", kategori="", guven=0.5):
    imz = imza_uret(hedef, cozum[:50])
    conn = _db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO ogrenmeler (imza, hedef, cozum, kaynak, guven, tarih, kategori) VALUES (?,?,?,?,?,?,?)",
            (imz, hedef, cozum, kaynak, guven, int(time.time()), kategori)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def basari_kaydet(hedef):
    conn = _db()
    conn.execute("UPDATE ogrenmeler SET basari=basari+1, guven=MIN(guven+0.1, 1.0) WHERE hedef=?", (hedef,))
    conn.commit()
    conn.close()

def hata_kaydet(hedef):
    conn = _db()
    conn.execute("UPDATE ogrenmeler SET hata=hata+1, guven=guven-0.1 WHERE hedef=?", (hedef,))
    conn.commit()
    conn.close()

def temizle():
    """TTL asimi ve max kayit siniri kontrolu."""
    conn = _db()
    cutoff = int(time.time()) - _TTL
    conn.execute("DELETE FROM ogrenmeler WHERE tarih < ? AND tarih > 0 AND basari < 3", (cutoff,))
    cur = conn.execute("SELECT COUNT(*) FROM ogrenmeler")
    count = cur.fetchone()[0]
    if count > _MAX_KAYIT:
        conn.execute(
            "DELETE FROM ogrenmeler WHERE id IN (SELECT id FROM ogrenmeler ORDER BY guven ASC, basari ASC LIMIT ?)",
            (count - _MAX_KAYIT,))
    conn.commit()
    conn.close()

def istatistik():
    conn = _db()
    cur = conn.execute("SELECT COUNT(*), COALESCE(SUM(basari),0), COALESCE(SUM(hata),0) FROM ogrenmeler")
    row = cur.fetchone()
    conn.close()
    return {"kayit": row[0], "basari": row[1], "hata": row[2]}
# --- Vektor Hafiza (ChromaDB) ---

import chromadb
from sentence_transformers import SentenceTransformer

_VEKTOR_DB = None
_VEKTOR_MODEL = None
_VEKTOR_KOLEKSIYON = None

def _v_get():
    global _VEKTOR_DB, _VEKTOR_MODEL, _VEKTOR_KOLEKSIYON
    if _VEKTOR_DB is not None:
        return _VEKTOR_DB, _VEKTOR_MODEL, _VEKTOR_KOLEKSIYON
    try:
        _VEKTOR_DB = chromadb.Client(chromadb.config.Settings(
            persist_directory=str(DB_DIR / "chroma"),
            anonymized_telemetry=False
        ))
        _VEKTOR_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        _VEKTOR_KOLEKSIYON = _VEKTOR_DB.get_or_create_collection(
            name="cozumler",
            metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        _VEKTOR_DB = None
    return _VEKTOR_DB, _VEKTOR_MODEL, _VEKTOR_KOLEKSIYON


def vektor_ekle(hedef, cozum, kaynak="kullanici", kategori=""):
    """Cozumu vektor DB'ye ekle."""
    db, model, koleksiyon = _v_get()
    if db is None:
        return False
    try:
        metin = f"{hedef} {cozum}"
        embedding = model.encode(metin).tolist()
        doc_id = imza_uret(hedef, cozum[:50])
        koleksiyon.add(
            embeddings=[embedding],
            documents=[cozum],
            metadatas=[{"hedef": hedef, "kaynak": kaynak, "kategori": kategori}],
            ids=[doc_id]
        )
        return True
    except Exception:
        return False


def vektor_ara(sorgu, n_results=5, esik=0.3):
    """Vektor DB'de semantik arama."""
    db, model, koleksiyon = _v_get()
    if db is None:
        return []
    try:
        sorgu_emb = model.encode(sorgu).tolist()
        sonuc = koleksiyon.query(
            query_embeddings=[sorgu_emb],
            n_results=n_results
        )
        # Sonuclari esik degerine gore filtrele
        donen = []
        if sonuc and sonuc.get("ids") and sonuc["ids"][0]:
            for i, doc_id in enumerate(sonuc["ids"][0]):
                distance = sonuc["distances"][0][i] if sonuc.get("distances") else 0
                guven = 1.0 - distance  # cosine distance -> similarity
                if guven >= esik:
                    meta = sonuc["metadatas"][0][i] if sonuc.get("metadatas") else {}
                    donen.append({
                        "hedef": meta.get("hedef", ""),
                        "cozum": sonuc["documents"][0][i],
                        "guven": round(guven, 3),
                        "kaynak": meta.get("kaynak", "vektor"),
                        "vektor": True
                    })
        return donen
    except Exception:
        return []


def vektor_durum():
    """Vektor DB istatistik."""
    db, model, koleksiyon = _v_get()
    if db is None or koleksiyon is None:
        return {"aktif": False, "kayit": 0}
    try:
        count = koleksiyon.count()
        return {"aktif": True, "kayit": count, "model": "all-MiniLM-L6-v2"}
    except Exception:
        return {"aktif": True, "kayit": "?"}
