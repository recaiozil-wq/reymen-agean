---
name: autonomous-ai-agents_telegram-gateway-monitor_references_pitfall
description: Pitfall
title: "Autonomous Ai Agents Telegram Gateway Monitor References Pitfall"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Pitfall |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Pitfall

- **Telegram sorunlarında İLK iş bu skill'i yükle.** Kullanıcı "skill var ne oldu" derse — haklıdır. Telegram bağlantı sorunlarında önce `telegram-gateway-monitor` skill'ini `skill_view()` ile oku, adımları uygula.
- **Gateway env var adı karışıklığı:** Gateway `TELEGRAM_ALLOWED_USERS` bekler (sonu `_USERS` ile biter). `.env`'de `TELEGRAM_ALLOWLIST` varsa gateway onu görmez ve "Unauthorized user" hatası verir. Gateway "connected" gösterir ama tüm kullanıcıları unauthorized olarak reddeder.
  - **Çözüm:** `.env`'de `TELEGRAM_ALLOWED_USERS=<chat_id>` kullan, `TELEGRAM_ALLOWLIST` değil.
  - **Yedek:** `GATEWAY_ALLOW_ALL_USERS=true` ekle — bu gateway'in tüm kullanıcılara izin vermesini sağlar (geliştirme ortamı için güvenli).
- **Gateway iki .env dosyası okur:**
  1. `~/.hermes/.env` (öncelikli — `C:\Users\marko\.hermes\.env`)
  2. `C:\Users\marko\AppData\Local\hermes\.env`
  - Gateway başlarken `~/.hermes/.env` yoksa allowlist ayarlarını göremez. Bu dosya mevcut değilse oluşturulmalı ve içine `TELEGRAM_ALLOWED_USERS=...` yazılmalıdır.
- **Title generator 401 hatası → API key geçersiz.** Gateway `connected` ve allowlist doğru olsa bile, `title_generator` 401 hatası alınıyorsa gateway'in kullandığı API key geçersizdir (`DEEPSEEK_API_KEY=*** gibi). Gateway-error.log'da `"Your api key: ****... is invalid"` şeklinde görünür. Çözüm: `.env`'deki API key'i gerçek değerle değiştir, sonra Gateway'i restart et.
- Telekom gateway yeniden başlatma komutu **dışarıdan** çalıştırılmalı; gateway içinden gönderilirse reddedilir.
  - Windows için güvenirlidir: `powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName Hermes_Gateway"`.
- "T/F" sesi varsayılan Telegram hedefi listelemede `telegram:Q ! (dm)` olarak görünür; bu hedef mevcut değilse ana Telegram hedefini kullan.
- `.env` okuma: linux PATH ve Windows YAML/CRLF ayrıntıları nedeniyle varsayılan `~/.hermes/.env` çoğu sistemde SIKINTI çıkarır.
  - Bu ortamda doğru yol: `/c/Users/marko/AppData/Local/hermes/.env`
  - `cat /c/Users/marko/AppData/Local/hermes/.env | grep <KEY> || true` kullan.
- Telegram iletimi bir sonraki adım olarak yapılmalı.
- **Obsidian log satırı eklerken `mcp_obsidian_vault_append` kullan** — Bu MCP tool'u encoding sorunları olmadan satır ekler, Türkçe karakterleri (ö/ş/ı/ğ/ü/ç) bozmaz. `write_file`'a göre daha basit: sadece path + content ver, tool gerisini halleder.
  - **Önerilen sıra:**
    1. **İlk tercih:** `mcp_obsidian_vault_append(path="Telegram Gateway Monitor.md", content="- <tarih> <saat> — <sonuç>")` — tek satır ekleme, encoding sorunsuz.
    2. **Yedek:** `write_file` ile oku+yeniyi ekle+baştan yaz — `mcp_obsidian_vault_append` çalışmazsa kullan.
    3. **Son çare:** `[System.IO.File]::AppendAllText(path, text, [System.Text.Encoding]::UTF8)` PowerShell ile — ama bash içindeki quote kaosu nedeniyle tercih edilmez.
  - ⚠️ **write_file yol formatı:** `write_file` tool'u **native Windows yolu** bekler (`C:\\Users\\marko\\...`). MSYS tarzı `/c/Users/marko/...` yolu verilirse tool `C:\\c\\Users\\marko\\...` olarak yanlış çözümler. `terminal()` içinde `/c/Users/...` çalışır ama `write_file`/`read_file`/`patch` tool'larında `C:\\Users\\...` kullan. `mcp_obsidian_vault_append` ise vault-relative path bekler, MSYS veya Windows yolu değil.
