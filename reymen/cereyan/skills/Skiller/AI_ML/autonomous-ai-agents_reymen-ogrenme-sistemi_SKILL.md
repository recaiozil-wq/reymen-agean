---
name: autonomous-ai-agents-reymen-ogrenme-sistemi
description: loop.ilgili_becerileri_cagir("windows")
title: Autonomous Ai Agents Reymen Ogrenme Sistemi
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

raporlama + Hermes modül entegrasyonu — tüm Reymen bileşenleri
```
### Fonksiyonlar
### Değişen Sınıf Metodları
- `yetenek_olustur()` — frontmatter ile başlar
- `yetenek_ogret()` — `usage_count++` ve `last_used` günceller
- `yetenek_test_et()` — frontmatter varlığını kontrol eder (CRLF uyumlu)
- `_yetenekleri_tara()` — frontmatter'ı parse edip saklar
## Aşama 2: Dinamik Beceri Evrimi
**Dosya:** `closed_learning_loop.py` — `beceri_kristallestir()`
### Fonksiyonlar
### Akış
```
beceri_kristallestir()
  → _fts5_benzer_beceri_ara()
    → VARSA: _merge_beceri_dosyasi()
      → "Yeni Varyasyonlar / Ek Adımlar" başlığı ekle
      → usage_count++, last_used güncelle
      → FTS5 UPDATE
    → YOKSA: _yeni_beceri_olustur()
      → beceri_karti_uret() ile yeni .md, sonra FTS5 INSERT
```
### PITFALL: Merge Sıralaması
`_merge_beceri_dosyasi` içinde şu sıra **ZORUNLUDUR:**
```
1. mevcut_icerik + eklenti → yeni_icerik
2. yol.write_text(yeni_icerik)          ← ÖNCE içerik yaz
3. _frontmatter_guncelle(yol, ...)      ← SONRA frontmatter güncelle
```
Ters sıra yapılırsa: frontmatter güncellenir, sonra eski `mevcut_icerik` (frontmatter'ı güncellenmemiş hal) dosyaya yazılarak güncelleme **silinir**.
### PITFALL: auto_index Performansı
`ClosedLearningLoop.__init__()` varsayılan olarak `auto_index=True` ile tüm skills/ dizinini tarar. 5.000+ dosyada bu ~0.7sn sürer.
**Testlerde `auto_index=False` kullanmak ZORUNLUDUR**, yoksa pytest timeout olur:
```python
loop = ClosedLearningLoop(db_yolu=..., skills_dir=..., auto_index=False)
```
## Aşama 3: Güvenli Bağlam Enjeksiyonu
**Dosya:** `closed_learning_loop.py` — `beceri_baglamini_al()`
- `MAKS_BAGLAM_KARAKTER = 4000` karakter sınırı
- FTS5 BM25 rank ile sıralı sonuç: `_ilgili_becerileri_skorlu()`
- Karakter sınırı aşılınca döngü kırılır, en yüksek skorlu sonuçlar döndürülür
### Kategori Filtreleme (category: IO_Operations)
`ilgili_becerileri_cagir(sorgu, adet, kategori)` ve `_ilgili_becerileri_skorlu(sorgu, adet, kategori)` artık opsiyonel `kategori` parametresi alır:
```python
# Kategorisiz: tüm beceriler taranır
loop.ilgili_becerileri_cagir("windows")

# Kategorili: sadece IO_Operations etiketli beceriler taranır
loop.ilgili_becerileri_cagir("windows", kategori="IO_Operations")
```

FTS5 MATCH sorgusu `"{kategori} AND {sorgu}"` şekline dönüşür. `kategori=None` (default) → eski davranış, geriye dönük uyumlu.

### main.py Entegrasyonu

`main.py`'de her turda `sistem_prompt` oluşturulduktan **hemen sonra**, LLM'e gönderilmeden önce beceri bağlamı eklenir. Detay: `references/main-entegrasyon-pattern.md`

## Bulunan ve Düzeltilen Hatalar

| # | Hata | Sebep | Çözüm |
|---|------|-------|-------|
| 1 | CRLF uyumsuzluğu | Windows `\r\n` satır sonu, kod `\n` bekliyordu | Tüm fonksiyonlarda `icerik.replace("\r\n", "\n")` normalizasyonu |
| 2 | Merge sıralama | Önce frontmatter güncellenip sonra eski içerik yazılıyordu | Önce içerik yaz, sonra frontmatter güncelle |
| 3 | `last_used` tipi | float timestamp (`st_mtime`) string yerine yazılıyordu | `datetime.now().strftime("%Y-%m-%d")` |
| 4 | Frontmatter alan koruma | Özel alanlar yeni frontmatter'da kayboluyordu | Tüm alanları tarayan döngü eklendi |
| 5 | FTS5 index güncellemesi | Migration betiği FTS5'i güncellemiyordu | `_fts5_index_guncelle()` eklendi |
| 6 | Yedek silme hatası | OneDrive kilidi `shutil.rmtree`'yi patlatıyordu | Fallback: zaman damgalı yedek |

## Windows CRLF Uyumluluğu (Genel Kural)

Windows'ta `write_text()` ile yazılan dosyalar `\r\n` (CRLF) satır sonu kullanır. **Herhangi** bir dosya parse/güncelle fonksiyonu yazarken:

```python
# Her zaman normalize et
icerik_norm = icerik.replace("\r\n", "\n")
# Sonra normalize edilmiş metin üzerinde çalış
if icerik_norm.startswith("---\n"):
    ...
