---
skill_id: 4cd1254f88f1
usage_count: 1
last_used: 2026-06-16
---
# ChromaDB + Ollama Custom Embedding Function — Hata Çözüm Rehberi

Bu doküman, ChromaDB'ye özel embedding function (Ollama) entegre ederken karşılaşılan hataları çözmek için yazıldı.

## 1. `AttributeError: 'XxxEmbeddingFunction' object has no attribute 'embed_query'`

**Hata (ChromaDB v1.x):**
```
AttributeError: 'OllamaEmbeddingFunction' object has no attribute 'embed_query' in query.
```

**Sebep:** ChromaDB v1.x, query sırasında `embed_query()` metodunu çağırır. Eski API (`__call__` yeterliydi) artık çalışmaz.

**Çözüm:** Sınıfa `embed_query` metodu ekle:
```python
def embed_query(self, input):
    """ChromaDB query'de çağırır — hem string hem list kabul eder."""
    if isinstance(input, list):
        return [self._get_embedding(t) for t in input]
    return self._get_embedding(input)
```

## 2. `TypeError: ...got an unexpected keyword argument 'input'`

**Hata:**
```
TypeError: OllamaEmbeddingFunction.embed_query() got an unexpected keyword argument 'input'
```

**Sebep:** `embed_query` metodun imzası `(self, text)` veya `(self, input: str)` yerine `(self, input)` olmalı. ChromaDB keyword arg ile çağırır.

**Çözüm:** Parametre adını `input` yap:
```python
def embed_query(self, input):  # DOĞRU
    ...
# Yanlış:
def embed_query(self, text):   # HATA! ChromaDB embed_query(input=input) çağırır
def embed_query(self, input: str):  # type hint varsa da çalışır
```

## 3. `NotFoundError: Collection [obsidian_vault] does not exist`

**Hata:**
```
chromadb.errors.NotFoundError: Collection [obsidian_vault] does not exist
```

**Sebep 1 — Farklı DB yolu:** Get/query farklı `PersistentClient(path=...)` kullanıyor olabilir. Create'de A yolu, query'de B yolu.

**Çözüm:** Create ve query'de AYNI path'i kullan:
```python
DB_PATH = r"C:\Users\marko\AppData\Local\hermes\obsidian_rag_db"
client = chromadb.PersistentClient(path=DB_PATH, ...)
```

**Sebep 2 — Embedding function uyumsuzluğu:** `get_collection` farklı embedding function ile çağrılırsa ChromaDB collection'ı bulamaz.

**Çözüm:** Aynı embedding function objesini (veya aynı sınıfı) kullan:
```python
ef = OllamaEmbeddingFunction()  # her yerde aynı model
# Create:
col = client.create_collection(name="x", embedding_function=ef)
# Query:
col = client.get_collection("x", embedding_function=ef)
```

## 4. ChromaDB `add()`'den sonra collection bulunamıyor

**Sebep:** Rust backend çalışma dizininde `chroma.sqlite3` oluşturur. Eğer script A dizininde, script B başka dizinde çalışırsa farklı SQLite dosyaları oluşur.

**Çözüm:** Mutlak yol kullan:
```python
DB_PATH = r"C:\Users\marko\AppData\Local\hermes\rag_db"
client = chromadb.PersistentClient(path=DB_PATH)
```
Göreceli yol (`./chroma_db`) her script için farklı dizinlere çözümlenir.

## 5. Ollama API Hatası: `/api/embeddings` vs `/api/embed`

**Hata:**
```
HTTP Error 500: Internal Server Error
```

**Sebep:** Eski Ollama sürümleri `/api/embeddings` (tekil, `prompt` key) kullanır. Ollama v0.24+ `/api/embed` (plural, `input` key) kullanır.

| Özellik | Eski API | Yeni API (v0.24+) |
|---------|----------|-------------------|
| Endpoint | `/api/embeddings` | `/api/embed` |
| Input key | `"prompt"` | `"input"` |
| Response | `{"embedding": [...]}` | `{"embeddings": [[...]]}` |
| Batch | Tek tek çağrı | `"input": ["a", "b", "c"]` |

**Çözüm:** Yeni API'ı kullan:
```python
data = json.dumps({"model": "nomic-embed-text", "input": text}).encode()
req = urllib.request.Request(f"{base_url}/api/embed", data=data, ...)
# Cevap: result["embeddings"][0]
```

## 6. Embedding Function `name()` gereklidir

ChromaDB, collection oluştururken embedding function'ın `name()` metodunu çağırır ve metadata'ya kaydeder. Yoksa hata alınır.

```python
def name(self) -> str:
    return f"ollama_{self.model}"
```

## 7. Token Limit Aşımı

nomic-embed-text varsayılan token limiti **512 token**. 3000 karakter (~750 Türkçe token) genelde sığar. Daha uzun metinlerde kes:
```python
content = content[:3000]  # güvenli sınır
```

## 8. Progress Bar için flush

ChromaDB batch add yavaş olabilir. `\r` ile satır başına dön ama `flush=True` ile stdout'a hemen yaz:
```python
print(f"\r[{bar}] %{pct}", end="", flush=True)
```

## Özet: ChromaDB + Özel EF için Kontrol Listesi

- [ ] Embedding function sınıfında `name()`, `embed_query(input)`, `__call__(input: list[str])` var mı?
- [ ] `embed_query` parametresi `input` olarak adlandırılmış mı? (`text` değil)
- [ ] Add/create/query'de aynı embedding function objesi kullanılıyor mu?
- [ ] `PersistentClient(path=...)` tüm scriptlerde AYNI mutlak yol mu?
- [ ] Ollama API endpoint `/api/embed` (plural) kullanılıyor mu?
- [ ] Input key `"input"` olarak gönderiliyor mu? (eski: `"prompt"`)
- [ ] Response `result["embeddings"][0]` ile alınıyor mu? (eski: `result["embedding"]`)
- [ ] `TOKENIZERS_PARALLELISM=*** set edilmiş mi?
- [ ] Fallback (zero vector) var mı? Embedding hatasında tüm pipeline kırılmaz.
