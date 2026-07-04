---
name: rey-men-bot
description: Run, troubleshoot, and manage the ReYMeN Telegram bot. 3 bot (Kral_38, Pasa_38, ReYMeN) with shared command module and DURUM_OKU() integration.
category: genel
audience: user
author: Watcher-Hermes
tags: [rey-men, telegram, bot, python, hermes-fork, durum-oku, ortak-modul, kesilme, polling]
version: 2.2.0
---

# ReYMeN Telegram Bot — 3 Bot Entegre Sistem

3 bot: **Kral_38** (`telegram_bot/bot.py`), **Pasa_38** (`reymen/ag/telegram_bot.py`), **ReYMeN** (`telegram_bot/ai_bot.py`).
Hepsi ayni **15 ortak komutu** kullanir (`reymen/ag/ortak_komutlar.py`).

## Bot Dosyalari

| Bot | Token (.env) | Dosya | Platform | AI Yetenegi |
|:---:|:------------:|:-----:|:--------:|:-----------:|
| **Kral_38** | `BOT_TOKEN_KRAL` | `telegram_bot/bot.py` | Telegram | OnceHafiza |
| **Pasa_38** | `BOT_TOKEN_PASA` | `reymen/ag/telegram_bot.py` | Telegram | AIAgentOrchestrator |
| **ReYMeN** | `BOT_TOKEN_REYMEN` | `telegram_bot/ai_bot.py` | Telegram | Beyin + OnceHafiza |

## Komut Seti (15 Ortak Komut)

Tum komutlar `reymen/ag/ortak_komutlar.py`'de tanimlidir.
Her bot `komut_isle()` fonksiyonu ile bu modulu cagirir.

| Komut | Aciklama | Kimde |
|:------|:---------|:-----:|
| `/start` | Hosgeldin | ✅ Hepsi |
| `/help` | Yardim listesi | ✅ Hepsi |
| `/run <hedef>` | Ajana gorev ver | ✅ Hepsi |
| `/status` | Sistem durumu (durum.json) | ✅ Hepsi |
| `/logs` | Gateway log (son 15) | ✅ Hepsi |
| `/cancel` | Gorev iptal | ✅ Hepsi |
| `/clarify <soru>` | Talebi netlestir (| ile secenek) | ✅ Hepsi |
| `/exec <kod>` | Python calistir | ✅ Hepsi |
| `/beceriler` | Beceri listesi | ✅ Hepsi |
| `/model [model]` | Model goster/degistir | ✅ Hepsi |
| `/provider [p]` | Provider goster/degistir | ✅ Hepsi |
| `/sistem [p]` | Sistem prompt goster/degistir | ✅ Hepsi |
| `/ayarlar` | Tum ayarlar | ✅ Hepsi |
| `/sifirla` | Ayarlari sifirla | ✅ Hepsi |
| `/durum` | durum.json ham JSON | ✅ Hepsi |

### Mimarisi

```
reymen/ag/ortak_komutlar.py  ← TEK KAYNAK (15 komut)
         ↙                ↘               ↘
  Pasa_38 (telegram_bot.py)   ReYMeN (ai_bot.py)   Kral_38 (bot.py)
   → komut_isle()              → kendi ayar komutlari  → kendi cron komutlari
                                 + ortak modul           + ortak modul
```

**Komut ekleme:** Sadece `ortak_komutlar.py`'ye fonksiyon ekle + `KOMUTLAR` sozlugune kaydet.
**Bot ozel komut:** Bot'un kendi `komut_isle()` metoduna elif ekle, ortak modul cagrisindan ONCE kontrol et.

## .env Yapilandirmasi

Bot `.env`'yi su sirayla yukler (`_env_yukle()` fonksiyonu):

1. **Ortam degiskeni** (bot_supervisor.py ile gelen TELEGRAM_BOT_TOKEN)
2. **Proje kokundeki `.env`** (`ReYMeN-Ajan/.env`)
3. **Hermes profil `.env`'si** (`AppData/Local/hermes/profiles/<HERMES_PROFILE>/.env`)

```python
from dotenv import load_dotenv

# 1. Proje koku .env
_env_yolu = PROJE_KOK / ".env"
if _env_yolu.exists():
    load_dotenv(str(_env_yolu), override=True)

# 2. Hermes profil .env (fallback)
profil = os.environ.get("HERMES_PROFILE", "reymen")
hermes_env = Path.home() / "AppData/Local/hermes/profiles" / profil / ".env"
if hermes_env.exists():
    load_dotenv(str(hermes_env), override=False)
```

