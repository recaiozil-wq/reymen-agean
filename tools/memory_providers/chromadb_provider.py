# -*- coding: utf-8 -*-
"""memory_providers/chromadb_provider.py — ChromaDB vektör bellek."""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .base import BellekSaglayici
import logging
logger = logging.getLogger(__name__)


class ChromaDBBellek(BellekSaglayici):
    """ChromaDB ile anlamsal (vektör) bellek."""

    def __init__(self, koleksiyon: str = "ReYMeN",
                 dizin: str = ".ReYMeN/vektor"):
        self._dizin      = dizin
        self._kol_ad     = koleksiyon
        self._koleksiyon = None
        self._aktif      = False
        self._hata_msg   = ""
        self._init()

    def _init(self) -> None:
        try:
            import chromadb  # type: ignore
            istemci = chromadb.PersistentClient(path=self._dizin)
            self._koleksiyon = istemci.get_or_create_collection(
                name=self._kol_ad,
                metadata={"hnsw:space": "cosine"},
            )
            self._aktif = True
        except ImportError:
            self._hata_msg = "chromadb kurulu değil (pip install chromadb)"
        except Exception as e:
            self._hata_msg = str(e)

    def _guard(self) -> Optional[str]:
        """Aktif değilse hata mesajı döndür; aksi halde None."""
        if not self._aktif:
            return f"[Hata]: ChromaDB kullanılamıyor — {self._hata_msg}"
        return None

    # ── Interface ─────────────────────────────────────────────
    def kaydet(self, anahtar: str, deger: Any,
               namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        if not anahtar:
            return "[Hata]: anahtar boş olamaz."
        try:
            # upsert: mevcut ID'yi günceller, yoksa ekler
            self._koleksiyon.upsert(
                ids=[anahtar],
                documents=[str(deger)],
                metadatas=[{"namespace": namespace}],
            )
        except Exception as e:
            return f"[Hata]: ChromaDB kayıt — {e}"
        return f"[Tamam] ChromaDB: '{anahtar}' upsert edildi."

    def oku(self, anahtar: str,
            namespace: str = "default") -> Optional[Any]:
        if self._guard():
            return None
        try:
            sonuc = self._koleksiyon.get(ids=[anahtar])
            if sonuc and sonuc.get("documents"):
                return sonuc["documents"][0]
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return None

    def ara(self, sorgu: str, limit: int = 5) -> List[Dict]:
        if self._guard():
            return []
        if not sorgu.strip():
            return []
        try:
            # n_results toplam kayıt sayısını aşamaz
            toplam = self._koleksiyon.count()
            n = min(limit, max(1, toplam))
            sonuc = self._koleksiyon.query(
                query_texts=[sorgu],
                n_results=n,
            )
        except Exception:
            return []
        ids  = sonuc.get("ids",       [[]])[0]
        docs = sonuc.get("documents", [[]])[0]
        return [
            {"id": ids[i], "icerik": self._sinirla(docs[i])}
            for i in range(len(ids))
        ]

    def sil(self, anahtar: str, namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        try:
            self._koleksiyon.delete(ids=[anahtar])
        except Exception as e:
            return f"[Hata]: ChromaDB silme — {e}"
        return f"[Tamam] ChromaDB: '{anahtar}' silindi."

    def durum(self) -> Dict:
        if not self._aktif:
            return {"tur": "chromadb", "aktif": False,
                    "hata": self._hata_msg}
        try:
            sayi = self._koleksiyon.count()
        except Exception:
            sayi = -1
        return {"tur": "chromadb", "aktif": True,
                "kayit": sayi, "koleksiyon": self._kol_ad}
