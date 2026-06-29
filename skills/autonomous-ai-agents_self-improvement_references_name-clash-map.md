---
name: autonomous-ai-agents_self-improvement_references_name-clash-map
description: Hermes ↔ Obsidian İsim Çakışması Haritası
title: "Autonomous Ai Agents Self Improvement References Name Clash Map"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes ↔ Obsidian İsim Çakışması Haritası |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes ↔ Obsidian İsim Çakışması Haritası

> Bu referans, `find` + `comm` tabanlı fark analizinde Hermes-only veya Obsidian-only
> görünen ama aslında eşleşmiş olan skill'leri listeler. Son güncelleme: 2026-06-04.

## Tespit Edilen Çakışmalar (8 Adet)

| Hermes Adı | Obsidian Adı | Açıklama |
|---|---|---|
| `audiocraft` | `audiocraft-audio-generation` | Hermes kategori ismi, Obsidian açıklayıcı |
| `creative-ideation` | `ideation` | Hermes geniş, Obsidian kısa |
| `lm-evaluation-harness` | `evaluating-llms-harness` | Aynı konu, farklı terminoloji |
| `notion-research` | `notion-research-documentation` | Obsidian daha spesifik |
| `openai-pdf` | `pdf` | Hermes sağlayıcı-spesifik, Obsidian jenerik |
| `playwright-browser` | `playwright` | Hermes kategori dahil, Obsidian sadece araç adı |
| `segment-anything` | `segment-anything-model` | Obsidian "model" eklemiş |
| `vllm` | `serving-llms-vllm` | Obsidian açıklayıcı prefix eklemiş |

## Tespit Yöntemi

1. `find` ile Hermes skill adlarını çıkar (`basename $(dirname SKILL.md)`)
2. `find` ile Obsidian not adlarını çıkar (`basename .md`, `_*` indeksleri hariç)
3. Normalize et: tire/altçizgi kaldır, lowercase yap
4. `comm -23` → Hermes-only, `comm -13` → Obsidian-only
5. Hermes-only çıktıdaki her adı Obsidian-only listede **çoğul eşleşme** ile manuel kontrol et

## Cron İşlemi İçin Kullanım

`otonom-gece-gelistirme` ve `self-improvement` cron job'ları her çalıştığında
yeni çakışma tespit ederse bu harita güncellenmelidir. Önce bu dosyayı oku,
ardından yeni bulunan çakışmaları ekle.

## Sync Script Davranışı

`sync_skills_to_obsidian.py` YAML frontmatter'daki `name` alanına bakar, dosya adına değil.
Bu sayede Hermes `audiocraft` (dosya adı) ile Obsidian `audiocraft-audio-generation.md`
(frontmatter `name: audiocraft`) sorunsuz eşleşir. Çakışmalar sadece insan tarafından
yapılan fark analizinde görünür — sync script'i bundan etkilenmez.