Her bot kendi profil `.env`'sinde `TELEGRAM_BOT_TOKEN=` ile calisir.
`bot_supervisor.py` her bot icin ayri token set eder.

| Bot | Profil | Token Kaynagi |
|:----|:-------|:-------------|
| @Pasa_38_bot | default | `profiles/default/.env` |
| @Kiral38bot | kiral38 | `profiles/kiral38/.env` |
| @ReYMeN_ReYMeNbot | reymen | `profiles/reymen/.env` |

## Bot Calistirma

### Supervisor ile (Onerilen — 3 Bot, Crash Restart)

```bash
cd /c/Users/marko/Desktop/Reymen\ Proje/ReYMeN-Ajan
python bot_supervisor.py
# 3 bot'u ayri token ile baslatir, crash'te restart eder
# Durdurmak icin: Ctrl+C veya python bot_supervisor.py --stop
```

`bot_supervisor.py`:
- Her bot icin kendi profil `.env`'sinden token okur (409 Conflict cozumu)
- Bot crash yaparsa 5sn sonra restart eder
- Loglari goruntulemek icin supervisor window'una bak

### Tek seferlik (arka planda, supervisor yok)

```bash
python bot_supervisor.py --once
```

### Elle Calistirma

#### Pasa_38 (standalone polling)
```bash
cd '/c/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan'
set TELEGRAM_BOT_TOKEN=<pasa-token> && python reymen/ag/telegram_bot.py
```

#### ReYMeN (ai_bot.py — redirect to telegram_bot.py)
```bash
cd '/c/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan'
set TELEGRAM_BOT_TOKEN=<reymen-token> && python telegram_bot/ai_bot.py
```

#### Kral_38 (bot.py — redirect to telegram_bot.py)
```bash
cd '/c/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan'
set TELEGRAM_BOT_TOKEN=<kiral-token> && python telegram_bot/bot.py
```

### Bot Restart (Her Degisiklik Sonrasi Zorunlu)

```bash
# Supervisor ile:
python bot_supervisor.py --stop
python bot_supervisor.py

# Elle (process bul + kill):
tasklist /fi "WINDOWTITLE eq Pasa_38"   # PID bul
taskkill //PID <PID> //F
cd '/c/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan'
python reymen/ag/telegram_bot.py &

# Dogrula (3 saniye sonra process ayakta mi?)
sleep 3 && ps aux | grep telegram_bot | grep -v grep
```

**Kural:** durum.json, SOUL.md, conversation_loop.py, telegram_bot.py, ortak_komutlar.py degisikligi → **bot restart ZORUNLU**. Yoksa degisiklik gorulmez.

## DURUM_OKU() Dört Katmanli Entegrasyon

### Sorun
Bot üç şekilde eski veri gösteriyordu:
1. `.env` yanlış yolda aranıyordu — bot başlamıyordu
2. `/status` komutu hardcoded kontroller kullanıyordu
3. AI yanıtları kendi eğitim verisinden eski karşılaştırma üretiyordu
4. İnsan okunabilir özet → model kendi ezberini kullanıyordu

### Çözüm (4 Katmanli)

**Katman 0 — `.env` Yolu:** Bot dotenv'i `ROOT / ".env"` ile arar, bulamazsa `PROJE_KOK / ".env"` dener.

**Katman 1 — `/status` komutu:** `_cmd_status()` önce durum.json'u okur, yoksa eski hardcoded yönteme düşer (graceful degrade).

**Katman 2 — conversation_loop.py prompt enjeksiyonu:** Her AI yanıtından önce prompt'a durum.json **HAM JSON** verisi gider + `[ZORUNLU KURAL]` talimati:

```
[ZORUNLU KURAL — ASAGIDAKI JSON TEK KAYNAKTIR]
1. Kendi training bilgini KULLANMA. Bu JSON TEK KAYNAK.
2. 'hermes>reymen yonleri' sorusunda:
   → 'ReYMeN_karsilastirma/detaylar' bolumundeki veriyi tablo yap.
3. 'eksik listesi' sorusunda:
   → 'mevcut_eksikler/maddeler' bolumunu kullan.
4. ESKI BILDIGIN LISTELER yanlis. Bu JSON dogru.
5. Asla tahmin etme, asla uydurma.
==================================================
{ham json verisi (ilk 8000 karakter)}
==================================================
```

**Katman 3 — Ham JSON (insan okunabilir ozet YOK):**
`conversation_loop.py` (1341-1366): `from reymen.sistem.durum import _yukle` ile ham JSON okunur, dogrudan prompt'a eklenir. **İnsan okunabilir özet kaldırıldı.** Model JSON'u tabloya çevirmek zorunda kalır, kendi ezberini kullanamaz.

