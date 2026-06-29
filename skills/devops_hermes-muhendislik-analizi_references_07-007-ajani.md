
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Hermes Muhendislik Analizi_References_07 007 Ajani |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Bölüm 7: 007 Ajan Mimarisi

## Temel İlkeler

007 ajanı Hermes v7'nin güçlü yanlarını koruyarak 3 boyut ekler:
1. Çok boyutlu bellek — anlık + uzun vadeli + karar + graf entegre
2. Güven piramidi — her skill'in güvenilirliği bilinir
3. Kapalı öğrenme döngüsü — üretim -> doğrulama -> kullanım -> güncelleme

## Skill Güven Piramidi

Kademe 4 — VERIFIED   : 2+ bağımsız kaynak + quiz geçti + trust >= 85
Kademe 3 — CONFIDENT  : 1 kaynak + critique geçti + trust >= 70
Kademe 2 — PROVISIONAL: yeni skill, henüz doğrulanmamış
Kademe 1 — STALE      : eski, trust < 40 veya çelişki işaretli

## Geliştirilmiş Öğrenme Döngüsü

Mevcut: Kaynak -> Temizleme -> Üretim -> Critique (1 tur) -> Kayıt

007 Ajan (eklemeler):
- Çift-tur critique: "Yeniden yazım gerçekten iyileşti mi?"
- Bağlamsal critique: "Önceki skill'lerle tutarlı mı?"
- quiz_skill(): "Gerçekten öğrendim mi?" sorusu
- Çapraz kaynak: 2+ bağımsız kaynak -> VERIFIED işareti

## GraphRAG Entegrasyonu

Mevcut: Sadece doğrudan benzerlik (top-k ChromaDB)
007 Ajan (2-hop genişletme):
  direct_hits = vault_store.search(query, top_k=5)
  for hit in direct_hits:
      neighbors = graph_memory.neighbors(hit.concepts, max_distance=2)
      expanded = vault_store.search_by_concepts(neighbors, top_k=3)
  results = merge_and_rerank(direct_hits + expanded)

## Yeni Benchmark Metrikleri
- skill_staleness_rate: Bayat skill %
- curiosity_to_skill_rate: Soru -> skill dönüşümü
- conflict_detection_rate: Çelişki tespiti sıklığı
- concept_drift_rate: Ontoloji merge sayısı/hafta

## 007 Ajan Modül Haritası

007_agent/
  core/       agent_loop.py, brain_router.py, task_orchestrator.py
  memory/     vault_store.py, graph_rag.py, decision_memory.py, trust_registry.py
  skills/     skill_pipeline.py, reflection_engine.py, skill_verifier.py, benchmark_harness.py
  integrations/ telegram_bot.py, obsidian_engine.py, source_adapters.py
  ops/        cost_tracker.py, vram_manager.py, error_recovery.py
