---
skill_id: 9610332b8016
usage_count: 1
last_used: 2026-06-16
---
# Bölüm 4: Skill Üretim Sistemi

## Tam Üretim Boru Hattı

Kaynak (YouTube/GitHub/Web/Dosya)
  -> TranscriptCleaner
       Kademe 1: 100+ regex (nmap, SQL injection, Kubernetes...)
       Kademe 2: LLM cila (hermes3, temperature=0.1)
  -> ContentProcessor
       Enjeksiyon savunması (11 regex, zero-width chars, RTL)
       Güven skoru (github:70, web:55, youtube:45 + bonuslar)
       SHA-256[:16] provenance hash
  -> CanonicalOntology.canonicalize()
       Normalize -> takma ad -> embedding centroid (>=0.86)
  -> BrainRouter.ask() -> SKILL.md üretimi
  -> _post_skill_hooks() (10 adım)
  -> SkillAcquisition.register() -> kayıt + Obsidian notu

## Self-Reflection Döngüsü

SKILL.md üretildi
  -> critique_skill()
     Critic LLM -> {score: 0-10, issues: [...]}
     score >= 7: geç, kaydet
     score < 7: _rewrite() (bir kez)
                Skor hala < 7: orijinal kaydedilir

Tasarım kararı: Eşik 7/10. 6 çok gevşek, 8 çok pahalı.

## Kalite Metrikleri

| Metrik | Hesap |
|---|---|
| task_success_rate | Son 500 görevde başarı % |
| knowledge_precision | Son 500 skill ortalama kalitesi (0-10) |
| hallucination_signal | Kalitesi <5 olan skill oranı |
| repair_success_rate | Hata kurtarma başarı % |

## Evaluation Council — 4 Ajan

| Ajan | Odak |
|---|---|
| Ajan 1 — Uyum | Test sayısı, modül boyutu, dokümantasyon |
| Ajan 2 — Zayıflık | En büyük modüller, bare-except |
| Ajan 3 — Çözüm | Parçalama, type hints, registry |
| Ajan 4 — Meta | Diğer 3 ajanı analiz derinliği için puanlar |

## Skill Evrimi

- Versiyon takibi: _v2, _v3 suffix ile
- Eski skill SİLİNMEZ — tarihsel iz korunur
- derive_navigation(): workflow graftan prerequisites/related/advanced
- Obsidian'da "## Öğrenme Ağacı" -> vault öğrenme grafiğine dönüşür
