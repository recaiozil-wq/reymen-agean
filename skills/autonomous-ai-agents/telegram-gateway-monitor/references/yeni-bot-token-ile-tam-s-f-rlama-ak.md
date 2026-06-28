---
skill_id: 138d20fccf3b
usage_count: 1
last_used: 2026-06-16
---
## Yeni Bot Token'ı ile Tam Sıfırlama Akışı

Kullanıcı "bot engellendi" hatası alıp yeni token verdiğinde (veya herhangi bir token değişikliğinde) şu adımlar **kesin sırayla** uygulanır:

1. **Token'ı .env'ye Python ile yaz** — PowerShell'de tırnak içeren token'lar bozulur:
   ```python
   import re
   with open('/c/Users/marko/AppData/Local/hermes/.env', 'r') as f:
       content = f.read()
   content = re.sub(r'^TELEGRAM_BOT_TOKEN=*** 'TELEGRAM_BOT_TOKEN=*** content, flags=re.MULTILINE)
   with open('/c/Users/marko/AppData/Local/hermes/.env', 'w') as f:
       f.write(content)
   ```
   ⚠️ `***` karakteri token'da varsa f-string kullanma, string concatenation yap.

2. **Token'ı doğrula:**
   ```
   grep "TELEGRAM_BOT_TOKEN" /c/Users/marko/AppData/Local/hermes/.env | xxd
   ```
   Token tam olmalı, sonunda `0a` (newline) olmalı.

3. **Gateway state'i sıfırla** — `gateway_state.json`'u aşağıdaki içerikle değiştir:
   ```json
   {"pid":null,"kind":"hermes-gateway","gateway_state":"stopped","platforms":{"telegram":{"state":"disconnected","error_code":null,"error_message":null}}}
   ```
   Veya script: `scripts/reset_gateway_state.py` (varsa kullan)

4. **Gateway'i --replace ile başlat:**
   ```
   cd /c/Users/marko/AppData/Local/hermes/hermes-agent
   REYMEN_HOME_PATH=/c/Users/marko/AppData/Local/hermes /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m hermes_cli.main gateway run --replace
   ```

5. **20 sn bekle, sonra state'i kontrol et:**
   ```
   cat /c/Users/marko/AppData/Local/hermes/gateway_state.json
   ```
   `"state":"connected"` ve `"error_message":null` görene kadar bekle.

6. **Bot username'ini API'den bul** (kullanıcıya bildirmek için):
   ```
   curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
   ```
   `result.username` = `@bot_username`, `result.first_name` = bot adı

7. **Test mesajı gönder:**
   ```
   hermes send --to "telegram:Q !" "Test mesajı"
   ```
   - `Forbidden: bot was blocked by the user` → kullanıcıya bot @username'ini söyle, Telegram'da unblock yapmasını iste
   - Başarılı → gateway çalışıyor, sorun yok