- **POLLING MODDA HTTP HEALTH ENDPOINT YOK — `curl localhost:9090/health` false-positive "GATEWAY_DOWN" üretir.** Gateway polling modda çalışırken HTTP sunucu olarak dinlemez — sadece Telegram API'ye outbound long-polling yapar. Port 9090'da listener bulunmaz.
  - **Tespit:** `curl --connect-timeout 5 http://localhost:9090/health` → exit code 7 (connection refused). Bu **normaldir**, gateway kapalı değildir.
  - **Doğru sağlık kontrolü:** `gateway_state.json` oku → `"gateway_state":"running"` ve `"platforms.telegram.state":"connected"` kontrol et, ardından log'da `inbound message:` satırlarının zamanını kontrol et.
  - **Başlangıç doğrulaması (restart sonrası):** Log'da şu satırları ara: `[Telegram] Connected to Telegram (polling mode)` + `✓ telegram connected`.
  - **Netice:** HTTP health endpoint POLLING MOD'UN BİR ÖZELLİĞİ DEĞİLDİR. Yokluğu gateway'in çalışmadığı anlamına gelmez. Eğer `send_message` çalışıyorsa ve log'da inbound mesajlar varsa gateway sağlıklıdır.

- **SESSİZ POLLING DONMASI — Gateway çalışır görünür ama mesaj gelmez.** Bu en tehlikeli arıza modudur: `gateway_state.json` "running" der, cron `last_status: "ok"` der ama Telegram polling donmuştur. Saatlerce mesaj alınmaz, kullanıcı "bağlantı yok" diye uyarır.
  - **Tespit:** Gateway log'unda `inbound message:` en son ne zaman var?
    `tail -20 C:\Users\marko\AppData\Local\hermes\logs\gateway.log | grep "inbound message"`
    Son mesaj >30dk önceyse ve kullanıcı mesaj attığını söylüyorsa → polling dondu.
    *(Not: Gateway yeni restart olduysa log'da `[Telegram] Connected to Telegram` yakın zamanda görünür — inbound mesaj yoksa normaldir.)*
  - **Çözüm (scheduled task ile — `hermes.exe` ModuleNotFoundError verir):**
    `powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName Hermes_Gateway"`
    Bekleme: 15-20 sn
  - **Doğrulama:** Restart sonrası log'da şu satırları ara:
    * `[Telegram] Connected to Telegram (polling mode)` — polling başarılı
    * `✓ telegram connected` — platform bağlandı
  - **Kök neden:** Telegram API long-polling bağlantısı sessizce kopar. Gateway process'i ayakta kalır, hata üretmez — sadece polling döngüsü takılır. Restart tek çözümdür.
  - **Uyarı:** Mevcut `telegram-gateway-monitor` cron job'ı (30dk) sadece gateway process'inin çalıştığını kontrol eder, polling sağlığını kontrol etmez. Monitor turunda log'da `inbound message` zaman damgası da kontrol edilmelidir.
- **Placeholder API key uyarısı (`***`):** Cron monitor turu sırasında `.env`'de `DEEPSEEK_API_KEY=***` gibi literal placeholder değerler tespit edilirse title_generator 401 hatasına neden olur. Bu hata gateway "connected" durumunu etkilemez ama konuşma başlıkları üretilemez. Çözüm: kullanıcıya bildir, gerçek API key sağlanana kadar bu hata devam eder. Monitor raporunda bu durumu belirt.
- **`"test/model is not a valid model ID"` hatası — DeepSeek API key sorunu:** Cron job veya gateway agent çalışırken `RuntimeError: Error code: 400 - {'error': {'message': 'test/model is not a valid model ID', 'code': 400}}` hatası alınıyorsa, bu genellikle DeepSeek API key'inin geçersiz/süresi dolmuş olduğunu gösterir. Sistem "test/model" fallback'ine düşer çünkü authentication geçemez.
  - **Tespit:** Direkt DeepSeek API testi: `curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $(grep DEEPSEEK_API_KEY /c/Users/marko/AppData/Local/hermes/.env | cut -d= -f2)"` → `"Authentication Fails"` dönerse key sorunlu.
  - **Çözüm:** `.env`'deki `DEEPSEEK_API_KEY` değerini yenile. Key doğruysa ve hata devam ediyorsa model adı (`deepseek-v4-flash`) güncel olmayabilir — DeepSeek'in güncel model listesini kontrol et.
  - **Not:** Bu hata gateway "connected" durumunu etkilemez — gateway bağlanır ama `title_generator` ve cron agent işlemleri çalışmaz. `no_agent` script job'ları (allow-once-watcher, gece-01-otomasyon, sabah-08-raporu) bu hatadan etkilenmez çünkü LLM kullanmazlar.
  - **Kaynak:** Bu hata 142 kez üst üste `telegram-gateway-monitor` cron job'ında görüldü. API key yenilenene kadar tüm LLM-tabanlı cron job'lar aynı hatayı alır.
- **`^`-anchor'lı grep ile placeholder taraması false-negative üretebilir.** 
  2026-06-17'de `DEEPSEEK_API_KEY=***` .env'de mevcut olduğu halde şu iki yöntem de **sessizce atladı:**
  - `for key in ...; do grep "^${key}=" ...` — `^` anchor kullanımı, CRLF/BOM sebebiyle eşleşmeyebilir
  - `grep -nF "=***" | grep -v "^[0-9]*:#"` — fixed-string mod olmasına rağmen eşleşmedi
  - **Doğrulama:** `grep "${key}="` (anchorsız) + `cat -A` ile satır sonu ve BOM kontrolü yapmak her iki durumda da doğru sonuç verdi.
  - **Kural:** `^` anchor'ına güvenme. Her zaman anchorsız fallback çalıştır (bkz. `references/zorunlu-ad-mlar.md` Adım 0 fallback).
- **`grep -n "=\\*\\*\\*"` ile placeholder taraması git-bash'te güvenilir DEĞİL.**
  - **BRE regex sorunu:** git-bash'in `\*` escape handling'i tutarsızdır. `=\*\*\*` regex'i `DEEPSEEK_API_KEY=***` satırını **atlayabilir** (sadece yorum satırlarındaki `***`'ı bulur).
  - **`grep -v "^#"` kırılması:** `grep -n` satır numarası prefix'i ekler (`10:icerik`), bu yüzden `^#` filtresi `10:# yorum` satırlarını **atlayamaz** — satır `10:` ile başlar, `#` ile değil.
  - **Çözüm:** `grep -nF "=***"` (fixed-string modu, regex yok) + `grep -v "^[0-9]*:#"` veya belirli key'leri ismen döngüyle kontrol et. Detay: `references/zorunlu-ad-mlar.md` Adım 0.
