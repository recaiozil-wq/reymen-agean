# ReYMeN Agent — 5 Kategoride Hata Analizi Raporu

> **Tarih:** 2026-06-21  
> **Veritabanı:** 54 kayıt | `reymen/cereyan/.ReYMeN/ogrenmeler.db`  
> **Analiz Edilen Dosyalar:** `once_hafiza.py` (604 satır), `conversation_loop.py` (1619 satır), `gorev_once_kontrol.py` (940 satır), `_web_tetikleyici.py` (183 satır), `AGENTS.md`

---

## VERİTABANI ÖZET İSTATİSTİKLERİ

| Metrik | Değer | Anlamı |
|--------|-------|--------|
| Toplam kayıt | 54 | Hafıza boyutu |
| Ortalama güven | **0.96** | Çok yüksek — sorunlu |
| guven=1.0 olan kayıt | **49 (%90.7)** | Neredeyse tamamı maksimum güvende |
| basari=1 / hata=0 / guven=1.0 | **42 (%77.8)** | İlk denemede direkt maksimum güven |
| Hiç hata görmemiş kayıt | 49 | 54 kaydın 49'u sıfır hatalı |
| Geçerliliği geçmiş kayıt | **0** | Henüz hiçbiri süreyi doldurmamış |
| Hata > başarı olan kayıt | 2 | (`karma_test`, `test_belirsiz`) |
| `kaynak_url` kolonu | **YOK** | Kaynak URL gömülü değil, ayrı kolon yok |
| `web_arama_sebebi` kolonu | **VAR** | Sonradan ALTER TABLE ile eklenmiş |

### Güven Dağılımı

| Güven Aralığı | Kayıt Sayısı | Ort. Başarı | Ort. Hata |
|:-------------:|:------------:|:-----------:|:---------:|
| 1.0 | 49 (%90.7) | 1.16 | 0.0 |
| 0.75 | 2 | 3.0 | 1.0 |
| 0.67 | 1 | 2.0 | 1.0 |
| 0.33 | 2 | 1.0 | 2.0 |

---

## KATEGORİ 1 — TETİKLEYİCİ HATALARI

### Hata 1A: T4 Geçerlilik — Sadece Tarihe Bakıyor, İçerik Eskiyebilir

**(1) Tanım:** T4 tetikleyicisi (`tetikleyici_4_gecerlilik_asmis`) sadece `gecerlilik_tarihi < bugün` kontrolü yapıyor. 
`ara()` fonksiyonu da benzer şekilde `gecerlilik_tarihi >= date('now')` filtreliyor.

```python
# _web_tetikleyici.py satır 58
row = con.execute(
    "SELECT gecerlilik_tarihi, guven_skoru FROM ogrenmeler WHERE ... AND gecerlilik_tarihi < ? LIMIT 1",
    (f"%{hedef[:30]}%", bugun)
).fetchone()
```

**(2) Ne Zaman Oluşur:** 
- Bir tool'un versiyonu değiştiğinde (örn. nmap 7.x → 8.x, yeni parametreler geldi)
- Web API'leri güncellendiğinde (endpoint değişikliği, yeni auth)
- 180 gün dolmamış olsa bile içerik kullanılamaz hale geldiğinde
- Bir kayıt 179 gün önce oluşturuldu — tarihsel olarak "geçerli" ama içerik çöp

**(3) Sonucu:**
- Eski/çalışmayan bilgi hafızadan sorgulanıp **direkt kullanıcıya döndürülür** (`isle()` fonksiyonu satır 346-359)
- Tool versiyonu değişmişse hata alır, bu da yeni bir hata kaydı oluşturur
- Ama T4 ateslenmez çünkü **tarihsel geçerlilik hala yerinde**
- `guven_guncelle()` ile hata eklenir, güven düşer — ama bu pasif bir düzeltme, kullanıcı önce hatayı görecek

