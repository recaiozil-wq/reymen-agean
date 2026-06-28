# -*- coding: utf-8 -*-
"""
plugins/memory/chromadb_vektor/__init__.py — ChromaDB Vektörel Hafıza Plugin'i.

ReYMeN Memory Provider Plugin standardına uygun ReYMeN implementasyonu.
ChromaDB kurulu değilse graceful degrade: musait_mi() False döndürür.

Özellikler:
  - Kosinüs benzerliği ile anlamsal arama (embedding tabanlı)
  - .ReYMeN/chroma_db/ altında kalıcı vektör deposu
  - prefetch(): anlamsal yakınlık ile geçmişten bağlam getirir
  - tur_senkronize(): arka planda vektör indeksine yazar (non-blocking)
  - Araçlar: VEKTOR_ARA, VEKTOR_KAYDET, VEKTOR_ISTATISTIK
"""


__all__ = ['AbstraktHafizaSaglayici', 'Any', 'ChromaDBVektor', 'Dict', 'HafizaPluginKayit', 'List', 'Optional', 'Path', 'Settings', 'ad', 'arac_cagri_isle', 'arac_sema_al', 'baslat', 'kapat', 'kaydet', 'konfig_sema_al', 'musait_mi', 'onceden_getir', 'oturum_bitti', 'sistem_prompt_bloku']
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory_provider import AbstraktHafizaSaglayici, HafizaPluginKayit

logger = logging.getLogger(__name__)

PLUGIN_ADI = "chromadb_vektor"
PLUGIN_ACIKLAMA = "ChromaDB ile anlamsal (vektörel) hafıza — pip install chromadb gerekir"

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_MUSAIT = True
except ImportError:
    CHROMA_MUSAIT = False


