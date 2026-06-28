---
skill_id: 5fe15dfe0520
usage_count: 1
last_used: 2026-06-16
---
# Dosya-Dosya Karşılaştırma Metodolojisi

Bu referans, bir projeyi referans bir sisteme (örn: ReYMeN Agent) karşı dosya bazında, modül bazında karşılaştırma tekniğini açıklar.

## Ne Zaman Kullanılır

- Kullanıcı "şunu şuna benzet" dediğinde ve iki sistem arasında büyük boyut farkı varsa
- Dosya sayısı 10x+ farklı olduğunda soyut kategori karşılaştırması yetmez, somut dosya bazında göstermek gerekir
- Kullanıcı "detaylı karşılaştır" dediğinde

## Adımlar

### 1. Tüm Dosya İsimlerini Topla

Önce her iki sistemin tüm dosyalarını al:

```bash
# Hedef sistem (referans, örn: ReYMeN Agent)
ls -R "C:/hermes/" | sort

# Mevcut proje
ls -R "proje_klasoru/" | sort
```

**ÖNEMLİ:** Bazen MCP filesystem aracı `C:\hermes` gibi yollara erişemez (allowed directories dışı). O zaman `terminal` kullan:

```bash
ls -R "C:/hermes/agent/" | sort
```

### 2. Kategori Başlıkları Belirle

ReYMeN Agent gibi büyük sistemlerde dosyaları mantıksal gruplara ayır:

```
1. ÇEKİRDEK          → agent loop, context engine, conversation
2. LLM PROVIDER      → transport katmanları, provider adapter'ları
3. ARAÇ SİSTEMİ      → tools/ altındaki her .py, motor.py'deki her araç
4. GATEWAY           → platform/ altındaki her kanal
5. SKILL             → skills/ sayısı, yapısı, indeks
6. CLI               → hermes_cli/ altındaki her komut
7. GÜVENLİK          → file safety, redact, threat detection
8. İZLEME            → rate limit, budget, usage
```

### 3. Tablo Oluştur — ✅/❌/⚠️ Sistemi

Her satır için:

```
║ conversation_loop.py — ReAct döngüsü        │ evet (1) │ main.py  │ R'de 321 satır        ║
```

- **✅** = var ve çalışıyor
- **❌** = tamamen yok
- **⚠️** = var ama çok basit/zayıf (yanına satır sayısı yaz)

**Satır sayısı ekle** — bu karşılaştırmanın en önemli detayı:
```
R'de 321 satır    ← yeterli
R'de 64 satır ⚠️ ← zayıf, genişletilmeli
R'de 34 satır ❌  ← iskelet bile sayılmaz
```

### 4. Özet İstatistik Çıkar

Tablonun altına:

```
SİSTEM A: 7.078 dosya, 82 araç, 101 CLI komutu, 30+ platform
SİSTEM B:    59 dosya, 15 araç,  30 CLI komutu,  3 platform
ORAN: ~100x
```

### 5. "Kütüphane Kurulumuyla Çözülebilir" Etiketi

Tabloda her eksik için belirt:

- **pip install ile çözülür** → chromadb, easyocr, bs4 gibi
- **kod değişikliği gerek** → tool sistemi yeniden mimari, gateway genişletme
- **manuel iş gerek** → skill biriktirme, test yazma

Claude Code'a gönderirken sadece "kod değişikliği gerek" olanları listele.

### 6. Özgün Özellikler Bölümü

Karşılaştırmanın sonuna ekle:

```
═══ ReYMeN'E ÖZGÜ (ReYMeN'te OLMAYAN) ═══
- Ekran OCR + tıklama (araclar_ekran.py)  ← ★
- Makro kaydetme/oynatma (araclar_makro.py)
```

Bu bölüm kullanıcıya "senin sistemin değerli, farklı bir iş yapıyor" mesajını verir.