**(4) Çözüm Önerisi:**
- **İçerik sürüm kontrolü:** Her kayda `tool_versiyonu` veya `son_dogrulama` metin alanı ekle
- **Versiyon tespit tetikleyicisi (T6):** `calistir()` fonksiyonundan önce tool versiyonunu sorgula, hafızadakiyle karşılaştır
- **Akıllı geçerlilik:** 180 gün sabit yerine, güven × geçerlilik çarpımı; yüksek güvenli (≥0.9) kayıtlar daha uzun süre geçerli olsun
- **Arka plan doğrulama:** `isle()` her çağrıldığında, hafızadan döndürse bile arka planda bir doğrulama thread'i başlat

### Hata 1B: Puan Hesaplaması Hatalı Olabilir Mi?

**(1) Tanım:** `_web_tetikleyici.py`'de 5 tetikleyicinin öncelik sıralaması ve puan hesaplaması tutarsız.

```python
# _web_tetikleyici.py satır 80-95
tetikleyiciler = [
    ("T1: Hafiza bos",     tetikleyici_1_hafiza_bos(hedef)),      # puan = 1.0
    ("T3: Gorev basarisiz", tetikleyici_3_gorev_basarisiz(hata)), # puan = hata/10
    ("T2: Guven dusuk",    tetikleyici_2_guven_dusuk(hedef)),     # puan = guven_skoru (<0.5)
    ("T4: Gecerlilik asmis", tetikleyici_4_gecerlilik_asmis(hedef)), # puan = 0.3
    ("T5: Celiski",        tetikleyici_5_celiski(h_icerik, v_icerik)), # puan = 0.6
]
tetikleyiciler.sort(key=lambda t: -t[1][2])  # puana gore sirala
```

**(2) Ne Zaman Oluşur:**
- T5 (çelişki) puani 0.6, T2 (güven düşük) puani 0.3-0.5. Yani çelişki varsa, güven düşük tetikleyicisinden **önce** kontrol edilir
- T3 puanı `hata_sayisi / 10` — bu 2 hata için 0.2, 3 hata için 0.3. Çok düşük.
- T4 puanı sabit 0.3 — her zaman en düşük öncelik
- AGENTS.md'de belirtilen **öncelik sırası** (T1→T3→T2→T4→T5) ile `sort(key=puan)` farklı sonuç verebilir

**(3) Sonucu:**
- T5 (çelişki) 0.6 puanıyla T2'yi (güven düşük, 0.3-0.5) eziyor
- T3 (2 hata = 0.2 puan) T4 (0.3 puan)'ten düşük kalıyor
- Asıl öncelik sırası değil, puan büyüklüğü belirleyici oluyor
- Mantıksal öncelik (hafıza boşsa web'e git, başarısızsa web'e git) ile puan sıralaması uyuşmuyor

**(4) Çözüm Önerisi:**
- İki aşamalı sistem: **Önce tetikleyici tipine göre sırala** (mantıksal öncelik), **sonra aynı tiptekileri puana göre sırala**
- Veya sabit bir öncelik numarası kullan (T1=100, T3=80, T2=60, T4=40, T5=20)
- T3 puanını `min(0.8, hata/3 * 0.8)` olarak düzelt (2 hata=0.53, 3 hata=0.8)

---

## KATEGORİ 2 — PUANLAMA HATALARI

### Hata 2A: Puan Kriterleri Sabit — Göreve Göre Değişmiyor

**(1) Tanım:** `once_hafiza.py`'daki güven hesaplaması sadece **başarı/hata oranına** bakar:
```python
guven = round(yeni_basari / toplam, 4)  # basari / (basari + hata)
```
AGENTS.md'de tanımlanan 5 kriterli puanlama sistemi (hız %20, başarı %30, çıktı %20, güvenlik %15, kaynak %15) **kodda hiç uygulanmamış**. Sadece belge seviyesinde kalmış.

