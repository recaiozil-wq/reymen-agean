---
name: software-development_project-gap-analysis_references_scored-comparison-format
description: Puanlı Karşılaştırma Formatı
title: "Software Development Project Gap Analysis References Scored Comparison Format"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Puanlı Karşılaştırma Formatı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Puanlı Karşılaştırma Formatı

İki sistemi (örn: Hermes vs R>eYMeN, Hermes vs Claude) tüm geçmiş verilerle kapsamlı ve puanlı karşılaştırmak için kullanılan format.

## Ne Zaman Kullanılır

- Kullanıcı "karşılaştır puanla" veya "kıyasla" dediğinde
- İki projenin artı/eksi yönlerini somut puanlarla göstermek gerektiğinde
- Kullanıcı "hangisi daha iyi" diye sorduğunda (tek cevap yerine kategorilere böl)
- Claude Code'a hangi projeye odaklanacağını göstermek için

## Adımlar

### Adım 1: Sayısal Verileri Topla

Her iki sistemin somut metriklerini çıkar:

```bash
# Python dosya sayısı
find /path/to/project/ -name "*.py" ! -path "*/__pycache__/*" ! -path "*/venv/*" | wc -l

# Kod satırı
find /path/to/project/ -name "*.py" ! -path "*/__pycache__/*" ! -path "*/venv/*" -exec wc -l {} + | tail -1

# Test sayısı
find /path/to/project/tests/ -name "*.py" | wc -l

# Tool sayısı
ls /path/to/project/tools/*.py 2>/dev/null | wc -l
```

### Adım 2: Genel Tablo

Önce bir ham veri tablosu göster:

```
| Metrik | Sistem A | Sistem B | Fark |
|--------|:--------:|:--------:|:----:|
| Python dosyası | 2,379 | 625 | 3.8x |
| Kod satırı | 121,372 | 15,413 | 7.9x |
| Tool sayısı | 86 | 88 | +2 🏆 |
| Skill sayısı | 1,059 | ~6 | 176x |
```

### Adım 3: 7 Kategoride Puanlama (10 üzerinden)

Her kategori için ayrı tablo, her tabloda 3-5 kriter, her kriter 0-10 puan.

**Standart 7 kategori:**

| # | Kategori | Neye Bakılır |
|:-:|----------|-------------|
| 1 | Kod Olgunluğu & Derinlik | dosya sayısı, kod satırı, hata yönetimi, docstring, modülerlik |
| 2 | Özgünlük & Kimlik | kendi mimarisi, rakiplerden farkı, özgün araçlar, bağımsızlık |
| 3 | Kod Kalitesi | try/except, docstring kapsamı, renkli çıktı, --help, bütünsel geliştirme |
| 4 | Çalışma Kararlılığı | startup başarısı, kesintisiz çalışma, gateway bağlantısı, test geçme oranı |
| 5 | Ekosistem & Araçlar | skill sistemi, cron, bellek katmanları, plugin, gateway platform |
| 6 | Kullanıcı Deneyimi | kurulum, kullanım, CLI, dökümantasyon, hata mesajları |
| 7 | Proje Ömrü & Bakım | ekip büyüklüğü, güncelleme sıklığı, arka plandaki ekip |

**Tablo formatı:**

```
#### N. KATEGORİ ADI
| Kriter | Sistem A | Sistem B |
|--------|:--------:|:--------:|
| Kriter 1 | 9 | 6 |
| Kriter 2 | 10 | 4 |
| **TOPLAM** | **8.0** | **5.0** |
```

### Adım 4: Son Skor Tablosu

Tüm kategorileri tek tabloda topla:

```
| # | Kategori | Sistem A | Sistem B | Kazanan |
|:-:|----------|:--------:|:--------:|:-------:|
| 1 | Kod Olgunluğu | 8.0 | 6.8 | A |
| 2 | Özgünlük & Kimlik | 8.8 | 7.3 | A |
| 3 | Kod Kalitesi | 4.8 | 8.8 | B 🏆 |
| | **GENEL ORTALAMA** | **7.5** | **7.1** | **A** |
```

### Adım 5: Tarihsel Dönüm Noktaları

Her sistemin kullanıcıyla yaşadığı önemli olayları kronolojik sırala (son güncellemeden itibaren):

**Sistem A'nın yolculuğu:**
- ✏️ 247 kırık link düzeltildi
- ✏️ 1.059 skill'e Router+Reference yapısı
- ✏️ 166 şişkin skill references/ altında
- ⚠️ Telegram gateway 2 kere düştü, kurtarıldı

**Sistem B'nin yolculuğu:**
- ✏️ 23 araçtan 88 araca (Hermes'i geçti)
- ✏️ CLI: 10 modülden 130 modüle (12.5x)
- ✏️ 5.095 test, %100 başarı

### Adım 6: Özet

3 maddelik özet:

```
| Yön | Açıklama |
|-----|----------|
| A'nın güçlü yanı | Ölçek, olgunluk, skill ekosistemi |
| A'nın zayıf yanı | Kod kalitesi, kararlılık |
| B'nin güçlü yanı | Kod kalitesi, test kapsamı, özgün araçlar |
| B'nin zayıf yanı | Küçük ekip, skill sistemi emekleme |
```

Kazananı söyle ve nedenini 1 cümleyle açıkla.