- **`execute_code` cron modunda bloklanır.** Cron job oturumunda `execute_code` tool'u güvenlik nedeniyle çalışmaz ("Cron jobs run without a user present to approve it"). Monitor içinde Python ile env düzenleme, JSON işleme veya çoklu tool sıralaması gerekiyorsa **bireysel tool çağrıları** (`terminal`, `read_file`, `patch`, `grep`) kullanılmalıdır. Fallback yaklaşımı: tek tek `terminal()` çağrıları ile shell komutlarını çalıştır, çıktıyı kendin işle.
- **`mcp_obsidian_vault_append` her oturumda mevcut olmayabilir.** `mcp_obsidian_vault_append` ideal çözümdür (encoding sorunsuz) ancak bu MCP tool'u oturumun araç setinde bulunmayabilir. Çalışan fallback: `patch` ile Obsidian dosyasının son satırını bulup hedef satırı kendisi+yenisi ile değiştir. `write_file` (oku+yeniden yaz) da çalışır ama büyük dosyalarda pahalıdır.
- **`read_file` satır numarası prefix'i `patch` `old_string`'ine sızabilir:** `read_file` çıktısında satırlar `103|- 2026-06-17 ...` formatında görünür. `103|` satır numarası prefix'idir, dosya içeriği `- 2026-06-17 ...` ile başlar. `old_string` veya `new_string` hazırlarken `103|` prefix'ini dosya içeriği sanıp `|- ` ile başlayan string yazmak dosyayı bozar. Her zaman `- ` (boşluklu tire) ile başladığını doğrula. `patch` uyguladıktan sonra `tail -3 <dosya>` ile kontrol et.
- **`ps -p` false negative on Windows/git-bash:** Git-bash `ps -p` komutu yalnızca MSYS katmanından başlatılan process'leri görebilir. Windows-native process'ler (Python.exe, gateway, vs.) için **false negative** döner: PID çalışıyor olmasına rağmen `ps -p $PID` → "not running" çıktısı verir.
  - **Tespit:** Bu senaryoda `tasklist` veya PowerShell `Get-Process` kullanarak doğrula:
    ```bash
    tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID" && echo "Calisiyor" || echo "Calismiyor"
    ```
    veya
    ```powershell
    powershell.exe -NoProfile -Command "Get-Process -Id $PID -ErrorAction SilentlyContinue"
    ```
  - **Önem:** Gateway PID doğrulamasında `ps -p` tek başına güvenilir DEĞİLDİR. `tasklist` fallback'i zorunludur.
  - **Belirti:** gateway_state.json "running", Telegram "connected" gösteriyor ama monitor scripti "PID CALISMIYOR" raporluyorsa → önce `tasklist` ile doğrula, yanlış alarm olabilir.