**(2) Ne Zaman Oluşur:**
- Her güven hesaplamasında — 54 kaydın 49'u guven=1.0
- Hız gerektiren bir görev (örn. "ping at ve sonucu hızlı döndür") ile doğruluk gerektiren görev (örn. "port taraması yap ve her portu doğrula") aynı formülle hesaplanır
- "1 başarı = guven 1.0" her görev türü için geçerlidir

**(3) Sonucu:**
- Yavaş ama doğru çalışan bir çözüm ile hızlı ama yanlış çalışan bir çözüm aynı güven skoruna sahip olabilir
- Göreve bağlı kriter ağırlıklandırması yok
- Örn. bir güvenlik aracı için "güvenlik" kriteri %50 olmalıyken "hız" %5 olmalı — bu fark gözetilmiyor
- Sürekli aynı görevi 3 kez başarıyla çalıştıran bir kayıt (guven=1.0) ile 1 kez deneyip başarılı olan kayıt (guven=1.0) **aynı güvende** — fark yok

**(4) Çözüm Önerisi:**
- **Kategori bazlı kriter ağırlıkları:** Her kategori için farklı ağırlık seti (örn. `kali/network` için hız=%10, başarı=%40, güvenlik=%30; `windows/terminal` için hız=%30, başarı=%25, çıktı=%25)
- **Performans metrikleri ekle:** Çalışma süresi, çıktı doğruluğu (LLM ile karşılaştırma), güvenlik skoru
- **Bayesian güven:** İlk başarıya otomatik 1.0 verme, `(basari + prior) / (toplam + prior*2)` formülü kullan (prior=0.5)

### Hata 2B: Dinamik Eşik Yok

**(1) Tanım:** `isle()` fonksiyonu `min_guven=0.5` sabit eşikle çalışır. 
```python
kayitlar = ara(hedef, kategori, min_guven=min_guven, gecerli_mi=gecerli_mi)
```

**(2) Ne Zaman Oluşur:** Her `isle()` çağrısında. Kritik görevler (sistem değişikliği, dosya silme) için 0.5 çok düşük, basit görevler (bilgi sorgulama) için 0.5 çok yüksek olabilir.

**(3) Sonucu:** 
- Kritik görevlerde düşük güvenli bilgi kullanılabilir
- Basit görevlerde hafıza kullanılamaz, gereksiz yere tekrar çalıştırılır

**(4) Çözüm Önerisi:** Görevin risk seviyesine göre dinamik eşik: kritik=0.9, normal=0.5, basit=0.3

---

## KATEGORİ 3 — HAFIZA HATALARI

### Hata 3A: Kaynak URL Gomulu — Ayri Kolon Yok

**(1) Tanım:** Tabloda `kaynak_url` veya `source_url` kolonu bulunmuyor. Sadece sonradan eklenen `web_arama_sebebi` metin alanı var.

```
PRAGMA table_info(ogrenmeler):
  id | hedef | kategori | icerik | guven_skoru | basari_sayisi | hata_sayisi |
  son_kullanim | gecerlilik_tarihi | olusturulma | guncelleme | web_arama_sebebi
                                                        ^^^^^^^^^^^^^^^^^^
  KAYNAK_URL: YOK!                                       Sadece sebep alanı
```

**(2) Ne Zaman Oluşur:**
- Web'den alınan bilgi kaydedilirken kaynak URL'si kaybolur
- `kaydet(hedef, kategori, icerik, basari=True)` — URL parametresi yok
- Kullanıcı "bunu nereden öğrendin?" diye sorduğunda cevap verilemez
- Çelişki durumunda (T5) hangi kaynağın doğru olduğu tespit edilemez

**(3) Sonucu:**
- Bilginin kaynağı takip edilemez
- Web scraping sonuçlarının orijinal URL'i kaybolur
- Güvenilirlik değerlendirmesi yapılamaz (resmi doküman mı, blog mu, forum mu?)
- Zamanla hangi bilginin nereden geldiği unutulur

