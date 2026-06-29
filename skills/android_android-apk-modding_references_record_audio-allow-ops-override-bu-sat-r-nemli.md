
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Record_Audio Allow Ops Override Bu Sat R Nemli |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

#        "RECORD_AUDIO: allow" (ops override, bu satır önemli)
```

Bu, uygulamanın arka planda da ses kaydetmesine izin verir. Özellikle "ekran kilitlenince kayıt dursun" sorununu çözebilir.

**İşe yaramazsa:** Uygulamayı kapatıp aç, tekrar dene. Bazı uygulamalar `foreground`→`allow` değişikliğini runtime'da okumaz, restart gerekir.

**2. Bildirim iznini kontrol et:**
```bash
adb shell "appops get com.target.package POST_NOTIFICATION"
```

**3. Uygulamanın debuggable durumunu değiştir (root'suz çalışmaz):**
```bash