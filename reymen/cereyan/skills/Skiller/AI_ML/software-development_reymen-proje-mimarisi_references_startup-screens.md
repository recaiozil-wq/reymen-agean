---
name: software-development_reymen-proje-mimarisi_references_startup-screens
description: ReYMeN Başlangıç Ekranları ve Giriş Noktaları
title: "Software Development Reymen Proje Mimarisi References Startup Screens"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ReYMeN Başlangıç Ekranları ve Giriş Noktaları |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ReYMeN Başlangıç Ekranları ve Giriş Noktaları

## Genel Bakış

ReYMeN projesinin 5 farklı giriş noktası vardır ve her biri farklı bir başlangıç
ekranı/banner gösterir. Hermes Agent'ın kendi giriş ekranından tamamen farklıdır.

**Proje tanımı (tüm dosyalarda tutarlı):** ReYMeN — Otonom Uygulama Otomasyonu Ajani

**Stil kuralı:** Banner'lar sade ve minimaldir — ASCII art/logografi İÇERMEZ.
Hermes'in kendi startup ASCII art'ı gibi süslemeler ReYMeN'de kullanılmaz.

## 1. ReYMeN.bat (Ana Başlatıcı)

**Dosya:** `ReYMeN.bat`

Parametresiz çalıştırıldığında menü gösterir:

```
    ╔══════════════════════════════════════════╗
    ║        ReYMeN  —  Otonom Ajan             ║
    ║   Uygulama Otomasyonu ve ReAct Dongusu    ║
    ╚══════════════════════════════════════════╝
```

Komutlar:
- `ReYMeN.bat start` — Tüm servisleri başlat (bağımlılık + .env kontrolü + start.py --all)
- `ReYMeN.bat agent` — Sadece ReAct ajanı (python main.py)
- `ReYMeN.bat dashboard` — Sadece Web UI (python start.py --dashboard-only)
- `ReYMeN.bat gateway` — Sadece Gateway (python start.py --agent-only)
- `ReYMeN.bat doctor` — Sistem sağlık kontrolü
- `ReYMeN.bat hermes ...` — Nous Hermes Agent CLI komutları
- `ReYMeN.bat --help` — Yardım menüsü

## 2. python start.py (Orkestratör Bannerı)

**Dosya:** `start.py` — `banner_goster(port)` fonksiyonu

Servisler başarıyla başlatıldığında gösterilen banner:

```
    ╔══════════════════════════════════════════════════════════╗
    ║                ReYMeN — Otonom Ajan                      ║
    ║         Uygulama Otomasyonu ve ReAct Dongusu             ║
    ╠══════════════════════════════════════════════════════════╣
    ║  🌐 Web UI      → http://127.0.0.1:{port}                ║
    ║  🤖 Telegram    → bot.py (polling)                       ║
    ║  🔄 Gateway     → multi-channel runner                   ║
    ╚══════════════════════════════════════════════════════════╝
```

Öncesinde durum tablosu gösterilir (servis adı, durum ✅/⚠️/❌, PID).

Özel parametreler:
- `--port 9090`: Varsayılan 8080 yerine özel port
- `--dashboard-only`: Sadece web UI (Telegram/Gateway başlamaz)
- `--agent-only`: Sadece gateway (Web UI başlamaz)

### banner_goster() Düzenleme Notları

`banner_goster()` fonksiyonu Python f-string + Unicode box-drawing karakterleri
kullanır. Düzenlerken şu tuzaklara dikkat et:

- **PATCH tool ile `"""` sorunu**: `old_string`/`new_string` içinde `"""` (triple quote)
  geçince escape-drift hatası alınır. Çözüm: `mcp_filesystem_write_file` ile tüm dosyayı
  yeniden yaz, veya `execute_code` ile satır bazlı düzenle.
- **Python 3.11+ f-string `\u` kısıtı**: `\u2500` gibi Unicode escape'leri f-string
  `{...}` ifadelerinin İÇİNDE kullanılamaz. Çözüm: önce bir değişkene ata,
  sonra `{degisken}` olarak kullan: `cizgi = "\u2500"` + `f"  {cizgi * 20}"`.
