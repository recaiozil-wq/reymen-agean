---
skill_id: a0fd585b5091
usage_count: 1
last_used: 2026-06-16
---
# ReYMeN ↔ Obsidian İsim Çakışması Haritası

> Bu referans, `find` + `comm` tabanlı fark analizinde ReYMeN-only veya Obsidian-only
> görünen ama aslında eşleşmiş olan skill'leri listeler. Son güncelleme: 2026-06-04.

## Tespit Edilen Çakışmalar (8 Adet)

| ReYMeN Adı | Obsidian Adı | Açıklama |
|---|---|---|
| `audiocraft` | `audiocraft-audio-generation` | ReYMeN kategori ismi, Obsidian açıklayıcı |
| `creative-ideation` | `ideation` | ReYMeN geniş, Obsidian kısa |
| `lm-evaluation-harness` | `evaluating-llms-harness` | Aynı konu, farklı terminoloji |
| `notion-research` | `notion-research-documentation` | Obsidian daha spesifik |
| `openai-pdf` | `pdf` | ReYMeN sağlayıcı-spesifik, Obsidian jenerik |
| `playwright-browser` | `playwright` | ReYMeN kategori dahil, Obsidian sadece araç adı |
| `segment-anything` | `segment-anything-model` | Obsidian "model" eklemiş |
| `vllm` | `serving-llms-vllm` | Obsidian açıklayıcı prefix eklemiş |

## Tespit Yöntemi

1. `find` ile ReYMeN skill adlarını çıkar (`basename $(dirname SKILL.md)`)
2. `find` ile Obsidian not adlarını çıkar (`basename .md`, `_*` indeksleri hariç)
3. Normalize et: tire/altçizgi kaldır, lowercase yap
4. `comm -23` → ReYMeN-only, `comm -13` → Obsidian-only
5. ReYMeN-only çıktıdaki her adı Obsidian-only listede **çoğul eşleşme** ile manuel kontrol et

## Cron İşlemi İçin Kullanım

`otonom-gece-gelistirme` ve `self-improvement` cron job'ları her çalıştığında
yeni çakışma tespit ederse bu harita güncellenmelidir. Önce bu dosyayı oku,
ardından yeni bulunan çakışmaları ekle.

## Sync Script Davranışı

`sync_skills_to_obsidian.py` YAML frontmatter'daki `name` alanına bakar, dosya adına değil.
Bu sayede ReYMeN `audiocraft` (dosya adı) ile Obsidian `audiocraft-audio-generation.md`
(frontmatter `name: audiocraft`) sorunsuz eşleşir. Çakışmalar sadece insan tarafından
yapılan fark analizinde görünür — sync script'i bundan etkilenmez.
