"""
Obsidian Vault → ChromaDB RAG Engine
Full workflow: embedding + index + query with Ollama nomic-embed-text

Usage:
  python obsidian_rag.py               # Normal index (varsa ekle)
  python obsidian_rag.py --reindex     # Sil + baştan indexle
  python obsidian_rag.py --query "soru"  # Sorgula
"""

import os
import re
import hashlib
import sys
import urllib.request
import json as json_mod
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("[HATA] chromadb yüklü değil. Koş: uv pip install chromadb")
    sys.exit(1)

# --- Yollar ---
VAULT = Path(r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault")
DB_PATH = Path(r"C:\Users\marko\AppData\Local\ReYMeN\obsidian_rag_db")


# --- Ollama Embedding Function ---
class OllamaEmbeddingFunction:
    """ChromaDB uyumlu Ollama embedding function."""

    def __init__(self, model="nomic-embed-text", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._cache = {}

    def name(self) -> str:
        return f"ollama_{self.model}"

    def embed_query(self, input):
        if isinstance(input, list):
            return [self._get_embedding(t) for t in input]
        return self._get_embedding(input)

    def __call__(self, input):
        try:
            data = json_mod.dumps({"model": self.model, "input": input}).encode()
            req = urllib.request.Request(
                f"{self.base_url}/api/embed",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json_mod.loads(resp.read().decode())["embeddings"]
        except Exception as e:
            print(f"[UYARI] Batch embedding hatası: {e}, tek tek deneniyor...")
            return [self._get_embedding(t) for t in input]

    def _get_embedding(self, text):
        if text in self._cache:
            return self._cache[text]
        data = json_mod.dumps({"model": self.model, "input": text}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/embed",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                emb = json_mod.loads(resp.read().decode())["embeddings"][0]
                self._cache[text] = emb
                return emb
        except Exception as e:
            print(f"[UYARI] Ollama embedding hatası: {e}")
            return [0.0] * 768


# --- Dosya tarama ---
def get_all_markdown_files(vault: Path) -> list[Path]:
    return list(vault.rglob("*.md"))


def extract_metadata(filepath: Path, vault: Path) -> dict:
    """Extract YAML frontmatter and metadata from a markdown file."""
    rel_path = str(filepath.relative_to(vault))
    title = filepath.stem
    tags = ""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                frontmatter = text[3:end].strip()
                for line in frontmatter.split("\n"):
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("tags:"):
                        tags = line.split(":", 1)[1].strip()
                        tags = re.sub(r"[\[\]\"]", "", tags)
        return {"path": rel_path, "title": title, "tags": tags, "source": "vault"}
    except Exception as e:
        return {"path": rel_path, "title": title, "tags": "", "source": "vault"}


# --- Indexleme ---
def index_vault(force_reindex=False):
    """Index all vault files into ChromaDB."""
    print(f"Tüm dosyalar indexleniyor: {len(files)}\n")
    files = get_all_markdown_files(VAULT)

    client = chromadb.PersistentClient(
        path=str(DB_PATH), settings=Settings(anonymized_telemetry=False)
    )

    ef = OllamaEmbeddingFunction()

    if force_reindex:
        try:
            client.delete_collection("obsidian_vault")
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        collection = client.create_collection(
            name="obsidian_vault",
            metadata={"hnsw:space": "cosine"},
            embedding_function=ef,
        )
    else:
        try:
            collection = client.get_collection("obsidian_vault", embedding_function=ef)
        except Exception:
            collection = client.create_collection(
                name="obsidian_vault",
                metadata={"hnsw:space": "cosine"},
                embedding_function=ef,
            )

    existing_count = collection.count()
    if existing_count > 0 and not force_reindex:
        print(f"Zaten {existing_count} döküman indexli. Yeni dosyalar taranıyor...")
        existing_ids = set()
        existing = collection.get(limit=existing_count)
        if existing and existing.get("ids"):
            existing_ids = set(existing["ids"])
    else:
        existing_ids = set()

    documents, metadatas, ids = [], [], []

    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if not content.strip():
            continue
        if len(content) > 3000:
            content = content[:3000]

        meta = extract_metadata(f, VAULT)
        doc_id = hashlib.md5(meta["path"].encode()).hexdigest()[:12]

        if doc_id in existing_ids and not force_reindex:
            continue

        documents.append(content)
        metadatas.append(meta)
        ids.append(doc_id)

    if not documents:
        print("Yeni eklenecek dosya yok.")
        return

    BATCH = 50
    total = len(documents)
    for i in range(0, total, BATCH):
        batch_end = min(i + BATCH, total)
        collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end],
        )
        progress = int((batch_end / total) * 20)
        bar = "█" * progress + "░" * (20 - progress)
        print(f"\r[{bar}] {int(batch_end/total*100)}% ({batch_end}/{total})", end="")
    print(f"\n✅ Index tamam. Toplam: {collection.count()} döküman.")


# --- Sorgulama ---
def query_vault(question: str, n_results: int = 3) -> list[dict]:
    """Search vault and return top results."""
    client = chromadb.PersistentClient(
        path=str(DB_PATH), settings=Settings(anonymized_telemetry=False)
    )
    ef = OllamaEmbeddingFunction()
    collection = client.get_collection("obsidian_vault", embedding_function=ef)

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results and results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            doc = results["documents"][0][i] if results.get("documents") else ""
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            score = (
                1.0 - (results["distances"][0][i] if results.get("distances") else 0)
            )

            path = meta.get("path", "?") if isinstance(meta, dict) else "?"
            title = (
                meta.get("title", doc_id) if isinstance(meta, dict) else doc_id
            )
            snippet = doc[:300].strip().replace("\n", " ")

            output.append(
                {"path": path, "title": title, "score": round(score, 3), "snippet": snippet}
            )

    return output


# --- Ana ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reindex":
        index_vault(force_reindex=True)
    elif len(sys.argv) > 2 and sys.argv[1] == "--query":
        results = query_vault(sys.argv[2])
        print(f"\n📚 Sorgu: {sys.argv[2]}\n")
        if not results:
            print("❌ Eşleşme bulunamadı.")
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} (benzerlik: {r['score']})")
                print(f"   📄 {r['path']}")
                print(f"   💬 {r['snippet'][:200]}...\n")
    else:
        index_vault()
