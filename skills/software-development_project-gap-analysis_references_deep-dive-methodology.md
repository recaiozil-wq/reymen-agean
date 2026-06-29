---
name: software-development_project-gap-analysis_references_deep-dive-methodology
description: Derinlemesine Çoklu-Repo Karşılaştırma Metodolojisi
title: "Software Development Project Gap Analysis References Deep Dive Methodology"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Derinlemesine Çoklu-Repo Karşılaştırma Metodolojisi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Derinlemesine Çoklu-Repo Karşılaştırma Metodolojisi

Bu referans, `project-gap-analysis` skill'inde 2+ sistem aynı anda karşılaştırıldığında kullanılacak derin-dalış tekniğini açıklar.

## Ne Zaman Kullanılır

- Kullanıcı elinde birden fazla kod tabanı (repo) varsa ve bunları birbiriyle karşılaştırmak istiyorsa
- "Şunun eksiklerini bul, diğerinden ne alabiliriz" benzeri bir talep geldiğinde
- Yüzeysel dosya listesi yetmez, her dosyanın içeriğini anlamak gerektiğinde

## Adım 1: Fiziksel Envanter Çıkar

Tüm sistemlerin dosya envanterini aynı anda al:

```bash
# Her sistem için ayrı ayrı:
cd "SISTEM_YOLU" && find . -type f -name "*.py" | sort
cd "SISTEM_YOLU" && wc -l *.py 2>/dev/null | sort -rn

# Sadece proje dosyaları (venv, __pycache__, node_modules hariç):
cd "SISTEM_YOLU" && find . -type f -name "*.py" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/node_modules/*" | sort
```

**ÖNEMLİ:** `find` çıktısı çok büyükse (500+ satır), venv/site-packages/npm gibi bağımlılık klasörlerini hariç tut. Yoksa anlamlı envanter göremezsin.

## Adım 2: wc -l ile Büyüklük Haritası

Satır sayıları sana hangi dosyanın önemli olduğunu söyler:

```bash
# Tüm .py dosyalarının satır sayıları (büyükten küçüğe)
cd "SISTEM_YOLU" && wc -l *.py 2>/dev/null | sort -rn | head -30
```

Kurallar:
- **500+ satır** = Ana modül (CLI, web UI, gateway gibi)
- **200-500 satır** = Önemli yardımcı (agent runtime, batch runner gibi)
- **50-200 satır** = Araç/ek modül
- **<50 satır** = Basit araç, config wrapper

Bu ayrımı yapmadan hangi dosyayı okuyacağına karar verme.

## Adım 3: Sistematik Dosya Okuma (15+ Dosya)

Yüzeysel analiz yapma — en az 10-15 dosyayı oku:

```txt
OKUMA SIRASI:
  1. Ana giriş dosyası (main.py, app.py) → İlk 80 satır (CONFIG, imports)
  2. CLI dosyası (varsa) → İlk 80 satır (argparse yapısı)
  3. Gateway/iletişim → İlk 50 satır
  4. Motor/eylem çözümleyici → TAMAMEN OKU (genelde küçük)
  5. LLM provider → İlk 60 satır
  6. Web UI (varsa) → İlk 60 satır
  7. MCP serve (varsa) → TAMAMEN OKU
  8. Agent runtime → TAMAMEN OKU
  9. Self-improvement → TAMAMEN OKU
  10. Kritik araçlar (ekran, makro, web) → TAMAMEN OKU
  11. Küçük araçlar (tool_registry, salted_gateway) → TAMAMEN OKU
  12. Config/README/CLAUDE.md
```

**Neden 80 satır?** Çoğu Python dosyasında class tanımı, CONFIG, importlar ve docstring ilk 50-80 satırda biter. Oradan sonra gelen metodların ne yaptığını isimlerinden anlayabilirsin.

## Adım 4: Progress Tracking (Todo)

Her adımda `todo` kullan:

```python
# İlk adım
todo(merge=False, todos=[
  {"id": "1", "content": "Sistem A yapısını tara", "status": "in_progress"},
  {"id": "2", "content": "Sistem B yapısını tara", "status": "pending"},
  {"id": "3", "content": "Dosya bazında karşılaştırma", "status": "pending"},
  {"id": "4", "content": "Eksiklik raporu", "status": "pending"},
])
```

Bitince `completed`, bloklanınca `cancelled` yap. Bu:
- Uzun analizlerde hangi adımda olduğunu hatırlamanı sağlar
- Kullanıcıya anlık durum gösterir
- Kesintisiz çalışmanı sağlar

