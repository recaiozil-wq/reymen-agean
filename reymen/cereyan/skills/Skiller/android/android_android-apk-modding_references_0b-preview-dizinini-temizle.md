
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_0B Preview Dizinini Temizle |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 0b — Preview dizinini temizle
rm -rf _preview/
```

**GATE 0:** Eğer targetSdk > cihaz SDK'sı → düşürmeyi not et. Native libs varsa split merge gerekebilir. Rapor çıktısı üret, kullanıcıya neyle uğraştığını göster.

**SİSTEM UYGULAMASI KONTROLÜ (Pipeline'ın en kritik kararı):**
```bash
adb shell pm list packages -s | grep com.target.package