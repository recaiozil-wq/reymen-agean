
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Android Apk Hardening_References_Smali De Lisans Premium Ile Ilgili T M Referanslar Tar |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Smali'de lisans/premium ile ilgili tüm referansları tar
grep -r -i "premium\|license\|pro\|unlock\|subscription\|purchase" _audit/smali/ | grep -v ".line" | head -30
```

**SORULAR:**
```
- Premium kararı client'ta mı?    → KIRILGAN
- Sunucu doğrulaması var mı?      → Token replay'e açık mı?
- SharedPreferences mı?           → Tek satır
- root tespiti var mı?            → Atlanabilir mi?
- Integrity API kullanılıyor mu?  → Verdict client'ta mı doğrulanıyor?
```

### 1c — String ve sabitler

```bash