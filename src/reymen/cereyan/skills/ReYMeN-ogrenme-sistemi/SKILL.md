---
name: ReYMeN-ogrenme-sistemi
description: ReYMeN ajanı için kapalı öğrenme döngüsü — YAML frontmatter, FTS5 çakışma kontrolü, güvenli bağlam enjeksiyonu
category: genel
last_used: 2026-06-16
skill_id: SKILL
usage_count: 4
version: 1.0.0
---

# ReYMeN Öğrenme Sistemi

Kapalı döngü öğrenme mimarisi: görev bittiğinde öğren, bir daha aynı hatayı yapma.

Kapsar: `closed_learning_loop.py` + `yetenek_fabrikasi.py` + `migrate_skills.py`

Referans: `references/crlf-normalizasyon-pattern.md`
Referans: `references/read-only-teardown-pattern.md`
Referans: `references/main-entegrasyon-pattern.md`
Referans: `references/hafiza-pitfall-json-index-fts5-stale.md`

## Aşama 0: Veri Taşıma (Migration)

**Dosya:** `migrate_skills.py` (tek seferlik bağımsız betik)

Mevcut skills/ dizinindeki frontmatter içermeyen .md dosyalarına YAML frontmatter ekler.

### Akış

1. Yedek al (skills/ → skills_backup/). Eski yedek silinemezse (OneDrive kilidi) zaman damgalı yedek al: `skills_backup_YYYYMMDD_HHMMSS/`
2. Tüm .md dosyaları taranır, `---\n` ile başlamayanlar tespit edilir
3. Her dosyaya: `skill_id` (MD5 hash), `usage_count: 1`, `last_used: [bugün]` frontmatter'ı eklenir
4. **FTS5 index güncellenir** — `_fts5_index_guncelle()` ile
5. Orijinal Markdown içeriği bozulmaz

### ÖNEMLİ: FTS5 Güncellemesi