```

Bu kural Windows'ta **tüm** metin dosyası işlemleri için geçerlidir. Detay: `references/crlf-normalizasyon-pattern.md`

## Test

Her iki dosyada `if __name__ == "__main__":` bloğu mevcuttur:
```bash
python yetenek_fabrikasi.py
python closed_learning_loop.py
```

### Otonom Test Modülü

**Dosya:** `test_learning_loop.py` (17 test, 3 kategori)

```bash
# Tüm testler
pytest test_learning_loop.py -v

# Kategori bazlı
pytest test_learning_loop.py -v -k "HappyPath"
pytest test_learning_loop.py -v -k "Kaos"
pytest test_learning_loop.py -v -k "Negatif"
```

| Kategori | Test | Açıklama |
|----------|------|----------|
| HappyPath | 6 | Temel frontmatter, beceri oluşturma, merge, bağlam |
| Kaos | 6 | CRLF, read-only, bozuk meta, bozuk dosya, alan koruma |
| Negatif | 5 | Boş sorgu, sınır aşımı, olmayan dosya, geçersiz ad |

### Özel Not: PermissionError Teardown

Windows'ta read-only testinin `finally` bloğunda dosyayı yazılabilir yapmak **ZORUNLUDUR**. 3 kademeli çözüm. Detay: `references/read-only-teardown-pattern.md`

### ZORUNLU KURAL: Kırılma Analizi

Her görev/çözüm **sonrasında** şu soruyu sor:

> "Bu çözüm hangi ortamda/koşulda kırılır?"

Edge case'leri önceden düşün (Windows için):
- CRLF satır sonu (`\r\n` vs `\n`)
- OneDrive dosya kilidi (PermissionError)
- Read-only cleanup başarısızlığı
- FTS5 index tutarsızlığı
- Temp dizin silinememesi
- chmod sınırlamaları (S_IWRITE / S_IREAD)
- Bozuk/geçersiz meta veri
- Concurrent erişim

Sadece happy path değil, alternatif senaryoları da test et. Bu kural atlanırsa "Kritik Sistem Hatası" sayılır.

\n---\n\n## Claude Code Bridge — Analiz → Kod Düzeltme\n\nReymen (Hermes) bulguyu yapar, Claude Code düzeltmeyi kodlar.\n\n### İş Akışı\n\n```\n🧠 Reymen (analiz + strateji)\n   → Kodu tara, hatayı bul, çözüm stratejisi belirle\n   → Bridge komutu oluştur (hedef dosyalar + ne yapılacağı)\n   \n📤 vscode_yaz.bat <komut>\n   → VS Code Claude Agent input'una yapıştır + Enter\n   \n🛠️ Claude Code (kod düzeltir)\n   → Dosyaları okur, düzeltir, test eder\n   \n🔍 Reymen (kontrol)\n   → Dosyaları doğrula, yeni hata var mı kontrol et\n   → Çözümü skill/Obsidian olarak kaydet\n```\n\n### Bridge Komutu Formatı\n\n```\nGörev: <dosya_adı> düzeltmesi\n\n## Bulgu\n<Hermes'in analizi: hata nedir, nerede, neden>\n\n## Yapılacaklar\n1. <adım 1>\n2. <adım 2>\n\n## Kısıtlamalar\n- Hermes import kullanma\n- Reymen dosyalarını değiştirme\n- Sadece belirtilen dosyayı düzelt\n```\n\n### Kullanım\n\n```bash\nterminal(command='powershell -ExecutionPolicy Bypass -Command \"& C:\\\\Users\\\\marko\\\\AppData\\\\Local\\\\hermes\\\\scripts\\\\vscode_yaz.bat Görev: ...\"')\n```\n\n### Önemli\n\n- Claude Code'a **ne yapılacağını** değil, **neyin düzeltileceğini** söyle — strateji Hermes'ten\n- Kısıtlamaları net yaz (hangi dosyalara dokunma, hangi import'lar yasak)\n- Sonucu her zaman kontrol et — Claude Code bazen gereksiz değişiklik yapar\n- Başarılı çözümü skill olarak kaydet\n\nDetay: Hermes `claude-code` skill → `references/windows-orchestration-bridge.md`

## Aşama 5: Stratejik Ajan Seçici

**Dosya:** `akilli_yonlendirici.py` — `stratejik_ajan_sec()` + `ajan_talimatini_getir()`

5 ajan personası (genel_cozucu, kod_uzmani, sistem_mimari, guvenlik_uzmani, veri_uzmani), 30+ hata deseni, LLM çağrısı yapmaz.

### main.py Entegrasyonu

`main.py`'nin `calistir()` metodunda, circuit breaker bloğu içinde:

1. Hata algılanır → `stratejik_ajan_sec(aktif_ajan_id, gozlem)` çağrılır
2. Ajan değişirse → yeni persona prompt'a enjekte edilir, hata sayacı sıfırlanır
3. 3 ardışık hata → reflexion/circuit breaker normal akışı devreye girer

Detay: `references/stratejik-ajan-secici.md`

## Aşama 6: Çöküş Raporlayıcı

**Dosya:** `cokus_raporlayici.py` — `cokus_raporu_uret()`

Maks tur aşılınca insan-okunabilir crash raporu → `.ReYMeN/cokus_raporlari/`

### main.py Entegrasyonu

`main.py` satır ~802: maks tur aşılınca otomatik çağrılır. Graceful degrade (try/except).

Detay: `references/cokus-raporlayici.md`

Bu skill, `windows-dev-check` yeteneğine bağımlıdır. Her görev öncesi `category: IO_Operations` filtresiyle windows-dev-check'in 8 KIRILMA KOŞULU'nu doğrula.

## Dosya Yolları

```
C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\
├── yetenek_fabrikasi.py
├── closed_learning_loop.py
└── migrate_skills.py
```
