---
name: 5n1k-kategori-duzenleme
title: "5N1K Kategori Düzenleme — Skill Dosyalarını Ana/Alt Başlıklara Yerleştirme"
description: "Use when reorganizing skill .md files into the 27+ 5N1K category system. Covers: bulk move, directory merge, rename, duplicate filename detection, and verification at scale."
version: 1.0.0
audience: maintainer
tags: [skills, organization, categories, 5n1k, bulk-move]
---

# 5N1K Kategori Düzenleme

Bir projedeki skill `.md` dosyalarını 27+ ana başlık altında organize etme prosedürü. Özellikle `misc/` gibi dağınık klasörleri doğru kategorilere dağıtmak, küçük klasörleri birleştirmek ve klasör isimlerini standartlaştırmak için.

## Ne Zaman Kullanılır

- Skill sayısı 200+ ve kategorize edilmemiş `misc/` benzeri klasörler biriktiğinde
- Yeni bir ana başlık eklendiğinde (örn. `ag/`, `test/`, `sistem/`)
- 5N1K formatına uygun hale getirilmemiş skill'ler olduğunda
- Klasör isimleri standart dışı olduğunda (örn. `software-development/` → `kod/`)

## Ana Başlıklar (27+ Kategori Sistemi)

| Dizin | Emoji | Ana Başlık | Açıklama |
|-------|-------|-------------|----------|
| `ai-ml/` | 🤖 | AI/ML | agent-systems, ecc, evaluation, inference, mcp, memory, multimodal, nlp, prompt, rag, safety, training, vision |
| `kod/` | 💻 | Kod | Software development, coding patterns |
| `windows/` | 🪟 | Windows | automation, shortcuts, system, troubleshooting |
| `devops/` | 🚀 | DevOps | infrastructure, cicd, scaling |
| `security/` | 🔒 | Güvenlik | safety, audit, compliance, red-team |
| `productivity/` | ⚡ | Verimlilik | email, ocr, workflow, workbench |
| `creative/` | 🎨 | Yaratıcı | content-creation, ascii, excalidraw, p5js, music, video |
| `media/` | 📺 | Medya | audio, video, youtube, gif |
| `ag/` | 🌐 | Ağ | network, vpn, firewall, router, port-scan |
| `test/` | 🧪 | Test | benchmark, qa, framework |
| `katalog/` | 📋 | Katalog | Ana katalog dosyaları (SKILLS_KATALOG, SKILL_INDEX) |
| `sistem/` | 🔬 | Sistem | windows, linux, boot |
| `user/` | 👤 | Kullanıcı | Kullanıcı profili ve tercihleri |
| `research/` | 📚 | Research | arxiv, blogwatcher, llm-wiki |
| `egitim/` | 📚 | Eğitim | note-taking, obsidian |
| `gaming/` | 🎮 | Gaming | Oyun geliştirme ve araçları |
| `github/` | 🐙 | Github | PR, issue, repo yönetimi |
| `kali/` | 🧅 | Kali | Kali Linux pentest araçları |
| `reymen/` | ⚙️ | ReYMeN | Projeye özel skill'ler |
| `tor/` | 🧅 | Tor | Tor ağı ve gizlilik |
| `voice/` | 🔊 | Voice | Ses ve konuşma |
| `android/` | 📱 | Android | Mobil uygulama |
| `apple/` | 🍎 | Apple | iOS/Mac geliştirme |
| `cross-platform/` | 🔗 | Cross-platform | Platformlar arası araçlar |
| `data-science/` | 📊 | Veri Bilimi | Jupyter, pandas, HF Hub |
| `smart-home/` | 🏠 | Smart Home | Hue ve IoT |
| `social-media/` | 🌐 | Sosyal Medya | Bot ve otomasyon |
| `autonomous-ai-agents/` | 🤖 | Autonomous Agents | Otonom ajan yapılandırması |
| `mlops/` | 🔧 | MLOps | model yönetimi, inference, training |

## Prosedür

### 1. Durum Tespiti

```bash
# Kök dizinde başıboş dosya var mı?
find . -maxdepth 1 -type f -name '*.md'

# misc/ gibi dağınık klasör var mı?
for d in */; do
  total=$(find "$d" -type f -name '*.md' | wc -l)
  echo "$d → $total"
done
```

### 2. misc/ Dağıtma

`misc/` bir "çöp kutusudur" — içindeki her alt klasör doğru ana başlığa taşınmalıdır:

| misc/ Alt Klasörü | Hedef | Gerekçe |
|-------------------|-------|---------|
| agent-systems | `ai-ml/agent-systems/` | AI ajan sistemleri |
| architecture | `ai-ml/architecture/` | AI mimarisi |
| evaluation | `ai-ml/evaluation/` | AI değerlendirme |
| hermes-integration | `ai-ml/hermes-integration/` | Hermes AI entegrasyonu |
| llm-inference | `ai-ml/inference/` | LLM çıkarım |
| mcp-integration | `ai-ml/mcp/` | MCP protokolü |
| prompt-engineering | `ai-ml/prompt/` | Prompt mühendisliği |
| rag-search | `ai-ml/rag/` | RAG arama |
| training | `ai-ml/training/` | AI eğitimi |
| vision | `ai-ml/vision/` | Bilgisayarlı görü |
| safety-security | `security/safety/` | Güvenlik |
| infrastructure | `devops/infrastructure/` | DevOps altyapı |
| gaming | `gaming/` | Oyun |
| video | `media/video/` | Medya video |

