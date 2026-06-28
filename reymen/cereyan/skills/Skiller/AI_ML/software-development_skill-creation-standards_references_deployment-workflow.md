---
name: software-development_skill-creation-standards_references_deployment-workflow
description: Skill Deployment Workflow
title: "Software Development Skill Creation Standards References Deployment Workflow"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Skill Deployment Workflow |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Skill Deployment Workflow

Bir skill oluşturulduktan veya güncellendikten sonra şu adımlar TAMAMLANMALIDIR:

## Adımlar

### 1. Hermes'e Kaydet
```bash
skill_manage(action='create'|'edit', name='...', content='...')
```

### 2. Gözden Geçir — Origin İzlerini Temizle
Eğer skill başka bir kaynaktan (GitHub repo, NemoClaw, ECC, vs.) import edildiyse:

| Alan | Ne Yap | Örnek |
|------|--------|-------|
| `phase:` | Sil | NVIDIA eğitim modülü |
| `lesson:` | Sil | NVIDIA ders no |
| `origin:` | Sil | `origin: ECC`, `origin: oh-my-agent-check` |
| `tools:` | Sil | NemoClaw'a özgü alan |
| Tag'lerde `nemo` | "Guardrails" ile değiştir | `nemo-guardrails` → `guardrails` |
| Marka adları (NeMo, Nemotron) | Jenerik terimlerle değiştir | `NeMo Guardrails` → `Guardrails` |

Kural: Skill'in içinde başka bir şirkete/sisteme ait olduğunu gösteren hiçbir meta veri kalmamalıdır.

### 3. Obsidian'a Sync Et
```bash
# ÖNCE şu Python'u dene:
python "C:\Users\marko\hermes-ai\venv\Scripts\python.exe" "C:\Users\marko\AppData\Local\hermes\hooks\sync_skills_to_obsidian.py"
# Fallback (venv python.exe bozuksa — null byte hatası): system python kullan
# python "C:\Users\marko\AppData\Local\hermes\hooks\sync_skills_to_obsidian.py"
```

### 4. GitHub'a Push Et (hermes-skills)

#### Tekil Skill (tek skill güncellemesi)
```bash
cd /c/Users/marko/hermes-skills
git pull origin master

# Skill dosyalarını Hermes'ten GitHub kopyasına kopyala
SKILL_DIR="skills/<kategori>/<skill-adi>"
mkdir -p "$SKILL_DIR"
cp -r "/c/Users/marko/AppData/Local/hermes/skills/<kategori>/<skill-adi>/"* "$SKILL_DIR/"

git add -A
git commit -m "update: <skill-adi> — <kısa açıklama>"
git push origin master
```

#### Bulk Sync (çoklu skill — yeni kurulum/senaryo)
Local'de olup GitHub'da olmayan tüm skill'leri bulup toplu push:
```bash
cd /c/Users/marko/hermes-skills

# 1. Eksik skill'leri bul
find /c/Users/marko/AppData/Local/hermes/skills -name "SKILL.md" -exec dirname {} \; \
  | sed 's|.*/skills/||' | sort > /tmp/local_skills.txt
find skills -name "SKILL.md" -exec dirname {} \; \
  | sed 's|skills/||' | sort > /tmp/repo_skills.txt
MISSING=$(comm -23 /tmp/local_skills.txt /tmp/repo_skills.txt)
echo "$MISSING"

# 2. Her birini kopyala (SKILL.md + references/ + templates/ + scripts/ + assets/)
for skill in $MISSING; do
  src="/c/Users/marko/AppData/Local/hermes/skills/$skill"
  dest="skills/$skill"
  mkdir -p "$dest"
  cp -r "$src/"* "$dest/"
  echo "[OK] $skill"
done

# 3. Commit + Push
git add -A
git commit -m "sync: $SAYI eksik skill eklendi"
git push origin master
```

## Önemli
- GitHub push atlanırsa skill sadece yerel kalır, diğer cihazlara gitmez
- Origin izleri temizlenmezse telif/takip riski oluşur
- Sıralama: HERMES'E KAYDET → TEMİZLE → OBSIDIAN SYNC → GITHUB PUSH
