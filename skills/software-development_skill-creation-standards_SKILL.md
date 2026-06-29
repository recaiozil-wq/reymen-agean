---
name: software-development-skill-creation-standards
description: '# skill_view(name=''skill-creation-standards'')'
title: Software Development Skill Creation Standards
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

structure, frontmatter requirements, and zero-bloat policy. Load before any skill_manage(action='create')
  or skill_manage(action='edit') call.
```
**YASAL UYARI:** `license:` alanı frontmatter'da **kullanılmaz**. Bu repo Unlicense (Public Domain) olarak yayımlanmıştır — hiçbir yasal yükümlülük, garanti veya kısıtlama yoktur. Skill içinde license belirtmek bu durumla çelişir.
**ORİJİN İZİ TEMİZLİĞİ:** Frontmatter'da şu alanlar **KESİNLİKLE bulunmamalıdır** (NemoClaw/ECC/NVIDIA kalıntıları):
- `phase:` — NVIDIA eğitim modülü numarası
- `lesson:` — NVIDIA ders numarası
- `origin:` — ECC/oh-my-agent-check kaynak işareti
- `tools:` — NemoClaw araç listesi
Bu alanlar varsa silinmelidir. Ayrıca tag'lerde `nemo`, `nemo-guardrails` gibi NVIDIA ürün adları varsa `guardrails` olarak değiştirin.
Detaylı şema ve örnekler → [references/frontmatter-standards.md](references/frontmatter-standards.md)
### 3. Sıfır Şişkinlik Politikası
Dosya içine devasa kod blokları, log çıktıları veya ham metinler **doğrudan gömülmeyecektir.** Hepsi referans dosyalarına asenkron çağrı yapılacak şekilde tasarlanacaktır.
Kod taşıma kuralları → [references/sifir-siskinlik.md](references/sifir-siskinlik.md)
## Kullanım
```yaml
# skill_manage çağrısından ÖNCE bu skill'i yükle:
# skill_view(name='skill-creation-standards')
# references/ altındaki ilgili dosyaları oku
# Sonra skill_manage(action='create'|'edit') yap
```

## Skill Deployment (Oluşturma/Güncelleme Sonrası)

Skill kaydedildikten sonra **5 adım tamamlanmalıdır**:

```
1. Hermes'e kaydet (skill_manage)
2. Origin izlerini temizle (phase/lesson/origin/tools — NemoClaw/ECC/NVIDIA kalıntıları)
3. Obsidian'a sync et (sync_skills_to_obsidian.py)
4. GitHub hermes-skills reposuna push et
5. Repo README + description/topics güncel mi kontrol et
```

Detaylı workflow → [references/deployment-workflow.md](references/deployment-workflow.md)

**Sık yapılan hata:** Skill sadece yerel Hermes'e kaydedilip GitHub'a push edilmez. Bu durumda skill diğer cihazlara gitmez ve repo güncel kalmaz.

**Sık yapılan hata #2:** Repo README'si, description ve topic'ler güncellenmez. GitHub ana sayfası eski/kalabalık kalır. README'deki istatistikler (skill sayısı, reference sayısı) güncellenmeli.

**Sık yapılan hata #3:** Skill rewrite (temizlik) sırasında eski reference'lar GitHub'da kalır. `git rm` ile silinmeli, yoksa repo şişer.

### Skill Rewrite (Temizlik) Prosedürü

Eski bir skill'in reference'ları birikip şiştiğinde (35+ dosya gibi) tamamen temizlemek gerekir:

```
1. skill_manage(action='edit') ile SKILL.md'yi yeniden yaz
2. Eski references/ klasörünü sil (rm -rf)
3. Eğer skill adı ile aynı isimde references/*.md varsa → AMBIGUITY hatası oluşur
4. Her mes-skills reposunda da aynı temizliği yap
5. git rm ile eski dosyaları kaldır, git add -A ile yenisini ekle
6. Obsidian sync
```

**Skill isim çakışması (ambiguity) pitfall:** `references/lm-studio-local-llm.md` gibi bir dosya, skill adıyla aynı ismi taşırsa `skill_view(name='lm-studio-local-llm')` çağrısı `"Ambiguous skill name"` hatası verir. **Çözüm:** Referans dosyaları asla skill adını taşımamalıdır. Açıklayıcı ama farklı isimler kullanın (örn. `api-kullanimi.md`, `sorun-giderme.md`).

## İhlal Durumu

Standartlara uymayan bir skill oluşturulursa (örn. 10KB+ tek dosya, frontmatter'sız, kod gömülü):

1. `skill-shrink` otomatik dedektörü yakalar
2. Router + Reference yapısına böler
3. references/ altına taşır
4. Kullanıcıya bildirim gider

## Verification Checklist

### Skill Yapısı
- [ ] Ana SKILL.md ≤ 3-4 KB
- [ ] Uzunsa references/ altına bölünmüş
- [ ] Frontmatter valid YAML — title, tags, audience var
- [ ] `license:` alanı frontmatter'da yok (Unlicensed repo)
- [ ] Kod blokları, loglar, ham metinler references/'de
- [ ] `skill_view(name)` ile yüklenebiliyor (ambiguity yok)
- [ ] references/ altında skill adıyla aynı isimde dosya yok
- [ ] Origin izleri temiz (phase/lesson/origin/tools yok)
- [ ] Tag'lerde nemo/nvidia marka adları yok
- [ ] Obsidian'a sync edildi
- [ ] GitHub hermes-skills reposuna push edildi
- [ ] Eski reference'lar GitHub'da temizlendi (git rm)
- [ ] Repo README istatistikleri güncel

### Kod Bütünlüğü (Python/.env/config)
Herhangi bir Python dosyası, `.env` veya YAML/JSON config patch'lendiğinde aşağıdakileri kontrol et:
- [ ] `f"..."` prefix'i — `print("...{DEGISKEN}...")` gibi f-string'siz print'ler literal `{DEGISKEN}` basar. Her print/string interpolation'da f öneki var mı kontrol et
- [ ] `.env` satır bütünlüğü — yazılan her satırda `ANAHTAR=DEGER` formatı bozulmamış mı? Yorumlar (`#`) ayrı satırda mı, değerin içine karışmamış mı?
- [ ] `***` kontrolü — `deger == "***"` yerine `deger.startswith("***")` kullan (`***xxx` formatlı değerleri de yakalamak için). Aynı kural `"...", "*** ", "***xxx"` varyasyonları için de geçerli
- [ ] Hardcoded değer var mı? — `.env`'de tanımlı bir değişken (`REYMEN_MAX_TURNS`, `PORT`, `MODEL` gibi) Python kodunda hardcode edilmiş mi? `` yerine `os.environ.get("...")` kullan
- [ ] Model adı tutarlılığı — test blokları, `__main__` blokları ve varsayılan config'ler güncel model adını mı kullanıyor? Eski model adları (`llava-v1.6-mistral-7b` → `cognitivecomputations.dolphin3.0-llama3.1-8b` gibi) kalmış mı?
- [ ] Terminal/Python ile yazılan dosyalar — `write_file` aracı bazen satır sonlarını bozabilir. Özellikle `.env` ve yapılandırma dosyalarını yazdıktan sonra `cat` veya Python ile okuyarak doğrula
