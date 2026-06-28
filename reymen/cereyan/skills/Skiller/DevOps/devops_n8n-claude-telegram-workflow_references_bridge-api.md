
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_N8N Claude Telegram Workflow_References_Bridge Api |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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
- Telegram trigger -> bridge API -> Hermes -> bridge API -> n8n -> Telegram dönüş

---
