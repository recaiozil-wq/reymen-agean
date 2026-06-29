---
name: software-development-self-improvement-loop
description: 15 dakikada bir cron job ile çalışır (`*/15 * * * *`). Veya günde 1 (`0
  1 * * *`).
title: Software Development Self Improvement Loop
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

→ cron yönetimi → sonlu kampanyalar'
# Self-Improvement Loop

## Tetikleyici
15 dakikada bir cron job ile çalışır (`*/15 * * * *`). Veya günde 1 (`0 1 * * *`).
`repeat=N` ile sonlu kampanya, `repeat=forever` ile sürekli döngü.
- 7 gün × 24 saat × 4 (15dk) = 672 iterasyon
- Son iterasyonda otomatik durur, final raporu gönderilir

## Çalışma Modları

### Mod A — Normal Döngü (5 alan rotasyonu)
Sırayla döner:
1. Hafıza yönetimi
2. Planlama
3. Kod kalitesi
4. Hız
5. Hata düzeltme

Her saat bir alan. 5 saatte tüm alanlar tazelenir.
session_search ile hangi alanın sırada olduğunu bul (son kararın "Sonraki Alan" satırından çıkar).

#### Alan Tanımları (konkre tool çağrıları)

| # | Alan | Ne Yapılır? | Tool'lar |
|:-:|------|-------------|----------|
| 1 | **Hafıza yönetimi** | decisions.md tutarlılık kontrolü + INDEX.md güncelle + MEMORY.md gürültü temizliği (bkz. `references/memory-noise-cleanup.md`) + USER.md okuma + eski state dosyalarını temizleme (`.pid`, `.lock`, `.tmp`) + Karar #N eksik/kopuk kontrolü | `read_file`, `search_files`, `patch`, `write_file` |
| 2 | **Planlama** | (a) Proje geneli syntax doğrulama: `py_compile.compile()` ile tüm .py dosyalarını tara (vendor dizinleri hariç: venv, node_modules, .git, hermes-memory-backup, __pycache__, desktop, dist), (b) Core modül import testi: 9+ temel modülü (`toolsets`, `sistem_talimati`, `reymen.sistem.toolsets`, `reymen.cereyan.beyin`, `ReYMeN_cli.env_loader`, vb.) `importlib.import_module()` ile dene, (c) Test dosyası syntax scan (145+ dosya), (d) upstream Hermes release'lerini kontrol et (bkz. `scripts/planlama-scan.py`), (e) kalan hata/config warning'lerini tespit et | `session_search`, `search_files`, `web_search`, `web_extract`, `terminal` (`python3 -c "py_compile.compile(...)"`, `timeout 10 python3 scripts/`) |
| 3 | **Kod kalitesi** | `search_files` ile regex kokuları tara + `ast.walk()` ile bare-except (sadece Exception değil) tespiti + BOM karakteri kontrolü (`--fix-bom` ile otomatik düzeltme) + syntax doğrulama + `# TODO`/FIXME tespiti. **Script ile çalıştır** (bkz. `scripts/code_quality_scan.py`): `python3 scripts/code_quality_scan.py --proj PATH` — 5 kontrolü tek seferde yapar. `--fix-bom` flagi eklenince BOM'lu dosyaları otomatik düzeltir. Detaylar: `references/code-smell-detection.md` | `search_files`, `terminal` (python3 scripts/code_quality_scan.py --proj PATH), `skill_view` (references) |
| 4 | **Hız** | (a) session.db boyut kontrolü (bulunamazsa atla — Hermes internal olabilir), (b) `__pycache__/` temizliği (main project sadece, .ReYMeN hariç), (c) büyük dosya tespiti (>500 satır, refactor adayı, Python kodu ile), (d) INDEX.md'ye Hız skoru ekle (yoksa), (e) decisions.md'de kayıt | `terminal`, `search_files`, `execute_code` |
| 5 | **Hata düzeltme** | session_search ile son 24 saatteki hata/kırılma tespiti + yeni import/kırık test sorgulaması + decisions.md'ye **her durumda** kayıt (0 hata = sistem sağlıklı raporu) | `session_search`, `search_files`, `read_file` |

**Pitfall:** Alan 1 (Hafıza yönetimi) sadece INDEX.md güncelleme DEĞİLDİR. Önce decisions.md'nin Karar #1'den son karara kadar eksiksiz olduğunu teyit et, sonra INDEX.md'ye yansıt. "decisions.md güncel" varsayımı yapma — oku.

