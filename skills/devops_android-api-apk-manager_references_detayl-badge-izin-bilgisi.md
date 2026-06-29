
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Detayl Badge Izin Bilgisi |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Detaylı badge/izin bilgisi
"/c/Users/marko/AppData/Local/Android/Sdk/build-tools/34.0.0/aapt" dump badging "<apk_yolu>"
```

**Çıktıda kontrol edilecekler:**
| Alan | Ne aranır |
|------|-----------|
| `package:` | Paket adı (örn. `com.livetranscriber`) |
| `targetSdkVersion:` | Telefonun Android sürümüne uygun mu? |
| `sdkVersion:` | Minimum SDK (eski cihazlar için 26+ yeterli) |
| `uses-permission:` | İzinler (RECORD_AUDIO, INTERNET, vb.) |
| `launchable-activity:` | Ana Activity adı |
| `application-label:` | Uygulama görünen adı |