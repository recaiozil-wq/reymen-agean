
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Cihaz G R N Yorsa |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Cihaz görünüyorsa:
\"/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe\" install \"<apk_yolu>\"
```

### 2. ADB cihaz görmüyorsa — USB Debugging AÇTIR

Kullanıcı "ben beceremem" dese bile şu adımları **tek tek, net** söyle:

```
1. Telefonda: Ayarlar → Telefon hakkında → Yazılım bilgisi
2. "Yapı numarası"na 7 kere tıkla (Geliştirici seçenekleri açılır)
3. Geri gel → Geliştirici seçenekleri → USB Debugging AÇ
4. USB'yi çıkar tak, telefonda "İzin ver" de
```

### 3. Telegram üzerinden parçalı gönder (ADB yoksa)

**Kural:** 15MB+ APK'yı `send_message` ile MEDIA: olarak göndermek timeout yiyor.

Çözüm: 9MB'lık parçalara böl, her parçayı ayrı `send_message` ile gönder:
```bash
split -b 9M signed.apk apk9_