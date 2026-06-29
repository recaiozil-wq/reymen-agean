---
name: autonomous-ai-agents_claude-code_references_import-chain-debugging
description: Import Zinciri Hata Ayıklama Metodolojisi
title: "Autonomous Ai Agents Claude Code References Import Chain Debugging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Import Zinciri Hata Ayıklama Metodolojisi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Import Zinciri Hata Ayıklama Metodolojisi

Hermes'in bulduğu import kırıklarını Claude Code'a düzelttirme yöntemi.

## Adımlar

### 1. Modülü Tek Başına Test Et
```
python -c "import modul_adi" 2>&1
```

### 2. Zinciri Takip Et
Her `ImportError` döndüğünde, hata mesajındaki **son dosyaya** bak. O dosyadaki import satırı bir sonraki hedeftir.

### 3. Eksik Şeyi Bul
- **Sabit** (değişken/constant) eksikse → tanımla (`= 0` veya `= {}` yeter)
- **Fonksiyon** eksikse → stub ekle (`def f(): return None`)
- **Modül** eksikse → import'u try/except ile sar

### 4. Düzelt ve Tekrar Dene
Her düzeltmeden sonra zincirin en üstündeki modülü import et. Yeni hata çıkarsa adım 2'ye dön.

### 5. Ne Zaman Durmalı
5+ tur düzeltmeden sonra hala yeni hatalar çıkıyorsa:
1. Modülü main.py'de `try/except` ile sar (graceful degrade)
2. Kullanıcıya rapor et
3. Alternatif: Claude Code'a toplu gönder

## Püf Noktalar
- **Dosya vs Paket Çakışması:** `X.py` (dosya) ile `X/` (paket) aynı anda var olduğunda Python dosyayı bulur. Çözüm: dosyayı yeniden adlandır.
- **Büyük-Küçük Harf:** Windows dosya sisteminde fark etmez ama Python import'larında bazen fark eder.
- **Graceful Degrade:** Çözülemeyen import'ları `try/except` ile sar.
