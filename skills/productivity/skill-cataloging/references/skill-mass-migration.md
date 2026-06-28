---
skill_id: a55739a44235
usage_count: 1
last_used: 2026-06-16
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
| hermes-agent | ReYMeN ayarları |
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
- **Obsidian vault:** `ls -1 /c/Users/marko/OneDrive/Belgeler/Obsidian\ Vault/ReYMeN/Skills/ | wc -l`

## Karakter Düzeltme Problemleri ve Çözümleri

### Çift Tire (--) → Tek Tire (-)

Windows `ls`'de gözükür, dizin adında sorun oluşturmaz. ReYMeN skill_manage'da sorun çıkarmaz çünkü tam isimle eşleşir.

### Unicode Combining Characters

Türkçe karakterlerin NFC/NFD formu farkı. Örn:
- `i̇` = `i` + `U+0307` (COMBINING DOT ABOVE)
- Normalde: `i` (noktasız i) → `i` (noktalı i)

**Çözüm:** Python `unicodedata.normalize('NFC', name)` veya `unicodedata.normalize('NFKD', name)` ile birleştir.

### Obsidian Senkronizasyonu

Obsidian Sync, taşıma sonrası eski klasördeki silinmiş skill'leri vault'tan **otomatik silmez**. Manuel temizlik gerekir:

```bash
# Vault'taki dosyaları listele
ls -1 /c/Users/marko/OneDrive/Belgeler/Obsidian\ Vault/ReYMeN/Skills/

# Disk'te olmayanları temizle (karşılaştırmalı)
```

## Pitfall'lar

### 🚨 Aynı İsimde Dosyalar — `mv` Sessiz Üzerine Yazar

Farklı klasörlerde aynı ada sahip `.md` dosyaları varsa, `mv kaynak/* hedef/` ile taşırken son taşınan dosya öncekinin üzerine **sessizce yazar** (hiçbir uyarı vermez, hata kodu 0 döner).

**Örnek:** `mlops/session-aware-qa.md` ve `reymen/session-aware-qa.md` → ikisi de `test/qa/` altına taşındı → 1 dosya sessizce kayboldu.

**Korunma adımları:**

1. **Taşıma öncesi tarama:**
   ```bash
   # Aynı isimde dosya var mı kontrol et
   cd /hedef/dizin
   find . -type f -name '*.md' | sed 's|.*/||' | sort | uniq -d
   ```
   Çıktı boşsa güvenle taşıyabilirsiniz.

2. **`cp -n` ile no-clobber taşıma (güvenli):**
   ```bash
   # Önce kopyala (üzerine yazmaz)
   cp -rn kaynak/* hedef/
   # Fark kontrolü
   diff -r kaynak hedef
   # Sonra temizle
   rm -rf kaynak
   ```

3. **Taşıma sonrası sayım doğrulaması:**
   Taşıma öncesi toplam dosya sayısını not et. Taşıma sonrası aynı olmalı.
   Bire bir eşleşmiyorsa, aynı isimde dosya çakışması olmuş olabilir.

- `os.rename` **farklı dosya sistemi** arasında çalışmaz (D: → C:). Aynı sürücüde olduğundan emin ol.
- Windows'ta büyük/küçük harf farkı sorun çıkarmaz, ama Obsidian vault'ta dosya ismi çakışması olabilir.
- API'de skill_count hemen güncellenmez. `hermes skill scan` çalıştırmak gerekir.

## İlgili Skill'ler

- `5n1k-kategori-duzenleme` — Proje seviyesi skill'leri 27+ 5N1K ana başlık altında organize etme (bu doküman Hermes profili migration'ı içindir, onun proje içi skill düzenleme içindir)