```python
from reymen.sistem.durum import _yukle
import json as _json_mod
_ham_veri = _yukle()
_ham_json = _json_mod.dumps(_ham_veri, indent=2, ensure_ascii=False)
ek_bilgi += "\n\n[ZORUNLU KURAL — ASAGIDAKI JSON TEK KAYNAKTIR]\n..."
ek_bilgi += _ham_json[:8000]
```

### Hata Ayiklama Sirasi

```
Katman 0 → .env path (bot baslamazsa)
Katman 1 → /status DURUM_OKU (bot calisiyor ama eski veri)
Katman 2 → conversation_loop enjeksiyonu (AI model eski karsilastirma uretiyorsa)
Katman 3 → Ham JSON vs ozet (model hala training data'sini kullaniyorsa)
```

## durum.json Yapisi

Dosya: `ReYMeN-Ajan/durum.json`
Guncelleyen: ReYMeN_Agent (elle) veya self-improve cron (otomatik)

### Bolumler

| Alan | Icerik |
|:-----|:-------|
| `aktif_ajanlar` | 7 ajan: Pasa_38, Kral_38, ReYMeN_Bot, DiscordBot, AIAgentOrchestrator, ACPServer, GatewayYonetici |
| `ozellikler` | 21 ozellik (web_arama, goruntu_uretimi, ses_tts, ...) |
| `ReYMeN_karsilastirma` | Hermes vs ReYMeN: 25/30 tamam, 5 eksik |
| `tohum_self_improve` | Self-improve metrikleri (0.874 skor, 6282 dosya) |

### Her Ajanda Bulunmasi Gereken Alanlar

```json
{
  "tur": "telegram_bot",
  "dosya": "reymen/ag/telegram_bot.py",
  "platform": "telegram",
  "durum": "polling|hazir",
  "komutlar": ["/start", "/help", ...],
  "yetki": "tam|standart",
  "son_guncelleme": "2026-06-30",
  "aciklama": "..."
}
```

**Guncelleme:** `aktif_ajanlar` elle guncellenir. Self-improve cron otomatik olarak sadece `tohum_self_improve` ve `ozellikler` bolumlerini gunceller.

## Bot Yetki Sistemi

3 Telegram botu da `yetki: tam` olarak isaretlenmistir.
Diger ajanlar (DiscordBot, AIAgentOrchestrator, ACPServer) `yetki: standart`.

### Yetki Seviyeleri

| Seviye | Anlam | Bot |
|:------:|:------|:---:|
| `tam` | Tum komutlara erisim, kod calistirma, sistem ayarlari | Kral_38, Pasa_38, ReYMeN |
| `standart` | Sinirli komut seti, ayar degistirme yok | DiscordBot, diger ajanlar |

## Paşa_38 Bot'un Hardcoded Hermes Karşılaştırma Verisi

### Sorun
Paşa_38 bot, Hermes vs ReYMeN karşılaştırma tablosu gönderdiğinde sıklıkla güncel olmayan veri gösterir. Bunun sebebi:
- AI model kendi eğitim verisindeki eski karşılaştırmayı kullanır
- İnsan okunabilir özet gördüğünde "ben daha iyisini biliyorum" diye düşünüp kendi ezberini tercih eder

### Cozum
1. **Ham JSON enjeksiyonu** (Katman 3) — model JSON'u tabloya çevirmek zorunda kalır
2. `[ZORUNLU KURAL]` — prompt'taki net talimat modelin kendi bilgisini bastırır
3. Bot restart edilmezse hiçbiri çalışmaz

### Doğrulama

```bash
# Bot'un gördüğü prompt'u kontrol et (teşhis amaçlı)
python -c "
from reymen.sistem.durum import _yukle
import json
d = _yukle()
print(f'Ajan: {len(d.get(\"aktif_ajanlar\", {}))}')
print(f'Karsilastirma: {d.get(\"ReYMeN_karsilastirma\", {}).get(\"tamam\")}/30')
"
```

## Bot Disconnection (Kesilme) Troubleshooting

Kullanici "bot kesiliyor", "hafiza sorunu var", "yanit vermiyor" dediginde su sirayla kontrol et:

### Root Cause Tablosu

