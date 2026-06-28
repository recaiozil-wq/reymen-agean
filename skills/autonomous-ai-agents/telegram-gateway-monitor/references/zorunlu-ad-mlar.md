---
skill_id: d9de8103a0ed
usage_count: 1
last_used: 2026-06-16
---
## Zorunlu adımlar

0. **Ön kontrol – env sağlık taraması (her monitor turunda):**
    - `C:\Users\marko\AppData\Local\hermes\.env` içinde `***` (placeholder) değeri olan API key'leri tara:
      ```bash
      grep -E "KEY=[*]{3}$|TOKEN=[*]{3}$|API_KEY=[*]{3}$" /c/Users/marko/AppData/Local/hermes/.env || echo "Placeholder key yok"
      ```
    - `~/.hermes/.env` mevcut mu ve allowlist doğru mu kontrol et:
      ```bash
      cat /c/Users/marko/.hermes/.env 2>/dev/null | grep -E "TELEGRAM_ALLOWED_USERS|GATEWAY_ALLOW_ALL_USERS" || echo "EKSIK: ~/.hermes/.env allowlist ayari yok"
      ```
    - `gateway_state.json`'daki PID canlı mı kontrol et (⚠️ git-bash `ps -p` Windows process'lerini görmeyebilir — fallback kullan):
      ```bash
      PID=$(python3 -c "import json; print(json.load(open('/c/Users/marko/AppData/Local/hermes/gateway_state.json'))['pid'])" 2>/dev/null)
      if [ -n "$PID" ] && (ps -p $PID >/dev/null 2>&1 || tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID"); then
        echo "PID $PID calisiyor"
      elif [ -n "$PID" ]; then
        echo "PID $PID CALISMIYOR"
      else
        echo "PID YOK (gateway_state.json bos veya okunamadi)"
      fi
      ```
    - Placeholder key bulunursa rapora ekle (onarım: kullanıcıya gerçek key bildirimi — otomatik düzeltme mümkün değil).

1. `.env`'ye yeni bir `TELEGRAM_BOT_TOKEN` yazıldığında **her zaman** şu adımları sırasıyla uygula:
    - `.env` yolu: `C:\Users\marko\AppData\Local\hermes\.env`
    - PowerShell ile dışarıdan gateway restart: `powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName ReYMeN_Gateway"`
      - Not: linux/workarounds veya `schtasks /Run` bash içinde güvenilir çalışmaz.
    - Bekleme: restart sonrası bağlanma için 15-20 saniye bekle.
    - Önce hedefi listele (PYTHONPATH ile — bkz. `references/hermes-cli-invocation.md`):
      ```
      cd /c/Users/marko/AppData/Local/hermes/hermes-agent && \
      REYMEN_HOME_PATH=/c/Users/marko/AppData/Local/hermes \
      PYTHONPATH=/c/Users/marko/AppData/Local/hermes/hermes-agent \
      /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \
      -m hermes_cli.main send --list telegram
      ```
      (çıktıda `telegram:Q !` gibi bir hedef görünür)
    - Hedefi tırnak içinde kullan:
      ```
      cd /c/Users/marko/AppData/Local/hermes/hermes-agent && \
      REYMEN_HOME_PATH=/c/Users/marko/AppData/Local/hermes \
      PYTHONPATH=/c/Users/marko/AppData/Local/hermes/hermes-agent \
      /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \
      -m hermes_cli.main send --to "telegram:Q !" "[telegram-watchdog] Bağlantı testi başarılı."
      ```
    - ⚠️ `telegram:Q !` içindeki `!` shell'de özel anlam taşır — **tırnak içine almak zorunludur**, aksi halde hata alırsın.
    - ⚠️ `hermes.exe` veya `hermes` kısa komutu çalışmaz (`ModuleNotFoundError`). Her zaman yukarıdaki PYTHONPATH ile çalıştır.
2. Token doğrulama ve hata ayıklama:
    - Test mesajı düzgün gittiyse tamam.
    - "Not Found"/InvalidToken gelirse ne `.env`'ye ne de gateway yapısına müdahale et.
    - Sonuç: kullanıcıya yeni bir bot token iste; yeni token ile sadece Adım 1'i baştan uygula.
    - **"bot was blocked by the user"** (Forbidden) hatası:
      - Bu bir **kullanıcı tarafı** sorunudur. Bot token'ı geçerli, gateway bağlı, hata yok.
      - **Bot username'ini API'den çek** (kullanıcıya söylemek için):
        ```
        curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
        ```
        `result.username` ve `result.first_name` değerlerini kullanıcıya bildir.
      - Kullanıcı Telegram'da bot profilini açıp **Unblock / Engeli Kaldır** yapmalıdır.
      - Gateway restart, token değişikliği veya state reset ÇÖZMEZ. Kullanıcıya net bir şekilde bildir.
      - Örnek: "Bot @kullanici_adi (isim) — Telegram'da bulup Unblock yap, sonra dene."
3. Gateway state takibi ve restart:
    - `C:\Users\marko\AppData\Local\hermes\gateway_state.json` içindeki Telegram state `connected` olana kadar kontrol et.
    - **ÖNCE PID kontrolü:** gateway_state.json'daki PID ile `tasklist`'te görünen PID'yi karşılaştır. Eğer state'teki PID çalışmıyorsa, başka bir PID'de gateway zaten çalışıyor olabilir.
      - Gateway log'una bak: gateway örneği çalıştırmayı dene, "Gateway already running (PID X)" mesajı alırsan o PID doğru olan.
      - Doğru PID'yi öldür: `powershell.exe -NoProfile -Command "Stop-Process -Id <PID> -Force -ErrorAction SilentlyContinue"`
    - **Temiz restart (--replace ile):**
      ```
      cd /c/Users/marko/AppData/Local/hermes/hermes-agent
      REYMEN_HOME_PATH=/c/Users/marko/AppData/Local/hermes /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m hermes_cli.main gateway run --replace
      ```
      `--replace` eski gateway instance'ını otomatik öldürür ve yeniden başlatır.
    - **State reset (sadece --replace çalışmazsa):**
      1. `gateway_state.json` içinde `platforms.telegram.state`'i `"disconnected"` yap, `pid`'yi `null` yap
      2. Ardından `--replace` ile gateway'i başlat
      3. 15-20 sn bekle, state'i tekrar kontrol et
    - Eski hatalı token hatası (`115309...JhnYh` gibi) kalıntıysa, gateway process'ini öldür: `taskkill /F /PID <pid>` ardından scheduled task'ı tekrar başlat.
4. Nihai durumu raporla:
    - "Telegram bağlantı testi başarılı."
    - "Telegram bağlantı testi başarısız ve otomatik onarım denendi."