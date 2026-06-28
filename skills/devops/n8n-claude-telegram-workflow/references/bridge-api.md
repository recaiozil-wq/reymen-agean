---
skill_id: 118169e47a66
usage_count: 1
last_used: 2026-06-16
---
# Bridge API Referans

## Sunucu
- `/_bridge/server.py`
- Port: `15680`
- Host: `127.0.0.1`

## Sağlık
```
GET http://127.0.0.1:15680/health
```

## Endpoint Detayları

### Kuyruğa Ekle
```
POST http://127.0.0.1:15680/_bridge/queue/{chat_id}.json
Body: {"chat_id": "...", "text": "..."}
```

### Cevap Al
```
GET http://127.0.0.1:15680/_bridge/answers/{chat_id}.json
```

### Klasörler
- `/_bridge/queue/` - gelen mesajlar
- `/_bridge/answers/` - giden cevaplar

## n8n Entegrasyon
- `n8n/workflow.json` import edilebilir workflow şablonu
- Telegram trigger -> bridge API -> ReYMeN -> bridge API -> n8n -> Telegram dönüş

---