**Pitfall: decisions.md gap tespiti (numaralandırma).** Karar numaralarında atlama (ör: #3→#7) tespit edilirse:
- Atlanan kararlar içerik bilinmiyorsa **uydurma** — sadece "Karar #4-6 kayıp" notu ekle
- Root `decisions.md` (numbered, Karar #N) ile `.ReYMeN/decisions.md` (dated daily entries) **ayrı dosyalardır**. İkisini de oku.
- `.ReYMeN/decisions.md` genelde numarasız girişler içerir — bu normaldir, düzeltme gerektirmez.

**Pitfall: decisions.md duplicate Karar # (aynı numara, farklı içerik).** GAP'ten farklıdır — iki farklı karar aynı #N altında yazılmış olabilir (ör: `## Karar #19 — Kod Kalitesi` ardından `## Karar #19 — 4 Eksik Kod`). Tespit:
- `read_file` ile decisions.md'yi oku, `^## Karar #(\d+)` kalıbındaki tüm satırları topla
- Son karar no'su ile toplam `## Karar #` satır sayısını karşılaştır — eşit değilse dupe var
- **Sadece en sonraki dupe'i yeniden numaralandır** — geriye dönük tüm dupe'leri düzeltmeye çalışma (decisions.md kronolojisini bozar)
- Fix: `patch("## Karar #N — ...", "## Karar #N+1 — ...")` ile en sondaki dupe'in header'ını değiştir
- Yeni karar eklemeden önce son karar no'sunu teyit et

**Pitfall: MSYS path resolution — `/c/Users/...` yazma, `C:\Users\...` kullan.**
Windows'ta git-bash/MSYS2 shell kullanıldığında `/c/Users/...` gibi **MSYS yolları** `patch` ve `write_file` tool'larına verildiğinde çifte `c:` öneki eklenebilir (`C:\c\Users\...` → dosya bulunamaz/hatalı yazma).
- ❌ `patch(path="/c/Users/marko/Desktop/proje/.ReYMeN/decisions.md")` → `C:\c\Users\...`
- ✅ `patch(path="C:\\Users\\marko\\Desktop\\proje\\.ReYMeN\\decisions.md")`
- ✅ `read_file(path="C:/Users/marko/Desktop/proje/.ReYMeN/INDEX.md")` — ileri slash da çalışır, yeter ki Windows sürücü harfiyle başlasın
- `search_files` ve `terminal` (`cd /c/Users/...`) MSYS yollarını doğru çözümler — buralarda `/c/...` güvenlidir
- `patch`, `write_file`, `read_file` **kesinlikle** Windows native path (`C:\...` veya `C:/...`) ile çağrılmalı

**Pitfall: "Partial Write" gap (iki yönlü) — INDEX.md ↔ decisions.md tutarsızlığı.**
Önceki cron iterasyonu bir dosyayı güncellemiş ama diğerini atlamış olabilir. İKİ yön de mümkün:

**Yön A — INDEX.md güncellenmiş, decisions.md güncellenmemiş.**
Önceki cron iterasyonu INDEX.md header'ını güncellemiş (ör: "Self-Improvement cron — Hata düzeltme — 2. tur İt. 13" at 20:05) ama decisions.md'ye karar yazmamış olabilir. Tespit:
1. INDEX.md header'ındaki iterasyon no'su ile decisions.md'deki son Karar no'sunu karşılaştır
2. decisions.md'de "Sonraki Alan" tablosundaki ⏳ satırı hala kalmışsa ve INDEX.md o alanı ✅ olarak gösteriyorsa → gap var
3. Aradaki iterasyonu INDEX.md header bilgisinden doldur: önceki cron INDEX.md'ye yazdıysa hangi alan olduğu bellidir
4. Recovery: `read_file` ile INDEX.md header'ını oku → hangi alan/kaçıncı tur olduğunu çıkar → "0 hata" varsa rekonstrüksiyon yap → Karar #N olarak decisions.md'ye ekle

**Yön B — decisions.md güncellenmiş (Karar #N var), INDEX.md güncellenmemiş (header hala eski alanı gösteriyor).**
Tespit:
1. decisions.md'deki son Karar no'sunu oku, INDEX.md header'ındaki İt. no'su ile karşılaştır
2. decisions.md'deki "Sonraki Alan" satırı bir sonraki alana işaret ediyorsa ve INDEX.md rotation status satırı hala o alanı ⏳ gösteriyorsa → gap var
3. Recovery: decisions.md kararından alan bilgisini çıkar, INDEX.md header + rotation status satırını güncelle. decisions.md'deki Karar #N içeriği INDEX.md header'ına yansıt

**Her iki yön için ortak doğrulama:**
- Düzeltme sonrası INDEX.md ↔ decisions.md tutarlılığını doğrula (ikisi de aynı son iterasyonu referans alıyor olmalı)
- Sadece decisions.md veya sadece INDEX.md okumak yetmez — İKİSİNİ de oku

**Pitfall:** GÖZLEM adımı `memory` tool'unu kullanmayı varsayar, ancak memory config'de devre dışı bırakılmış olabilir (`Memory is not available`). Bu durumda:
- `memory` çağrısı fail eder — hatayı yakala ve atla (kritik değil)
- Alternatif: `session_search` ile son iterasyon durumunu kontrol et
- Memory yoksa, karar kaydı doğrudan decisions.md'ye yapılır

**Pitfall:** Alan 5 (Hata düzeltme) 0 hata bulduğunda:
- Hala decisions.md'ye kaydet — **"0 hata" bir sonuçtur**, atlanmamalıdır
- Tablodaki her metrik için "0" olduğunu belirt
- Bu, sistemin sağlıklı olduğunu kanıtlar — sessiz geçiş yapma

**Pitfall:** Tur tamamlama (tüm 5 alan bittiğinde):
- INDEX.md'de `"1. tur tamam ✅ (Hafıza→Planlama→Kod→Hız→Hata)"` yaz
- Yeni tur başlangıcını işaretle: `"➡️ 2. tur başlıyor → Hafıza yönetimi (İt. N+1)"`
- decisions.md'de "Sonraki Alan" tablosunun altına yeni tur satırı ekle: `| **1** (yeni tur) | **Hafıza yönetimi** | ⏳ Sonraki → **İt. N+1** |`
- Tur sayacını artır: INDEX.md son güncelleme satırına tur bilgisini ekle

**Pitfall:** Nested quotes in `execute_code`. `terminal(f'python3 -c "...")` inside `execute_code` causes syntax errors because the outer single-quote (f'...') and inner double-quote (python3 -c "...") collide. **Fix:** Write inline Python to a `.py` file first with `write_file`, then `terminal("python3 path/to/script.py")` to call it. This avoids quote-escaping entirely and produces a reusable script.

**Pitfall:** INDEX.md dual-update. INDEX.md has TWO places that need updating after each Alan:
1. **Header lines 2-3**: `> Son güncelleme: ...` + `> Kaynak: Self-Improvement cron — {Alan adı}`
2. **Rotation status line** (~line 43): `➡️ 2. tur — Alan X ✅ → **Sonraki Alan 🔜** (İt. N+1)`
Both must be patched. Missing either causes INDEX.md to show stale data.

**Pitfall: Terminal bloke = scheduler tick atlamaz.** Eğer ana konuşmada `terminal()` ile uzun süreli bir işlem çalışıyorsa (ör: pytest, big find, compile), scheduler yeni cron tick'i başlatamaz. **Çözüm:**
- Cron prompt'unda asla `pytest` veya uzun süren terminal komutu kullanma — timeout'a düşer
- `timeout N` ile her terminal çağrısını sınırla (max 30sn)
- Backup cron'ları (no_agent=True) ayrı thread'de çalışır, LLM cron'larıyla çakışmaz
- Hızlı biten işlemler için foreground + timeout kullan, background=TRUE kullanma

**Pitfall: `pytest --collect-only` hang yiyor.** Test dosyalarından biri import sırasında bloke oluyorsa (örn. `run_interrupt_test.py` → `AIAgent` import), `pytest --collect-only` sonsuza kadar bekler ve cron timeout'a düşer. **Kullanma.** Bunun yerine:
- Syntax kontrolü: `python3 -c "compile(open(f).read(), f, 'exec')"` (5sn timeout'lu)
- Import kontrolü: `timeout 5 python3 -c "import importlib; importlib.import_module('tests.$(basename $f .py)')"` (her dosya için ayrı)
- **Proje geneli scan:** `py_compile.compile()` ile tüm .py dosyalarını tara (vendor hariç: venv, node_modules, .git, hermes-memory-backup, __pycache__, desktop, dist) + `importlib.import_module()` ile 9+ core modülü test et. `scripts/planlama_scan.py` sadece `tests/` dizinini tarar — daha kapsamlı scan için `python3 -c` ile `os.walk` + `py_compile.compile` döngüsü çalıştır.

**Pitfall: Scoring engine (`_puanla.py`).** Alan 2 (Planlama) ve Alan 5 (Hata) sonuçlarını değerlendirirken `reymen/sistem/_puanla.py`yi kullan:
```python
from reymen.sistem._puanla import hesapla, karar_aciklamasi
sonuc = hesapla(url=url, tarih=tarih, kaynak_sayisi=3)
# puan > 0.7 kaydet, 0.4-0.7 danis, < 0.4 reddet
```
Puan = guncellikx0.3 + kaynakx0.3 + dogrulamax0.2 + celiskix0.2.

**Pitfall: Cross-agent iletişim (`_ajan_iletisim.py`).** Kali/Windows/CAD arasında JSON mesajlaşma:
```python
from reymen.sistem._ajan_iletisim import AjanIletisim
ai = AjanIletisim()
mid = ai.gonder("kali", "windows", komut="PORT_SCAN", icerik={"port": 1234})
msgs = ai.al("windows")
ai.ack(msgs[0]["mesaj_id"])
ai.heartbeat("kali")
```
Timeout 30sn. Retry max 3. Circuit breaker 3 hata.

**Pitfall: DB cleanup cron** (`reymen/cereyan/temizlik_cron.sh`, 04:00 daily).
Silinenler: tarihi gecmis, guven<0.2 + hata>5, 6 aydir kullanilmayan, 7 gunluk mesajlar.

Pitfall: Alan 4 (Hız) pratik tuzaklar:
- **session.db bulunamazsa**: `HERMES_HOME` altında `.db` dosyası yoksa, Hermes internal/memory-mapped storage kullanıyordur. `find` ile 5 saniyeden fazla tarama yapma — hemen "Hermes internal, kontrol yok" olarak raporla.
- **Pycache temizliği timeout:** 3845+ `__pycache__` dizini olduğunda `find -exec rm -rf {} +` zaman aşımına uğrar. Kullan: `find ... -print0 | xargs -0 rm -rf`
- **Pycache dışlama:** `.ReYMeN/skills/` ve `.ReYMeN/scripts/` altındaki pycache'leri temizleme — bunlar skill asset'leri, yeniden oluşturulması gerekmez. `-not -path "*/.ReYMeN/*"` ekle.
- **Pycache boyut ölçümü:** Temizlemeden önce freed space'i raporla — `find ... -exec du -sk {} + | awk '{sum+=$1} END {printf "%.1f MB (%d dirs)", sum/1024, NR}'` ile toplam boyutu hesapla. 755.7MB / 3501 dirs gibi bir değer normal.
- **`execute_code` bağlantı hatası:** Hız alanı `execute_code` ile big file tespiti yapmayı önerir ama `execute_code`'un internal `terminal()`'ı bazen bağlantı zaman aşımına uğrayabilir (`TimeoutError: WinError 10060`). **Fix:** Python script'ini `.ReYMeN/scripts/big_files_check.py` gibi bir dosyaya `write_file` ile yaz, sonra `terminal("python3 path/to/script.py")` ile çağır. `execute_code`'un terminal proxy'si değil, doğrudan terminal tool kullanılmış olur.
- **Big file taramasında vendor dizin dışlama:** `os.walk('.')` ile tarama yaparken `venv/`, `bot_venv/`, `node_modules/`, `.git/`, `ReYMeN_mirror/`, `hermes-memory-backup/`, `desktop/`, `dist/`, `ReYMeN-full-backup/`, `optional-skills/` gibi vendor dizinlerini MUTLAKA dışla. Aksi halde 7000+ dosya çıkar (çoğu vendor lib). Doğru yöntem: `parts = root.replace(os.sep, '/').split('/')` ile path parçalara ayır, `any(s in parts for s in skip_dirs)` ile filtrele. Gerçek proje dosyası sayısı genelde 400-500 arası olur.
- **Big file referans script:** `write_file` ile `.ReYMeN/scripts/big_files_check.py`'ye aşağıdaki şablonu yaz:
  ```python
  import os
  skip_dirs = ['venv', 'bot_venv', 'node_modules', '.git', '__pycache__',
               '.ReYMeN', 'ReYMeN_mirror', 'hermes-memory-backup',
               'desktop', 'dist', 'ReYMeN-full-backup', 'optional-skills']
  big_files = []
  for root, dirs, files in os.walk('.'):
      parts = root.replace(os.sep, '/').split('/')
      if any(s in parts for s in skip_dirs): continue
      for f in files:
          if f.endswith('.py'):
              path = os.path.join(root, f)
              with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                  lines = len(fh.readlines())
              if lines > 500:
                  big_files.append((lines, path.replace(os.sep, '/').replace('./', '')))
  big_files.sort(reverse=True)
  for lines, path in big_files:
      print(f'{lines:5d} lines  {path}')
  ```
- **INDEX.md güncelleme:** Hız alanı çalıştıktan sonra INDEX.md'de "Hız" satırı yoksa ekle (Hız skoru = pycache cleaned + big files count + freed MB). decisions.md'ye freed MB mutlaka kaydet.
- **INDEX.md tablo satırı ekleme (safe pattern):** Proje durumu tablosuna yeni satır eklerken `patch` ile iki satırı tek satırda birleştirmeye çalışma — fragile. Bunun yerine:
  1. `read_file` ile INDEX.md'nin tablo bölümünü oku, hangi satırın altına ekleneceğini belirle
  2. `patch(old_string="| **Hafıza** | 100% | ...\n| **Platform**", new_string="| **Hafıza** | 100% | ...\n| **Hız** | 100% | ✅ Pydata MB freed (N dirs), M big files\n| **Platform**")`
  Yani hedef satır ile bir alt satır arasına yenisini **newline + yeni satır** olarak ekle. Tek satırda birleştirme yapma.

- **INDEX.md satır birleşmesi onarımı (table row merge):** Önceki bir `patch` işlemi iki tablo satırını yanlışlıkla tek satırda birleştirmiş olabilir (ör: `| **Hız** | 100% | ... | **Platform** | -2 | ... |`). Tespit: INDEX.md tablosunda `|` sayısını satır başına kontrol et (her satırda eşit sayıda olmalı). Onarım:
  1. `read_file` ile INDEX.md'yi oku ve birleşik satırı bul
  2. `patch(old_string="...| **Hız** | 100% | ...| **Platform**", new_string="| **Hız** | 100% | ...\n| **Platform**")` ile iki satıra ayır
  3. Tablonun markdown formatını doğrula: tüm satırlar aynı sütun sayısına sahip olmalı

### Mod B — Öncelikli Görev (Acil durum)
Bir kullanıcı "öncelikli görev" veya "acil" dediğinde:
1. Normal rotasyonu durdurma — görevi ekle, sıradaki saatten itibaren işle
2. Görevi kategorilere böl (ör: 70 test hatası → 7 kategori)
3. Her saat bir kategori çöz
4. Tüm kategoriler bitince normal rotasyona dön

Görev cron prompt'una eklenir (`cronjob action='update' prompt=...`).
Karar #4 olarak `decisions.md`'ye kaydedilir.

### Mod B → Mod A Geçiş Protokolü
Son kategori çözüldükten SONRA rotasyona dönmeden önce şu state doğrulamalarını yap:

**Adımlar:**
1. **decisions.md state doğrula** — `read_file` ile decisions.md'yi oku. Session çıktısında "kaydedildi" yazmasına güvenme, dosyayı oku ve tüm kararların gerçekten yazıldığını teyit et.
2. **Import doğrulama** — Her kategori için terminal'de `python3 -c "from MODULE import SYMBOL"` çalıştır. Tüm kategorileri batch ile test et.
3. **Kalan kategori kontrolü** — Eğer bir kategori zaten önceki iterasyonlarda çözülmüş olabilir. `search_files` ile hala import eden .py dosyaları olup olmadığını kontrol et (sadece source, `__pycache__/` değil).
4. **Alan sırasını belirle** — `session_search` ile son kaydedilen kararı bul, hangi alanın sırada olduğunu çıkar. Eğer hiç normal rotasyon işlenmemişse Alan 1'den (Hafıza yönetimi) başla.
5. **Geçiş kararı** — decisions.md'ye Karar #N olarak ekle: "Öncelikli görev tamamlandı (X/Y kategori). Normal rotasyona geçildi. Sıradaki alan: {alan_adı}."
6. **INDEX.md güncelle** — Proje durumu (test skoru, platform skoru) değiştiyse INDEX.md'yi güncelle.

**Pitfall:** Mod B'de iterasyonlar birbirinden bağımsız cron çalıştırmalarıdır. Bir önceki iterasyonun kategorisini çözdüğünü varsayma — state doğrulaması her çalıştırmada yeniden yapılmalıdır.

## Otonom Çalışma (No-Approval Mode — ReYMeN/Q! Kullanıcısı)

Bu kullanıcı için tüm cron işlemleri **onaysız** yapılır. Bekleme kuralları:

| Durum | Aksiyon |
|:------|:--------|
| Kullanıcıya soru soruldu | 2 dk bekle |
| 2 dk sonra cevap yok | En mantıklı seçenekle devam et, tekrar sorma |
| Belirsiz karar | Hafızada ara → benzer durum → en düşük riskli seçenek |
| Geri döndürülemez işlem | Kullanıcı onayı bekle (silme, deploy, ödeme) |
| 3 ardışık hata | Circuit breaker → KULLANICIYA BILDIR, dur |

### Mod C — Sonlu Kampanya (N iterasyon)
`repeat=N` ile cron oluştur:
- 7 gün × 15dk aralık = 672 iterasyon
- Son iterasyonda otomatik durur
- Kullanıcıya final raporu gönderilir (7 günlük özet)
- Backup cron'ları (no_agent) ayrı çalışır, LLM harcamaz

Python referans implementasyonu: `scripts/self_improvement_loop.py`
Bu script tam döngüyü (Gözlem → Keşif → Karşılaştır → Dene → Kaydet) modüler olarak gösterir.

## Adımlar (her iterasyon)

### 0. ÖNCE HAFIZAYA BAK (OnceHafiza)
Her göreve başlamadan önce mutlaka hafızaya bak. LLM çağrısı yapmadan önce SQLite'da ara:

```
Görev al
  ↓
OnceHafiza.hafizada_ara(hedef)
  ├── BULUNDU → direkt döndür (0 LLM çağrısı)
  │              ├── gecerlilik_tarihi kontrolü → eskiyse uyarı ekle
  │              └── son_kullanim + guven_skoru otomatik güncellenir
  └── BULUNAMADI → normal döngüye geç (Adım 1)
```

**Nerede?** `reymen/sistem/once_hafiza.py` (sınıf tabanlı motor), `reymen/cereyan/once_hafiza.py` (doğrudan fonksiyon tabanlı)
**Veritabanı:** `reymen/cereyan/.ReYMeN/ogrenmeler.db` (TÜM ajanlar ortak — Kali, Windows, CAD, Hermes)

#### ogrenmeler Tablosu (güncel şema)
| Kolon | Tip | Varsayılan | Açıklama |
|-------|-----|-----------|----------|
| `hedef` | TEXT UNIQUE | — | Görev adı (arama anahtarı) |
| `cozum` | TEXT | — | Çözüm içeriği |
| `kaynak` | TEXT | `''` | "kesif", "skills", "ogrenme" |
| `basari_sayisi` | INTEGER | 1 | Kaç kez başarılı |
| `hata_sayisi` | INTEGER | 0 | Kaç kez hata |
| `son_basari` | TEXT | — | Son başarı zamanı |
| `son_hata` | TEXT | — | Son hata zamanı |
| `guven_skoru` | FLOAT | 1.0 | basari/(basari+hata) |
| `son_kullanim` | TEXT | — | Son okuma zamanı (cache freshness) |
| `kategori` | TEXT | `''` | "kali", "dron", "cad" — farklı ajan kendi kategorisine baksın |
| `gecerlilik_tarihi` | TEXT | — | Bugün + 6 ay — eski bilgi tespiti |
| `olusturulma` | TEXT | now() | Kayıt oluşturma zamanı |

#### API
```python
from reymen.sistem.once_hafiza import OnceHafiza, isle, kaydet, hafizada_ara

oh = OnceHafiza()

# Ara
kayit = oh.hafizada_ara("kali_metasploit_kurulum")
# → {"hedef": ..., "cozum": ..., "kaynak": ..., "kategori": ..., "uyari": "..."}

# Kaydet (kategori desteği)
oh.kaydet("gorev_adi", "cozum_metni", kategori="kali")

# Ana döngü (önce hafıza, sonra dene)
sonuc = oh.isle("hedef", calistirici=benim_fonksiyon, kategori="kali")
# → {"durum": "hafiza"|"basarili"|"basarisiz", "sonuc": ..., "kaynak": ...}

# Hata kaydet (otomatik ogrenmeler.hata_sayisi++ + guven_skoru güncelle)
oh.hata_kaydet("hedef", "Hata mesajı", traceback.format_exc())
```

#### Migration (eski DB'ler)
`_db_kur()` hem CREATE TABLE IF NOT EXISTS (yeni şema) hem de ALTER TABLE migration içerir.
Kolon bazlı index'ler migration sonrası kurulur — eski DB'lerde kolon bulunamazsa fail vermez.

#### Guven Skoru Davranışı
- **Başarı:** `guven_skoru = basari / (basari + hata)` → `kaydet()` içinde otomatik hesaplanır
- **Hata:** `hata_kaydet()` hem `hatalar` tablosuna kayıt ekler hem de `ogrenmeler`'de `hata_sayisi++` ve `guven_skoru` günceller
- **Okuma:** `hafizada_ara()` her buluşta `son_kullanim` + `basari_sayisi++` + `guven_skoru` günceller

#### Geçerlilik Kontrolü
- Kayıt oluşturulurken `gecerlilik_tarihi = bugün + 6 ay`
- `hafizada_ara()` bulduğunda kontrol eder: süre geçmişse sonuca `"uyari"` alanı ekler
- Güven skoru düşük **veya** geçerliliği geçmiş kayıtlar için LLM çağrısı yapılabilir (opsiyonel)

**Pitfall:** `OnceHafiza` cache'ten dönen sonuç LLM çağrısı yapmadığı için sıfır token harcar. Ancak kategori filtresi yok — tüm ajanlar aynı DB'yi paylaşır. Farklı ajanlar (Kali, Dron, CAD) kendi kategorilerine bakmalı; kategori filtreli sorgu şu an LIKE aramasında yok, elle eklenmeli.

**Pitfall:** Migrate edilmiş eski kayıtlarda `kategori` ve `gecerlilik_tarihi` NULL olabilir. `hafizada_ara()` `len(row) > N` kontrolleri ile None/eksik kolonları güvenle atlar. Yeni kayıtlarda tüm kolonlar doldurulur.

Detaylı şema, SQL pattern'leri ve migration kodu: `references/once-hafiza-schema.md`

**Pitfall: Centralized knowledge store — Hermes `memory` tool'u KULLANMA.**
ReYMeN'de TÜM ajanlar (Kali, Windows, CAD, Hermes) ortak bir dosyaya yazar:
`.ReYMeN/kazanimlar.md` (proje kökü).

Hermes `memory` tool'u (`AppData/.../kiral38/memories/MEMORY.md`) sadece Hermes internal'e yazar —
diğer ajanlar erişemez. Bu yüzden:
- ❌ `memory()` tool'unu kullanma
- ✅ Her skill/memory/karar/OnceHafiza kaydı → `echo >> .ReYMeN/kazanimlar.md`
Format: `## {TARİH} {SAAT} — {KAYNAK_AJAN} — {ALAN}` + kazanım metni

### 1. GÖZLEM
- `session_search` ile son saatteki aktiviteyi kontrol et
- Zayıf alanları belirle (en çok tekrar eden hata, en yavaş işlem)
- Not: `.ReYMeN/kazanimlar.md`'yi oku — Hermes `memory` tool'unu kullanma

### 2. KEŞİF
- `web_search` ile zayıf alan için en iyi metodları araştır
- Veya: öncelikli görev varsa sıradaki kategoriyi çöz

### 3. KARŞILAŞTIR
- Mevcut metot ile yeni metodu karşılaştır
- Kriter: hız, doğruluk, uygulanabilirlik, güvenlik
- Karar: UYGULA / REDDET / DAHA_FAZLA_ARAŞTIR

### 4. DENE / UYGULA
- Sandbox ortamında test et (terminal)
- `decisions.md`'ye karar olarak kaydet
- Güvenlik kurallarına uy

### 5. KAYDET
- Çalışıyorsa `skill_manage` ile skill olarak kaydet
- Kaynak URL, performans skoru, tarih ekle

### 6. RAPORLA
- Kısa özet (Cave Modu)
- Son iterasyon ise: tüm kampanya özeti

## Hata Kategorilendirme Pattern'i (test/import)
Büyük bir hata kümesini çözerken:
1. Tüm test dosyalarını tara: `python3 -c "__import__(mod_name)"` döngüsü
2. Hataları eksik sembole göre grupla (7 kategori çıktı)
3. Her saat bir kategori çöz
4. Çözüm: upstream-uyumlu dataclass ekle / upstream'ten port et / mock / testi güncelle / testi sil
5. Her kategoriyi decisions.md'ye kaydet
6. Tüm kategoriler çözüldükten SONRA son bir full scan yap: `compile()` + `__import__()` ile tüm core test dosyalarını tara. Kategorizasyon dışında kalan semboller olabilir.
7. referans: `references/test-import-debugging.md`

**Pitfall: Post-Kategorizasyon Artık Hatalar**
Tüm kategoriler çözülmüş olsa bile, orijinal kategorizasyonda olmayan yeni hatalar kalabilir.
Örnek: 6 kategori fixlendikten sonra `tests.run_interrupt_test`'te `_run_single_child` hatası bulundu
— bu sembol orijinal 7 kategoride yoktu, çünkü sadece 2 referans test dosyasında import ediliyordu.
**Fix yöntemi:** Tüm kategoriler bittikten sonra her zaman full `compile()` + `__import__()` scan'i yap.

## Önemli: Ön-Kategorilendirme Tuzakları
Decisions.md veya skill içinde önceden yazılı kategorilere KÖRÜNE güvenme.
Bu kategoriler farklı bir codebase durumundan çıkarılmış olabilir.
Her iterasyonun başında GÖZLEM adımında **kategorileri doğrula**:
- `search_files` ile eksik sembolün gerçekten .py dosyalarında import edildiğini teyit et
- Sadece `__pycache__/` sonuçlarına takılma (bunlar derlenmiş bytecode, source değil)
- Eğer hiç source dosyası eşleşmiyorsa, o kategori zaten çözülmüş olabilir → atla

## Önemli: Değer Bazlı Önceliklendirme
Tüm fix'ler eşit değerde DEĞİL. Kullanıcı "testler faydalı olacak mı" diye
sorduğunda veya şüphe duyduğunda — veya sormasa bile — şu sıralamayı kullan:
1. **Proje testleri** (`tests/` içi, ReYMeN_reference değil) → 🟢 Fixle + çalıştır
2. **Upstream referans testleri** (`tests/ReYMeN_reference/`) → 🟡 Import fix, test çalışmazsa sil
3. **Kullanılmayan modüller** (ACP, Yuanbao) → 🔴 Sil, fix zaman kaybı

### 🔴🔀🟢 Overlap: Kullanılmayan modül + Proje testi
Bir modül kullanılmayan (🔴) olarak sınıflandırılmış olsa bile, proje testleri (🟢)
o modülü import edip test ediyorsa ikisi birleştirilmelidir:

| Durum | Eylem |
|-------|-------|
| Modül kullanılmıyor + proje testi **YOK** | 🔴 Sil, zaman kaybı |
| Modül kullanılmıyor + proje testi **VAR** | 🔀 Shim/stub ekle, testleri koru |
| Modül kullanılmıyor + sadece **referans testleri** VAR | 🟡 En kısa shim + testi çalıştır, çalışmazsa sil |

**Örnek:** Yuanbao platformu (🔴) ReYMeN'de kullanılmıyor ama 75 proje testi
yuanbao modüllerini import ediyor. Doğru yaklaşım: yuanbao.py'ye stub sınıflar
ve sabitler ekle, yuanbao_media.py'ye eksik fonksiyonları ekle — testler
korunur (75/75 ✅).

Fix stratejisi ve karar ağacı için → `references/test-import-debugging.md`

## Önemli: Karar Tutarlılığı Kontrolü
Bir önceki iterasyonun çıktısında "Karar #N decisions.md'ye kaydedildi" yazması,
o kararın GERÇEKTEN decisions.md'de olduğu anlamına GELMEZ. Yeni bir karar
eklemeden ÖNCE:

1. `read_file` ile decisions.md'yi oku — son kararın gerçekten yazıldığını teyit et
2. Karar sıra numarası çakışması kontrol et (iki farklı #4 olabilir → yeniden numaralandır)
3. Eksik karar varsa tamamla, sonra kendi kararını ekle
4. Karar ekledikten sonra INDEX.md'yi de güncelle (test skoru, platform durumu değiştiyse)

**Neden?** Cron iterasyonları birbirinden bağımsız çalışır. Terminal çıktısı
dosyaya yazıldı anlamına gelmez. Eğer önceki iterasyon bir sub-agent
üzerinden decisions.md'ye yazdıysa bile, sub-agent'ın summary'sini değil
dosyayı oku.

## Güvenlik Kuralları
1. Kendi ana kodunu değiştirme
2. İnsan onayı olmadan deploy etme
3. Sandbox dışında test etme
4. Kaynağı doğrulanmamış kodu çalıştırma

## Rapor Formatı (ZORUNLU — ReYMeN/Q! kullanıcısı)
Her iterasyon çıktısı şu kompakt formatta:
```
🔄 Self-Improvement — İt. {N}/{TOPLAM} ({ALAN_ADI})

Run #{SIRA}: {SAAT} ✅/❌ ({açıklama})

**Alan:** {alan_adı}
**İşlem:** {ne yapıldı — tek satır}
**Sonuç:** {✅/❌/⏳} — {kısa açıklama}
📌 Kazanım: {öğrenilen şey — varsa}
```
ASLA: 5 paragraflı açıklama. ASLA: süslü giriş/çıkış cümleleri. Direkt tablo + kazanım.

## Çıktı
- `decisions.md`'ye yeni karar
- Başarılıysa yeni skill
- **kazanimlar.md'ye append et**: her yeni skill oluşturma/güncelleme ve her memory kaydetme `echo "...Tarih — Skill/Memory: ..." >> kazanimlar.md` ile eklenir. Detaylı format: `references/kazanimlar-logging.md`
- Kullanıcıya yukarıdaki kompakt formatta rapor (Cave Modu)

## Konkre Kod: ClosedLearningLoop.run_forever()
Bu skill'in soyut adımları, `reymen/cereyan/closed_learning_loop.py`'de `ClosedLearningLoop` sınıfına
konkre metodlar olarak eklenmiştir:

- `observe_self()` — FTS5 becerilerini tara, zayıf alanları bul
- `discover_better_methods(focus)` — Web'de araştır (DuckDuckGo HTML scrape)
- `compare_and_decide(current, new)` — Skor tabanlı karşılaştır
- `test_in_sandbox(method)` — İzole syntax testi (compile-only)
- `save_as_skill(method, score)` — Beceri kristallestir (`beceri_kristallestir()`)
- `run_forever(cycle_hours=24, test_mode=False, max_test_iter=672)` — Ana döngü

**Parametreler:**
| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|-----------|----------|
| `cycle_hours` | int | 24 | Gerçek modda bekleme süresi |
| `test_mode` | bool | False | True → hiç beklemez, iterasyonları hızlıca tamamlar |
| `max_test_iter` | int | 672 | Test modunda max iterasyon (7 gün × 15dk = 672) |

**Test modu kullanımı:**
```python
# 672 iterasyonu (7 gün) hemen tamamla:
loop.run_forever(cycle_hours=24, test_mode=True, max_test_iter=672)
# veya sadece 5 iterasyon test et:
loop.run_forever(cycle_hours=24, test_mode=True, max_test_iter=5)
```

Detaylar: `references/closed-learning-loop-run-forever.md`
Tur tamamlama pattern'i: `references/rotation-cycle-complete.md`
