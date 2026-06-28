---
skill_id: 3e61c0f45ac4
usage_count: 1
last_used: 2026-06-16
---
# ReYMeN Dashboard Web UI Kurulumu ve Çalıştırma

## Portlar
| Servis | Port | Başlatma |
|--------|------|----------|
| ReYMeN Agent Dashboard | 9119 | `hermes dashboard --no-open` |
| ReYMeN_output Dashboard | 8000 | `python app.py` (hermes_output/dashboard/) |
| LM Studio API | 1234 | LM Studio GUI üzerinden |

## ReYMeN Dashboard (9119) — İlk Kurulum

İlk çalıştırmada `hermes dashboard` şu hatayı verir:
```
Error: Cannot find module '.../typescript/bin/tsc'
✗ Web UI build failed
```

**Çözüm:**
```bash
cd C:\Users\marko\AppData\Local\hermes\hermes-agent
npm install --workspace web
```
Bu işlem `node_modules/typescript` ve diğer bağımlılıkları kurar.
Sonra `hermes dashboard --no-open` tekrar çalıştırılır.

## .url Kısayol Dosyaları

Localhost servislerine hızlı erişim için klasör: `C:\Users\marko\OneDrive\Desktop\ReYMeN-Localhosts\`

Format:
```
[InternetShortcut]
URL=http://localhost:<PORT>
```

Dosya adı: `<Servis Adı> (<PORT>).url`

## Servis Durumu Kontrolü

```bash
# Çalışan portları listele
netstat -ano | grep "LISTENING"

# Belirli portu test et
curl -s --connect-timeout 3 http://localhost:<PORT>/ | head -5

# Tümünü tek seferde kontrol et
for port in 8000 9119 1234; do
  curl -s --connect-timeout 2 http://localhost:$port/ >/dev/null && echo "$port: CALISIYOR" || echo "$port: KAPALI"
done
```