**(4) Çözüm Önerisi:**
- `kaynak_url` ve `kaynak_turu` (resmi/blog/forum/video/LLM) kolonları ekle
- `kaydet()` fonksiyonuna `kaynak_url` parametresi ekle
- Web'den alınan kayıtlarda URL otomatik doldurulsun

### Hata 3B: guven=1.0 Ilk Basarida Cok Yuksek

**(1) Tanım:** `kaydet()` fonksiyonunda yeni kayıt oluştururken basari=True ise direkt `guven_skoru=1.0` atanır:
```python
# once_hafiza.py satır 153-154
(1.0 if basari else 0.0,  # guven_skoru
 1 if basari else 0,      # basari_sayisi
```

**(2) Ne Zaman Oluşur:**
- Her yeni kayıt oluşturulduğunda (42/54 kayıt bu durumda)
- Tek bir başarılı deneme = maksimum güven
- Test amaçlı veya şans eseri başarılı olan bir işlem bile kalıcı yüksek güven kazanır

**(3) Sonucu:**
- DB'deki 49 kayıt guven=1.0 (90.7%)
- Bunların 42'si sadece 1 kez denenmiş (basari=1, hata=0)
- Gerçekte güvenilir olmayan bilgiler "mükemmel" olarak işaretlenir
- `isle()` fonksiyonu bu kayıtları görünce direkt döndürür, alternatif aramaz
- `eski_kayitlari_temizle()` bu kayıtları **asla silmez** çünkü guven ≥ 0.8

**(4) Çözüm Önerisi:**
- **Bayesian güven başlangıcı:** `guven = (basari + 1) / (toplam + 2)` — prior=1 ekle
- Minimum 3 başarı gerektiren "güvenli" statüsü
- İlk kayıtta guven=0.7, 3 başarıdan sonra 1.0'a yükselsin
- `isle()` fonksiyonu guven=1.0 olan kayıtları 30 günde bir pasif doğrulamaya tabi tutsun

### Hata 3C: Cok Eski Ama Kullanilmayan Kayit Ne Zaman Silinecek?

**(1) Tanım:** `eski_kayitlari_temizle(gun_limiti=200)` fonksiyonu var ama sadece **geçerlilik tarihi geçmiş** VE **guven < 0.8** olan kayıtları siler.

```python
def eski_kayitlari_temizle(gun_limiti: int = 200) -> int:
    sil = con.execute(
        "DELETE FROM ogrenmeler "
        "WHERE gecerlilik_tarihi < date('now', ?) AND guven_skoru < 0.8",
        ("-{} days".format(gun_limiti),),
    ).rowcount
```

**(2) Ne Zaman Oluşur:**
- Şu anda DB'de **hiç gecerliliği geçmiş kayıt yok** (en erken 2026-12-18)
- Otomatik temizlik çağrılmıyor — cron/scheduler bağlantısı yok
- guven=1.0 olan eski kayıtlar asla temizlenmez (guven < 0.8 koşulu)
- Kullanılmayan kayıtlar DB'de birikir

**(3) Sonucu:**
- `eski_kayitlari_temizle()` hiçbir zaman otomatik çağrılmaz
- Şu an 54 kayıt olsa da zamanla gereksiz bilgi birikimi olur
- guven=1.0 olan kayıtlar kalıcı olur — temizleme fonksiyonu onları dokunulmaz sayar
- 6 ay sonra tüm kayıtların gecerliliği geçecek ama guven=1.0 olanlar kalacak

**(4) Çözüm Önerisi:**
- **Zaman ağırlıklı güven:** Eski kayıtların güvenini zamana göre azalt: `guven = guven * (1 - gecen_gun/365)`
- **Kullanım takibi:** `son_kullanim` alanı var ama temizlemede kullanılmıyor. 200 gündür kullanılmayan kayıtları arşivle
- **Otomatik cron:** conversation_loop başlangıcında veya belirli aralıklarla `eski_kayitlari_temizle()` çağır
- **Kullanılmayan silme:** "son_kullanim > 365 gün" VE "guven < 0.5" ise sil

