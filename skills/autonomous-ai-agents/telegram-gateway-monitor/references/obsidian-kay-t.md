---
skill_id: 2b2625c03572
usage_count: 1
last_used: 2026-06-16
---
## Obsidian kayıt

Kullanıcının Obsidian vault yolunu `.env`'de güncelle:
- Anahtar: `OBSIDIAN_VAULT_PATH`
- Not dosyası: `<vault>/Telegram Gateway Monitor.md`

Her test sonrasında aşağıdaki satırı bu dosyaya ekle (`mcp_obsidian_vault_append` kullan — encoding sorunsuz, Türkçe karakterler bozulmaz):
- İçerik: `- <tarih> <saat> — <sonuç>` (örn. `2026-06-02 19:36 — Telegram bağlantı testi başarılı.`)
- Kullanım: `mcp_obsidian_vault_append(path="Telegram Gateway Monitor.md", content="- <tarih> <saat> — <sonuç>")`

⚠️ `write_file`/`read_file`/`patch` tool'ları **native Windows yolu** bekler (`C:\Users\marko\...`), MSYS `/c/Users/` değil. `mcp_obsidian_vault_append` ise vault-relative path bekler (sadece dosya adı yeterli).