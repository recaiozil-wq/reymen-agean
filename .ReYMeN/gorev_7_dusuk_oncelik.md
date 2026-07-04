# GÖREV: ReYMeN'E KALAN DÜŞÜK ÖNCELİKLİ ÖZELLİKLERİ EKLE (7 ADET)

## NE
ReYMeN'te olup ReYMeN'de eksik kalan düşük öncelikli 7 özellik.

---

## ADIM 1: Cost Tracking (Harcama Takibi)

**Yer:** `reymen/sistem/budget_config.py` (mevcut, geliştir)
**Ne yap:**
- `budget_config.py`'ye provider-based cost hesaplama ekle
- Her API çağrısında token sayısını + maliyeti logla
- `cost_log.json` dosyasına günlük/aylık harcama kaydet
- `cost_istatistik()` fonksiyonu: toplam harcama, günlük ortalama, en pahalı provider
- DeepSeek: $0.27/1M input (cache'li $0.07), $1.10/1M output
- Motor kaydı: `motor_kaydet("maliyet", cost_istatistik, "API harcama istatistikleri")`

**API:** `cost_log(provider, model, input_tokens, output_tokens)` → otomatik hesaplar + kaydeder

---

## ADIM 2: Çapraz Platform Desteği (WSL/Linux)

**Yer:** `reymen/sistem/platform_adapter.py` (yeni)
**Ne yap:**
- `PlatformAdapter` sınıfı, `platform_tespit()` → "windows" / "wsl" / "linux"
- `komut_calistir(komut)` → platforma göre uygun shell seç
  - Windows: cmd.exe /c
  - WSL: wsl --exec
  - Linux: direkt bash
- Windows'da çalışan kodun Linux/WSL'de de çalışması için path çevirici (C:\ → /mnt/c/)
- `kali_baglan(host, user)` → SSH ile Kali VM'e bağlan (192.168.56.103)
- Motor kaydı: `motor_kaydet("platform", platform_tespit, "Platform bilgisi")`

---

## ADIM 3: TUI (Terminal UI) İyileştirme

**Yer:** `reymen/sistem/cli_tui.py` (mevcut 3,983 satır, geliştir)
**Ne yap:**
- Rich library ile zenginleştir (yüklü değilse fallback koru)
- Status bar: provider, model, maliyet, token sayısı
- Spinner: işlem sırasında animasyon
- Progress bar: batch işlemlerde ilerleme
- Tablo: düzenli veri gösterimi
- Panel: hata/sonuç kutuları

**Hedef:** ReYMeN TUI'sine yakın görünüm. Ama Rich bağımlılığı zorunlu değil — varsa kullan, yoksa düz metin.

---

## ADIM 4: Self-Improvement Döngüsü

**Yer:** `reymen/cereyan/self_improve.py` (yeni)
**Ne yap:**
- `SelfImprovement` sınıfı
- `calistir()` metodu: her çalışmada:
  1. Projedeki .py dosyalarını tara
  2. Kalite metriklerini topla (satır sayısı, except:pass, shell=True)
  3. Önceki çalışmayla karşılaştır
  4. İyileşme varsa kaydet, yoksa LLM'e sor "ne geliştirilebilir?"
  5. `.ReYMeN/self_improve_log.json`'a kaydet
- Cron entegrasyonu: her 6 saatte çalışır
- Motor kaydı: `motor_kaydet("self_improve", SelfImprovement().calistir, "Kendini geliştirme döngüsü")`

---

## ADIM 5: Kanban Geliştirme

**Yer:** `reymen/arac/kanban_orchestrator.py` (mevcut, geliştir)
**Ne yap:**
- Kart ekleme/silme/güncelleme
- Kolonlar: backlog, in_progress, review, done
- Kullanıcı atama
- Öncelik (🔴🟠🟡🟢)
- Deadline takibi
- JSON depolama: `.ReYMeN/kanban.json`
- Motor kaydı: mevcut kaydı genişlet

---

## ADIM 6: Video Araçları

**Yer:** `reymen/arac/araclar_video.py` (mevcut, geliştir)
**Ne yap:**
- YouTube video indirme (yt-dlp wrapper)
- Video bilgisi alma (başlık, süre, çözünürlük)
- Video'dan ses çıkarma (ffmpeg)
- Video'dan kare yakalama (ffmpeg)
- Motor kaydı: mevcut kaydı genişlet
- Araçlar opsiyonel: yt-dlp/ffmpeg yoksa hata mesajı döndür, çökme

---

## ADIM 7: A2A Basit Prototip

**Yer:** `reymen/core/a2a_bridge.py` (yeni)
**Ne yap:**
- Çok basit bir agent-to-agent mesajlaşma
- `A2ABridge` sınıfı, JSON mesaj formatı
- `mesaj_gonder(hedef, icerik)` → hedef agent'ın HTTP endpoint'ine POST
- `mesaj_dinle(port)` → basit HTTP server, gelen mesajları kuyruğa al
- Motor kaydı: `motor_kaydet("a2a_gonder", ...)`
- **Kısıt:** Çok basit, sadece prototip seviyesinde. ReYMeN'teki gibi full A2A değil.

---

## DOĞRULAMA

Her adımda:
```bash
python -c "compile(open('DOSYA.py').read(), 'DOSYA.py', 'exec'); print('OK')"
```

Tüm adımlar bitince:
```bash
python -m pytest tests/ -x --timeout=10 -q 2>&1 | tail -5
```

## YASAKLAR
- __pycache__/.git/node_modules içinde değişiklik yok
- Test dosyalarını düzenleme
- Public API kırma
