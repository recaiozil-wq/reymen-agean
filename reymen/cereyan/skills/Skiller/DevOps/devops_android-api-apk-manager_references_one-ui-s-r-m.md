
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_One Ui S R M |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# One UI sürümü
adb shell getprop ro.build.version.oneui
```

"Telefonunuzla uyumlu değil" hata sebepleri:
1. **Split APK referansı** — manifest'te `isSplitRequired=true` veya `split` niteliği var
2. **Native lib mimari uyuşmazlığı** — APK sadece `arm64-v8a` ama cihaz `x86` veya vice versa
3. **minSdk > cihaz SDK'sı** — APK Android 14+ gerektiriyor ama cihaz Android 13
4. **targetSdk 36 (çok yeni)** — Android 16'da hedef SDK 36 yeni kısıtlamalar getirir, 35 kullan