---

## KATEGORİ 4 — AJAN İLETİŞİM HATALARI

### Hata 4A: Bir Ajan Cokerse Digeri Anliyor Mu?

**(1) Tanım:** `conversation_loop.py` içinde **cross-agent iletişim veya heartbeat mekanizması bulunmuyor.** AGENTS.md'de tanımlanan Kali/Windows koordinasyonu sadece belge seviyesinde; kodda uygulanmamış.

```
AGENTS.md'de yazılı:                          Kodda gerçek:
────────────────────────                      ────────────────
- JSON mesaj formatı                          ❌ Yok
- Kali/Windows orkestratör                    ❌ Yok
- Maks 3 retry                                ✅ Var (tek ajan)
- Circuit breaker (3 hata → dur)              ✅ Var (tek ajan)
- Biri hata yaparsa diğeri devralır           ❌ Yok
- Heartbeat / health check                    ❌ Yok
```

**(2) Ne Zaman Oluşur:**
- Bir ajan (örn. Kali) çöktüğünde, Windows bunu algılayamaz
- Ajanlar arası mesajlaşma için bir kanal (queue/socket/dosya) yok
- `cross_agent_ekle()` ve `cross_agent_tara()` sadece pasif dosya taraması yapar — gerçek zamanlı iletişim değil

**(3) Sonucu:**
- Bir ajan çökerse diğer ajan işlemeye devam eder, diğer ajanı beklemez
- Koordinasyon gerektiren görevlerde (örn. port engelleme: Kali tespit eder, Windows engeller) çöken ajan işi yarım bırakır
- `cross_agent_tara()` pasif bir fonksiyon — ajan çöktüğünde hiçbir şey yapmaz
- Bir ajan "diğer ajana sor" dediğinde soracak bir mekanizma yok

**(4) Çözüm Önerisi:**
- **Shared SQLite queue:** `reymen/cereyan/.ReYMeN/agent_queue.db` — ajanlar bu tabloya mesaj yazar/okur
- **Heartbeat tablosu:** Her ajan 30 saniyede bir `son_can_sinyali` günceller. 2 dakika güncellemezse "çökmüş" sayılır
- **Health check endpoint:** Her ajan kendi durumunu `/health` ile raporlasın
- **Failover:** Ajan çökerse, diğer ajan DB'deki "bekleyen görev" listesini devralır
- **Orkestratör thread:** conversation_loop'da periyodik olarak diğer ajanların durumunu kontrol et

### Hata 4B: Timeout Suresi Yeterli Mi?

**(1) Tanım:** `conversation_loop.py`'de API çağrıları için `_interruptible_api_call` var. Retry mekanizması da mevcut:
```python
CIRCUIT_BREAKER_MAX_HATA = 3
MAX_RETRY = 3
MAX_API_RETRY = 3
TAKILMA_ESIĞI = 3
```

**(2) Ne Zaman Oluşur:**
- Uzun süren tool çağrıları (örn. nmap taraması 10 dakika sürebilir)
- `_interruptible_api_call` thread bazlı kesme destekler ama tool çağrılarının timeout limiti kodda net tanımlanmamış
- `_api_call_with_retry`'de exponential backoff var (1s, 2s, 4s) — bu API çağrıları için geçerli, tool çağrıları için değil
- Tool çağrıları `_arac_calistir()` ile yapılır ve timeout kontrolü YOKTUR

**(3) Sonucu:**
- Uzun süren bir tool çağrısı conversation_loop'u bloke eder
- Tool çağrısı sonsuz döngüye girerse ajan kilitlenir
- Exponential backoff sadece API hataları için, tool hataları için retry yok
- Bir tool 3 kez başarısız olursa circuit breaker açar — ama bu tüm ajana yayılır, sadece o tool'a özel değil

