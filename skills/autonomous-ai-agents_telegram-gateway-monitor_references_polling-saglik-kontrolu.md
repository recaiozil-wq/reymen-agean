---
name: autonomous-ai-agents_telegram-gateway-monitor_references_polling-saglik-kontrolu
description: Polling Sağlık Kontrolü
title: "Autonomous Ai Agents Telegram Gateway Monitor References Polling Saglik Kontrolu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Polling Sağlık Kontrolü |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Polling Sağlık Kontrolü

Gateway çalışıyor görünür ama Telegram mesajları gelmiyorsa, polling donmuş olabilir.

### Tespit Adımları

1. Gateway process çalışıyor mu kontrol et (`hermes.exe` ModuleNotFoundError verir — gateway_state.json kullan):
   ```bash
   # Normal mod (interaktif oturum) — Python ile JSON parsing:
   PID=$(cat /c/Users/marko/AppData/Local/hermes/gateway_state.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('pid',''))")
   if ps -p "$PID" >/dev/null 2>&1; then
     echo "✓ Gateway PID $PID calisiyor (ps)"
   elif tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID"; then
     echo "✓ Gateway PID $PID calisiyor (tasklist ile dogrulandi)"
   else
     echo "✗ Gateway PID $PID CALISMIYOR"
   fi
   ```

   **Cron modu alternatifi** — Python inline `-c` flag'i + compound conditional (`if/elif/else`) paterni `pending_approval` tetikleyebilir. Cron modunda su sade yaklasimi kullan:
   ```bash
   # 1. PID'yi shell araclariyla JSON'dan cikar (Python kullanmadan):
   PID=$(grep '"pid"' /c/Users/marko/AppData/Local/hermes/gateway_state.json | grep -oE '[0-9]+' | head -1)
   # 2. Dogrudan tasklist ile dogrula (ps -p degil — false negative riski):
   if [ -n "$PID" ]; then
     tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID" && echo "✓ PID $PID calisiyor" || echo "✗ PID $PID CALISMIYOR"
   else
     echo "PID YOK (gateway_state.json bos veya okunamadi)"
   fi
   ```
   ⚠️ `python3 -c` tek basina calisir ama compound shell conditional (if/elif/else) + inline Python birlikte cron'da bloklanabilir. Ayrica `grep -oE '[0-9]+'` ile shell-only PID cikarma daha guvenilirdir.

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
# ⚠️ hermes.exe ModuleNotFoundError hatasi verir (bkz. references/hermes-cli-invocation.md).
# 1. Tercih — doğrudan scheduled task ile restart
powershell.exe -NoProfile -Command "Start-ScheduledTask -TaskName Hermes_Gateway"
# Bekle: 15-20 sn sonra dogrulamaya gec.
#
# 2. Alternatif — PYTHONPATH ile python -m (scheduled task calismazsa):
# cd /c/Users/marko/AppData/Local/hermes/hermes-agent
# HERMES_HOME=/c/Users/marko/AppData/Local/hermes PYTHONPATH=/c/Users/marko/AppData/Local/hermes/hermes-agent ./venv/Scripts/python.exe -m hermes_cli.main gateway run --replace
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
`send_message(target="telegram", message="Hermes polling test - <zaman>")`

Kullanıcıdan cevap yazmasını iste — eğer burdan görülüyorsa tamir tamamdır.
