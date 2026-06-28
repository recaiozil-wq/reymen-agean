---
skill_id: 4121c0acb005
usage_count: 1
last_used: 2026-06-16
---
## Polling Sağlık Kontrolü

Gateway çalışıyor görünür ama Telegram mesajları gelmiyorsa, polling donmuş olabilir.

### Tespit Adımları

1. Gateway process çalışıyor mu kontrol et (`hermes.exe` ModuleNotFoundError verir — gateway_state.json kullan):
   ```bash
   PID=$(python3 -c "import json; print(json.load(open('/c/Users/marko/AppData/Local/hermes/gateway_state.json'))['pid'])" 2>/dev/null)
   # ⚠️ git-bash ps -p Windows process'lerini görmeyebilir (false negative).
   # ÖNCE ps -p dene, başarısız olursa tasklist ile doğrula:
   if ps -p "$PID" >/dev/null 2>&1; then
     echo "✓ Gateway PID $PID calisiyor (ps)"
   elif tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID"; then
     echo "✓ Gateway PID $PID calisiyor (tasklist ile dogrulandi)"
   else
     echo "✗ Gateway PID $PID CALISMIYOR"
   fi
   ```

2. Gateway log'unda son inbound mesajı kontrol et:
   `tail -20 C:\Users\marko\AppData\Local\hermes\logs\gateway.log | grep "inbound message"`

3. Kriter:
   - Son `inbound message` <5dk önce → polling sağlıklı
   - Son `inbound message` >30dk önce VE kullanıcı mesaj attığını söylüyor → polling dondu
   - Hiç `inbound message` yoksa → gateway yeni başlamış olabilir, 1-2dk bekle

### Tespitteki Kör Nokta

Gateway `hermes gateway status` çıktısı `✓ Gateway process running` dese bile **polling donmuş olabilir**. 
Bu oturumda yaşandı: PID 35444 çalışıyor, status "Ready", monitor cron "ok" raporluyor — ama 7+ saat hiç mesaj alınmamış.

**Sebep:** Gateway'in Telegram bağlantısı (TCP) canlı ama `getUpdates` long-polling döngüsü bir yerde takılı kalmış. Gateway log'unda hata veya uyarı yok, sadece sessizlik.

**Kural:** Gateway PID'sinin var olması YETERLİ DEĞİL. Her zaman log'da inbound mesaj zamanını da kontrol et.

**Teşhis Akışı (bu oturumda doğrulandı):**
1. `hermes gateway status` → "Process running, Status Ready" ✅ (yanıltıcı)
2. `send_message` → mesaj gitti (message_id 5033) ✅ (yanıltıcı)
3. `tail -20 C:\\Users\\marko\\AppData\\Local\\hermes\\logs\\gateway.log | grep "inbound message"` → son mesaj 7 saat önce ❌ (GERÇEK DURUM)
4. `tail -20 C:\\Users\\marko\\AppData\\Local\\hermes\\logs\\gateway-error.log` → sadece eski uyarılar, yeni hata yok
5. Karar: polling dondu, restart gerekli

### Çözüm

```bash
# 1. Tercih edilen yol — hermes CLI ile graceful restart
"C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe" gateway restart
# Çıktı: ✓ Gateway stopped (drained cleanly) + ✓ Gateway started via Scheduled Task (PID: ...)

# 2. Alternatif — doğrudan scheduled task
powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName ReYMeN_Gateway"
```

Restart sırasında:
- Gateway mevcut session'ları drain eder, home channel'a shutdown bildirimi gönderir
- Telegram'dan disconnect olur
- Tekrar başlar, polling mode'da reconnect (10-15 sn)
- Bekle: `sleep 15` sonra doğrulamaya geç

### Doğrulama

Restart sonrası log'da şu satırları kontrol et:
- `[Telegram] Connected to Telegram (polling mode)`
- `✓ telegram connected`

### Gönderme Testi

Restart'tan sonra Telegram'a test mesajı gönder:
`send_message(target="telegram", message="ReYMeN polling test - <zaman>")`

Kullanıcıdan cevap yazmasını iste — eğer burdan görülüyorsa tamir tamamdır.
