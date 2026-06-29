---
name: autonomous-ai-agents_telegram-gateway-monitor_references_zorunlu-ad-mlar
description: Zorunlu adımlar
title: "Autonomous Ai Agents Telegram Gateway Monitor References Zorunlu Ad Mlar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Zorunlu adımlar |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Zorunlu adımlar

0. **Ön kontrol – env sağlık taraması (her monitor turunda):**
    - `C:\\Users\\marko\\AppData\\Local\\hermes\\.env` içinde `***` (placeholder) değeri olan API key'leri tara:
      ```bash
      # ⚠️ IKILI TUZAK: (1) CRLF dosyalarda $ anchor calismaz.
      # (2) grep -n ile "=\\*\\*\\*" regex'i git-bash'te guvenilir DEGILDIR
      #     (BRE escape handling shell'e gore degisir, DEEPSEEK_API_KEY=*** gibi
      #     satirlari atlayabilir). Ayrica -n eklenince satir "N:icerik" olur,
      #     grep -v "^#" ile yorum satiri filtrelemesi BOZULUR.
      #
      # DOGRU: Belirli key'leri ismen kontrol et:
      # ⚠️ Windows .env dosyalari CRLF (\\r\\n) ile biter. cut -d= -f2-
      # degeri "***\\r" olarak dondurur, "$val" = "***" karsilastirmasi
      # sessizce BASARISIZ OLUR. tr -d '\\r' ZORUNLUDUR.
      for key in DEEPSEEK_API_KEY TELEGRAM_BOT_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY; do
        val=$(grep "^${key}=" /c/Users/marko/AppData/Local/hermes/.env 2>/dev/null | cut -d= -f2- | tr -d '\\r')
        [ "$val" = "***" ] && echo "PLACEHOLDER: $key=***"
      done
      # Ayrica -F (fixed-string) ile genel tarama:
      grep -nF "=***" /c/Users/marko/AppData/Local/hermes/.env | grep -v "^[0-9]*:#" || :
      ```
      **⚠️ `^`-anchor'lı grep false-negative üretebilir.** 2026-06-17'de `DEEPSEEK_API_KEY=***` mevcut olduğu halde hem `^`-anchor'lı döngü hem de `grep -nF "=***"` sessizce atladı. Sebep kesin değil (BOM / ^ anchor / git-bash CRLF handling). **Fallback — her zaman aşağıdaki anchorsız + `cat -A` kontrolünü de çalıştır:**
      ```bash
      # Fallback: ^ anchor kullanmadan direkt key adıyla tara, ardından
      # cat -A ile görünürlük kontrolü yap (satır sonu, BOM, Unicode).
      for key in DEEPSEEK_API_KEY TELEGRAM_BOT_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY; do
        line=$(grep "${key}=" /c/Users/marko/AppData/Local/hermes/.env 2>/dev/null | head -1)
        [ -n "$line" ] && echo "RAW[$key]=$line"
      done
      grep -n "DEEPSEEK_API_KEY\|TELEGRAM_BOT_TOKEN\|GITHUB_TOKEN\|ANTHROPIC_API_KEY" /c/Users/marko/AppData/Local/hermes/.env | cat -A
      ```
    - `~/.hermes/.env` mevcut mu ve allowlist doğru mu kontrol et:
      ```bash
      cat /c/Users/marko/.hermes/.env 2>/dev/null | grep -E "TELEGRAM_ALLOWED_USERS|GATEWAY_ALLOW_ALL_USERS" || echo "EKSIK: ~/.hermes/.env allowlist ayari yok"
      ```
    - `gateway_state.json`'daki PID canlı mı kontrol et (⚠️ git-bash `ps -p` Windows process'lerini görmeyebilir — fallback kullan):
      ```bash
      # ⚠️ git-bash: Python /c/Users/... yolunu anlamaz (native Windows binary).
      # cat ile pipe et:
      PID=$(cat /c/Users/marko/AppData/Local/hermes/gateway_state.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('pid',''))")
      if [ -n "$PID" ] && (ps -p $PID >/dev/null 2>&1 || tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID"); then
        echo "PID $PID calisiyor"
      elif [ -n "$PID" ]; then
        echo "PID $PID CALISMIYOR"
        # ⚠️ State.json'daki PID ölü olabilir ama gateway başka PID'de çalışıyor olabilir
        # (test run'ları state.json'ı üzerine yazar — bkz. references/gateway-state-json-corruption.md).
        # gateway-exit-diag.log'un son kaydındaki PID'i kontrol et:
        REAL_PID=$(grep '"gateway.start"' /c/Users/marko/AppData/Local/hermes/logs/gateway-exit-diag.log 2>/dev/null | tail -1 | grep -oE '"pid": [0-9]+' | grep -oE '[0-9]+')
        if [ -n "$REAL_PID" ]; then
          tasklist //FI "PID eq $REAL_PID" 2>/dev/null | grep -q "$REAL_PID" && echo "GERCEK PID $REAL_PID CALISIYOR (exit-diag.log) — state.json kirli, fix icin bkz. references/gateway-state-json-corruption.md" || echo "GERCEK PID $REAL_PID de calismiyor"
        fi
      else
        echo "PID YOK (gateway_state.json bos veya okunamadi)"
      fi
      ```
    - Placeholder key bulunursa rapora ekle (onarım: kullanıcıya gerçek key bildirimi — otomatik düzeltme mümkün değil).

1. `.env`'ye yeni bir `TELEGRAM_BOT_TOKEN` yazıldığında **her zaman** şu adımları sırasıyla uygula:
    - `.env` yolu: `C:\Users\marko\AppData\Local\hermes\.env`
    - PowerShell ile dışarıdan gateway restart: `powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName Hermes_Gateway"`
      - Not: linux/workarounds veya `schtasks /Run` bash içinde güvenilir çalışmaz.
    - Bekleme: restart sonrası bağlanma için 15-20 saniye bekle.
    - Önce hedefi listele (PYTHONPATH ile — bkz. `references/hermes-cli-invocation.md`):
      ```
      cd /c/Users/marko/AppData/Local/hermes/hermes-agent && \
      HERMES_HOME=/c/Users/marko/AppData/Local/hermes \
      PYTHONPATH=/c/Users/marko/AppData/Local/hermes/hermes-agent \
      /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe \
      -m hermes_cli.main send --list telegram
      ```
      (çıktıda `telegram:Q !` gibi bir hedef görünür)
    - Hedefi tırnak içinde kullan:
      ```
      cd /c/Users/marko/AppData/Local/hermes/hermes-agent && \
      HERMES_HOME=/c/Users/marko/AppData/Local/hermes \
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
      HERMES_HOME=/c/Users/marko/AppData/Local/hermes /c/Users/marko/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m hermes_cli.main gateway run --replace
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
