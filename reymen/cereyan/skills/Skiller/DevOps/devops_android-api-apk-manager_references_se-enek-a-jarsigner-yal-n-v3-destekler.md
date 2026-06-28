
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Se Enek A Jarsigner Yal N V3 Destekler |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Seçenek A — jarsigner (yalın, V3 destekler)
keytool -genkey -v -keystore my.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my.keystore rebuilt_unsigned.apk myalias
jarsigner -verify -verbose rebuilt_unsigned.apk