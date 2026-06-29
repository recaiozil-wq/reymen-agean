---
name: autonomous-ai-agents_telegram-gateway-monitor_references_gateway-state-json-corruption
description: gateway_state.json Kirlenmesi
title: "Autonomous Ai Agents Telegram Gateway Monitor References Gateway State Json Corruption"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | gateway_state.json Kirlenmesi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## gateway_state.json Kirlenmesi

gateway_state.json dosyası, dış test run'ları veya hatalı state yazmaları nedeniyle **gerçek gateway durumunu yansıtmayan** hale gelebilir. Gateway aslında çalışırken state.json "fatal" gösterir, ölü PID tutar, argv alanı pytest/başka komutlarla bozulur.

### Belirti

- `gateway_state.json` → `telegram.state: "fatal"`, `error_code: "telegram_polling_conflict"`, PID ölü
- `gateway_state.json` → `argv` alanı pytest komutu veya başka bir program gösteriyor
- Gateway log'u (`gateway.log`) hala yeni inbound mesajlar içeriyor (son birkaç dakika)
- `gateway-exit-diag.log` son `gateway.start` kaydındaki PID hala çalışıyor

### Kök Neden

Bir dış süreç (pytest test run'ı, Hermes test suite'i, manuel hata ayıklama) `gateway_state.json`'ı kendi PID'i ve state'i ile üzerine yazar. Gateway'in kendi PID yönetimi bypass edilir. Gateway restart edilmezse çalışmaya devam eder ama state.json yanlış kalır.

2026-06-17'de yaşandı: `argv` = `["pytest", "test_status.py", ...]`, PID 49208 (ölü), telegram state "fatal" — gerçekte PID 29560 çalışıyor, Telegram connected, son inbound mesaj 20:36.

### Teşhis Akışı

```bash
# 1. gateway_state.json'daki PID'yi oku
PID=$(grep '"pid"' /c/Users/marko/AppData/Local/hermes/gateway_state.json | grep -oE '[0-9]+' | head -1)
echo "State.json PID: $PID"

# 2. Bu PID çalışıyor mu? (tasklist ile, ps -p DEĞİL)
if [ -n "$PID" ]; then
  tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID" && echo "PID $PID calisiyor" || echo "PID $PID CALISMIYOR"
else
  echo "PID YOK"
fi

# 3. Eğer ölüyse, gateway-exit-diag.log'daki son gateway.start PID'ini bul
echo "--- gateway-exit-diag.log son gateway.start ---"
grep '"gateway.start"' /c/Users/marko/AppData/Local/hermes/logs/gateway-exit-diag.log | tail -5 | python3 -c "
import sys, json
for line in sys.stdin:
    if '\"gateway.start\"' in line:
        # find the part between { and }
        import re
        m = re.search(r'({.*})', line.strip())
        if m:
            d = json.loads(m.group(1))
            print(f'  PID={d.get(\"pid\")} time={d.get(\"ts\",\"?\")} replace={d.get(\"replace\",False)}')
"

# 4. Bu PID'yi tasklist ile doğrula
REAL_PID=$(grep '"gateway.start"' /c/Users/marko/AppData/Local/hermes/logs/gateway-exit-diag.log | tail -1 | grep -oE '"pid": [0-9]+' | grep -oE '[0-9]+')
if [ -n "$REAL_PID" ]; then
  tasklist //FI "PID eq $REAL_PID" 2>/dev/null | grep -q "$REAL_PID" && echo "GERCEK PID $REAL_PID CALISIYOR" || echo "GERCEK PID $REAL_PID de calismiyor"
fi

# 5. Log'da son inbound mesaj var mı kontrol et (gateway gerçekten çalışıyor mu?)
echo "--- Log son inbound mesaj ---"
tail -10 /c/Users/marko/AppData/Local/hermes/logs/gateway.log | grep "inbound message:" | tail -3
```

### Onarım

gateway çalışıyorsa (log canlı, inbound mesajlar var), restart GEREKMEZ. Sadece state.json'u düzelt:

```bash
python3 -c "
import json
path = r'C:\Users\marko\AppData\Local\hermes\gateway_state.json'
data = json.load(open(path))
data['pid'] = <REAL_PID>       # gateway-exit-diag.log'dan alınan gerçek PID
data['gateway_state'] = 'running'
data['platforms']['telegram']['state'] = 'connected'
data['platforms']['telegram']['error_code'] = None
data['platforms']['telegram']['error_message'] = None
data['argv'] = ['python', '-m', 'hermes_cli.main', 'gateway', 'run']
json.dump(data, open(path, 'w'), indent=2)
print('OK - gateway_state.json fixed')
"
```

### Önleme

- `zorunlu-ad-mlar.md` Step 0'daki PID kontrolü "CALISMIYOR" dediğinde hemen restart'a atlama — önce exit-diag.log'u kontrol et.
- `gateway_state.json`'daki `argv` alanı gateway dışı bir komut gösteriyorsa → state.json kirli demektir.
