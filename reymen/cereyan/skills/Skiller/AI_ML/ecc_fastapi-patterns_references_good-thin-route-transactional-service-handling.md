
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Fastapi Patterns_References_Good Thin Route Transactional Service Handling |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Good: thin route, transactional service handling.
@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: DbDep):
    try:
        return await UserService(db).create(payload)
    except DuplicateUserError:
        raise HTTPException(status_code=400, detail="Email already registered")