
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Notion_References_Api Version 2025 09 03 Databases Vs Data Sources |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## API Version 2025-09-03 — Databases vs Data Sources

- **Databases became data sources.** Use `/data_sources/` endpoints for queries and retrieval.
- **Two IDs per database:** `database_id` and `data_source_id`.
  - `database_id` when creating pages: `parent: {"database_id": "..."}`
  - `data_source_id` when querying: `POST /v1/data_sources/{id}/query`
- Search returns databases as `"object": "data_source"` with the `data_source_id` field.