```bash
# Örnek: misc/ alt klasörlerini taşıma
mkdir -p ai-ml/agent-systems
mv misc/agent-systems/* ai-ml/agent-systems/ && rm -rf misc/agent-systems
```

### 3. Küçük Klasörleri Birleştirme

Tek başına duran küçük klasörler uygun ana başlık altına taşınır:

| Kaynak | Hedef | Gerekçe |
|--------|-------|---------|
| `content-creation/` | `creative/content-creation/` | Yaratıcı içerik |
| `email/` | `productivity/email/` | Verimlilik aracı |
| `video/` | `media/video/` | Medya |
| `audio/` | `media/audio/` | Medya |
| `vision/` | `ai-ml/vision/` | AI görü |

```bash
mkdir -p media/video
mv video/* media/video/ && rm -rf video
```

### 4. Klasör İsmi Standardizasyonu

| Eski İsim | Yeni İsim | Gerekçe |
|-----------|-----------|---------|
| `ai/` | `ai-ml/` | AI/ML ana başlığıyla uyum |
| `software-development/` | `kod/` | 5N1K "Kod" başlığı |
| `note-taking/` | `egitim/` | 5N1K "Eğitim" başlığı |

```bash
mv ai ai-ml
mv software-development kod
mv note-taking egitim
```

### 5. Eksik Ana Başlıkları Oluşturma

Kullanıcının 5N1K tablosunda olup da fiziksel dizini olmayan ana başlıklar için:

```bash
mkdir -p ag/network ag/vpn ag/firewall ag/router ag/port-scan
mkdir -p test/benchmark test/qa test/framework
mkdir -p sistem/windows sistem/linux sistem/boot
mkdir -p katalog
```

### 6. Doğrulama

```bash
# Toplam dosya sayısı
grand=$(find . -type f -name '*.md' | wc -l)
echo "TOPLAM: $grand"

# Önceki toplamla karşılaştır (kayıp var mı?)
# Kayıp varsa aynı isimde dosya çakışması olabilir

# Kategori bazında dağılım
for d in */; do
  total=$(find "$d" -type f -name '*.md' | wc -l)
  printf "%-25s %4d\n" "$d" "$total"
done

# Boş klasör var mı?
find . -type d -empty
```

## Pitfall'lar

### 🚨 Aynı İsimde Dosyalar — Sessiz Üzerine Yazma

En tehlikeli hata. Farklı klasörlerde aynı ada sahip `.md` dosyaları varsa, `mv kaynak/* hedef/` ile taşırken son taşınan dosya öncekinin üzerine **sessizce yazar** (hiçbir uyarı vermez).

**Örnek:** `mlops/session-aware-qa.md` ve `reymen/session-aware-qa.md` → ikisi de `test/qa/` altına taşındığında, ikincisi birincinin üzerine yazar → **1 dosya kaybı**.

**Korunma:**
```bash
# Taşımadan ÖNCE aynı isimde dosya var mı kontrol et
cd skills
find . -type f -name '*.md' | sed 's|.*/||' | sort | uniq -d
```
Bu komut tüm `.md` dosyalarını tara ve **birden fazla yerde bulunan aynı isimdeki dosyaları** listeler. Çıktı boşsa güvenle taşıyabilirsiniz.

**Alternatif (cp ile):** `mv` yerine önce `cp -n` (no-clobber) yap, sonra `rm -rf` kaynak:
```bash
# Önce kopyala (üzerine yazmaz)
cp -rn misc/agent-systems/* ai-ml/agent-systems/
# Sonra kontrol et
diff -r misc/agent-systems ai-ml/agent-systems
# Sonra temizle
rm -rf misc/agent-systems
```

### Windows Git-Bash Yol Sorunları

- `find "$d"` içinde `$d` değişkeni çift tırnak içinde olmalı (boşluklu yollar için)
- Eğer `find -maxdepth` çağrısında `"ai-ml/"` gibi tırnaklı değişken kullanılıyorsa, bash onu literal string olarak yorumlayabilir → "No such file or directory" hatası
- **Çözüm:** Değişkenleri tırnaksız veya doğrudan `find` çağrısında yaz

### Alt Klasör Sayma

```bash
# Doğru: skills/ kökünden say
total=$(find "ai-ml" -type f -name '*.md' | wc -l)

# Yanlış: for döngüsünde "$d" değişkeni (sonunda / var)
# "ai-ml/" şeklinde, -maxdepth 2 -mindepth 2 ile alt-klasör sayısı
# "${d%/}/" şeklinde temizlenmeli
subs=$(for s in "$d"*/; do [ -d "$s" ] && echo "$s"; done | wc -l)
```

## Related

- `skill-cataloging/references/skill-mass-migration.md` — Hermes profili skill migration (farklı senaryo)
- `skill-creation-standards` — 5N1K formatında skill oluşturma standartları