**(4) Çözüm Önerisi:**
- **Tool bazlı timeout:** `_arac_calistir()`'a timeout parametresi ekle (varsayılan 30s, nmap gibi uzun araçlar için 300s)
- **Tool bazlı circuit breaker:** Her tool'un kendi hata sayacı olsun, tüm ajana yayılmasın
- **Asenkron tool çağrısı:** Uzun süren araçları arka planda çalıştır, sonucu callback ile al

### Hata 4C: Mesaj Kaybolursa Ne Oluyor?

**(1) Tanım:** `conversation_loop.py`'de mesajlar `_konusma_gecmisi: list` içinde tutulur. Mesaj kaybı veya sıra bozulması için bir tampon/kurtarma mekanizması yok.

**(2) Ne Zaman Oluşur:**
- Network kesintisi sırasında API'ye gönderilen mesaj kaybolursa retry sistemi devreye girer ama eski mesajlar kaybolabilir
- `_konusma_gecmisi` bellekte tutulur — ajan yeniden başlarsa kaybolur
- Session DB (FTS5) var ama sadece arama için, her mesajı kaydetmez
- Mesaj sıralama tamircisi (`mesaj_siralamasi_tamir_et`) var ama bu API'ye göndermeden önce düzeltme yapar, kaybı engellemez

**(3) Sonucu:**
- Ajan yeniden başlatılırsa tüm konuşma geçmişi kaybolur
- Uzun oturumlarda hafıza kaybı yaşanabilir
- Önemli kararların bağlamı kaybolabilir

**(4) Çözüm Önerisi:**
- **Message journal:** Her mesajı (gönderilen/alınan) ayrı bir SQLite tablosuna kaydet (`message_log`)
- **Session persistence:** conversation_loop her tur sonunda mesaj geçmişini session DB'ye otomatik kaydetsin
- **Acknowledgment sistemi:** Her önemli mesaj için ACK bekle, gelmezse tekrar gönder

---

## KATEGORİ 5 — ÖĞRENME DÖNGÜSÜ HATALARI

### Hata 5A: Yanlis Ogrenme — Hatali Bilgi guven=1.0 ile Kaydedilebilir

**(1) Tanım:** `kaydet()` fonksiyonu basari parametresini CALLER'dan alır. Caller hatalı bir bilgiyi "başarılı" olarak işaretlerse, bu bilgi guven=1.0 ile kaydedilir.

```python
# once_hafiza.py satır 365-372 -> isle() fonksiyonu
try:
    sonuc = calistir()
    kaydet(hedef, kategori, str(sonuc)[:5000] if sonuc else "", basari=True)  # Her zaman True!
except Exception as e:
    hata_mesaji = "[HATA] {}: {}".format(type(e).__name__, e)
    kaydet(hedef, kategori, hata_mesaji, basari=False)
```

**(2) Ne Zaman Oluşur:**
- `calistir()` fonksiyonu çalıştı ama **yanlış sonuç üretti** — exception fırlatmadı (örn. nmap yanlış port taraması yaptı ama çalıştı)
- Dış kaynaktan (web scraping, YouTube transcript) hatalı bilgi alındı
- Kullanıcı yanlış bilgi verdi
- LLM halüsinasyon yaptı ve agent bunu başarılı olarak kaydetti
- **Tüm bu durumlarda:** `basari=True` ile kaydedilir, guven=1.0 alır

**(3) Sonucu:**
- Hatalı bilgi kalıcı olarak "en güvenilir" bilgi haline gelir
- `isle()` fonksiyonu bu kaydı görünce LLM çağırmadan direkt döndürür (sıfır doğrulama)
- Aynı görev tekrar geldiğinde hatalı bilgi kullanılır, hata üstüne hata birikir
- Güven düşmez çünkü hata yok — sadece yanlış bilgi
- DB'de şu an 49 kaydın hepsi "hatasız" görünüyor — bazıları aslında hatalı olabilir

