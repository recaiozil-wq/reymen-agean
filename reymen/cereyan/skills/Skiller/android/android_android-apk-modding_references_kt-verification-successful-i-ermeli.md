
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Kt Verification Successful I Ermeli |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı "Verification successful" içermeli
```

Başarısızsa: APK bozuk, rebuild'e dön. `-f` flag'i ekle (üzerine yaz):

```bash
"$ZIPALIGN" -f -p 4 _build_unsigned.apk _build_aligned.apk
```

---

### Adım 5 — İMZALA

**UYARI:** jarsigner KULLANMA. jarsigner sadece v1 imza üretir. Android 7+ v2/v3 ister. **apksigner zorunlu.**

```bash
"$APKSIGNER" sign \
  --ks "$KEYSTORE" \
  --ks-key-alias "$KEYALIAS" \
  --ks-pass pass:${KSPASS} \
  --key-pass pass:${KSPASS} \
  _build_aligned.apk
```

**GATE 5:**
```bash
"$APKSIGNER" verify _build_aligned.apk