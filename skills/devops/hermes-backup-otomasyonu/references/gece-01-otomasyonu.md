---
skill_id: f637b71dc7a3
usage_count: 1
last_used: 2026-06-16
---
# Gece 01:00 Otomasyonu — Screenshot + Telegram + Claude Terminal

## Amaç

Her gece 01:00'da bilgisayar açıkken:
1. Ekran görüntüsü al (çalışan işlemleri kaydet)
2. Telegram'dan kullanıcıya gönder (sabah kontrol için)
3. VS Code Claude terminal'e "islemlerine devam et" yaz (gece boyu çalışmaya devam)

## Cron Job

| Alan | Değer |
|------|-------|
| Job ID | `d0e778272e9e` |
| Adı | `gece-01-otomasyon` |
| Zaman | Her gün 01:00 (`0 1 * * *`) |
| Tür | `no_agent: true` — LLM harcamaz, script doğrudan çalışır |
| Script | `gece_01_otomasyon.py` |
| Deliver | `telegram:6328823909` |

## Script: `gece_01_otomasyon.py`

Konum: `C:\Users\marko\AppData\Local\hermes\scripts\gece_01_otomasyon.py`

### Yaptıkları (Sırayla)

1. **Screenshot** — `screenshot_v2.py` (Python 3.14 + mss, monitors[1]) ile tam ekran görüntüsü alır
2. **Telegram** — `.env`'den `TELEGRAM_BOT_TOKEN` okur, `sendPhoto` API ile fotoğrafı gönderir, caption: `🌙 01:00 otomasyon - Ekran goruntusu`
3. **VS Code Yazı** — `vscode_yaz.bat "islemlerine devam et"` ile Claude terminal'e komut enjekte eder

### Önemli Detaylar

- **Python 3.14** kullanır (`C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe`)
- `.env` yolu: `C:\Users\marko\AppData\Local\hermes\.env`
- Telegram bot token `.env`'den okunur, `urllib` ile multipart upload yapar (requests bağımlılığı yok)
- Chat ID: `6328823909`
- Screenshot bulunamazsa sadece mesaj gönderir

## Bilinen Sorunlar

1. **Gateway çökmesi** — `"Devam et ip ucuc gateway cokmnis olduğunda PID 2564 hatası veryor"` — gateway çökünce PID 2564 hatası verir. Çözüm: Enter tuşuna basmak veya OK butonuna tıklamak yeterlidir. `gorsel-onaylama` skill'ine bak.
2. **Session limit** — ReYMeN "You've hit your session limit" uyarısı verirse, OK/Enter yeterlidir. Cron job script'i bu uyarıyı otomatik geçemez (no_agent, sadece screenshot alır). Gerekirse LLM cron job'ına çevir.

## İlgili Skill'ler

- `hermes-backup-otomasyonu` — Bu cron job'un bağlı olduğu umbrella skill
- `gorsel-onaylama` — OK/Allow Once butonlarını otomatik tıklama
- `windows-automation/gorsel-onaylama` — Aynı skill'in Windows yolu
