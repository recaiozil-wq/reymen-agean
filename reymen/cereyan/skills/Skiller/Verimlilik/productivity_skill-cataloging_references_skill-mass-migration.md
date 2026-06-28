
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Skill Cataloging_References_Skill Mass Migration |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Skill Kütüphanesi Toplu Taşıma (Mass Migration) Prosedürü

## Ne Zaman Yapılır

- Root/categorized klasörlerde **uncategorized** skill'ler biriktiğinde
- Skill sayısı 300+ ve flat liste yönetilemez hale geldiğinde
- Windows `cat`/`ls`'de isimlerde sembol/karakter sorunu görüldüğünde

## Adımlar

### 1. Tarama

```bash
ls -1 /c/Users/marko/AppData/Local/hermes/skills/
```

Root seviyesindeki her SKILL.md sahibi dizin = kategorize edilmemiş skill. Kategori içi skill'ler `kategori_adı/skill_adı/` şeklinde olur.

### 2. Kategori Atama

Her root-level skill için uygun kategori belirlenir:

| Kategori | İçerik |
|----------|--------|
| windows-automation | Sistem otomasyonu, fare/klavye, ekran, pencere, batch |
| windows-shortcuts | Klavye kısayolları (sistem, tarayıcı, pencere, dosya, metin, erişilebilirlik) |
| windows-system-automation | ADB, kamera, WiFi, sistem araçları |
| automation | n8n, scheduler, workflow bridges |
| autonomous-ai-agents | Otonom ajanlar, çözüm döngüleri, model switch |
| creative | ASCII, Excalidraw, p5.js, pixel-art, diyagram, müzik, video |
| data-science | Jupyter, HF Hub |
| devops | VM, n8n, Android, webhook, kanban, yedek |
| email, gaming, github | Aynı isimli kategoriler |
| hermes-agent | Hermes ayarları |
| mcp | MCP ile ilgili |
| media | YouTube, GIF, müzik, Spotify |
| mlops | Ollama, ChromaDB, hibrit mimari, SAM |
| note-taking | Obsidian |
| productivity | Airtable, Notion, Google, PDF, PPT, OCR, maps, kamera |
| red-teaming | Jailbreak |
| research | arXiv, blogwatcher, repo import, LLM wiki |
| smart-home | Hue |
| software-development | Spring, React Native, Playwright, debug, TDD, kod review |
| user-preferences | nexus-core-omega, terminal-communication |
| Kalan windows-shortcuts | Tarayıcı kısayolları, pencere kısayolları |

### 3. Taşıma (Python)

Windows'ta `os.rename` ile taşınır. HEDEF dizin yoksa önce oluşturulur:

```python
import os, shutil

src = os.path.join(SKILLS_DIR, skill_name)
dst = os.path.join(SKILLS_DIR, category, skill_name)
os.makedirs(os.path.dirname(dst), exist_ok=True)
os.rename(src, dst)
```

### 4. SKILL.md İç Referans Güncelleme

Taşınan skill'lerin SKILL.md'lerinde `path` alanı varsa onu güncelle. Internal wikilink'lerde `[[skill/...]]` varsa düzelt.

### 5. Sync to Obsidian

Taşıma sonrası Obsidian vault'taki skill sayısını eşitle:

```bash
python "/c/Users/marko/AppData/Local/hermes/skills/00-00-readme/sync_new_skills.py"
```

### 6. Doğrulama

Üç yönlü tutarlılık:
- **Disk:** `find /c/Users/marko/AppData/Local/hermes/skills -name SKILL.md | wc -l`
- **API:** `hermes skill scan → skills_list()`
- **Obsidian vault:** `ls -1 /c/Users/marko/OneDrive/Belgeler/Obsidian\ Vault/Hermes/Skills/ | wc -l`

## Karakter Düzeltme Problemleri ve Çözümleri

### Çift Tire (--) → Tek Tire (-)

Windows `ls`'de gözükür, dizin adında sorun oluşturmaz. Hermes skill_manage'da sorun çıkarmaz çünkü tam isimle eşleşir.

### Unicode Combining Characters

Türkçe karakterlerin NFC/NFD formu farkı. Örn:
- `i̇` = `i` + `U+0307` (COMBINING DOT ABOVE)
- Normalde: `i` (noktasız i) → `i` (noktalı i)

**Çözüm:** Python `unicodedata.normalize('NFC', name)` veya `unicodedata.normalize('NFKD', name)` ile birleştir.

### Obsidian Senkronizasyonu

Obsidian Sync, taşıma sonrası eski klasördeki silinmiş skill'leri vault'tan **otomatik silmez**. Manuel temizlik gerekir:

```bash
# Vault'taki dosyaları listele
ls -1 /c/Users/marko/OneDrive/Belgeler/Obsidian\ Vault/Hermes/Skills/

# Disk'te olmayanları temizle (karşılaştırmalı)
```

## Pitfall'lar

- `os.rename` **farklı dosya sistemi** arasında çalışmaz (D: → C:). Aynı sürücüde olduğundan emin ol.
- Windows'ta büyük/küçük harf farkı sorun çıkarmaz, ama Obsidian vault'ta dosya ismi çakışması olabilir.
- API'de skill_count hemen güncellenmez. `hermes skill scan` çalıştırmak gerekir.
