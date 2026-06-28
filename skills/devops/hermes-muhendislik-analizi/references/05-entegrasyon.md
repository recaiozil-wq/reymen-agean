---
skill_id: fd6e619f9e07
usage_count: 1
last_used: 2026-06-16
---
# Bölüm 5: Entegrasyon ve Operasyon

## Telegram Entegrasyonu

TelegramBot (dinleyici):
- Long-polling, timeout=30
- Güvenlik: sadece TELEGRAM_CHAT_ID'den gelenleri kabul et
- /sor <soru> -> KnowledgeQA.ask() -> Vault RAG
- /durum -> Vault belge sayısı
- Başarılı RAG -> daily note'a yaz

Notifier (yayıncı):
- Skill üretildi -> SUCCESS
- Bütçe %80 -> WARNING
- Quarantine -> ERROR

## Obsidian Engine

| Metod | Görev |
|---|---|
| read_note(path) | YAML frontmatter + tag + wikilink ayrıştırma |
| find_notes(tag, contains) | Yapısal arama (ChromaDB'den bağımsız) |
| backlinks(note) | Bu notaya kimler bağlı? O(n) tarama |
| build_moc(category) | Kategori MOC dosyası yenile |
| append_to_daily(entry) | Bugünün günlük notuna ekle |
| gather_context(topic) | Brain prompt için bağlam topla |

## Kaynak Adaptörleri

| Kaynak | İşlem |
|---|---|
| github | --depth 1 clone -> README + klasörler -> 40 unit |
| web | HTML -> düz metin -> 1 unit |
| file | md/py/txt okuma -> 1 unit |
| txt | Düz metin yapıştırma -> 1 unit |
| youtube | video_pipeline'a devredilir |

## Bütçe ve VRAM

API Maliyetleri (1M token):
- DeepSeek: $0.27 giriş / $1.10 çıkış
- Claude Sonnet: $3.00 / $15.00
- Ollama/lokal: $0.00

VRAM: BoundedSemaphore(MAX=1), model_session() context manager, OOM tespiti + purge_all()
