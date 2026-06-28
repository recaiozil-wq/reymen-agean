---
skill_id: 0e90c7c51b69
usage_count: 1
last_used: 2026-06-16
---
# Bölüm 3: Bellek ve RAG Katmanı

## ChromaDB Yapısı

Tek koleksiyon: hermes_vault (cosine benzerlik, HNSW)
- id: tam dosya yolu
- embedding: 768 boyutlu (nomic-embed-text)
- metadata.mtime: son değişiklik zamanı
- metadata.category: frontmatter'dan
- document: ilk 2000 karakter

Dirty-tracking: Sadece mtime değişen dosyalar yeniden embed edilir.

## RAG Pipeline

Kullanıcı sorusu
  -> embed(soru) -> 768-d vektör (Ollama nomic)
  -> ChromaDB.query(n=10, where=category)
  -> filtre: similarity >= 0.35
  -> obsidian.read_note(hit.path) -> not gövdesi
  -> BrainRouter.ask(sistem: "SADECE kaynaktan yanıtla")
  -> QAResult(answer, sources, found)
  -> Telegram'a gönder + daily note'a kaydet

## Bellek Türleri

| Tür | Konum | İçerik |
|---|---|---|
| Kısa vadeli | workspace/memories/{proje}.json | feedback, değişiklik, hata |
| Uzun vadeli (Skill) | knowledge_base/skills/**/*.md | Teknik bilgi birimi |
| Karar belleği | workspace/memory/successes/ | Başarı/başarısızlık JSON |
| Graf belleği | workspace/graph_db/graph.json | Kavram ilişkileri |
| Hygiene | workspace/hygiene/registry.json | Güven skoru + eskime |

## Güven Skoru Formülü

effective_score = trust_score
  - decay (180 günden sonra 90 günde -0.1)
  - contradictions x 0.1
  - 0.3 (eğer deprecated)

## Bilgi Grafı

- Düğüm: Skill (md) + Concept (teknik terim)
- Kenar: MENTIONS (Skill->Concept), RELATED (co-occurrence)
- Jaccard >= 0.20 VEYA 2 ortak kavram -> "## İlişkili" eklenir
- Jaccard >= 0.65 -> "Güncelleme Adayı" işareti
- Kavram 3+ skill'de -> _genel_bakis_<kavram>.md üretilir