**(4) Çözüm Önerisi:**
- **Sonuç doğrulama katmanı:** `isle()`'da `calistir()` sonucunu LLM'ye doğrulat (opsiyonel)
- **0.9 güven tavanı:** İlk 5 başarıya kadar maksimum güven 0.9 olsun
- **Kullanıcı onayı:** Kritik bilgiler kaydedilmeden önce kullanıcıya sor
- **Cross-validation:** Aynı görev birden fazla kaynaktan doğrulansın

### Hata 5B: Zehirli Hafiza — Web'den Yanlis Kaynak Gelirse

**(1) Tanım:** Web'den veri çekme mekanizması (AGENTS.md'de T1-T5 tetikleyicileriyle) var ama **kaynak doğrulama** yok. Web'den gelen hatalı/yanlış/zararlı bilgi direkt hafızaya kaydedilir.

**(2) Ne Zaman Oluşur:**
- Web'den yanlış/eskimiş bir blog yazısı çekilir
- Kötü niyetli bir kaynak (veya güvenilmez forum) doğru olmayan bilgi verir
- YouTube transcript'i hatalı çeviri/transkripsiyon içerir
- Stack Overflow'daki hatalı cevap kaynak olarak kullanılır
- Tüm bu durumlarda: web scraping başarılı olduğu için `basari=True` → `guven=1.0`

**(3) Sonucu:**
- Yanlış bilgi hızla yayılır — diğer ajanlar da aynı DB'yi kullandığı için tüm sistemi zehirler
- Zehirli bilgiyi düzeltmek için manuel müdahale gerekir (guven=1.0 olduğu için otomatik silinmez)
- AGENTS.md'de "T5: Çelişki" tetikleyicisi var ama önceki bilgi de zehirli olabilir
- Kaynak güvenilirliği hiçbir zaman değerlendirilmez

**(4) Çözüm Önerisi:**
- **Kaynak güvenilirlik puanı:** resmi=0.9, SO=0.7, blog=0.5, forum/reddit=0.3, medya=0.4
- **Çoklu kaynak doğrulama:** Aynı bilgi en az 2 farklı kaynaktan teyit edilsin
- **Zehirli hafıza tespiti:** Anomali tespiti — beklenen değerden çok farklı sonuç gelirse uyar
- **Rollback mekanizması:** Zehirli kayıt tespit edilirse önceki güvenli sürüme dön
- **Karantina:** Web'den gelen yeni kayıtlar ilk 24 saat "karantina" statüsünde, düşük öncelikli

### Hata 5C: 1 Basari = guven 1.0 Cok Mu Yuksek? (Detayli Analiz)

**(1) Tanım:** Yukarıda 3B'de tanımlandı. Burada sayısal kanıtlarla detaylandırıyorum.

**İstatistiksel Kanıt:**

| Gösterge | Değer |
|----------|-------|
| guven=1.0 olan kayıt sayısı | 49 (%90.7) |
| Bunlardan basari=1, hata=0 | 42 (%77.8) |
| basari=2, hata=0 olanlar | 6 |
| basari=3, hata=0 olanlar | 1 |
| **Tek denemeyle "mükemmel" olanlar** | **42** |
| Deneyip hata gören kayıt oranı | 5/54 (%9.3) |

**(2) Ne Zaman Oluşur:** İlk kayıt oluşturulduğu anda. Her yeni öğrenmede.
```python
# once_hafiza.py satır 148-158: Yeni kayıt
con.execute("""INSERT INTO ogrenmeler ... guven_skoru = ? ... """,
    (1.0 if basari else 0.0, ...))  # basari=True ise direkt 1.0
```

**(3) Sonucu:**
- Güven skalası kullanılamaz hale gelir — 0.9 ile 1.0 arasında ayrım yok
- "Biraz güvenilir" ile "çok güvenilir" arasındaki fark kaybolur
- Yeni bilgilerin eski bilgileri geçmesi neredeyse imkansız (ikisi de 1.0)
- Güven skoru **anlamsız** hale gelir — 49/54 kayıt aynı değerde
- `isle()`'daki `min_guven=0.5` eşiği anlamsızlaşır (neredeyse her şey 1.0)
- `guven_seviyesi` hesaplaması (≥0.8 = yuksek) işlevsiz kalır