| # | Sorun | Kaynak | Cozum |
|---|-------|--------|-------|
| 1 | **409 Conflict** | Ayni token ile 2+ bot polling yapiyor | Her bota AYRI token ver. `baslat_tum_botlar.bat`'i kontrol et. |
| 2 | **Watchdog I/O patlamasi** | `ortak_watchdog.py` her 30sn'de 755+ .py hash'liyor | Watchdog interval'ini 120sn'ye cek: `watchdog_baslat(interval=120)` |
| 3 | **No .env** | `_PROJE_KOK / ".env"` yoksa token bos gelir | Proje kokunde `.env` olustur: `TELEGRAM_BOT_TOKEN=<token>` |
| 4 | **Polling backoff yok** | `polling()` satir 1290: 5sn bekle + devam, exponential backoff yok | 409: 30sn bekle, sonra 60sn, sonra 120sn. 3. denemede alarm ver. |
| 5 | **Process supervisor yok** | `start /B` ile baslayan bot crash olursa sessizce olur | Windows Task Scheduler veya `baslat_bot.bat` ile supervisor loop |
| 6 | **3x Beyin belleği** | Her BotProcess ayri Beyin (LLM client) yukler -> 3x RAM | BotProcess'leri ayri profile'da calistir, config havuzu paylas |
| 7 | **Graceful degrade eksik** | `urllib.request.urlopen(timeout=35)` exception'u 5sn bekle + loop | Network hatasi ile API hatasini ayristir, farkli backoff uygula |
| 8 | **start_bot.bat yanlis yol** | Eski `.bat` dosyalari farkli proje dizinine gidiyor olabilir | Her `.bat`'in `cd /d` yolunu dogrula |

### 409 Conflict — En Yaygin Neden (COZULDU)

**Belirti:** Bot calisiyor gorunur ama mesaj almaz. Log'da `"409"` veya `Conflict` gecer.

**Kok neden:** `baslat_tum_botlar.bat` 3 farkli .py dosyasi baslatir — hepsi ayni `TELEGRAM_BOT_TOKEN` env variable'ini okursa Telegram 409 atar.

**Cozum (bot_supervisor.py ile):** Her bot kendi profil `.env`'sinden token okur. `bot_supervisor.py`:
```python
BOTLAR = [
    {"ad": "Pasa_38",  "profil": "default", "env_anahtar": "TELEGRAM_BOT_TOKEN"},
    {"ad": "Kiral38",  "profil": "kiral38", "env_anahtar": "TELEGRAM_BOT_TOKEN"},
    {"ad": "ReYMeN",   "profil": "reymen",  "env_anahtar": "TELEGRAM_BOT_TOKEN"},
]
```
Her bot baslatilirken `TELEGRAM_BOT_TOKEN` ortam degiskeni o profilin token'i ile doldurulur → **3 ayri token, 3 ayri poll, 409 yok**.

**Eski cozum (manuel):**
1. Her bot ayri token kullanmali (BotFather'dan 3 ayri token al)
2. Her token kendi `.bat`'inda `set TELEGRAM_BOT_TOKEN=*** ile verilmeli

### Polling Exponential Backoff (COZULDU)

`telegram_bot.py`'ye `_polling_yonetici()` eklendi:
- Exponential backoff: 2^N saniye (max 60sn)
- 409 Conflict'te offset sifirlanir (0'dan baslar)
- 10 ardısık hata → log'a kritik uyari basar
- Her basarili turda hata sayaci sifirlanir

```python
_MAX_BACKOFF = 60   # maksimum bekleme
_MAX_RETRY = 10     # maksimum ardışık hata

def _polling_yonetici(ad, poll_fn, durma_events=None):
    ardisik_hata = 0
    while True:
        try:
            poll_fn()
            ardisik_hata = 0  # basarili tur
        except Exception as e:
            ardisik_hata += 1
            backoff = min(2 ** ardisik_hata, _MAX_BACKOFF)
            if ardisik_hata >= _MAX_RETRY:
                logger.critical("...yeniden baslatiliyor...")
                time.sleep(5); ardisik_hata = 0; continue
            time.sleep(backoff)
```

### Watchdog Performans Kontrolu (COZULDU)

Watchdog intervali 30sn → **120sn** olarak degistirildi (`ortak_watchdog.py` satir 33).
I/O yuku 4x azaldi.

## Pitfall: .env Permission Lock

durum.json bazen `-r--r--r--` (read-only) iznine sahip olur. Bu durumda write_file basarisiz olur.
Cozum: `rm dosya` + python ile yeniden olustur.

```bash
rm '/c/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan/durum.json'
python -c "import json; json.dump({'proje':'ReYMeN Ajan'}, open('durum.json','w'), indent=2)"
```

## References
- `references/hermes-karsilastirma.md` — Guncel Hermes vs ReYMeN feature karsilastirmasi