class ChromaDBVektor(AbstraktHafizaSaglayici):
    """
    ChromaDB tabanlı vektörel anlamsal hafıza.
    ChromaDB kurulu değilse musait_mi() False döndürür —
    sistem sqlite_fts gibi bir fallback'e otomatik geçer.
    """

    def __init__(self):
        self._istemci = None
        self._koleksiyon = None
        self._oturum_id: str = "varsayilan"
        self._db_yolu: Optional[Path] = None

    @property
    def ad(self) -> str:
        return PLUGIN_ADI

    def musait_mi(self) -> bool:
        return CHROMA_MUSAIT

    def baslat(self, oturum_id: str, **kwargs) -> None:
        if not CHROMA_MUSAIT:
            raise RuntimeError("chromadb kurulu değil. pip install chromadb")

        self._oturum_id = oturum_id
        reymen_dizin = Path(
            kwargs.get("reymen_dizin",
                       Path(__file__).parent.parent.parent.parent / ".ReYMeN")
        )
        self._db_yolu = reymen_dizin / "chroma_db"
        self._db_yolu.mkdir(parents=True, exist_ok=True)

        self._istemci = chromadb.PersistentClient(
            path=str(self._db_yolu),
            settings=Settings(anonymized_telemetry=False),
        )
        self._koleksiyon = self._istemci.get_or_create_collection(
            name="reymen_hafiza",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"[chromadb_vektor] Baslatildi — {self._db_yolu}")

    # ── Araç şemaları ──────────────────────────────────────────────────────

    def arac_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "ad": "VEKTOR_ARA",
                "aciklama": "Anlamsal benzerlik ile hafızada ara",
                "parametreler": {
                    "sorgu": {"tur": "str", "aciklama": "Doğal dil sorgusu"},
                    "limit": {"tur": "int", "varsayilan": 5},
                },
            },
            {
                "ad": "VEKTOR_KAYDET",
                "aciklama": "Hafızaya metin girdisi vektörize edip kaydet",
                "parametreler": {
                    "icerik": {"tur": "str", "aciklama": "Kaydedilecek metin"},
                    "meta": {"tur": "str", "varsayilan": "{}"},
                },
            },
            {
                "ad": "VEKTOR_ISTATISTIK",
                "aciklama": "Hafıza koleksiyonunun istatistiklerini göster",
                "parametreler": {},
            },
        ]

    def arac_cagri_isle(self, arac_adi: str, args: Dict[str, Any], **kwargs) -> str:
        if arac_adi == "VEKTOR_ARA":
            return self._ara(args.get("sorgu", ""), int(args.get("limit", 5)))
        if arac_adi == "VEKTOR_KAYDET":
            try:
                meta = json.loads(args.get("meta", "{}"))
            except json.JSONDecodeError:
                meta = {}
            return self._kaydet(args.get("icerik", ""), meta)
        if arac_adi == "VEKTOR_ISTATISTIK":
            return self._istatistik()
        return f"Bilinmeyen araç: {arac_adi}"

    # ── Lifecycle hooks ────────────────────────────────────────────────────

    def sistem_prompt_bloku(self) -> str:
        sayi = self._koleksiyon.count() if self._koleksiyon else 0
        return (
            f"[Hafıza: ChromaDB Vektörel aktif — {sayi} giriş]\n"
            "Anlamsal arama için VEKTOR_ARA, kaydetmek için VEKTOR_KAYDET kullan."
        )

    def onceden_getir(self, sorgu: str) -> str:
        if not sorgu or not self._koleksiyon:
            return ""
        try:
            sonuclar = self._koleksiyon.query(
                query_texts=[sorgu],
                n_results=3,
                include=["documents", "metadatas", "distances"],
            )
            docs = sonuclar.get("documents", [[]])[0]
            dists = sonuclar.get("distances", [[]])[0]
            if not docs:
                return ""
            satirlar = []
            for doc, dist in zip(docs, dists):
                benzerlik = round(1 - dist, 3)
                satirlar.append(f"[benzerlik={benzerlik}] {doc[:200]}")
            return "Anlamsal hafıza:\n" + "\n".join(satirlar)
        except Exception as e:
            logger.debug(f"[chromadb_vektor] onceden_getir hata: {e}")
            return ""

    def _tur_senkronize_impl(self, mesajlar: List[Dict[str, Any]]) -> None:
        if not self._koleksiyon or not mesajlar:
            return
        try:
            ids, docs, metas = [], [], []
            for m in mesajlar:
                icerik = m.get("content", "")
                if not icerik or not isinstance(icerik, str):
                    continue
                doc_id = f"{self._oturum_id}_{int(time.time() * 1000)}_{len(ids)}"
                ids.append(doc_id)
                docs.append(icerik)
                metas.append({
                    "rol": m.get("role", "unknown"),
                    "oturum": self._oturum_id,
                    "zaman": str(time.time()),
                })
            if ids:
                self._koleksiyon.upsert(ids=ids, documents=docs, metadatas=metas)
        except Exception as e:
            logger.debug(f"[chromadb_vektor] tur_senkronize_impl hata: {e}")

    def oturum_bitti(self) -> None:
        logger.debug(f"[chromadb_vektor] Oturum bitti: {self._oturum_id}")

    def kapat(self) -> None:
        self._koleksiyon = None
        self._istemci = None
        logger.debug("[chromadb_vektor] Kapatildi.")

    # ── Konfigurasyon ───────────────────────────────────────────────────────

    def konfig_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": "embedding_modeli",
                "label": "Embedding modeli (varsayılan: chromadb dahili)",
                "secret": False,
                "required": False,
                "default": "varsayilan",
            }
        ]

    # ── İç metodlar ────────────────────────────────────────────────────────

    def _ara(self, sorgu: str, limit: int = 5) -> str:
        if not self._koleksiyon:
            return "ChromaDB başlatılmadı."
        try:
            sonuclar = self._koleksiyon.query(
                query_texts=[sorgu],
                n_results=min(limit, self._koleksiyon.count()),
                include=["documents", "distances"],
            )
            docs = sonuclar.get("documents", [[]])[0]
            dists = sonuclar.get("distances", [[]])[0]
            if not docs:
                return f"'{sorgu}' için anlamsal sonuç yok."
            cikti = []
            for doc, dist in zip(docs, dists):
                benzerlik = round(1 - dist, 3)
                cikti.append(f"[{benzerlik}] {doc[:300]}")
            return f"{len(docs)} anlamsal sonuç:\n" + "\n---\n".join(cikti)
        except Exception as e:
            return f"Vektörel arama hatası: {e}"

    def _kaydet(self, icerik: str, meta: dict = None) -> str:
        if not self._koleksiyon:
            return "ChromaDB başlatılmadı."
        if not icerik:
            return "Hata: içerik boş."
        try:
            doc_id = f"{self._oturum_id}_{int(time.time() * 1000)}"
            self._koleksiyon.upsert(
                ids=[doc_id],
                documents=[icerik],
                metadatas=[{**(meta or {}), "oturum": self._oturum_id}],
            )
            return f"Vektör hafızasına kaydedildi (id={doc_id})."
        except Exception as e:
            return f"Kayıt hatası: {e}"

    def _istatistik(self) -> str:
        if not self._koleksiyon:
            return "ChromaDB başlatılmadı."
        try:
            return json.dumps({
                "koleksiyon": self._koleksiyon.name,
                "toplam_giri": self._koleksiyon.count(),
                "db_yolu": str(self._db_yolu),
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"İstatistik hatası: {e}"


# ── Plugin kayıt giriş noktası ────────────────────────────────────────────

def kaydet(ctx: HafizaPluginKayit) -> None:
    """ReYMeN Memory Provider Plugin standardı — kayıt giriş noktası."""
    ctx.hafiza_saglayici_kaydet(ChromaDBVektor())


if __name__ == "__main__":
    if not CHROMA_MUSAIT:
        print("ChromaDB kurulu degil. pip install chromadb")
    else:
        from memory_provider import HafizaPluginKayit
        ctx = HafizaPluginKayit()
        kaydet(ctx)
        ok = ctx.aktif_saglayici_sec("chromadb_vektor", "test-001")
        s = ctx.aktif_al()
        if s:
            print(s.sistem_prompt_bloku())
            print(s.arac_cagri_isle("VEKTOR_KAYDET", {"icerik": "ReYMeN test girişi"}))
            print(s.arac_cagri_isle("VEKTOR_ARA", {"sorgu": "test"}))
            print(s.arac_cagri_isle("VEKTOR_ISTATISTIK", {}))
