---
skill_id: ee975ea2a4b6
usage_count: 1
last_used: 2026-06-16
---
# Skill → GitHub Sync Workflow

## Amaç

Bir skill'i dış kaynaktan güncelledikten/sonra **3 adımda** tamamlama:
1. ReYMeN local skill kütüphanesine yükle/güncelle
2. GitHub `Watcher-Hermes/hermes-skills` reposuna push et
3. Gerekiyorsa README.md güncelle

## ZORUNLU — Bu Sırayla Uygula

### Adım 1 — ReYMeN Local

```
C:\Users\marko\AppData\Local\hermes\skills\kategori\skill-adi\SKILL.md
```

- Router+Reference yapısına uygun (SKILL.md ≤ 4 KB)
- Frontmatter zorunlu: name, title, description, version, audience, tags
- references/ altına detayları böl
- Sync to Obsidian:
  ```bash
  # ÖNCE: hermes-ai venv python'u dene (çoğu zaman çalışır)
  "C:\Users\marko\hermes-ai\venv\Scripts\python.exe" "C:\Users\marko\AppData\Local\hermes\hooks\sync_skills_to_obsidian.py"
  # FALLBACK: venv python.exe bozuksa (null byte hatası), system python kullan
  # python "C:\Users\marko\AppData\Local\hermes\hooks\sync_skills_to_obsidian.py"
  ```

### Adım 2 — GitHub hermes-skills

```bash
# 1. Clone varsa pull et
cd /c/Users/marko/hermes-skills
git pull origin master

# 2. Dosyaları kopyala (ReYMeN local'den repo'ya)
SKILL_DIR="skills/kategori/skill-adi"
mkdir -p "$SKILL_DIR"
cp -r "/c/Users/marko/AppData/Local/hermes/skills/kategori/skill-adi/"* "$SKILL_DIR/"

# 3. Commit + Push
git add -A
git commit -m "update: skill-adi vX.Y.Z — kısa açıklama"
git push origin master
```

**NOT:** hermes-skills repo local'de yoksa:
```bash
cd /c/Users/marko
git clone https://github.com/Watcher-Hermes/hermes-skills.git --depth 1
```

### Adım 3 — README (Gerekiyorsa)

Eğer yeni kategori, önemli istatistik değişikliği veya büyük güncelleme varsa:

1. İstatistikleri güncelle: skill sayısı, reference sayısı
2. README.md düzenle → commit → push

## Sık Yapılan Hatalar

| Hata | Çözüm |
|------|-------|
| Sadece local yükleyip GitHub'a atmamak | **Kullanıcı hatırlatır** — üç adım da zorunlu |
| MCP GitHub auth hatası | gh CLI kullan (git-bash'ten) |
| LF/CRLF uyarısı | Önemli değil, Git handle eder |
| README güncellemeyi unutmak | Yeni kategori eklendiyse veya istatistik değiştiyse zorunlu |
| Obsidian sync atlamak | Skill kullanılamaz olur, her zaman sync çalıştır |