**(4) Çözüm Önerisi:**
- **Bayesian başlangıç:** `guven = (basari + 1) / (basari + hata + 2)`
  - 1 başarı, 0 hata → (1+1)/(1+0+2) = 2/3 = 0.667 (eski: 1.0)
  - 3 başarı, 0 hata → (3+1)/(3+0+2) = 4/5 = 0.8
  - 10 başarı, 0 hata → (10+1)/(10+0+2) = 11/12 = 0.917
  - 10 başarı, 1 hata → (10+1)/(11+2) = 11/13 = 0.846
- **Maksimum güven tavanı:** İlk 3 başarıda maks 0.8, sonra kademeli artış
- **Zaman azaltması:** Güven = güven × max(0.5, 1 - gecen_gun/365)
- **Mevcut kayıtları düzelt:** 42 kaydın guven'ini Bayesian formülle yeniden hesapla

---

## ÖZET TABLOSU

| # | Kategori | Hata | Şiddet | Öncelik |
|:-:|:---------|:-----|:------:|:-------:|
| 1A | Tetikleyici | T4 sadece tarih kontrolü, içerik eskiyebilir | **YÜKSEK** | 1 |
| 1B | Tetikleyici | Puan sıralaması mantıksal öncelikle uyuşmuyor | ORTA | 4 |
| 2A | Puanlama | 5 kriterli sistem kodda yok, sadece başarı/hata | **YÜKSEK** | 2 |
| 2B | Puanlama | Dinamik eşik yok, sabit min_guven=0.5 | DÜŞÜK | 7 |
| 3A | Hafıza | Kaynak URL kolonu yok, bilgi kaynağı takipsiz | **YÜKSEK** | 3 |
| 3B | Hafıza | İlk başarıda guven=1.0 (42/54 kayıt) | **KRİTİK** | 0 |
| 3C | Hafıza | Eski kayıt temizleme otomatik çağrılmıyor | ORTA | 5 |
| 4A | İletişim | Ajan çökme tespiti / heartbeat yok | **KRİTİK** | 0 |
| 4B | İletişim | Tool çağrıları için timeout yok | **YÜKSEK** | 2 |
| 4C | İletişim | Mesaj kaybı durumunda kurtarma yok | ORTA | 5 |
| 5A | Öğrenme | Hatalı bilgi guven=1.0 ile kaydedilebilir | **KRİTİK** | 0 |
| 5B | Öğrenme | Web'den zehirli kaynak doğrulamasız kaydedilir | **KRİTİK** | 0 |
| 5C | Öğrenme | 1 başarı=1.0 güven skalayı anlamsızlaştırıyor | **KRİTİK** | 0 |

### Acil Aksiyonlar (Öncelik Sırası)

1. **Güven hesaplamasını düzelt:** Bayesian formüle geç, varolan 42 kaydı yeniden hesapla
2. **Cross-agent heartbeat mekanizması ekle:** SQLite tablosu + periyodik kontrol
3. **Kaynak URL ve güvenilirlik kolonu ekle:** `kaynak_url`, `kaynak_turu`, `kaynak_guven`
4. **Web kaynak doğrulama:** Kaynak türüne göre güven ağırlığı, çoklu kaynak kontrolü
5. **Tool timeout:** `_arac_calistir()`'a timeout + tool bazlı circuit breaker
6. **Otomatik temizlik cron:** conversation_loop başında `eski_kayitlari_temizle()` çağır
7. **5 kriterli puanlama kodla:** AGENTS.md'deki sistemi Python'da uygula
8. **T4 akıllı geçerlilik:** İçerik sürümü + tool versiyonu + güven çarpımı ile dinamik geçerlilik