## Adım 5: Yüzde-Tamamlama Değerlendirmesi

Her sistem için bir yüzde ver:

```txt
SİSTEM A — Durum: %X TAMAM
┌──────────────────────────────────┬──────────┐
│ Kriter                           │ Durum    │
├──────────────────────────────────┼──────────┤
│ 1. Çalışan ReAct döngüsü         │ ✅ Var   │
│ 2. Çoklu LLM provider            │ ✅ Var   │
│ 3. CLI (20+ alt komut)           │ ✅ Var   │
│ 4. Gateway (multi-channel)       │ ⚠️ Eksik │
│ 5. MCP desteği                    │ ❌ Yok   │
│ ...                              │          │
└──────────────────────────────────┴──────────┘
```

Yüzde hesabı: `(✅ sayısı / toplam kriter) × 100`

Kriter sayısını abartma — 8-15 kriter yeterli. Fazlası anlamsızlaştırır.

## Adım 6: "Eksikler Raporu" Değil "Durum Raporu" Ver

Kullanıcıya sadece eksikleri değil, **her sistemin ne durumda olduğunu**, **neyin fazla olduğunu** (diğerinde olmayan özellik) da göster:

```txt
SİSTEM A'da olan ama SİSTEM B'de olmayan:
  - Feature X
  - Feature Y

SİSTEM B'de olan ama SİSTEM A'da olmayan:
  - Feature Z
```

Bu, kullanıcının hangi sistemi ne için kullanacağına karar vermesini sağlar.

## .env Okuma Sorunu

Bazı araçlar `.env` dosyasını güvenlik nedeniyle okumaz (secret-bearing file). Çözüm:

```bash
# Terminal ile oku (tool bypass)
cat "SISTEM_YOLU/.env" 2>/dev/null | head -30

# Sadece anahtar isimlerini görmek için (değerleri gizle)
cat "SISTEM_YOLU/.env" 2>/dev/null | grep "=" | cut -d= -f1
```

## Adım 7: Runtime Doğrulama (Opsiyonel — Tavsiye Edilir)

Tüm yapısal analiz bittiğinde, projenin GERÇEKTEN çalıştığını kanıtlamak için
katmanlı runtime testi yap:

```txt
KATMAN 1: Import testi      → tüm .py import edilebiliyor mu?
KATMAN 2: Provider ping     → LLM bağlantısı var mı?
KATMAN 3: Web UI serve      → HTTP 200 dönüyor mu?
KATMAN 4: MCP sunucu        → tool listesi geliyor mu?
KATMAN 5: Session DB        → daha önce çalışmış mı? (kayıt var mı?)
KATMAN 6: ReAct döngüsü     → agent hedef alıp işleyebiliyor mu?
```

Her katman rapora somut kanıt ekler. Detay → [runtime-verification.md](runtime-verification.md)

**NEDEN ÖNEMLİ:** Bir proje struktur olarak eksiksiz görünebilir
ama:
- API anahtarları *** maskeliyse → provider çalışmaz
- .env yoksa → config boş gelir
- chromadb yoksa → vektör hafıza yedek belleğe düşer (çalışır ama yavaş)

Runtime testi bunların hepsini ortaya çıkarır.

## Örnek Çıktı Formatı (Proje Karşılaştırma Tablosu)

```txt
═════════════════════════════════════════════
X. SİSTEM KARŞILAŞTIRMASI
═════════════════════════════════════════════

KRİTİK EKSİKLER:
┌─────────────────────────────────────┬──────────────────────────────┐
│ Özellik                            │ R>eYMeN'de var mı?          │
├─────────────────────────────────────┼──────────────────────────────┤
│ 1. 1.000+ skill                    │ ❌ Sadece 6 beceri kartı     │
│ 2. Prompt caching                  │ ❌ Yok                       │
│ 3. Web search (multi-provider)     │ ⚠️ Basit                    │
└─────────────────────────────────────┴──────────────────────────────┘

SİSTEM A'da olan ama SİSTEM B'de olmayan:
  - Feature X — HERMES'TE YOK, PROJEYE ÖZGÜ

SİSTEM B'de olan ama SİSTEM A'da olmayan (en kritik):
  1. Notion entegrasyonu
  2. Rate limiting

DURUM: Sistem A %75 TAMAM, Sistem B %60 TAMAM
```