Migration betiği sadece dosyayı güncellemekle kalmaz, `.hermes/skills_index.db` içindeki FTS5 kaydını da UPDATE eder. Bu olmazsa FTS5 aramaları eski (frontmatter'sız) içeriği tarar.

### Kullanım

```bash
python migrate_skills.py
```

## Aşama 1: YAML Frontmatter

**Dosya:** `yetenek_fabrikasi.py`

Her `.md` beceri kartının en üstüne standart YAML frontmatter:

```yaml
---
skill_id: <md5_hash_ilk_12_karakter>
usage_count: 1
last_used: 2026-06-16
---
```

### Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `_frontmatter_olustur(ad, usage_count=1)` | YAML frontmatter bloku üretir |
| `_frontmatter_parse(icerik)` | CRLF/LF uyumlu — önce `\r\n` → `\n` normalize eder, sonra sözer |
| `_frontmatter_guncelle(dosya_yolu, alan, deger)` | Dosyadaki frontmatter alanını günceller, TÜM alanları korur |
| `beceri_karti_uret(beceri_adi, aciklama, adimlar, skills_dir)` | Standalone fonksiyon |

### Değişen Sınıf Metodları

- `yetenek_olustur()` — frontmatter ile başlar
- `yetenek_ogret()` — `usage_count++` ve `last_used` günceller
- `yetenek_test_et()` — frontmatter varlığını kontrol eder (CRLF uyumlu)
- `_yetenekleri_tara()` — frontmatter'ı parse edip saklar

## Aşama 2: Dinamik Beceri Evrimi

**Dosya:** `closed_learning_loop.py` — `beceri_kristallestir()`

### Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `_fts5_benzer_beceri_ara(beceri_adi)` | FTS5 MATCH (fallback LIKE) ile benzer isim ara |
| `_merge_beceri_dosyasi(...)` | Mevcut dosyaya merge et |
| `_yeni_beceri_olustur(...)` | Yeni dosya oluştur (fallback ile) |

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
| 7 | SQL result index kayması | `row[4]` (hata_sayisi) kaynak olarak kullanılıyordu | `row[2]` (kaynak) düzeltildi |
| 8 | FTS5 stale cache hit | Bozuk skill dosyası FTS5'te kaldı, cache hit döndürüyor | Dosya + index silindi, içerik doğrulama eklendi |
| 9 | Hızlı yol web aramasını atlıyor | `?` içerdiği için fiyat sorguları hızlı yola gidiyor | Güncel kelime tespiti → ReAct'e düşer |

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

### Bağımlılık: windows-dev-check

Bu skill, `windows-dev-check` yeteneğine bağımlıdır. Her görev öncesi `category: IO_Operations` filtresiyle windows-dev-check'in 8 KIRILMA KOŞULU'nu doğrula.

## Dosya Yolları

```
C:\Users\marko\OneDrive\Desktop\ReYMeN Proje\hermes_projesi\
├── yetenek_fabrikasi.py
├── closed_learning_loop.py
└── migrate_skills.py
```

---

## İyileştirme #1: OnceHafiza DB Şeması (2026-06-21)

**Dosyalar:**
- `reymen/cereyan/once_hafiza.py` — Modül-seviye fonksiyonlar (`isle()`, `kaydet()`, `ara()`, `hafizada_ara()`)
- `reymen/sistem/once_hafiza.py` — Class tabanlı OnceHafiza (agent entegrasyonu için)
- `once_hafiza.py` — Root shim (her yerden import edilebilir)

### ogrenmeler Tablosu

```sql
CREATE TABLE IF NOT EXISTS ogrenmeler (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    hedef             TEXT NOT NULL,
    kategori          TEXT NOT NULL DEFAULT 'genel',
    icerik            TEXT NOT NULL,
    guven_skoru       REAL NOT NULL DEFAULT 1.0,
    basari_sayisi     INTEGER NOT NULL DEFAULT 1,
    hata_sayisi       INTEGER NOT NULL DEFAULT 0,
    son_kullanim      TEXT NOT NULL DEFAULT (date('now')),
    gecerlilik_tarihi TEXT NOT NULL DEFAULT (date('now', '+180 days')),
    olusturulma       TEXT NOT NULL DEFAULT (datetime('now')),
    guncelleme        TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### Ana API Fonksiyonları

```python
from once_hafiza import kaydet, ara, isle, hafizada_ara

# Kaydet — otomatik guven_skoru hesaplar (basari/(basari+hata))
kaydet(hedef="gorev_adi", kategori="kali/network/nmap", icerik="...", basari=True)

# Ara — kategori filtresi + guven esigi + gecerlilik kontrolu
kayitlar = ara("nmap", kategori="kali/network", min_guven=0.3, gecerli_mi=True)
# Donus: [{"id", "hedef", "kategori", "icerik", "guven_skoru", "durum": "guvenilir"|"belirsiz"}]

# Isle — hafiza-oncelikli calistirma
sonuc, kaynak = isle("gorev", kategori="genel", calistir=lambda: terminal("..."))
# kaynak: "cache" (hafizadan) / "exec" (calistirildi) / "not_found"

# Guven guncelle
guven_guncelle(kayit_id=12, basari=True)  # basari++ veya hata++

# Istatistik
istatistik()  # toplam, gecerli, eski, ortalama_guven, kategori_dagilimi
```

### Guven Skoru

```
guven_skoru = basari_sayisi / (basari_sayisi + hata_sayisi)
  >= 0.5 → "guvenilir" — cache'ten direkt dondur
  <  0.5 → "belirsiz"  — uyar + dogrula
  >  0.8 → LLM atlanir, direkt hafizadan dondur (sifir maliyet)
```

### Gecerlilik

```
gecerlilik_tarihi = bugun + 180 gun
  eski_kayitlari_temizle(gun_limiti=200): guven<0.8 ve gecerlilik gecmis olanlari sil
  yuksek guvenli (>=0.8) olanlar korunur
```

### Kategori Sistemi

Hiyerarsik kategori yapisi (slash ile ayrilir):
```
"kali"                   → Kali Linux genel
"kali/network"           → Kali ag araclari
"kali/network/nmap"      → Nmap spesifik
"kali/network/nmap/skills" → Nmap flag bilgisi
```
Ayni kategori icinde arama: `ara("nmap", kategori="kali/network/nmap")`
Ust kategoride arama: `ara("nmap", kategori="kali/network")` (eslesmez — tam eslesme gerekir)

---

## İyileştirme #2-3: conversation_loop.py'ye 3 İyileştirme (2026-06-21)

**Dosya:** `reymen/cereyan/conversation_loop.py`

### Tam Karar Ağacı (Aktif)

```
GÖREV GELIR
  ↓
① ONCE_HAFIZA.hafizada_ara(hedef, kategori)
  ├── guven > 0.8  → "HAFIZA ATLAMASI: %60 maliyet düşüşü" → DÖNDÜR (0 LLM)
  └── guven <= 0.8 veya bulunamadi → devam
                                    ↓
② ONCELIK_CACHE (selam/teşekkür vs.)
  ├── eşleşme var → "CACHE ATLAMASI" → DÖNDÜR (0 LLM)
  └── yok → devam
            ↓
③ LLM DÖNGÜSÜ (DeepSeek, max 90 tur)
  ├── Her tur: sistem prompt + hafiza bilgisi + tool calls
  ├── Maks 3 retry (exponential backoff)
  └── 3 ardisik hata → KALICI circuit breaker (otomatik acilmaz)
```

### 8 Çıkış Koşulu

| # | Kosul | Detay | Kod (satir) |
|:-:|:------|:------|:------------|
| 1 | guven_skoru > 0.8 | Hafizadan direkt, LLM yok | 409-435 |
| 2 | Cache eslesmesi | Selam/tesekkur direkt dondur | 480-496 |
| 3 | budget(90) doldu | IterationBudget devam_etmeli_mi=false | 546-556 |
| 4 | GOREV_BITTI | LLM "bitti" dedi | ~1013 |
| 5 | tool.tamamlandi=true | Tool "bitti" sinyali | ~554 |
| 6 | Takilma (3x) | Ayni eylem 3x tekrar | ~559 |
| 7 | Circuit breaker (3x) | 3 ardisik hata, kalici dur | ~508 |
| 8 | Ctrl+C | Kullanici iptali | ~490 |

### Sabitler

```python
# Dosya: conversation_loop.py ~satir 182-207
CIRCUIT_BREAKER_MAX_HATA = 3     # 3 ardisik hata → kalici dur
CIRCUIT_BREAKER_KALICI = True     # otomatik acilmaz
CIRCUIT_BREAKER_SURESI = 0        # # kalici (sure yok)
MAX_RETRY = 3                      # mekanik retry: max 3 deneme
TAKILMA_ESIĞI = 3                  # ayni eylem 3x → takilma

# Oncelik cache (selamlasma/tesekkur bypass)
ONCELIK_CACHE = {
    "merhaba": "Merhaba! Size nasıl yardımcı olabilirim?",
    "selam": "Selam! Nasıl yardımcı olabilirim?",
    "hey": "Hey! Yardımcı olmamı istediğin bir şey var mı?",
    "teşekkür": "Rica ederim! Başka bir şeye ihtiyacın var mı?",
    "tesekkur": "Rica ederim! Başka bir şeye ihtiyacın var mı?",
    "sağol": "Ne demek, her zaman!",
    "sagol": "Ne demek, her zaman!",
    "görüşür": "Görüşmek üzere! İyi günler.",
    "gorusur": "Görüşmek üzere! İyi günler.",
}
```

### Hafiza Bypass Kodu (satir ~387-444)

```python
from reymen.sistem.once_hafiza import OnceHafiza
_oh = OnceHafiza()
hafiza_sonuc = _oh.hafizada_ara(hedef, kategori="")
if hafiza_sonuc:
    guven = float(hafiza_sonuc.get("guven", 0))
    if guven > 0.8:
        # LLM cagrilmadan direkt dondur
        return {"yanit": f"[Hafizadan] {cozum}"}
```

### KALICI Circuit Breaker Mesaji (satir ~508)

```
[KALICI DURDURMA] 3/3 ardisik hata. 3 deneme hakkiniz doldu.
```

---

## Hafıza Güncelleme Workflow (2026-06-21)

Web'den ogrenilen bilgiyi mevcut hafizaya nasil ekleyecegini belirleyen karar agaci:

### Adim Adim

```
ADIM 1: Web'den bilgi topla
  web_search + web_extract (resmi dokuman oncelikli)
  Kaynaklari isaretle: URL, tarih, guvenilirlik

ADIM 2: Mevcut skill ile karsilastir
  ara(hedef, kategori) ile mevcut kayitlari sorgula
  Farklari tablo ile goster

ADIM 3: Catisma cozumu — NE YAPILIR?

  | Eski bilgi | Yeni bilgi | Karar |
  |:-----------|:-----------|:------|
  | Dogru ama eksik | Detayli | ✅ UPDATE (append) — eskiyi koru, yeni ekle |
  | Yanlis | Dogru | ❌ OVERWRITE — tamamen degistir |
  | Celisiyor | Celisiyor | ⚠️ IKISINI DE TUT + not dus |
  | Ayni bilgi tekrar | Ayni | ✅ basari++ (guven artar) |

ADIM 4: Kaynagi kaydet
  Icerige URL ve tarih ekle (kaynak kolonu yoksa icerige gom)
  Ornek:
  ```
  === Kaynaklar ===
  [1] https://nmap.org/book/scan-methods-udp-scan.html
  [2] https://security.stackexchange.com/q/52566
  ```

ADIM 5: GUNCELLE (INSERT degil)
  UPDATE ogrenmeler SET icerik=?, basari_sayisi=basari_sayisi+1, ...
  Kayit sayisi DEGISMEMELI — ayni ID'yi guncelle
```

### PITFALL: Kaynak Kolonu Eksik

Mevcut DB'de `kaynak` kolonu YOK. `reymen/cereyan/once_hafiza.py`'nin `_kur()` fonksiyonunda CREATE TABLE'e eklenmedi. Kaynak bilgisi `icerik` icine gomulur. Gelecekte ALTER TABLE ile eklenmeli.

### ReYMeN vs Hermes Farkı

| Boyut | ReYMeN | Hermes |
|:------|:-------|:-------|
| **Mimari** | Muhendislik: hafiza oncelikli, LLM son care | LLM-first: her sey LLM, hafiza opsiyonel |
| **Maliyet** | Dusuk (cache + LLM'siz kararlar) | Yuksek (her adimda LLM) |
| **Hiz** | Hizli (cache'ten direkt) | Yavas (LLM her seyi dusunur) |
| **Tutarlilik** | Yuksek (SQLite, kuralli) | Orta (LLM dalgalanir) |
| **Unutkanlik** | Az (SQLite kalici) | Cok (her oturum sifir) |
| **Retry garantisi** | Var (3 retry + circuit breaker) | Yok (LLM insiyatifi) |
| **Cross-oturum** | Dunku bilgiyi bugun kullanir | Yeni oturum = yeni hayat |