- **Kutu karakterleri (╔═╗║╚╝╠╣)**: Bunlar f-string literal içinde güvenle
  kullanılabilir (`"""...╔═══..."""`), sadece `{...}` ifadelerindeki `\u` kaçar.
- **Minimal stil**: Sade kutu tercih edilir, ASCII art/logografi eklenmez.

## 3. reyment.py (CLI Bannerı)

**Dosya:** `reyment.bat` → `reyment.py`

CLI modunda doğrudan argparse çıktısı, renkli ANSI, kategorize komut grupları.

Örnek başlıklar:
- `ReYMeN Otonom Ajan Baslatiliyor`
- `ReYMeN Otonom Ajan — Sunucu Baslatiliyor`

Kategoriler:
```
  [Calistirma]   run, serve
  [Yetenekler]   skill list, skill search, skill add, skill remove, skill detail
  [Yapilandirma] config show, config set, config init
  [Gateway]      gateway start, gateway status, gateway stop
  [Provider]     provider list, provider test, provider switch, provider ping
  [Model]        model list, model detail, model recommend, model benchmark
  [Kanban]       kanban list, kanban add, kanban move, kanban remove
  [MCP]          mcp list, mcp serve, mcp test, mcp picker
  [Profil]       profile list, profile create, profile switch, profile current
  [Zamanlama]    cron list, cron add, cron remove
  [Hafiza]       memory show, memory clear
  [Sistem]       doctor, version, help
```

## 4. python kendini_anlat.py (Öz Refleksiyon Aracı)

**Dosya:** `kendini_anlat.py`

Projenin kendi kod tabanını analiz ederek durum raporu çıkaran meta-bilişsel araç.
Statik analiz ile projenin durumunu, eksiklerini ve benzersiz özelliklerini raporlar.

```bash
python kendini_anlat.py            # Tam analiz (özet + çözüm tarzı + eksikler + öneriler)
python kendini_anlat.py --ozet     # Sadece genel istatistik
python kendini_anlat.py --cozum    # Sadece çözüm tarzı ve benzersiz özellikler
python kendini_anlat.py --eksik    # Sadece eksikler ve test sonuçları
```

**Analiz edilenler:**
- **İstatistik:** Python dosyası sayısı, kod satırı, sınıf/fonksiyon sayısı, skill sayısı
- **Çözüm tarzı:** Mimari pattern'ler (ReAct, MCP, ACP), tool/provider/gateway sayısı, benzersiz özellikler
- **Eksikler:** TODO/FIXME sayısı, NotImplementedError, pass blokları
- **Test sonucu:** `test_suite.py` çıktısının son satırları
- **Öneriler:** Kritik eksiklere göre otomatik oluşturulan geliştirme önerileri

**Minimal bağımlılık:** Sadece Python stdlib kullanır (ast, pathlib, argparse).
Harici kütüphane gerektirmez.

## 5. python main.py (ReAct Döngüsü)

**Dosya:** `main.py` — docstring: `ReYMeN Otonom Ajan. Ana ReAct dongusu.`

Doğrudan ReAct döngüsü başlatılır. UTF-8 stdout wrapper, .env yükleme,
modül importları ve interaktif döngü. Belirgin bir ASCII banner göstermez.

## Başlık Tutarlılığı Kuralı

Proje genelinde tek bir tanım kullanılır:
**"ReYMeN — Otonom Uygulama Otomasyonu Ajani"**

Bu tanım şu dosyalarda tutarlı olmalıdır:
- `ReYMeN.bat` (title + banner)
- `start.py` (banner_goster + baslat mesaji)
- `reyment.py` (tüm başlıklar)
- `main.py` (docstring)
- `README.md` (ilk satır)
- `ReYMeN.md` (proje kimliği)
- `PROJE_REHBERI.md` (başlık)
- `TEKNIK_BRIFING.md` (başlık)
- `web_ui.py` (FastAPI title)
- `onboarding.py` (başlık)
- `hermes_cli/banner.py` (banner metni)

## Hermes Agent Farkı

Bu giriş ekranları Hermes Agent'ınkinden tamamen farklıdır. Hermes Agent
kendi TUI'sini gösterirken (Nous Research logosu, tool listesi, skor listesi),
ReYMeN kendi sade banner'ını gösterir. İkisi ayrı sistemlerdir
ve ayrı terminallerde çalışır.
