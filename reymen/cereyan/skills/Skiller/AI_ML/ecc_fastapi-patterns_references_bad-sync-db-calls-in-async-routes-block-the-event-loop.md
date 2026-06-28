
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Fastapi Patterns_References_Bad Sync Db Calls In Async Routes Block The Event Loop |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Bad: sync DB calls in async routes block the event loop.
@router.get("/items/")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()