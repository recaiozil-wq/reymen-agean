
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Sla Format Lcom Eski Paket Class |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Slaş format (Lcom/eski/paket/Class;)
grep -rl "com/eski/paket/yolu" smali/ smali_classes2/ | \
  xargs sed -i 's|com/eski/paket/yolu|com/yeni/paket/yolu|g'