
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Fastapi Patterns_References_Bad Business Logic Inside Route Handlers |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Bad: business logic inside route handlers.
@router.post("/users/")
async def create_user(payload: UserCreate, db: DbDep):
    hashed = bcrypt.hash(payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    return user