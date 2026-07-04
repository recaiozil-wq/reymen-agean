# GÖREV: Kalan 5 Düşük Öncelikli Modülü Kodla

## NE
ReYMeN'e 5 yeni modül ekle. Kodları yaz, test et.

## MODÜLLER

### 1. cost_tracker.py — API harcama takibi
**Yer:** `reymen/arac/cost_tracker.py`
**Ne yap:**
- `record_usage(provider, model, input_tokens, output_tokens)` — maliyet hesapla + kaydet
- `summary()` — toplam/günlük/aylık harcama özeti
- `reset()` — log sıfırla
- `dump_log()` — tüm kayıtları döndür
- Fiyatlar: DeepSeek $0.27/1M input, $1.10/1M output; diğerleri için config
- Depolama: `~/.ReYMeN/costs.db` (SQLite)
- Motor kaydı: `motor_kaydet("maliyet", summary, "Harcama özeti")`

### 2. platform_adapter.py — Çapraz platform desteği
**Yer:** `reymen/sistem/platform_adapter.py`
**Ne yap:**
- `detect()` → "windows" / "wsl" / "linux"
- `translate_path(windows_yolu)` → WSL/Linux yoluna çevir
- `run(komut)` → platforma uygun shell'de çalıştır
- Kali: `wsl -d kali-linux` üzerinden SSH (host: 192.168.56.103)
- Motor kaydı: `motor_kaydet("platform", detect, "Platform bilgisi")`

### 3. self_improve.py — Kalite metrikleri
**Yer:** `reymen/cereyan/self_improve.py`
**Ne yap:**
- `QualityMetric` sınıfı: başarı, hata sayısı, yeniden deneme, süre
- `evaluate()` — projedeki .py dosyalarını tara, metrikleri topla
- `suggest_fix()` — düşük kaliteli alanlar için LLM'den öneri al
- Depolama: `.ReYMeN/self_improve_log.json`
- Motor kaydı: `motor_kaydet("self_improve", evaluate, "Kalite metrikleri")`

### 4. video_tools.py — Video işleme
**Yer:** `reymen/arac/video_tools.py`
**Ne yap:**
- `download(url, output_yol)` — yt-dlp ile video indir
- `convert(kaynak, hedef_format)` — ffmpeg ile dönüştür
- `probe(video_yolu)` — video bilgisi al (süre, çözünürlük, codec)
- yt-dlp/ffmpeg yoksa hata döndür, çökme
- Motor kaydı: `motor_kaydet("video_indir", download, "Video indir")`

### 5. a2a.py — Agent mesajlaşma prototipi
**Yer:** `reymen/core/a2a.py`
**Ne yap:**
- `Agent(ad)` sınıfı — bir agent temsilcisi
- `Message(kaynak, hedef, icerik)` — mesaj nesnesi
- `send(mesaj)` — mesajı kuyruğa ekle
- `receive()` — gelen mesajları oku
- `Broker` — bellek içi kuyruk yöneticisi
- Motor kaydı: `motor_kaydet("a2a_gonder", send, "Agent mesaj gönder")`

## DOĞRULAMA
Her modül için:
```bash
python -c "compile(open('DOSYA.py').read(), 'DOSYA.py', 'exec'); print('OK')"
```

## YASAKLAR
- Mevcut dosyaları değiştirme
- Test dosyalarını düzenleme
- __pycache__/.git/node_modules
