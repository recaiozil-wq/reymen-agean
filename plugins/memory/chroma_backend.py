# -*- coding: utf-8 -*-
"""plugins/memory/chroma_backend.py — ChromaDB Memory Backend.

Vektor arama ve bellek depolama icin ChromaDB kullanir.
Graceful degrade: chromadb yoksa "Kurulu degil" mesaji dondurur.
"""

import logging

logger = logging.getLogger(__name__)

# ChromaDB kontrolu
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    _CHROMADB_VAR = True
except ImportError:
    _CHROMADB_VAR = False


class ChromaBackend:
    """ChromaDB tabanli vektor bellek backend'i.

    Fonksiyonlar:
        ekle(metin, metadata) -> str
        ara(sorgu, limit=5) -> str
        sil(id) -> str
    """

    def __init__(self, collection_name: str = "ReYMeN_memory", persist_dir: str = None):
        """ChromaBackend baslatma.

        Args:
            collection_name: Koleksiyon adi (varsayilan: ReYMeN_memory)
            persist_dir: Kalici depolama dizini (None = .ReYMeN/chroma/)
        """
        self.collection_name = collection_name
        self._collection = None
        self._client = None

        if not _CHROMADB_VAR:
            logger.warning("ChromaDB kurulu degil, vektor bellek kullanilamaz.")
            return

        try:
            if persist_dir is None:
                from pathlib import Path
                persist_dir = str(Path(__file__).parent.parent.parent / ".ReYMeN" / "chroma")

            self._client = chromadb.Client(ChromaSettings(
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            ))
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ChromaDB koleksiyonu '%s' hazir (%s).", collection_name, persist_dir)
        except Exception as e:
            logger.error("ChromaDB baslatilamadi: %s", e)
            self._client = None
            self._collection = None

    def _hazir_mi(self) -> bool:
        """ChromaDB'nin kullanima hazir olup olmadigini kontrol eder."""
        if not _CHROMADB_VAR:
            return False
        return self._collection is not None

    def ekle(self, metin: str, metadata: dict = None) -> str:
        """Hafizaya yeni bir metin ekler.

        Args:
            metin: Eklenecek metin
            metadata: Ek bilgiler (sozluk, opsiyonel)

        Returns:
            str: Islem sonucu
        """
        if not self._hazir_mi():
            return "[ChromaDB]: Kurulu degil."

        if not metin or not metin.strip():
            return "[ChromaDB]: Eklenecek metin bos."

        try:
            import uuid
            doc_id = str(uuid.uuid4())
            self._collection.add(
                documents=[metin],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            return f"[ChromaDB]: '{metin[:50]}...' eklendi (ID: {doc_id})."
        except Exception as e:
            return f"[ChromaDB]: Ekleme hatasi - {e}"

    def ara(self, sorgu: str, limit: int = 5) -> str:
        """Vektor benzerligine gore arama yapar.

        Args:
            sorgu: Aranacak metin
            limit: Maksimum sonuc sayisi (varsayilan: 5)

        Returns:
            str: Arama sonuclari
        """
        if not self._hazir_mi():
            return "[ChromaDB]: Kurulu degil."

        if not sorgu or not sorgu.strip():
            return "[ChromaDB]: Sorgu metni bos."

        try:
            results = self._collection.query(
                query_texts=[sorgu],
                n_results=min(limit, 20),
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]

            if not documents:
                return "[ChromaDB]: Sonuc bulunamadi."

            sonuc = [f"[ChromaDB]: {len(documents)} sonuc bulundu:"]
            for i, doc in enumerate(documents):
                mesafe = distances[i] if distances else 0
                sonuc.append(f"  {i+1}. (ID: {ids[i]}, Uzaklik: {mesafe:.4f})")
                sonuc.append(f"     {doc[:200]}")
                if metadatas and metadatas[i]:
                    sonuc.append(f"     Metadata: {metadatas[i]}")

            return "\n".join(sonuc)
        except Exception as e:
            return f"[ChromaDB]: Arama hatasi - {e}"

    def sil(self, doc_id: str) -> str:
        """Hafizadan bir ogeyi ID'sine gore siler.

        Args:
            doc_id: Silinecek dokuman ID'si

        Returns:
            str: Islem sonucu
        """
        if not self._hazir_mi():
            return "[ChromaDB]: Kurulu degil."

        if not doc_id:
            return "[ChromaDB]: ID gerekli."

        try:
            self._collection.delete(ids=[doc_id])
            return f"[ChromaDB]: '{doc_id}' silindi."
        except Exception as e:
            return f"[ChromaDB]: Silme hatasi - {e}"

    def __repr__(self) -> str:
        durum = "Hazir" if self._hazir_mi() else "Kurulu degil"
        return f"<ChromaBackend durum={durum}>"
