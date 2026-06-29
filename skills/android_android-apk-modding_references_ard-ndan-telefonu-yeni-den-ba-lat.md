
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Ard Ndan Telefonu Yeni Den Ba Lat |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Ardından telefonu YENİDEN BAŞLAT:
adb reboot && sleep 60 && adb wait-for-device
```

Normal kullanıcı uygulaması için:
```bash
adb install _build_aligned.apk
```

Eğer `INSTALL_FAILED_UPDATE_INCOMPATIBLE` alınırsa:
1. Sistem uygulaması mı kontrol et (`pm list packages -s`)
2. `adb uninstall -k --user 0 <pkg>` dene
3. Telefonu yeniden başlat
4. Tekrar dene
5. Hala hata alınıyorsa → root gerekir. Sistem uygulaması imza koruması kırılamaz.

**GATE 6a:** `adb shell pm list packages | grep com.package.name` ile kontrol et.

**6b — Logcat hazırlık + çalıştır:**
```bash
adb logcat -c                          # log temizle
adb shell monkey -p com.package.name 1  # uygulamayı aç