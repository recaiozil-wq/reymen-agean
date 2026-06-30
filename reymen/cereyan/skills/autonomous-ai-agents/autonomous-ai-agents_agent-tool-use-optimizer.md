---
name: autonomous-ai-agents_agent-tool-use-optimizer
title: Agent Tool-Use Optimizer
description: "Optimize AI agent tool selection, call patterns, and error recovery for efficient task completion."
tags: [agents, tools, optimization, efficiency, tool-calls]
category: autonomous-ai-agents
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Optimize AI agent tool selection, call patterns, and error recovery for efficient task completion. |
| **Nerede?** | autonomous-ai-agents/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Agent Tool-Use Optimizer

AI ajanlarının araç kullanımını optimize ederek daha hızlı, daha az maliyetli ve daha güvenilir sonuçlar elde etmeyi sağlar.

## 🎯 Temel Stratejiler

### 1. Araç Seçimi Optimizasyonu

Doğru aracı seçmek için karar matrisi:

| Durum | En İyi Araç | Alternatif |
|-------|-------------|------------|
| Dosya okuma | `read_file` | `search_files` (büyük dosyalar) |
| Metin arama | `search_files(target='content')` | `grep` (terminal) |
| Dosya yazma | `write_file` | `patch` (mevcut dosya düzenleme) |
| Shell komutu | `terminal` | `execute_code` (Python için) |
| Web'de ara | `web_search` | `browser_navigate` (detaylı okuma) |
| Dosya listele | `search_files(target='files')` | `directory_tree` (hızlı bakış) |
| Kod çalıştırma | `execute_code` | `terminal` (sistem komutları) |
| Veri analizi | `execute_code(Python)` | `terminal` (SQL, awk) |

### 2. Paralel Çağrı Deseni

Bağımsız işlemleri gruplayarak round-trip sayısını azalt:

```python
# KÖTÜ: Sıralı çağrılar (3 round-trip)
result1 = tool_a()
result2 = tool_b()
result3 = tool_c()

# İYİ: Paralel çağrılar (1 round-trip)
# Tüm bağımsız çağrıları tek mesajda yap
result1, result2, result3 = tool_a(), tool_b(), tool_c()
```

**Paralel çağrı kuralları:**
- Bağımlılığı olmayan tüm araç çağrılarını grupla
- Maksimum 8 paralel çağrı
- Her çağrı bağımsız olmalı (birinin sonucu diğerine bağımlı olmamalı)

### 3. Hata Kurtarma Desenleri

| Hata | Strateji | Fallback |
|------|----------|----------|
| Dosya bulunamadı | Alternatif yol dene | search_files ile bul |
| Ağ zaman aşımı | 3 kere dene (exponential backoff) | Farklı endpoint dene |
| Permission denied | Sudo/root gerekiyor | Kullanıcıya bildir |
| Syntax hatası | Kodu düzeltip yeniden dene | Alternatif yaklaşım dene |
| API rate limit | 60 saniye bekle | Kuyruğa al |

### 4. Maliyet Optimizasyonu

Tool çağrılarının token maliyetini azaltma:

```
Strateji                Tasarruf      Risk
─────────────────────────────────────────────
Batch okuma             30-40%        Düşük
Önbellekleme            50-60%        Düşük
Özyinelemeli arama      20-30%        Orta
Sonuçları birleştirme   15-25%        Düşük
Gereksiz çağrıları atla 10-40%        Düşük
```

### 5. Tool-Use Chain Pattern

```python
# Zincirleme araç kullanımı
chain = [
    ("search_files", {"pattern": "*.py", "path": "src/"}),
    ("read_file", {"path": lambda r: r[0]}),  # Önceki sonuca bağımlı
    ("execute_code", {"code": lambda r: f"analyze({repr(r)})"}),
]
```

## ⚡ Hızlı İpuçları

1. **Önce ara, sonra oku**: `search_files` ile bul, `read_file` ile oku
2. **Batch IO**: Küçük dosyaları grupla, tek seferde oku
3. **Pipeline**: `terminal` ile zincirleme komutlar (`cmd1 && cmd2`)
4. **Cache**: Sık kullanılan verileri değişkende tut
5. **Early exit**: İlk yeterli sonuçta dur

## 🚫 Kaçınılması Gerekenler

- Aynı veriyi iki kere isteme
- Her küçük işlem için ayrı round-trip yapma
- Büyük dosyaları `read_file` ile okuma (terminal ile head/tail kullan)
- Web sayfasını snapshot almadan tıklama
