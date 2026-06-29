# 📖 Kullanim Kilavuzu

## Temel Kullanim

### Sohbet Modu

reymen chat

ReYMeN ile dogal dilde konusabilirsiniz. Dosya islemleri, terminal komutlari,
web aramasi gibi islemleri otomatik olarak yapar.

### Web Arayuzu

reymen web

Tarayicida http://localhost:5000 adresini acin. JWT kimlik dogrulama ile
(admin/reymen) paneli kullanabilirsiniz.

## Gelismis Kullanim

### Model Degistirme

reymen model
reymen model deepseek
reymen model openai/gpt-4

### Kanban Board

reymen kanban board create "Proje X"
reymen kanban add "Backend gelistirme" --column backlog --priority high
reymen kanban claim KART_ID
reymen kanban done KART_ID
reymen kanban swarm baslat GOREV_TANIMI

### Cron Gorevleri

reymen cron add "30m" "Sistem kontrolu"
reymen cron add "0 9 * * *" "Gunluk rapor"

### Plugin Kullanimi

reymen plugin list
reymen plugin enable web_search_provider
reymen plugin enable image_gen_provider

### MCP Sunucu

python -m reymen.core.mcp_server --transport http --port 9000
python -m reymen.core.mcp_server --transport stdio

### Open WebUI Entegrasyonu

Open WebUI'de Custom OpenAI API ekleyin:
URL: http://localhost:5000/v1
API Key: reymen

## Guvenlik

### Approvals Sistemi
Varsayilan olarak destructive komutlar icin onay istenir.
--yolo bayragi ile atlanabilir.

### Secrets Redaction
Tool ciktilari API key, token, email gibi hassas bilgileri otomatik maskeler.

## Self-Improvement

reymen quality
reymen quality --trend
